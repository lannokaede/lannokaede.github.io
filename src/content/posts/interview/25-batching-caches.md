---
title: "面试复习 25｜MGET、Pipeline、Lua 与两级缓存"
published: 2026-10-30
description: "减少网络往返不等于命令并行，也不等于自动获得原子性。"
tags: [面试复习, Redis性能, 重点不会]
category: 面试复习
draft: false
lang: zh_CN
---

[← 面试复习总目录](/posts/interview/00-index/)

> **复习标记：重点不会** · 本文按真实模拟对话整理。“当时回答”与“我的追问”为原话摘录或明确标注的归纳；参考答案是整理后的解释，不表示已独立掌握。

减少网络往返不等于命令并行，也不等于自动获得原子性。

## Q1：逐个 GET 100 个商品有什么开销？

**当时回答**：不清楚。

### A：反复等待网络往返

`MGET` 一条命令获取多个 String；Pipeline 批量发送命令，不等待前一条响应再发下一条。Pipeline 减少通信等待，不保证整批原子，也不让普通命令并行执行。

---

## Q2：100 个 GET 写进同一个 Lua 可以吗？

**我的追问**：“那可不可以把 100 个 get 写在一个 Lua 里面？”

### A：可以，但单纯批量读取通常 MGET 更简单

脚本内部仍依次执行，长脚本会占用 Redis 命令执行线程。Lua 更适合还需要读取、判断、修改并整体执行的场景。批量大小也要控制，避免返回数据太大。

Cluster 原生跨 key 命令和脚本通常要求同槽；客户端拆批读取不意味着跨节点原子。

---

## Q3：本地缓存加 Redis 有什么好处和问题？

**当时回答正确**：Go 内存访问快，但缓存可能不同步。

### A：减少网络和 Redis 压力，但多份副本更难管理

```text
Go 本地缓存 → Redis → 数据库
```

本地命中省去网络；代价是各实例内存占用和旧值失效问题。更新 Redis 不会自动清理其他实例内存。可以按场景使用短 TTL、版本或失效通知，并处理通知丢失，不必所有场景都上两级。

**复测**：在“批量独立读”和“按条件扣减”两个需求里，分别选择 MGET、Pipeline、Lua，并说出原因。

---

**核对资料**

- [Redis Pipeline](https://redis.io/docs/latest/develop/using-commands/pipelining/)
- [MGET](https://redis.io/docs/latest/commands/mget/)

---

[返回总目录，选择下一个知识点 →](/posts/interview/00-index/)
