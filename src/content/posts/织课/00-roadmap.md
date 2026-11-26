---
title: 《织课》Go 后端记录
published: 2026-10-30
updated: 2026-11-24
description: 《织课》Go 后端技术笔记：RabbitMQ 异步任务、singleflight 合并预览与 OnlyOffice 版本 key。
image: /images/anime/kon-club.webp
tags: [织课, Go, PostgreSQL, Redis, RabbitMQ, MinIO, OnlyOffice]
category: 项目复盘
draft: false
lang: zh_CN
---

《织课》业务后端采用 Go + Gin + GORM，数据存 PostgreSQL，文件放 MinIO，异步任务走 RabbitMQ，缓存和限流用 Redis；下游 Python AI 服务使用 LangGraph、LightRAG 和 pgvector。

## 异步生成课件

课件生成包含文档解析、视频转写、检索和大纲拼装，耗时几十秒到数分钟，改为异步处理：

- **入口**：Redis Lua 做用户级原子限流，参数校验通过后投递 RabbitMQ，立即返回任务状态与 ID。
- **消费端**：预取数 + 固定大小 worker 池控并发，配合手动 ACK、消费幂等与有限次重试；调用下游 Python 服务加信号量和超时取消。

## singleflight 合并重复预览

课件元数据带版本号缓存在 Redis。同一版本课件被多人同时触发预览导入时，会并发回源拉取 MinIO 并重复转格式。

Go 侧引入 `singleflight`，以课件版本号为 key 合并进程内并发导入请求，仅回源一次，其余请求等待复用结果。多实例部署时，跨进程去重需配合共享存储与数据库版本锁。

## 阶段流转与 OnlyOffice 版本 key

流程拆分为素材上传、需求澄清、大纲审核与产物下载四个阶段，按状态流转校验，避免未过审即触发生成。

在线编辑接入 OnlyOffice，文档 `key` 必须包含版本号；不同版本复用同一 `key` 时 OnlyOffice 会直接返回旧缓存而不重新拉取。网页端保存回调 Go 后端，拉回新文件写入 MinIO 并在数据库新增版本记录，旧版本保留用于回退和重新预览。
