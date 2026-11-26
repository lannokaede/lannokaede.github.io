---
title: 《织课》Go 后端记录
published: 2026-10-30
updated: 2026-11-24
description: 团队项目《织课》后端里的异步队列、并发合并和 OnlyOffice 版本号问题。
image: /images/anime/kon-club.webp
tags: [织课, Go, PostgreSQL, Redis, RabbitMQ, MinIO, OnlyOffice]
category: 项目复盘
draft: false
lang: zh_CN
---

《织课》是之前跟团队做的项目（第十七届服创国二），后来给《人工智能时代》课程备课用过，覆盖近千名学生。我负责 Go 业务后端的开发、部署以及与前端、Python AI 服务的联调。

后端栈是 Go + Gin + GORM，数据存 PostgreSQL，素材和课件放 MinIO，异步任务走 RabbitMQ，缓存和限流用 Redis；Python 侧由队友负责，用了 LangGraph、LightRAG 和 pgvector。下面记几个当时调得比较多的点。

## 异步生成课件

生成课件包含文档解析、视频转写、检索和大纲拼装，耗时几十秒到几分钟，不适合同步挂在 HTTP 请求上。

接口入口用 Redis Lua 做用户级原子限流，校验完参数把任务投进 RabbitMQ，直接把任务状态和编号返回给前端。

消费端用预取数和固定大小 worker 池控并发，配合手动 ACK、消费幂等和有限次重试。下游调用 Python 服务加了信号量和超时取消，防止几个大文件同时压垮推理服务。

## singleflight 合并重复预览

课件元数据带版本号缓存在 Redis。备课或上课时，经常出现多人同时打开同一版本课件触发预览导入，导致后端并发拉取 MinIO 和重复转格式。

在 Go 里加了 `singleflight`，拿课件版本号当 key，把同一时刻的并发导入合并成一次回源，其余请求等待同一份结果。单实例下能挡住大部分并发热点；如果后续扩成多实例，跨进程去重还需要结合共享存储和数据库版本锁。

## OnlyOffice 版本 key

业务流程拆成了素材上传、需求澄清、大纲审核和产物下载几个阶段，联调时重点对齐状态流转，避免大纲未确认就触发生成。

在线编辑接了 OnlyOffice，有个坑是文档 `key` 必须带上版本号。如果不同版本复用同一个 `key`，OnlyOffice 会直接返回缓存里的旧文档，不去拉新版。

网页端保存时 OnlyOffice 会回调 Go 后端，后端拉回修改后的文件写入 MinIO，数据库新增一条版本记录，旧版本保留，方便回退或重新预览。
