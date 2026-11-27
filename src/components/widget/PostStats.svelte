<script lang="ts">
import { onMount } from "svelte";

interface Props {
	slug: string;
	"client:only"?: "svelte";
}

let { slug }: Props = $props();

const API_BASE = "https://111.230.43.176/blog-ai";

let views = $state<number | null>(null);
let likes = $state<number | null>(null);
let liked = $state(false);
let liking = $state(false);
let failed = $state(false);

onMount(async () => {
	try {
		const res = await fetch(`${API_BASE}/stats/view`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ slug }),
		});
		if (!res.ok) throw new Error("stats failed");
		const data = await res.json();
		views = typeof data.views === "number" ? data.views : 0;
		likes = typeof data.likes === "number" ? data.likes : 0;
		liked = Boolean(data.liked);
	} catch {
		failed = true;
	}
});

async function handleLike() {
	if (liked || liking) return;
	liking = true;
	try {
		const res = await fetch(`${API_BASE}/stats/like`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ slug }),
		});
		if (!res.ok) throw new Error("like failed");
		const data = await res.json();
		views = typeof data.views === "number" ? data.views : views;
		likes = typeof data.likes === "number" ? data.likes : likes;
		liked = Boolean(data.liked);
	} catch {
		// keep silent if offline
	} finally {
		liking = false;
	}
}
</script>

{#if !failed}
	<div class="inline-flex items-center gap-2 font-mono-tech text-xs">
		<span
			class="inline-flex items-center gap-1.5 rounded-xl px-2.5 py-1.5 bg-black/[0.03] dark:bg-white/[0.05] text-60 border border-[var(--card-border)]"
			title="文章阅读量（同 IP 10 分钟内去重）"
		>
			<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/>
				<circle cx="12" cy="12" r="3"/>
			</svg>
			<span>{views === null ? "…" : views}</span>
		</span>

		<button
			type="button"
			onclick={handleLike}
			disabled={liked || liking}
			aria-pressed={liked}
			class={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 font-medium transition cursor-pointer active:scale-95 border ${
				liked
					? "bg-rose-500/12 text-rose-600 dark:text-rose-300 border-rose-500/30 cursor-default"
					: "btn-regular border-transparent"
			}`}
		>
			<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill={liked ? "currentColor" : "none"} stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
			</svg>
			<span>{liked ? "已赞" : "点赞"} {likes === null ? "" : likes}</span>
		</button>
	</div>
{/if}
