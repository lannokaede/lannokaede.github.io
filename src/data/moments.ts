export interface MomentItem {
	id: string;
	date: string;
	tag: string;
	content: string;
	link?: {
		label: string;
		href: string;
	};
}

export const moments: MomentItem[] = [
	{
		id: "2026-11-27-site-upgrade",
		date: "2026-11-27",
		tag: "博客",
		content:
			"把追番墙、碎碎念、收藏清单和友链页都补进来了。追番数据直接写了个本地脚本从 Animeko (Ani) 的 SQLite 数据库同步，省得两边重复记。",
		link: { label: "去看追番墙", href: "/anime/" },
	},
	{
		id: "2026-11-27-bocchi-ai",
		date: "2026-11-27",
		tag: "技术",
		content:
			"给左下角 Q 版波奇接了个轻量 Go 转发服务，挂在 111.230.43.176 原来的 Nginx HTTPS 后面。访客按 IP 每小时限 5 次，自己填 Token 走不限次模式，文章页还能顺带统计阅读量和点赞。",
	},
	{
		id: "2026-11-24-anime-season",
		date: "2026-11-24",
		tag: "追番",
		content:
			"最近在 Ani 上追《药屋少女的呢喃 第三季》《学生会也有洞！》和《FX战士久留美》，久留美每集血压都拉满，但意外挺上头。",
	},
];
