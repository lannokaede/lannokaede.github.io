# lannokaedeのBlog

保持好奇，持续折腾。

基于 [Fuwari](https://github.com/saicaca/fuwari) 和 Astro 的个人博客，以技术笔记为主，也记录生活、游戏和动漫。

计划发布地址：<https://lannokaede.github.io/>。本地构建通过不代表 GitHub Pages 已上线，以仓库 Actions 的部署结果为准。

## 本地使用

使用 Node.js 22 和 `package.json` 固定的 pnpm 9.14.4。通过 Corepack 调用可以避免电脑上全局 pnpm 版本不同造成的安装冲突。

```sh
corepack pnpm install --frozen-lockfile
corepack pnpm dev
```

开发地址以终端打印为准，默认是 <http://localhost:4321/>。

```sh
corepack pnpm check
corepack pnpm build
corepack pnpm preview
```

`build` 同时生成静态网站和 Pagefind 搜索索引。搜索功能应在 `build` 后用 `preview` 验证；开发模式中的搜索为主题演示数据。

Windows PowerShell 若阻止 `.ps1` 命令，使用 `corepack.cmd pnpm ...` 即可，不需要修改系统执行策略。若 npm 遇到全局缓存目录权限错误，可为当前命令指定用户可写缓存：

```powershell
$env:npm_config_cache = "$env:LOCALAPPDATA\npm-cache"
```

## 写一篇文章

```sh
corepack pnpm new-post my-first-note
```

在 `src/content/posts/my-first-note.md` 编辑内容。新建文章默认是草稿，写完后将 `draft` 改为 `false`，提交到 GitHub 即可发布。

```yaml
---
title: 我的第一篇技术笔记
published: 2026-10-18
description: 用一句话概括文章。
tags: [技术笔记]
category: 技术
draft: false
---
```

正文支持 Markdown、代码高亮、数学公式和自动目录。插入文章图片时可将图片和文章放在同一文件夹，以相对路径引用。

## 修改个人资料与图片

- `src/config.ts`：博客名、副标题、作者简介、主题色、社交链接、文章转载许可。
- `src/content/spec/about.md`：关于我。
- `src/content/posts/`：文章。
- `astro.config.mjs`：正式站点地址和部署路径。
- `src/assets/images/`：头像、横幅及其他本地图片。

默认头像暂时保留。替换头像时，将图片放入 `src/assets/images/`，再修改 `profileConfig.avatar`；首页横幅目前关闭，如需启用，设置 `siteConfig.banner.enable: true` 并填写 `src`。图片路径 `assets/images/...` 相对于 `src/`。

评论目前未启用。公开链接为 GitHub、邮箱和哔哩哔哩。

## GitHub Pages 部署

1. 在 `lannokaede` 账号下创建公开仓库 `lannokaede.github.io`。
2. 上传本项目源码到 `main` 分支。
3. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
4. 工作流 **Build and Deploy to GitHub Pages** 会检查、构建、生成搜索索引并发布网站。首次设置 Pages 后，如果没有自动运行，可在 **Actions** 中手动运行工作流。
5. 部署任务成功后访问 <https://lannokaede.github.io/>。

`main` 分支每次推送会自动更新网站。Pull Request 只执行检查和构建，不发布。

当前使用用户站点根路径：`site: "https://lannokaede.github.io/"`、`base: "/"`。若以后改用独立域名，需要同步修改站点地址和 GitHub Pages 域名设置。

## 授权与来源

博客原创文章使用 **CC BY-NC-SA 4.0**，转载和改编须署名、非商业使用，并以相同许可分享。

主题代码保留上游 **MIT** 许可证，见 `LICENSE`。默认图片来源见 [主题与素材说明](docs/THEME.md)。
