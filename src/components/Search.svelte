<script lang="ts">
import { DARK_MODE, LIGHT_MODE } from "@constants/constants.ts";
import I18nKey from "@i18n/i18nKey";
import { i18n } from "@i18n/translation";
import Icon from "@iconify/svelte";
import { setTheme } from "@utils/setting-utils.ts";
import { url } from "@utils/url-utils.ts";
import { onMount } from "svelte";
import type { SearchResult } from "@/global";

interface QuickAction {
	id: string;
	label: string;
	hint: string;
	icon: string;
	href?: string;
	run?: () => void;
}

let keywordDesktop = "";
let keywordMobile = "";
let result: SearchResult[] = [];
let isSearching = false;
let pagefindLoaded = false;
let initialized = false;
let activeIndex = -1;
let panelOpen = false;
let desktopInput: HTMLInputElement | null = null;
let mobileInput: HTMLInputElement | null = null;

const fakeResult: SearchResult[] = [
	{
		url: url("/"),
		meta: {
			title: "开发模式示例搜索结果",
		},
		excerpt: "本地 <mark>dev</mark> 模式下不加载 Pagefind 索引，请运行 build && preview 测试。",
	},
];

const quickActions: QuickAction[] = [
	{ id: "home", label: "回到主页", hint: "/", icon: "material-symbols:home-outline-rounded", href: url("/") },
	{ id: "archive", label: "浏览文章归档", hint: "/archive/", icon: "material-symbols:inventory-2-outline-rounded", href: url("/archive/") },
	{ id: "about", label: "关于 lannokaede", hint: "/about/", icon: "material-symbols:person-outline-rounded", href: url("/about/") },
	{
		id: "theme",
		label: "切换亮色 / 暗色模式",
		hint: "Theme",
		icon: "material-symbols:contrast-rounded",
		run: () => {
			const isDark = document.documentElement.classList.contains("dark");
			setTheme(isDark ? LIGHT_MODE : DARK_MODE);
		},
	},
	{
		id: "bocchi",
		label: "展开 / 收起角落 Q 版波奇",
		hint: "2D",
		icon: "material-symbols:music-note-rounded",
		run: () => {
			window.dispatchEvent(new CustomEvent("bocchi:toggle"));
		},
	},
];

function navigateTo(href: string) {
	closePanel();
	window.location.href = href;
}

const openPanel = (focusInput = false) => {
	const panel = document.getElementById("search-panel");
	if (!panel) return;
	panel.classList.remove("float-panel-closed");
	panelOpen = true;
	activeIndex = 0;
	if (focusInput) {
		requestAnimationFrame(() => {
			if (window.innerWidth >= 1024 && desktopInput) {
				desktopInput.focus();
				desktopInput.select();
			} else if (mobileInput) {
				mobileInput.focus();
				mobileInput.select();
			}
		});
	}
};

const closePanel = () => {
	const panel = document.getElementById("search-panel");
	if (!panel) return;
	panel.classList.add("float-panel-closed");
	panelOpen = false;
	activeIndex = -1;
};

const togglePanel = () => {
	const panel = document.getElementById("search-panel");
	if (!panel) return;
	if (panel.classList.contains("float-panel-closed")) {
		openPanel(true);
	} else {
		closePanel();
	}
};

$: activeKeyword = (keywordDesktop || keywordMobile).trim();
$: showQuickActions = activeKeyword.length === 0;
$: navItemCount = showQuickActions ? quickActions.length : result.length;

const search = async (keyword: string, isDesktop: boolean): Promise<void> => {
	const trimmed = keyword.trim();
	if (!trimmed) {
		result = [];
		activeIndex = panelOpen ? 0 : -1;
		return;
	}

	if (!initialized) {
		return;
	}

	isSearching = true;
	if (isDesktop) openPanel(false);

	try {
		let searchResults: SearchResult[] = [];

		if (import.meta.env.PROD && pagefindLoaded && window.pagefind) {
			const response = await window.pagefind.search(trimmed);
			searchResults = await Promise.all(
				response.results.slice(0, 8).map((item) => item.data()),
			);
		} else if (import.meta.env.DEV) {
			searchResults = fakeResult;
		} else {
			searchResults = [];
		}

		result = searchResults;
		activeIndex = result.length > 0 ? 0 : -1;
	} catch (error) {
		console.error("Search error:", error);
		result = [];
		activeIndex = -1;
	} finally {
		isSearching = false;
	}
};

