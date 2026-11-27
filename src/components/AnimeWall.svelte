<script lang="ts">
interface AnimeItem {
	id: string;
	subjectId?: number;
	title: string;
	originalTitle?: string;
	status: "watching" | "watched" | "wish" | "on_hold" | "dropped";
	watched: number;
	total: number;
	score: number | null;
	bgmScore: number | null;
	cover: string;
	tags: string[];
	note: string;
	url?: string;
	updatedAt?: string;
	source?: string;
}

interface Props {
	items: AnimeItem[];
	updatedAt: string;
	source: string;
	"client:only"?: "svelte";
}

let { items, updatedAt, source }: Props = $props();

type FilterKey = "all" | AnimeItem["status"];
let activeTab = $state<FilterKey>("all");
let keyword = $state("");

const statusMeta: Record<
	AnimeItem["status"],
	{ label: string; dotClass: string; badgeClass: string }
> = {
	watching: {
		label: "在看",
		dotClass: "bg-emerald-500",
		badgeClass:
			"bg-emerald-500/12 text-emerald-700 dark:text-emerald-300 border-emerald-500/25",
	},
	watched: {
		label: "看过",
		dotClass: "bg-[var(--primary)]",
		badgeClass:
			"bg-[var(--btn-regular-bg)] text-[var(--primary)] border-[var(--card-border)]",
	},
	wish: {
		label: "想看",
		dotClass: "bg-amber-500",
		badgeClass:
			"bg-amber-500/12 text-amber-700 dark:text-amber-300 border-amber-500/25",
	},
	on_hold: {
		label: "搁置",
		dotClass: "bg-slate-400",
		badgeClass:
			"bg-black/5 dark:bg-white/10 text-60 border-[var(--card-border)]",
	},
	dropped: {
		label: "抛弃",
		dotClass: "bg-rose-400",
		badgeClass:
			"bg-rose-500/10 text-rose-600 dark:text-rose-300 border-rose-500/25",
	},
};

const tabs: { key: FilterKey; label: string }[] = [
	{ key: "all", label: "全部" },
	{ key: "watching", label: "在看" },
	{ key: "watched", label: "看过" },
	{ key: "wish", label: "想看" },
	{ key: "on_hold", label: "搁置" },
];

const counts = $derived.by(() => {
	const map: Record<FilterKey, number> = {
		all: items.length,
		watching: 0,
		watched: 0,
		wish: 0,
		on_hold: 0,
		dropped: 0,
	};
	for (const it of items) {
		map[it.status] = (map[it.status] || 0) + 1;
	}
	return map;
});

const totalWatchedEpisodes = $derived(
	items.reduce((sum, it) => sum + (it.watched || 0), 0),
);

const filtered = $derived.by(() => {
	const q = keyword.trim().toLowerCase();
	return items.filter((it) => {
		if (activeTab !== "all" && it.status !== activeTab) return false;
		if (!q) return true;
		const hay = `${it.title} ${it.originalTitle || ""} ${(it.tags || []).join(" ")} ${it.note || ""}`.toLowerCase();
		return hay.includes(q);
	});
});

function progressPct(it: AnimeItem): number {
	if (!it.total || it.total <= 0) return it.watched > 0 ? 100 : 0;
	return Math.min(100, Math.round((it.watched / it.total) * 100));
}
</script>

