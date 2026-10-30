---
title: "面试复习 26｜大 key、热 key 与 Redis 变慢排查"
published: 2026-10-30
description: "先区分业务慢还是 Redis 执行慢，再看命令、网络、资源和持久化。"
tags: [面试复习, Redis排障, 重点不会]
category: 面试复习
draft: false
lang: zh_CN
---

[← 面试复习总目录](/posts/interview/00-index/)

> **复习标记：重点不会** · 本文按真实模拟对话整理。“当时回答”与“我的追问”为原话摘录或明确标注的归纳；参考答案是整理后的解释，不表示已独立掌握。

先区分业务慢还是 Redis 执行慢，再看命令、网络、资源和持久化。

## Q1：大 key 与热 key 有什么区别？

**当时回答**：大 key 占用大，热 key 调用频繁。

### A：方向正确，补清“值”与“频率”

大 key 是值很大或集合元素多，不是名称很长；热 key 是访问集中。大 key 可能造成内存、传输和操作耗时，热 key 可能造成单节点热点。一个 key 可以同时又大又热。

---

## Q2：Redis 查询慢，从哪排查？

**当时回答**：穿透、击穿、雪崩，或内存满没及时清理；表示不确定。

### A：先拆耗时，别一开始套缓存故障名词

| 方向 | 关注内容 |
| --- | --- |
| 客户端与网络 | 连接池等待、连接失败、网络延迟、大响应 |
| 命令执行 | KEYS、复杂集合、长 Lua，查看 SLOWLOG |
| 资源 | CPU、内存、swap、淘汰与大 key |
| 持久化 | fork、AOF 写入、同步及磁盘状态 |
| 业务回源 | 未命中后数据库慢、集中重建 |

SLOWLOG 主要反映命令执行时间，不覆盖应用连接等待与所有网络耗时。没有慢日志，不代表用户感受到的请求一定快。

“缓存满了没及时清理”应具体检查 maxmemory、策略、淘汰频率和宿主机资源，而不是默认 Redis 忘了清理。

---

## Q3：为什么长 Lua 或 KEYS 会影响其他人？

普通命令执行主要串行，单个操作占用久，其他命令就要等待。大量遍历可以考虑 SCAN 分批，分批仍有成本，也不是得到一个固定时刻的完整快照。

**复测**：区分“缓存没命中导致整个接口慢”和“GET 在 Redis 里执行慢”，各给一个证据。

---

**核对资料**

- [Redis 延迟排查](https://redis.io/docs/latest/management/optimization/latency/)
- [延迟监控](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/)

---

[返回总目录，选择下一个知识点 →](/posts/interview/00-index/)
