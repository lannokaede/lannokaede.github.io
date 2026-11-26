---
title: LibreChat 自建 AI 聊天站
published: 2026-11-24
description: 用 LibreChat 搭的自用聊天站，接了常用模型线路和顶栏额度显示。
image: /images/anime/bocchi-ryo-balance.webp
tags: [LibreChat, Docker, VPS, AI]
category: 技术笔记
draft: false
lang: zh_CN
---

平时几个模型接口分散在不同网页里，看余额也要单独切标签页。后来在 VPS 上用 LibreChat 搭了个自用站，把常用的 Z-API 线路接进去，并在模型下拉框旁边加了余额和 Codex 剩余额度的显示。

## 部署与模型接入

服务端用 Docker Compose 跑 LibreChat `v0.8.9`（共 7 个容器），部署在之前 [大肥鱼 QQ 机器人](/posts/dafeiyu-qq-bot/)腾出来的那台机器上：MongoDB 存对话，Meilisearch 做全文检索，另外跑了一个本地中文嵌入模型处理上传文件的检索。拉官方镜像时直连比较慢，走了本机切到美国 VPS 的代理。外层配好 HTTPS，建完账号后关闭公开注册。

模型路由配置在 `librechat.yaml` 里，密钥通过环境变量注入。目前接了三个常用模型：Z-API 的 GPT-6.2 Sol 和 Astra，以及单独一条线的 Claude Opus 5.5（Opus 首次流式测试 50 秒超时，复测 17 秒返回完整结果；中间试过 `gpt-6-sol`，无法确认上游与网页版一致且 `chat-latest` 返回 404，测试完就移除了）。

本来还想接 Gemini 4 Hydrogen，供应商列表里能搜到，但换了两把密钥、把 `-high` / `-low` / `-medium` / `-xhigh` 几个档位都试了一遍，请求全部返回 404，提示当前分组没有对应上游账号（实际可用列表里只有 `gemini-3.8-flash` 系列）。

## 顶栏余额与额度显示

最早单做了个统计页，切模型前总要多点一次，后来缩成小组件放到模型选择器旁边：

- **Z-API 余额**：由服务端请求接口，前端只读展示数据。确认过 GPT 和 Claude 两把密钥共用同一个余额池，合并成一项显示。
- **Codex 额度**：依赖本地登录态，所以在 Windows 电脑上建了定时任务，每 10 分钟读取一次 5 小时/每周剩余百分比和重置时间并同步到站里。电脑关机后同步会停，页面加了过期状态，超时没更新会直接标出。

同一条 Z-API 线路在本地 CC Switch 里也遇到过一个小问题：切到 `gpt-6.2-sol` 后，旧长对话 8 分钟内自动压缩了 12 次。查配置发现本地默认上下文窗口只有 128K（115.2K 触发压缩），后来按公开规格把工作窗口调成 922K（1,050K 总窗减去 128K 输出，压缩线 829.8K），不过中转上游实际能承载多长上下文还没单独拿超长输入测过。

现在新对话都在这个站里进行。旧记录迁移还在等 ChatGPT 导出邮件，拿到导出包后再试导入。
