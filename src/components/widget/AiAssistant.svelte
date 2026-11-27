<script lang="ts">
import Icon from "@iconify/svelte";
import { onMount, tick } from "svelte";

interface Props {
	"client:only"?: "svelte";
}

let {}: Props = $props();

const API_BASE = "https://111.230.43.176/blog-ai";
const OWNER_TOKEN_KEY = "blog-ai-owner-token";

interface Msg {
	role: "user" | "assistant";
	content: string;
	streaming?: boolean;
	error?: boolean;
}

let isOpen = $state(false);
let showKeyBar = $state(false);
let ownerToken = $state("");
let ownerInput = $state("");
let keyFeedback = $state("");

let isOwner = $state(false);
let remaining = $state(5);
let limit = $state(5);
let statusLoaded = $state(false);

let input = $state("");
let isSending = $state(false);
let messages = $state<Msg[]>([]);
let hasArticleContext = $state(false);
let scrollEl: HTMLDivElement | null = null;
let inputEl: HTMLTextAreaElement | null = null;

function escapeHtml(raw: string): string {
	return raw
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;");
}

function renderMessageHtml(raw: string): string {
	let html = escapeHtml(raw);
	// Fenced code blocks
	html = html.replace(/```[\w-]*\n([\s\S]*?)```/g, (_m, code) => {
		return `<pre class="my-1.5 rounded-lg bg-slate-900/90 text-slate-100 p-2.5 text-[0.75rem] overflow-x-auto font-mono-tech leading-relaxed"><code>${code.trimEnd()}</code></pre>`;
	});
	// Inline code
	html = html.replace(/`([^`\n]+)`/g, '<code class="px-1 py-0.5 rounded bg-black/10 dark:bg-white/10 font-mono-tech text-[0.76rem]">$1</code>');
	// Bold
	html = html.replace(/\*\*([^*\n]+)\*\*/g, '<strong class="font-semibold">$1</strong>');
	// Line breaks
	html = html.replace(/\n/g, "<br>");
	return html;
}

function getPageContext(): { pageTitle: string; pagePath: string; pageContext: string } {
	const pageTitle = document.title || "";
	const pagePath = window.location.pathname || "/";
	const mdEl = document.querySelector<HTMLElement>(".markdown-content");
	const rawText = mdEl?.innerText?.replace(/\s+\n/g, "\n").trim() || "";
	hasArticleContext = rawText.length > 80;
	return {
		pageTitle,
		pagePath,
		pageContext: rawText.slice(0, 4800),
	};
}

async function refreshStatus() {
	try {
		const headers: Record<string, string> = {};
		if (ownerToken) headers["X-Owner-Token"] = ownerToken;
		const res = await fetch(`${API_BASE}/status`, { headers });
		if (!res.ok) return;
		const data = await res.json();
		isOwner = Boolean(data.owner);
		limit = typeof data.limit === "number" ? data.limit : 5;
		remaining = typeof data.remaining === "number" ? data.remaining : limit;
		statusLoaded = true;
	} catch {
		statusLoaded = false;
	}
}

async function scrollToBottom() {
	await tick();
	if (scrollEl) {
		scrollEl.scrollTop = scrollEl.scrollHeight;
	}
}

async function openChat() {
	isOpen = true;
	getPageContext();
	void refreshStatus();
	await tick();
	inputEl?.focus();
	await scrollToBottom();
}

function closeChat() {
	isOpen = false;
	showKeyBar = false;
}

function toggleChat() {
	if (isOpen) closeChat();
	else void openChat();
}

async function saveOwnerToken() {
	const trimmed = ownerInput.trim();
	ownerToken = trimmed;
	try {
		if (trimmed) localStorage.setItem(OWNER_TOKEN_KEY, trimmed);
		else localStorage.removeItem(OWNER_TOKEN_KEY);
	} catch {}
	keyFeedback = "验证中...";
	await refreshStatus();
	if (!trimmed) {
		keyFeedback = "已退出站长模式";
		showKeyBar = false;
	} else if (isOwner) {
		keyFeedback = "已解锁站长免限流模式";
		setTimeout(() => {
			showKeyBar = false;
			keyFeedback = "";
		}, 900);
	} else {
		keyFeedback = "口令不匹配，仍按访客限流";
	}
}

async function sendPrompt(textOverride?: string) {
	const text = (textOverride ?? input).trim();
	if (!text || isSending) return;
	if (!textOverride) input = "";

	const history = messages
		.filter((m) => !m.error && m.content.trim() !== "")
		.map((m) => ({ role: m.role, content: m.content }));

	messages = [...messages, { role: "user", content: text }, { role: "assistant", content: "", streaming: true }];
	const assistantIdx = messages.length - 1;
	isSending = true;
	await scrollToBottom();

	const ctx = getPageContext();
	const headers: Record<string, string> = { "Content-Type": "application/json" };
	if (ownerToken) headers["X-Owner-Token"] = ownerToken;

	try {
		const res = await fetch(`${API_BASE}/chat`, {
			method: "POST",
			headers,
			body: JSON.stringify({
				messages: [...history, { role: "user", content: text }],
				...ctx,
			}),
		});

		if (!res.ok) {
			let errMsg = `请求失败（HTTP ${res.status}）`;
			try {
				const errJson = await res.json();
				if (errJson?.error) errMsg = errJson.error;
				if (typeof errJson?.remaining === "number") remaining = errJson.remaining;
			} catch {}
			messages[assistantIdx] = { role: "assistant", content: errMsg, error: true };
			isSending = false;
			await scrollToBottom();
			return;
		}

		const reader = res.body?.getReader();
		if (!reader) {
			messages[assistantIdx] = { role: "assistant", content: "浏览器不支持流式读取。", error: true };
			isSending = false;
			return;
		}

		const decoder = new TextDecoder();
		let buffer = "";
		let accumulated = "";

		while (true) {
			const { value, done } = await reader.read();
			if (done) break;
			buffer += decoder.decode(value, { stream: true });
			const lines = buffer.split("\n");
			buffer = lines.pop() || "";

			for (const rawLine of lines) {
				const line = rawLine.trim();
				if (!line.startsWith("data:")) continue;
				const payloadStr = line.slice(5).trim();
				if (!payloadStr) continue;
				try {
					const evt = JSON.parse(payloadStr);
					if (typeof evt.delta === "string" && evt.delta) {
						accumulated += evt.delta;
						messages[assistantIdx] = {
							role: "assistant",
							content: accumulated,
							streaming: true,
						};
						await scrollToBottom();
					}
					if (evt.done) {
						if (typeof evt.remaining === "number") remaining = evt.remaining;
						if (typeof evt.owner === "boolean") isOwner = evt.owner;
					}
				} catch {}
			}
		}

		messages[assistantIdx] = {
			role: "assistant",
			content: accumulated || "没有收到模型输出，请重试。",
			streaming: false,
			error: !accumulated,
		};
		if (accumulated) {
			window.dispatchEvent(new CustomEvent("bocchi:react", { detail: { type: "ai-reply" } }));
		}
	} catch {
		messages[assistantIdx] = {
			role: "assistant",
			content: "网络连接异常，请稍后再试。",
			error: true,
		};
	} finally {
		isSending = false;
		await scrollToBottom();
	}
}

function handleKeydown(e: KeyboardEvent) {
	if (e.key === "Enter" && !e.shiftKey) {
		e.preventDefault();
		void sendPrompt();
	}
}

onMount(() => {
	try {
		const saved = localStorage.getItem(OWNER_TOKEN_KEY) || "";
		ownerToken = saved;
		ownerInput = saved;
	} catch {}
	getPageContext();

	const onOpen = () => toggleChat();
	window.addEventListener("bocchi:chat", onOpen);
	return () => {
		window.removeEventListener("bocchi:chat", onOpen);
	};
});

let quickPrompts = $derived(
	hasArticleContext
		? ["总结一下这篇文章的核心做法", "这里面最容易踩的坑是什么？"]
		: ["这个博客里主要写了哪些项目？", "LanAgent 的断点续跑是怎么实现的？"],
);
</script>

<!-- Mobile & tablet floating trigger (desktop uses Bocchi's dock 问答 button) -->
<button
	type="button"
	onclick={toggleChat}
	aria-label="打开波奇 AI 小助手"
	class="lg:hidden fixed right-4 bottom-4 z-40 bocchi-dock inline-flex items-center gap-1.5 rounded-full px-3.5 py-2 text-xs font-semibold text-90 hover:text-[var(--primary)] transition active:scale-95 cursor-pointer"
>
	<span class="w-2 h-2 rounded-full bg-pink-400 animate-soft-pulse"></span>
	<span>问波奇</span>
</button>

<!-- Studio Window AI Chat Panel -->
{#if isOpen}
	<section
		id="bocchi-ai-panel"
		aria-label="波奇 AI 小助手"
		class="card-base fixed z-50 left-3 right-3 bottom-16 sm:left-auto sm:right-5 sm:bottom-5 lg:left-[17.25rem] lg:right-auto lg:bottom-[3.25rem] w-auto sm:w-[23.5rem] flex flex-col overflow-hidden shadow-2xl"
		style="max-height: min(32rem, calc(100vh - 6rem));"
	>
		<!-- Window Chrome -->
		<div class="win-chrome">
			<div class="flex items-center gap-2 min-w-0">
				<span class="win-dots win-dots-vivid" aria-hidden="true"><span></span><span></span><span></span></span>
				<span class="font-mono-tech text-[0.68rem] text-75 font-semibold truncate">~/bocchi-ai</span>
				{#if statusLoaded}
					{#if isOwner}
						<span class="font-mono-tech text-[0.6rem] px-1.5 py-0.5 rounded-md bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 shrink-0">
							站长 · 不限次
						</span>
					{:else}
						<span class="font-mono-tech text-[0.6rem] px-1.5 py-0.5 rounded-md bg-[var(--btn-regular-bg)] text-[var(--btn-content)] shrink-0">
							剩 {remaining}/{limit} 次/h
						</span>
					{/if}
				{/if}
			</div>
			<div class="flex items-center gap-1 shrink-0">
				<button
					type="button"
					onclick={() => (showKeyBar = !showKeyBar)}
					title="站长口令（解锁不限次）"
					aria-label="站长口令"
					class="inline-flex items-center justify-center w-6 h-6 rounded-md text-50 hover:text-[var(--primary)] hover:bg-black/5 dark:hover:bg-white/10 transition cursor-pointer"
					class:text-emerald-500={isOwner}
				>
					<Icon icon="material-symbols:key-outline-rounded" class="text-[0.95rem]" />
				</button>
				{#if messages.length > 0}
					<button
						type="button"
						onclick={() => (messages = [])}
						title="清空对话"
						aria-label="清空对话"
						class="inline-flex items-center justify-center w-6 h-6 rounded-md text-50 hover:text-[var(--primary)] hover:bg-black/5 dark:hover:bg-white/10 transition cursor-pointer"
					>
						<Icon icon="material-symbols:delete-outline-rounded" class="text-[0.95rem]" />
					</button>
				{/if}
				<button
					type="button"
					onclick={closeChat}
					title="关闭窗口"
					aria-label="关闭窗口"
					class="inline-flex items-center justify-center w-6 h-6 rounded-md text-sm text-50 hover:text-[var(--primary)] hover:bg-black/5 dark:hover:bg-white/10 transition cursor-pointer"
				>
					×
				</button>
			</div>
		</div>

		<!-- Collapsible Owner Token Bar -->
		{#if showKeyBar}
			<div class="px-3 py-2 border-b border-[var(--card-border)] bg-black/[0.025] dark:bg-white/[0.03] flex flex-col gap-1.5">
				<div class="flex items-center gap-1.5">
					<input
						type="password"
						bind:value={ownerInput}
						placeholder="输入站长口令（留空保存即退出）"
						class="flex-1 min-w-0 rounded-lg border border-[var(--card-border)] bg-white/80 dark:bg-slate-900/70 px-2.5 py-1 text-xs text-90 outline-none focus:border-[var(--primary)]"
						onkeydown={(e) => { if (e.key === "Enter") void saveOwnerToken(); }}
					/>
					<button
						type="button"
						onclick={() => void saveOwnerToken()}
						class="rounded-lg px-2.5 py-1 text-xs font-medium text-white bg-[var(--primary)] hover:brightness-110 transition cursor-pointer shrink-0"
					>
						保存
					</button>
				</div>
				{#if keyFeedback}
					<div class="font-mono-tech text-[0.65rem] text-50">{keyFeedback}</div>
				{/if}
			</div>
		{/if}

		<!-- Messages Area -->
		<div bind:this={scrollEl} class="flex-1 overflow-y-auto px-3.5 py-3 space-y-2.5 min-h-[14rem] max-h-[21rem]">
			{#if messages.length === 0}
				<div class="rounded-xl border border-dashed border-[var(--line-divider)] bg-black/[0.015] dark:bg-white/[0.02] p-3">
					<div class="flex items-center gap-2 mb-1.5">
						<img src="/images/chibi/bocchi-default.webp" alt="波奇" width="32" height="34" class="w-8 h-8 object-contain" />
						<div>
							<div class="text-xs font-semibold text-90">波奇 AI 小助手</div>
							<div class="font-mono-tech text-[0.64rem] text-50">
								{hasArticleContext ? "已自动读取当前文章内容" : "支持站内文章与技术问答"}
							</div>
						</div>
					</div>
					<p class="text-xs text-75 leading-relaxed mb-2.5">
						可以直接问当前文章里的配置细节，或者博客里提到的 Go / Agent / VPS 相关问题。访客每小时限 {limit} 次提问。
					</p>
					<div class="flex flex-wrap gap-1.5">
						{#each quickPrompts as q}
							<button
								type="button"
								onclick={() => void sendPrompt(q)}
								class="text-left rounded-lg border border-[var(--card-border)] bg-white/75 dark:bg-white/5 hover:border-[var(--primary)]/50 hover:text-[var(--primary)] px-2.5 py-1 text-[0.72rem] text-75 transition cursor-pointer"
							>
								{q}
							</button>
						{/each}
					</div>
				</div>
			{:else}
				{#each messages as msg}
					<div class="flex" class:justify-end={msg.role === "user"} class:justify-start={msg.role === "assistant"}>
						{#if msg.role === "user"}
							<div class="max-w-[84%] rounded-2xl rounded-br-sm px-3 py-2 text-[0.8rem] leading-relaxed text-white bg-[var(--primary)] break-words">
								{msg.content}
							</div>
						{:else}
							<div
								class={`max-w-[90%] rounded-2xl rounded-bl-sm px-3 py-2 text-[0.8rem] leading-relaxed break-words border ${
									msg.error
										? "border-rose-400/60 text-rose-600 dark:text-rose-300 bg-rose-50/80 dark:bg-rose-950/40"
										: "border-[var(--card-border)] bg-black/[0.03] dark:bg-white/[0.05] text-90"
								}`}
							>
								{@html renderMessageHtml(msg.content)}
								{#if msg.streaming}
									<span class="terminal-cursor" aria-hidden="true"></span>
								{/if}
							</div>
						{/if}
					</div>
				{/each}
			{/if}
		</div>

		<!-- Input Bar -->
		<div class="p-2.5 border-t border-[var(--card-border)] bg-black/[0.015] dark:bg-white/[0.02]">
			<div class="flex items-end gap-2">
				<textarea
					bind:this={inputEl}
					bind:value={input}
					onkeydown={handleKeydown}
					rows="1"
					placeholder="输入问题，Enter 发送..."
					disabled={isSending}
					class="flex-1 resize-none rounded-xl border border-[var(--card-border)] bg-white/85 dark:bg-slate-900/75 px-3 py-2 text-xs text-90 placeholder:text-50 outline-none focus:border-[var(--primary)] max-h-24 leading-relaxed"
				></textarea>
				<button
					type="button"
					onclick={() => void sendPrompt()}
					disabled={isSending || !input.trim()}
					aria-label="发送"
					class="inline-flex items-center justify-center h-8 px-3 rounded-xl text-xs font-semibold text-white bg-[var(--primary)] hover:brightness-110 disabled:opacity-45 disabled:cursor-not-allowed transition cursor-pointer shrink-0 active:scale-95"
				>
					{isSending ? "..." : "发送"}
				</button>
			</div>
		</div>
	</section>
{/if}
