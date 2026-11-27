<script lang="ts">
import { onMount } from "svelte";

interface Props {
	"client:only"?: "svelte";
}
let {}: Props = $props();

let containerEl: HTMLDivElement | undefined;

function getGiscusTheme(): string {
	return document.documentElement.classList.contains("dark")
		? "dark_dimmed"
		: "light";
}

function syncGiscusTheme() {
	const iframe = containerEl?.querySelector<HTMLIFrameElement>(
		"iframe.giscus-frame",
	);
	if (!iframe || !iframe.contentWindow) return;
	iframe.contentWindow.postMessage(
		{ giscus: { setConfig: { theme: getGiscusTheme() } } },
		"https://giscus.app",
	);
}

onMount(() => {
	if (!containerEl) return;
	containerEl.innerHTML = "";
	const script = document.createElement("script");
	script.src = "https://giscus.app/client.js";
	script.async = true;
	script.crossOrigin = "anonymous";
	script.setAttribute("data-repo", "lannokaede/lannokaede.github.io");
	script.setAttribute("data-repo-id", "R_kgDOVNtGvg");
	script.setAttribute("data-category", "General");
	script.setAttribute("data-category-id", "DIC_kwDOVNtGvs4DMHGe");
	script.setAttribute("data-mapping", "pathname");
	script.setAttribute("data-strict", "0");
	script.setAttribute("data-reactions-enabled", "1");
	script.setAttribute("data-emit-metadata", "0");
	script.setAttribute("data-input-position", "top");
	script.setAttribute("data-theme", getGiscusTheme());
	script.setAttribute("data-lang", "zh-CN");
	script.setAttribute("data-loading", "lazy");
	containerEl.appendChild(script);

	const observer = new MutationObserver(() => syncGiscusTheme());
	observer.observe(document.documentElement, {
		attributes: true,
		attributeFilter: ["class"],
	});

	return () => observer.disconnect();
});
</script>

<section class="card-base z-10 overflow-hidden relative w-full mb-4 onload-animation">
	<div class="win-chrome">
		<div class="flex items-center gap-2 min-w-0">
			<span class="win-dots text-50" aria-hidden="true"><span></span><span></span><span></span></span>
			<span class="font-mono-tech text-[0.68rem] text-50 truncate">~/comments</span>
		</div>
		<span class="font-mono-tech text-[0.64rem] text-50 shrink-0">GISCUS · GITHUB DISCUSSIONS</span>
	</div>
	<div class="px-5 md:px-8 py-5">
		<div bind:this={containerEl} class="giscus-wrapper min-h-[120px]"></div>
	</div>
</section>