<div class="flex flex-col gap-4">
	<!-- Summary & Filter Bar -->
	<div class="card-base overflow-hidden">
		<div class="win-chrome">
			<div class="flex items-center gap-2 min-w-0">
				<span class="win-dots win-dots-vivid" aria-hidden="true"><span></span><span></span><span></span></span>
				<span class="font-mono-tech text-[0.68rem] text-50 truncate">~/anime</span>
			</div>
			<span class="font-mono-tech text-[0.64rem] text-50 shrink-0">
				{source} · {updatedAt}
			</span>
		</div>

		<div class="p-5 md:p-6 flex flex-col gap-4">
			<!-- Stats Strip -->
			<div class="grid grid-cols-3 gap-2.5">
				<div class="rounded-xl border border-[var(--card-border)] bg-black/[0.015] dark:bg-white/[0.02] px-3.5 py-2.5">
					<div class="font-mono-tech text-[0.66rem] text-50">正在追</div>
					<div class="font-display font-bold text-xl text-90 mt-0.5">{counts.watching}</div>
				</div>
				<div class="rounded-xl border border-[var(--card-border)] bg-black/[0.015] dark:bg-white/[0.02] px-3.5 py-2.5">
					<div class="font-mono-tech text-[0.66rem] text-50">已看完</div>
					<div class="font-display font-bold text-xl text-90 mt-0.5">{counts.watched}</div>
				</div>
				<div class="rounded-xl border border-[var(--card-border)] bg-black/[0.015] dark:bg-white/[0.02] px-3.5 py-2.5">
					<div class="font-mono-tech text-[0.66rem] text-50">累计集数</div>
					<div class="font-display font-bold text-xl text-90 mt-0.5">{totalWatchedEpisodes}</div>
				</div>
			</div>

			<!-- Filter Tabs + Search -->
			<div class="flex flex-wrap items-center justify-between gap-2.5">
				<div class="flex flex-wrap items-center gap-1.5" role="tablist" aria-label="追番状态筛选">
					{#each tabs as tab}
						{#if tab.key === "all" || counts[tab.key] > 0}
							<button
								type="button"
								role="tab"
								aria-selected={activeTab === tab.key}
								onclick={() => (activeTab = tab.key)}
								class={`px-3 py-1.5 rounded-xl text-xs font-medium transition cursor-pointer border ${
									activeTab === tab.key
										? "bg-[var(--primary)] text-white border-transparent shadow-sm"
										: "bg-black/[0.02] dark:bg-white/[0.03] text-75 border-[var(--card-border)] hover:border-[var(--primary)]/40 hover:text-[var(--primary)]"
								}`}
							>
								<span>{tab.label}</span>
								<span class={`ml-1 font-mono-tech text-[0.66rem] ${activeTab === tab.key ? "opacity-85" : "opacity-55"}`}>
									{counts[tab.key]}
								</span>
							</button>
						{/if}
					{/each}
				</div>

				<input
					type="search"
					bind:value={keyword}
					placeholder="筛选番名或标签..."
					class="w-full sm:w-48 rounded-xl border border-[var(--card-border)] bg-black/[0.02] dark:bg-white/[0.04] px-3 py-1.5 text-xs text-90 placeholder:text-50 focus:outline-none focus:border-[var(--primary)]/60 transition"
				/>
			</div>
		</div>
	</div>

	<!-- Anime Grid -->
	{#if filtered.length === 0}
		<div class="card-base p-8 text-center text-sm text-50">
			没有找到匹配的番剧记录。
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			{#each filtered as item (item.id)}
				{@const meta = statusMeta[item.status]}
				{@const pct = progressPct(item)}
				<article class="card-base overflow-hidden flex flex-row p-3.5 gap-3.5 hover:border-[var(--primary)]/40 transition group">
					<!-- Cover -->
					<a
						href={item.url || "#"}
						target={item.url ? "_blank" : undefined}
						rel={item.url ? "noopener noreferrer" : undefined}
						class="shrink-0 w-24 sm:w-28 aspect-[3/4] rounded-xl overflow-hidden bg-black/5 dark:bg-white/5 ring-1 ring-black/5 dark:ring-white/10 block"
					>
						{#if item.cover}
							<img
								src={item.cover}
								alt={item.title}
								loading="lazy"
								class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
							/>
						{/if}
					</a>

					<!-- Info -->
					<div class="flex-1 min-w-0 flex flex-col justify-between gap-2">
						<div>
							<div class="flex items-start justify-between gap-2">
								<a
									href={item.url || "#"}
									target={item.url ? "_blank" : undefined}
									rel={item.url ? "noopener noreferrer" : undefined}
									class="font-display font-bold text-[0.98rem] leading-snug text-90 hover:text-[var(--primary)] transition line-clamp-2"
								>
									{item.title}
								</a>
								<span class={`shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[0.66rem] font-medium border ${meta.badgeClass}`}>
									<span class={`w-1.5 h-1.5 rounded-full ${meta.dotClass}`}></span>
									{meta.label}
								</span>
							</div>

							{#if item.originalTitle && item.originalTitle !== item.title}
								<div class="text-[0.72rem] text-50 truncate mt-0.5">{item.originalTitle}</div>
							{/if}

							<!-- Scores -->
							<div class="flex flex-wrap items-center gap-2 mt-2 font-mono-tech text-[0.68rem]">
								{#if item.score}
									<span class="px-1.5 py-0.5 rounded-md bg-amber-500/12 text-amber-700 dark:text-amber-300">
										自评 {item.score}
									</span>
								{/if}
								{#if item.bgmScore}
									<span class="px-1.5 py-0.5 rounded-md bg-black/[0.04] dark:bg-white/[0.06] text-60">
										Bangumi {item.bgmScore}
									</span>
								{/if}
								{#if item.updatedAt}
									<span class="text-50">{item.updatedAt}</span>
								{/if}
							</div>

							{#if item.note}
								<p class="text-xs text-75 leading-relaxed mt-2 line-clamp-2">{item.note}</p>
							{/if}
						</div>

						<!-- Bottom progress + tags -->
						<div class="flex flex-col gap-2">
							{#if item.tags && item.tags.length > 0}
								<div class="flex flex-wrap gap-1">
									{#each item.tags.slice(0, 4) as tag}
										<span class="px-1.5 py-0.5 rounded-md text-[0.65rem] bg-black/[0.03] dark:bg-white/[0.05] text-60">
											#{tag}
										</span>
									{/each}
								</div>
							{/if}

							<div>
								<div class="flex items-center justify-between font-mono-tech text-[0.66rem] text-50 mb-1">
									<span>进度 {item.watched} / {item.total || "?"} 话</span>
									<span>{pct}%</span>
								</div>
								<div class="h-1.5 w-full rounded-full bg-black/[0.06] dark:bg-white/[0.08] overflow-hidden">
									<div
										class="h-full rounded-full bg-[var(--primary)] transition-all duration-300"
										style={`width: ${pct}%`}
									></div>
								</div>
							</div>
						</div>
					</div>
				</article>
			{/each}
		</div>
	{/if}
</div>
