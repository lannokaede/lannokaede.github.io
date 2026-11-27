export interface MusicItem {
	title: string;
	artist: string;
	album: string;
	tag: string;
	note: string;
	url: string;
}

export interface GameItem {
	title: string;
	platform: string;
	status: "在玩" | "常驻" | "通关";
	note: string;
}

export interface ToolItem {
	name: string;
	category: string;
	desc: string;
	url?: string;
}

// 如果希望在收藏页嵌入网易云公开歌单的实时同步外链播放器，填入纯数字歌单 ID 即可（例如 "123456789"）
export const neteasePlaylistId = "";

export const musicList: MusicItem[] = [
	{
		title: "結束バンド（团结乐队）",
		artist: "結束バンド",
		album: "結束バンド",
		tag: "J-Rock · 动画原声",
		note: "写代码循环最多的一张，吉他声部和鼓点都很提神。",
		url: "https://music.163.com/#/search/m/?s=%E7%B5%90%E6%9D%9F%E3%83%90%E3%83%B3%E3%83%89",
	},
	{
		title: "迷星叫 / 碧天伴走",
		artist: "MyGO!!!!!",
		album: "迷跡波",
		tag: "乐队 · 邦邦",
		note: "旋律抓耳，平时用 MyGo Music 听无损版。",
		url: "https://music.163.com/#/search/m/?s=MyGO%20%E8%BF%B7%E6%98%9F%E5%8F%AB",
	},
	{
		title: "ギターと孤独と蒼い惑星",
		artist: "結束バンド",
		album: "結束バンド",
		tag: "摇滚 · 孤独摇滚",
		note: "第五集 Live 回的名曲，副歌一进来就很燃。",
		url: "https://music.163.com/#/search/m/?s=%E3%82%AE%E3%82%BF%E3%83%BC%E3%81%A8%E5%AD%A4%E7%8B%AC%E3%81%A8%E8%92%BC%E3%81%84%E6%83%91%E6%98%9F",
	},
	{
		title: "星座になれたら",
		artist: "結束バンド",
		album: "結束バンド",
		tag: "乐队 · 压轴曲",
		note: "文化祭压轴曲，适合深夜收尾写完需求的时候听。",
		url: "https://music.163.com/#/search/m/?s=%E6%98%9F%E5%BA%A7%E3%81%AB%E3%81%AA%E3%82%8C%E3%81%9F%E3%82%89",
	},
];

export const gameList: GameItem[] = [
	{
		title: "明日方舟",
		platform: "PC / B服",
		status: "常驻",
		note: "长草期清体力、开活动推关，顺带在电脑上配过游戏进程直连规则。",
	},
];

export const toolList: ToolItem[] = [
	{
		name: "Animeko (Ani)",
		category: "追番",
		desc: "开源跨平台追番客户端，聚合在线与 BT 源，博客追番墙就是直接从它本地库同步的。",
		url: "https://github.com/open-ani/animeko",
	},
	{
		name: "MyGo Music",
		category: "音乐",
		desc: "轻量桌面音乐播放器，搭配网易云插件听高品/无损曲库。",
		url: "https://github.com/egoist/mygo-music",
	},
	{
		name: "WSL2 (Ubuntu 22.04)",
		category: "开发",
		desc: "Windows 下的主力 Linux 开发环境，跑 Go 后端、Docker 和实验项目。",
	},
	{
		name: "Clash Verge Rev",
		category: "网络",
		desc: "日常代理与分流管理，配合自建 Xray REALITY 节点和进程直连规则。",
	},
	{
		name: "LibreChat",
		category: "AI",
		desc: "自建在 VPS 上的 Web AI 聊天站，接了多条模型线路日常使用。",
		url: "https://github.com/danny-avila/LibreChat",
	},
	{
		name: "Astro + Tailwind CSS",
		category: "博客",
		desc: "本站技术栈，静态生成 + Pagefind 本地搜索 + Svelte 交互岛。",
		url: "https://astro.build/",
	},
];
