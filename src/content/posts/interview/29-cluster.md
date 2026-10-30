---
title: "面试复习 29｜Redis Cluster：key、槽与节点"
published: 2026-10-30
description: "分片分散不同 key，副本保留相同数据；先理解 16384 个槽的中间映射。"
tags: [面试复习, RedisCluster, 重点不会]
category: 面试复习
draft: false
lang: zh_CN
---

[← 面试复习总目录](/posts/interview/00-index/)

> **复习标记：重点不会** · 本文按真实模拟对话整理。“当时回答”与“我的追问”为原话摘录或明确标注的归纳；参考答案是整理后的解释，不表示已独立掌握。

分片分散不同 key，副本保留相同数据；先理解 16384 个槽的中间映射。

## Q1：Cluster 怎样分配 key？

**当时回答**：没了解过，要求详细讲解。

### A：key 先映射到槽，再映射到主节点

```text
slot = CRC16(key) % 16384
key → 槽编号 → 负责该槽的主节点
```

16384 是槽的总数，不是要求部署这么多节点。一个槽有很多 key，每个主节点负责部分槽，自己的从节点再复制这一部分。

---

## Q2：为什么不直接对节点数取模？

节点数从 3 变 4 时，直接取模会改变大量分配。槽数量固定后，扩容主要调整槽归属，迁移槽内数据。加入一个空节点不会自动立刻把所有数据分均匀，还要进行槽迁移。

---

## Q3：客户端怎么找到节点？

Cluster 客户端缓存槽映射并直接访问对应节点。访问错误或迁移时可能收到 MOVED、ASK 重定向，通常由兼容客户端处理。

---

## Q4：两个 key 在同一个节点，就能一起执行 Lua 吗？

### A：原生多 key 操作通常要求同一个槽

同节点但不同槽仍不满足要求。可以用 hash tag：

```text
user:{123}:profile
user:{123}:settings
```

两者按花括号中的 123 算槽。不要所有 key 都用同一个 tag，否则会集中到一个槽。脚本访问的 key 应显式通过 KEYS 提供，不能把单机动态拼 key 的用法直接视为 Cluster 兼容。

---

## Q5：Cluster 能自动解决单个大 key、热 key 吗？

不能自动把一个普通 key 拆到多个主节点，单 key 的热点写入也不会自动均分。槽数量均衡不等于内存、流量都均衡。

**复测**：分别画一个三主分片、一个一主两从图，指出数据哪些相同、哪些不同。

---

**核对资料**

- [Redis Cluster 规范](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [扩容与槽迁移](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)

---

[返回总目录，选择下一个知识点 →](/posts/interview/00-index/)
