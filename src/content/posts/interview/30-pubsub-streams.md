---
title: "面试复习 30｜Pub/Sub 广播与可靠消息的区别"
published: 2026-10-30
description: "在线推送不等于持久队列，收到消息也不等于业务处理成功。"
tags: [面试复习, Redis消息, 重点不会]
category: 面试复习
draft: false
lang: zh_CN
---

[← 面试复习总目录](/posts/interview/00-index/)

> **复习标记：重点不会** · 本文按真实模拟对话整理。“当时回答”与“我的追问”为原话摘录或明确标注的归纳；参考答案是整理后的解释，不表示已独立掌握。

在线推送不等于持久队列，收到消息也不等于业务处理成功。

## Q1：发布订阅具体怎样工作？

**当时回答**：不了解机制，要求讲解。

### A：发布者向频道广播，当前订阅者接收

```text
SUBSCRIBE coupon:claimed
PUBLISH coupon:claimed '{"coupon_id":"c123"}'
```

上面两条分别由订阅客户端、发布客户端执行。通知服务与统计服务都订阅时都可收到，不是两个 worker 抢同一个任务。

---

## Q2：订阅者断线几秒，重连后补收吗？

### A：普通 Pub/Sub 不提供离线重放

频道不是保存历史消息供稍后读取的队列，断线期间消息不会自动补发。投递语义是最多一次，不提供处理失败自动重试。

---

## Q3：在线收到消息，就保证短信发出了吗？

不能。收到后、调用短信前进程可能崩溃。PUBLISH 的接收客户端数量不是业务完成证明；普通 Pub/Sub 没有业务 ACK。开启 AOF/RDB 也不会把它变成可靠消息队列。

适合实时提示、可重新获取状态的广播；关键通知不能只依赖它。

---

## Q4：Streams 改善了什么？

Streams 保存消息记录，保留期间可以继续读取；消费者组支持分工与 ACK，未确认消息可通过恢复逻辑重新认领。不是一用就自动恢复、恰好执行一次，仍需保留策略、持久化、重试与幂等。

项目现在使用 PG Outbox 与数据库模拟通知，不要声称已经使用 Streams 或真实短信队列。

**复测**：区分消息“已发布、已投递、已处理、已确认”四个时刻。

---

**核对资料**

- [Redis Pub/Sub](https://redis.io/docs/latest/develop/pubsub/)
- [Redis Streams](https://redis.io/docs/latest/develop/data-types/streams/)

---

[返回总目录，选择下一个知识点 →](/posts/interview/00-index/)
