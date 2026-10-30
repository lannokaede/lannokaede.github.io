---
title: "面试复习 02｜context、并发名额与固定 worker"
published: 2026-10-30
description: "认识取消是协作信号，区分整个任务并发、模型并发和请求频率。"
tags: [面试复习, Go并发, 重点不会]
category: 面试复习
draft: false
lang: zh_CN
---

[← 面试复习总目录](/posts/interview/00-index/)

> **复习标记：重点不会** · 本文按真实模拟对话整理。“当时回答”与“我的追问”为原话摘录或明确标注的归纳；参考答案是整理后的解释，不表示已独立掌握。

认识取消是协作信号，区分整个任务并发、模型并发和请求频率。

## Q1：任务到期，怎样取消正在卡住的模型 HTTP 请求？

**当时回答**：“用 context 来规定当前任务的生命周期。”

### A：创建 context 后，还要把它传给具体操作

```go
ctx, cancel := context.WithTimeout(parentCtx, 120*time.Second)
defer cancel()
req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, body)
```

这是局部示例。真实代码还要检查错误、发送请求并关闭响应体。

context 传递期限和取消信号，不会强行杀死所有 goroutine。HTTP 请求需要绑定 context，等待 channel 的代码也要监听取消。

**我的疑问**：“没有 context 要怎么结束生命周期？”

没有绑定这个任务的 context，请求不会因为它到期而自动终止；还可能由其他机制，如 HTTP 客户端超时、网络错误结束。不能把 context 当作全局进程终止器。

---

## Q2：等待模型并发名额时，怎样响应取消？

**当时回答**：“获取名额的 channel 操作和上下文超时一块参与 select。”

### A：成功获取后立即注册释放

```go
select {
case slots <- struct{}{}:
    defer func() { <-slots }()
case <-ctx.Done():
    return ctx.Err()
}
```

这里采用“向有界 channel 写入代表占位”的约定。只有成功获得名额才能归还；`defer` 放在覆盖完整调用生命周期的函数里。`select` 两个分支同时就绪时不保证优先选择取消，后续操作仍应使用同一 context。

---

## Q3：已经限制模型并发，为什么还要固定 worker？

**当时回答**：“一个任务不一定只需要一个协程。”随后表示不太懂。

### A：它们限制不同范围

| 限制 | 控制的资源 |
| --- | --- |
| 请求限流 | 一段时间内允许进入多少请求 |
| 固定 worker | 同时执行多少个完整 Agent 任务 |
| 模型并发名额 | 同时进行多少个模型调用 |

任务还会访问数据库、执行工具、保存轨迹，不能只约束模型 HTTP 请求。固定 worker 也不等于整个服务只能有这么多 goroutine。

**提示后回答正确**：4 个 worker、2 个模型名额，最多 4 个任务在执行，最多 2 个模型请求同时进行，其余任务留在队列中。

---

## Q4：轮次限制和时间限制是一回事吗？

**当时回答**：“超出一定对话轮次就会自己超时终止循环。”

### A：是两个独立限制

达到最大轮次是轮次上限；超过期限才是超时。快而重复的无效调用可能先触发轮次限制；一次请求卡住可能先触发超时。

**复测**：画出“排队、worker 执行、等待模型名额、HTTP 请求、释放资源”，分别说明取消如何传播。Go 其他语言基础和手写题尚未验证，本轮后续按个人要求暂缓。

---

**核对资料**

- [Go：取消进行中的操作](https://go.dev/doc/database/cancel-operations)
- [context 文档](https://pkg.go.dev/context)

---

[返回总目录，选择下一个知识点 →](/posts/interview/00-index/)