function executeActiveItem() {
	if (showQuickActions) {
		const action = quickActions[activeIndex];
		if (!action) return;
		if (action.href) {
			navigateTo(action.href);
		} else if (action.run) {
			action.run();
			closePanel();
		}
	} else {
		const item = result[activeIndex];
		if (item?.url) {
			navigateTo(item.url);
		}
	}
}

function handleKeydown(e: KeyboardEvent) {
	const isKShortcut = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k";
	if (isKShortcut) {
		e.preventDefault();
		if (panelOpen && (document.activeElement === desktopInput || document.activeElement === mobileInput)) {
			closePanel();
			(document.activeElement as HTMLElement)?.blur();
		} else {
			openPanel(true);
		}
		return;
	}

	const target = e.target as HTMLElement | null;
	const isTyping = target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);
	if (!isTyping && e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey) {
		e.preventDefault();
		openPanel(true);
		return;
	}

	const panel = document.getElementById("search-panel");
	const currentlyOpen = !!panel && !panel.classList.contains("float-panel-closed");
	if (!currentlyOpen) return;

	if (e.key === "Escape") {
		e.preventDefault();
		closePanel();
		desktopInput?.blur();
		mobileInput?.blur();
	} else if (e.key === "ArrowDown") {
		e.preventDefault();
		if (navItemCount > 0) activeIndex = (activeIndex + 1) % navItemCount;
	} else if (e.key === "ArrowUp") {
		e.preventDefault();
		if (navItemCount > 0) activeIndex = (activeIndex - 1 + navItemCount) % navItemCount;
	} else if (e.key === "Enter" && activeIndex >= 0) {
		e.preventDefault();
		executeActiveItem();
	}
}

onMount(() => {
	const initializeSearch = () => {
		initialized = true;
		pagefindLoaded =
			typeof window !== "undefined" &&
			!!window.pagefind &&
			typeof window.pagefind.search === "function";
		if (keywordDesktop) void search(keywordDesktop, true);
		if (keywordMobile) void search(keywordMobile, false);
	};

	const onReady = () => initializeSearch();
	const onError = () => initializeSearch();

	if (import.meta.env.DEV) {
		initializeSearch();
	} else {
		document.addEventListener("pagefindready", onReady);
		document.addEventListener("pagefindloaderror", onError);
		setTimeout(() => {
			if (!initialized) initializeSearch();
		}, 2000);
	}

	window.addEventListener("keydown", handleKeydown);
	return () => {
		window.removeEventListener("keydown", handleKeydown);
		document.removeEventListener("pagefindready", onReady);
		document.removeEventListener("pagefindloaderror", onError);
	};
});

$: if (initialized) {
	void search(keywordDesktop, true);
}

$: if (initialized) {
	void search(keywordMobile, false);
}
</script>

<!-- search bar for desktop view -->
<div id="search-bar" class="hidden lg:flex relative transition-all items-center h-10 my-auto mr-2 rounded-xl
      border border-transparent focus-within:border-[var(--primary)]/40
      bg-black/[0.04] hover:bg-black/[0.06] focus-within:bg-black/[0.06]
      dark:bg-white/5 dark:hover:bg-white/10 dark:focus-within:bg-white/10
">
    <Icon icon="material-symbols:search" class="absolute text-[1.15rem] pointer-events-none ml-3 transition my-auto text-black/35 dark:text-white/35"></Icon>
    <input
        bind:this={desktopInput}
        placeholder="{i18n(I18nKey.search)}"
        aria-label={i18n(I18nKey.search)}
        bind:value={keywordDesktop}
        on:focus={() => openPanel(false)}
        class="transition-all pl-9 pr-14 text-sm bg-transparent outline-0
         h-full w-44 focus:w-60 text-black/75 dark:text-white/80 placeholder:text-black/35 dark:placeholder:text-white/35"
    >
    <kbd class="pointer-events-none absolute right-2.5 inline-flex items-center rounded-md border border-black/10 dark:border-white/15 bg-white/70 dark:bg-white/10 px-1.5 py-0.5 font-mono-tech text-[0.62rem] text-50">
        Ctrl K
    </kbd>
</div>

<!-- toggle btn for phone/tablet view -->
<button on:click={togglePanel} aria-label="Search Panel" id="search-switch"
        class="btn-plain scale-animation lg:!hidden rounded-lg w-11 h-11 active:scale-90">
    <Icon icon="material-symbols:search" class="text-[1.25rem]"></Icon>
</button>

