---
title: "面试复习 18｜缓存读写模式与数据库更新后的失效"
published: 2026-10-30
description: "从改价例子理解旁路缓存，以及读穿透、同步直写和异步回写。"
tags: [面试复习, 缓存设计, 重点不会]
category: 面试复习
draft: false
lang: zh_CN
---

[← 面试复习总目录](/posts/interview/00-index/)

> **复习标记：重点不会** · 本文按真实模拟对话整理。“当时回答”与“我的追问”为原话摘录或明确标注的归纳；参考答案是整理后的解释，不表示已独立掌握。

从改价例子理解旁路缓存，以及读穿透、同步直写和异步回写。

## Q1：数据库价格改成 80，Redis 仍是 100，怎么处理？

**当时先表示不清楚，随后自己回答**：更新数据库后删缓存，下次查询查数据库并回填。

### A：这是常见的旁路缓存失效方案

```text
读：查缓存 → 未命中 → 查数据库 → 回填缓存
写：更新数据库成功 → 删除对应缓存
```

它不保证任何时刻严格一致。删除失败、并发回填等还要根据时效性要求处理。

---

## Q2：Redis 不止这一种缓存方式吧？

**我的反问**：“在我的记忆中，Redis 好像不止这一种缓存方式。”

### A：是应用设计模式，不是 Redis 的几个自动开关

| 模式 | 谁做什么 |
| --- | --- |
| Cache Aside | 应用负责查库、回填与失效 |
| Read Through | 缓存层封装未命中后的加载 |
| Write Through | 一次写操作同步更新数据库和缓存 |
| Write Behind | 先接受缓存写入，再异步落数据库 |

普通 Redis GET 不会自动帮你查 MySQL；Read Through 需要框架或自定义加载层。Write Through 也不自动产生跨 Redis、数据库的原子事务。

异步回写需要处理未落库丢失、顺序和重试等问题，不应默认用于关键资金或库存事实。

---

## Q3：数据库写成功，但删缓存失败，怎么补救？

**当时回答**：会读到“过期的数据”，但不知道补救。

### A：这里是旧数据，不一定 TTL 已过期

有限退避重试；需要跨重启可靠补偿时，数据库同事务写缓存失效 Outbox 事件，由后台重试删除；TTL 限制旧值长期保留。详见[幂等与 Outbox](/posts/interview/05-idempotency-outbox/)。

这些措施改善最终一致性，不证明任何时刻均同步。

**复测**：分别说出缓存未命中、数据库更新、删除失败三条路径。

---

**核对资料**

- [微软：Cache Aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Redis：缓存策略](https://redis.io/blog/why-your-caching-strategies-might-be-holding-you-back-and-what-to-consider-next/)

---

[返回总目录，选择下一个知识点 →](/posts/interview/00-index/)
