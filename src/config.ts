import type {
	ExpressiveCodeConfig,
	LicenseConfig,
	NavBarConfig,
	ProfileConfig,
	SiteConfig,
} from "./types/config";
import { LinkPreset } from "./types/config";

export const siteConfig: SiteConfig = {
	title: "lannokaede 的手记",
	subtitle: "Go 后端、Agent 与服务器记录",
	lang: "zh_CN", // Language code, e.g. 'en', 'zh_CN', 'ja', etc.
	themeColor: {
		hue: 245,
		fixed: false, // Hide the theme color picker for visitors
	},
	banner: {
		enable: true,
		src: "/images/anime/bocchi-stage.webp",
		mobileSrc: "/images/anime/bocchi-stage-mobile.webp",
		position: "center 32%", // Equivalent to object-position, only supports 'top', 'center', 'bottom'. 'center' by default
		credit: {
			enable: true,
			text: "横幅 · 孤独摇滚！",
			url: "https://wallhaven.cc/w/1p2m2w",
		},
	},
	toc: {
		enable: true, // Display the table of contents on the right side of the post
		depth: 3, // Maximum heading depth to show in the table, from 1 to 3
	},
	favicon: [
		{
			src: "/favicon/avatar-32.png",
			sizes: "32x32",
		},
		{
			src: "/favicon/avatar-128.png",
			sizes: "128x128",
		},
		{
			src: "/favicon/avatar-192.png",
			sizes: "192x192",
		},
	],
};

export const navBarConfig: NavBarConfig = {
	links: [
		LinkPreset.Home,
		LinkPreset.Archive,
		{
			name: "追番",
			url: "/anime/",
		},
		{
			name: "碎碎念",
			url: "/moments/",
		},
		{
			name: "收藏",
			url: "/collection/",
		},
		{
			name: "友链",
			url: "/friends/",
		},
		LinkPreset.About,
	],
};

export const profileConfig: ProfileConfig = {
	avatar: "/images/avatar.webp",
	name: "lannokaede",
	bio: "电子科大软件工程在读，平时写 Go 后端和本地 Agent 工具。",
	links: [
		{
			name: "邮箱",
			icon: "fa6-solid:envelope",
			url: "mailto:lannokaede@gmail.com",
		},
		{
			name: "哔哩哔哩",
			icon: "fa6-brands:bilibili",
			url: "https://space.bilibili.com/499115598",
		},
		{
			name: "GitHub",
			icon: "fa6-brands:github",
			url: "https://github.com/lannokaede",
		},
	],
};

export const licenseConfig: LicenseConfig = {
	enable: true,
	name: "CC BY-NC-SA 4.0",
	url: "https://creativecommons.org/licenses/by-nc-sa/4.0/",
};

export const expressiveCodeConfig: ExpressiveCodeConfig = {
	// Note: Some styles (such as background color) are being overridden, see the astro.config.mjs file.
	// Please select a dark theme, as this blog theme currently only supports dark background color
	theme: "github-dark",
};