<!-- search / command palette panel -->
<div id="search-panel" class="float-panel float-panel-closed search-panel absolute md:w-[31rem]
top-[4.75rem] left-3 md:left-[unset] right-3 md:right-4 shadow-2xl rounded-2xl overflow-hidden">
    <!-- Studio Window Chrome -->
    <div class="win-chrome">
        <div class="flex items-center gap-2 min-w-0">
            <span class="win-dots win-dots-vivid" aria-hidden="true"><span></span><span></span><span></span></span>
            <span class="font-mono-tech text-[0.66rem] text-50 truncate">
                {showQuickActions ? "~/command-palette" : `~/search?q=${activeKeyword}`}
            </span>
        </div>
        <span class="font-mono-tech text-[0.62rem] text-50 shrink-0">↑↓ 选 · ↵ 进 · ESC 关</span>
    </div>

    <div class="p-2.5">
        <!-- search bar inside panel for phone/tablet -->
        <div id="search-bar-inside" class="flex relative lg:hidden transition-all items-center h-10 mb-2 rounded-xl
          bg-black/[0.04] hover:bg-black/[0.06] focus-within:bg-black/[0.06]
          dark:bg-white/5 dark:hover:bg-white/10 dark:focus-within:bg-white/10
      ">
            <Icon icon="material-symbols:search" class="absolute text-[1.15rem] pointer-events-none ml-3 transition my-auto text-black/35 dark:text-white/35"></Icon>
            <input
                bind:this={mobileInput}
                placeholder="{i18n(I18nKey.search)}"
                aria-label={i18n(I18nKey.search)}
                bind:value={keywordMobile}
                class="pl-9 pr-3 w-full h-full text-sm bg-transparent outline-0 text-black/75 dark:text-white/80"
            >
        </div>

        {#if showQuickActions}
            <div class="px-2 pt-0.5 pb-1.5 font-mono-tech text-[0.64rem] uppercase tracking-wider text-50">
                快捷入口 & 操作
            </div>
            <div class="flex flex-col gap-0.5">
                {#each quickActions as action, idx}
                    <button
                        type="button"
                        on:mouseenter={() => (activeIndex = idx)}
                        on:click={() => {
                            if (action.href) navigateTo(action.href);
                            else if (action.run) { action.run(); closePanel(); }
                        }}
                        class="w-full text-left flex items-center justify-between gap-3 rounded-xl px-3 py-2 text-sm transition cursor-pointer"
                        class:bg-[var(--btn-plain-bg-hover)]={activeIndex === idx}
                        class:text-[var(--primary)]={activeIndex === idx}
                        class:text-75={activeIndex !== idx}
                    >
                        <span class="inline-flex items-center gap-2.5 font-medium truncate">
                            <Icon icon={action.icon} class="text-base shrink-0 text-[var(--primary)]"></Icon>
                            <span>{action.label}</span>
                        </span>
                        <span class="font-mono-tech text-[0.66rem] text-50 shrink-0">{action.hint}</span>
                    </button>
                {/each}
            </div>
        {:else if isSearching}
            <div class="py-8 text-center font-mono-tech text-xs text-50">正在检索文章...</div>
        {:else if result.length === 0}
            <div class="py-8 px-4 text-center">
                <div class="text-sm font-medium text-75">没有找到包含「{activeKeyword}」的文章</div>
                <div class="mt-1 text-xs text-50">可以试试更短的关键词，比如 Go、Agent、Docker 或 VPS。</div>
            </div>
        {:else}
            <div class="px-2 pt-0.5 pb-1.5 font-mono-tech text-[0.64rem] text-50">
                命中 {result.length} 条结果
            </div>
            <div class="flex flex-col gap-0.5">
                {#each result as item, idx}
                    <a
                        href={item.url}
                        on:mouseenter={() => (activeIndex = idx)}
                        on:click={() => closePanel()}
                        class="transition group block rounded-xl px-3 py-2 hover:bg-[var(--btn-plain-bg-hover)] active:bg-[var(--btn-plain-bg-active)]"
                        class:bg-[var(--btn-plain-bg-hover)]={activeIndex === idx}
                    >
                        <div class="transition text-90 inline-flex items-center font-bold text-[0.95rem] group-hover:text-[var(--primary)]"
                             class:text-[var(--primary)]={activeIndex === idx}>
                            {item.meta.title}
                            <Icon icon="fa6-solid:chevron-right" class="transition text-[0.7rem] translate-x-1 my-auto text-[var(--primary)]"></Icon>
                        </div>
                        <div class="transition text-xs text-50 mt-0.5 leading-relaxed line-clamp-2">
                            {@html item.excerpt}
                        </div>
                    </a>
                {/each}
            </div>
        {/if}
    </div>
</div>

<style>
  input:focus {
    outline: 0;
  }
  .search-panel {
    max-height: calc(100vh - 100px);
    overflow-y: auto;
  }
</style>
