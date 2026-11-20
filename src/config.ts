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
	subtitle: "保持好奇，持续折腾",
	lang: "zh_CN", // Language code, e.g. 'en', 'zh_CN', 'ja', etc.
	themeColor: {
		hue: 245,
		fixed: false, // Hide the theme color picker for visitors
	},
	banner: {
		enable: true,
		src: "/images/anime/bocchi-stage.webp",
		mobileSrc: "/images/anime/bocchi-stage-mobile.webp",
		position: "center", // Equivalent to object-position, only supports 'top', 'center', 'bottom'. 'center' by default
		credit: {
			enable: true,
			text: "横幅 · 孤独摇滚！",
			url: "https://chromaticdreamers.com/bocchi-the-rock-songs-ranked-by-guitar-difficulty/",
		},
	},
	toc: {
		enable: true, // Display the table of contents on the right side of the post
		depth: 2, // Maximum heading depth to show in the table, from 1 to 3
	},
	favicon: [
		// Leave this array empty to use the default favicon
		// {
		//   src: '/favicon/icon.png',    // Path of the favicon, relative to the /public directory
		//   theme: 'light',              // (Optional) Either 'light' or 'dark', set only if you have different favicons for light and dark mode
		//   sizes: '32x32',              // (Optional) Size of the favicon, set only if you have favicons of different sizes
		// }
	],
};

export const navBarConfig: NavBarConfig = {
	links: [
		LinkPreset.Home,
		LinkPreset.Archive,
		LinkPreset.About,
		{
			name: "GitHub",
			url: "https://github.com/lannokaede", // Internal links should not include the base path, as it is automatically added
			external: true, // Show an external link icon and will open in a new tab
		},
	],
};

export const profileConfig: ProfileConfig = {
	avatar: "https://avatars.githubusercontent.com/u/181042428?v=4&s=512",
	name: "lannokaede",
	bio: "保持好奇，持续折腾",
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
