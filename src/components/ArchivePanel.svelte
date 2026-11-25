<script lang="ts">
import { onMount } from "svelte";

import I18nKey from "../i18n/i18nKey";
import { i18n } from "../i18n/translation";
import type { PostForList } from "../utils/content-utils";
import { getPostUrlBySlug, url } from "../utils/url-utils";

export let tags: string[] = [];
export let categories: string[] = [];
export let sortedPosts: PostForList[] = [];

const params = new URLSearchParams(window.location.search);
tags = params.has("tag") ? params.getAll("tag") : [];
categories = params.has("category") ? params.getAll("category") : [];
const uncategorized = params.get("uncategorized");
const hasActiveFilter = tags.length > 0 || categories.length > 0 || !!uncategorized;

interface Group {
	year: number;
	posts: PostForList[];
}

let groups: Group[] = [];

function formatDate(date: Date) {
	const month = (date.getUTCMonth() + 1).toString().padStart(2, "0");
	const day = date.getUTCDate().toString().padStart(2, "0");
	return `${month}-${day}`;
}

function formatTag(tagList: string[]) {
	return tagList.map((t) => `#${t}`).join(" ");
}

onMount(async () => {
	let filteredPosts: PostForList[] = sortedPosts;

	if (tags.length > 0) {
		filteredPosts = filteredPosts.filter(
			(post) =>
				Array.isArray(post.data.tags) &&
				post.data.tags.some((tag) => tags.includes(tag)),
		);
	}

	if (categories.length > 0) {
		filteredPosts = filteredPosts.filter(
			(post) => post.data.category && categories.includes(post.data.category),
		);
	}

	if (uncategorized) {
		filteredPosts = filteredPosts.filter((post) => !post.data.category);
	}

	const grouped = filteredPosts.reduce(
		(acc, post) => {
			const year = post.data.published.getUTCFullYear();
			if (!acc[year]) {
				acc[year] = [];
			}
			acc[year].push(post);
			return acc;
		},
		{} as Record<number, PostForList[]>,
	);

	const groupedPostsArray = Object.keys(grouped).map((yearStr) => ({
		year: Number.parseInt(yearStr, 10),
		posts: grouped[Number.parseInt(yearStr, 10)],
	}));

	groupedPostsArray.sort((a, b) => b.year - a.year);

	groups = groupedPostsArray;
});
</script>

<div class="card-base overflow-hidden">
    <div class="win-chrome">
        <div class="flex items-center gap-2 min-w-0">
            <span class="win-dots win-dots-vivid" aria-hidden="true"><span></span><span></span><span></span></span>
            <span class="font-mono-tech text-[0.68rem] text-50 truncate">~/archive</span>
        </div>
        <span class="font-mono-tech text-[0.65rem] text-50 shrink-0">TIMELINE</span>
    </div>
    <div class="px-5 md:px-8 py-6">
        {#if hasActiveFilter}
            <div class="flex flex-wrap items-center justify-between gap-2 pb-4 mb-2 border-b border-dashed border-[var(--line-divider)] text-sm">
                <div class="text-75 flex flex-wrap items-center gap-2">
                    <span>当前筛选：</span>
                    {#each categories as cat}
                        <span class="px-2 py-0.5 rounded-md bg-[var(--btn-regular-bg)] text-[var(--btn-content)] font-medium">{cat}</span>
                    {/each}
                    {#each tags as tag}
                        <span class="px-2 py-0.5 rounded-md bg-[var(--btn-regular-bg)] text-[var(--btn-content)] font-medium">#{tag}</span>
                    {/each}
                    {#if uncategorized}
                        <span class="px-2 py-0.5 rounded-md bg-[var(--btn-regular-bg)] text-[var(--btn-content)] font-medium">未分类</span>
                    {/if}
                </div>
                <a href={url("/archive/")} class="text-[var(--primary)] hover:underline font-medium">查看全部</a>
            </div>
        {/if}
        {#if groups.length === 0}
            <div class="py-10 text-center text-50 text-sm">没有符合条件的文章</div>
        {/if}
        {#each groups as group}
            <div>
                <div class="flex flex-row w-full items-center h-[3.75rem]">
                    <div class="w-[15%] md:w-[10%] transition font-mono-tech text-2xl font-bold text-right text-75">
                        {group.year}
                    </div>
                    <div class="w-[15%] md:w-[10%]">
                        <div
                                class="h-3 w-3 bg-none rounded-full outline outline-[var(--primary)] mx-auto
                      -outline-offset-[2px] z-50 outline-3"
                        ></div>
                    </div>
                    <div class="w-[70%] md:w-[80%] transition font-mono-tech text-sm text-left text-50">
                        {group.posts.length} {i18n(group.posts.length === 1 ? I18nKey.postCount : I18nKey.postsCount)}
                    </div>
                </div>

                {#each group.posts as post}
                    <a
                            href={getPostUrlBySlug(post.slug)}
                            aria-label={post.data.title}
                            class="group btn-plain !block h-10 w-full rounded-lg hover:text-[initial]"
                    >
                        <div class="flex flex-row justify-start items-center h-full">
                            <!-- date -->
                            <div class="w-[15%] md:w-[10%] transition font-mono-tech text-xs md:text-sm text-right text-50">
                                {formatDate(post.data.published)}
                            </div>

                            <!-- dot and line -->
                            <div class="w-[15%] md:w-[10%] relative dash-line h-full flex items-center">
                                <div
                                        class="transition-all mx-auto w-1 h-1 rounded group-hover:h-5
                           bg-[oklch(0.5_0.05_var(--hue))] group-hover:bg-[var(--primary)]
                           outline outline-4 z-50
                           outline-[var(--card-bg)]
                           group-hover:outline-[var(--btn-plain-bg-hover)]
                           group-active:outline-[var(--btn-plain-bg-active)]"
                                ></div>
                            </div>

                            <!-- post title -->
                            <div
                                    class="w-[70%] md:max-w-[65%] md:w-[65%] text-left font-bold
                         group-hover:translate-x-1 transition-all group-hover:text-[var(--primary)]
                         text-75 pr-8 whitespace-nowrap overflow-ellipsis overflow-hidden"
                            >
                                {post.data.title}
                            </div>

                            <!-- tag list -->
                            <div
                                    class="hidden md:block md:w-[15%] text-left text-xs font-mono-tech transition
                         whitespace-nowrap overflow-ellipsis overflow-hidden text-black/45 dark:text-white/45"
                            >
                                {formatTag(post.data.tags)}
                            </div>
                        </div>
                    </a>
                {/each}
            </div>
        {/each}
    </div>
</div>
