export interface FriendItem {
	name: string;
	url: string;
	avatar: string;
	desc: string;
	tag?: string;
}

export const friends: FriendItem[] = [
	// 后续互换友链直接往这里追加即可
];

export const mySiteInfo = {
	name: "lannokaede 的手记",
	url: "https://lannokaede.github.io/",
	avatar: "https://lannokaede.github.io/images/avatar.webp",
	desc: "电子科大软件工程在读，记录 Go 后端、Agent 工具、自建服务与追番日常。",
};
