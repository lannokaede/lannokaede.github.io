---
title: LibreChat 自建 AI 聊天站
published: 2026-11-24
description: VPS 部署 LibreChat、自定义模型路由与顶栏余额/额度接入记录。
image: /images/anime/bocchi-ryo-balance.webp
tags: [LibreChat, Docker, VPS, AI]
category: 技术笔记
draft: false
lang: zh_CN
---

## 部署与模型路由

Docker Compose 部署 LibreChat `v0.8.9`（共 7 个容器）：MongoDB 存对话，Meilisearch 做全文检索，本机运行中文嵌入模型处理上传文件检索。拉取官方镜像通过代理完成。外层套 HTTPS，创建自用账号后关闭公开注册。

模型路由写在 `librechat.yaml`，密钥从环境变量读取：

- **可用线路**：Z-API 接 GPT-6.2 Sol、Astra；Claude Opus 5.5 单独一条线路（首次流式测试 50 秒超时，复测 17 秒返回完整结果）。
- **已移除 / 不可用**：
  - `gpt-6-sol`：无法确认上游与网页版一致，`chat-latest` 返回 404，测试后移除。
  - Gemini 4 Hydrogen：供应商列表可见，换两把密钥并测试 `-high` / `-low` / `-medium` / `-xhigh` 均返回 404（当前分组无上游账号，接口仅返回 `gemini-3.8-flash` 系列）。

## 顶栏余额与额度

余额和用量入口放在模型选择器旁边：

- **Z-API 余额**：服务端查询接口，前端只读结果。GPT 与 Claude 两把密钥查回同一余额池，合并为一项。
- **Codex 额度**：依赖本地登录态，Windows 定时任务每 10 分钟读取 5 小时 / 每周剩余百分比及重置时间同步到服务端。电脑关机断更后，页面按超时阈值显示过期标记。

## CC Switch 上下文窗口修正

同一条 Z-API 线路在本地 CC Switch 切到 `gpt-6.2-sol` 后，长对话 8 分钟内自动压缩 12 次。原因是本地默认上下文窗口为 128K（115.2K 触发压缩）。已按公开规格在 CC Switch 数据源将工作窗口改为 922K（总窗 1,050K 扣 128K 输出，压缩线 829.8K），中转上游实际可承载长度尚未用超长输入实测。

旧对话导入待 ChatGPT 导出包送达后再测。
