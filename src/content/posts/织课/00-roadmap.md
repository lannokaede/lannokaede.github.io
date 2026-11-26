---
title: 《织课》Go 后端记录
published: 2026-10-30
updated: 2026-11-24
description: 《织课》Go 后端开发笔记，记录 RabbitMQ 异步队列、singleflight 合并预览和 OnlyOffice 版本号问题。
image: /images/anime/kon-club.webp
tags: [织课, Go, PostgreSQL, Redis, RabbitMQ, MinIO, OnlyOffice]
category: 项目复盘
draft: false
lang: zh_CN
---

《织课》业务后端用 Go + Gin + GORM 实现，结构化数据存 PostgreSQL，素材和课件放在 MinIO，异步任务走 RabbitMQ，缓存与限流使用 Redis；下游 Python AI 服务基于 LangGraph、LightRAG 和 pgvector。下面记录几个核心模块的处理方式。

## 异步生成课件

生成一套课件需要经过文档解析、视频转写、检索和大纲拼装，整个过程耗时几十秒到几分钟，无法在单次 HTTP 请求里同步等待。

接口入口先用 Redis Lua 做用户级原子限流，参数校验通过后把任务投递进 RabbitMQ，直接向前端返回任务状态和编号。消费端通过预取数和固定大小的 worker 池控制并发，配合手动 ACK、消费幂等与有限次重试；调用下游 Python 推理服务时加了信号量和超时取消，防止大文件并发压垮模型服务。

## 用 singleflight 合并重复预览

课件元数据带着版本号缓存在 Redis 里。多人同时打开同一版本课件做预览导入时，后端很容易在同一时刻发起多路完全相同的请求去拉 MinIO 并做格式转换。

在 Go 侧加了一层 `singleflight`，直接以课件版本号作为 key，把进程内的并发导入合并成一次回源，其余请求等待复用同一份结果。单实例下这样就能挡住大部分并发热点；后续如果要扩展成多实例部署，跨进程的去重还需要结合共享存储和数据库版本锁来做。

## 阶段流转与 OnlyOffice 版本 key

业务流程按素材上传、需求澄清、大纲审核和产物下载拆成四个阶段，前后端按状态机严格校验，避免大纲还没确认就触发生成。

在线编辑接入了 OnlyOffice，使用中需要注意文档 `key` 必须包含版本号。如果不同版本复用了同一个 `key`，OnlyOffice 会直接返回自己缓存里的旧文件而不会重新拉取新版。网页端保存时 OnlyOffice 会回调 Go 后端，后端拉回修改后的文件写入 MinIO 并在数据库新增版本记录，旧版本保留用于回退和历史预览。
