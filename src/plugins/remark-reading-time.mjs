import { toString as mdastToString } from "mdast-util-to-string";

export function remarkReadingTime() {
	return (tree, { data }) => {
		const textOnPage = mdastToString(tree) || "";
		const cjkMatches = textOnPage.match(/[\u4e00-\u9fff\u3400-\u4dbf]/g);
		const cjkCount = cjkMatches ? cjkMatches.length : 0;
		const withoutCjk = textOnPage.replace(/[\u4e00-\u9fff\u3400-\u4dbf]/g, " ");
		const asciiMatches = withoutCjk.match(/[A-Za-z0-9_]+(?:[./-][A-Za-z0-9_]+)*/g);
		const asciiCount = asciiMatches ? asciiMatches.length : 0;

		const totalWords = cjkCount + asciiCount;
		const minutes = Math.max(1, Math.round(cjkCount / 400 + asciiCount / 200));

		data.astro.frontmatter.words = totalWords;
		data.astro.frontmatter.minutes = minutes;
	};
}
