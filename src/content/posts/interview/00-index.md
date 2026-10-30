---
title: "面试复习｜真实模拟 Q&A 总目录与薄弱点"
published: 2026-10-30
description: "把两轮模拟中的回答、误区、反问与解释按知识点整理，先看重点不会，再做遮答案复测。"
tags: [面试复习, 复习目录, 薄弱点]
category: 面试复习
draft: false
lang: zh_CN
---

这组文章来自 2026 年 10 月 28 日开始的连续模拟，覆盖项目、Agent、RAG、Redis 和少量网络。它不是逐字聊天导出：合并了重复确认，省略“下一题”等导航用语，保留有实质内容的回答、疑问、反问与修正。

**学习状态以对话发生时为准，不因为看过解释就标记为掌握。** 技术解释已纠正对话中不够准确的表述；项目成果、通用设计、待核实经历分别标明，示例数值不冒充实际配置。

## Q1：怎么用这套复习笔记？

先看每篇的题目，遮住答案口述 30～60 秒，再对照“当时回答”和整理后的解释。每次挑两三个薄弱点，不要一次背完整个系列。

| 标记 | 含义 |
| --- | --- |
| **重点不会** | 当时明确不清楚，或核心机制需要完整讲解 |
| **易混淆** | 有部分理解，但概念、边界或因果关系不准确 |
| **待核实** | 模型、参数、个人分工或项目事实需要回查 |
| **待复测** | 讲过或答出要点，尚未通过独立变式与实践验证 |
| **未作答** | 已提出但没有回答；出现于相应题目，不算答错 |

文章使用短段落、分隔线和清晰 Q/A 标题。右侧目录可定位问题，窄屏保留正常滚动。标记不仅靠颜色表达，打印或深色模式下也能辨认。

## Q2：目前总体到哪一步？

**第一遍学习与口述已覆盖多个核心模块，独立作答与代码验证尚未完成。** 不能给一个看似精确的掌握百分比，也不能因为第一轮重点聊数据库，就说数据库已复习完。

| 模块 | 实际状态 |
| --- | --- |
| 项目表达 | 能讲目标和主要流程，需补职责、边界和真实证据 |
| Go | context/worker 等已练；切片、接口、运行时、手写仍空白 |
| 数据库 | 事务、锁、幂等经过讲解；索引、SQL、MVCC 未系统练 |
| Agent | 工具、SSE、编排、协议、沙箱已过；很多细节需提示 |
| RAG | 链路与优化有概念；实际模型、切分参数和分工待核实 |
| Redis | 第一遍覆盖较广，后半大量内容刚讲解，需独立复测 |
| 网络 | 只过常见用途；Cookie/Session、HTTPS 有明确误区 |
| 织课工程 | OnlyOffice、MinIO、并发请求合并尚未深入问 |
| 测试与经历 | 测试证据、真实排障、协作分工尚未充分练 |
| 算法与手写 | 本次未实际验证 |

**当前个人安排：Go 语言基础、SQL 暂缓；网络只建立大概概念。** 暂缓不代表已经掌握。后续可以继续织课工程、项目测试与真实排障，再回头做综合复测。

## Q3：哪些最该优先回看？

1. [事务提交与回滚](/posts/interview/03-transactions-locks/)：语句成功不等于提交成功。
2. [幂等与业务唯一约束](/posts/interview/05-idempotency-outbox/)：相同 ID 相同参数不是冲突。
3. [SSE 分帧](/posts/interview/08-sse-tool-deltas/)：Read、事件、参数是不同边界。
4. [Lua 与单线程](/posts/interview/20-lua-threading/)：原子执行不等于回滚或业务去重。
5. [TTL 与淘汰](/posts/interview/22-ttl-eviction/)：GET 不续期，LRU/LFU 不是过期清理。
6. [分布式锁](/posts/interview/24-distributed-locks/)：锁过期不会停止旧执行者。
7. [Cookie/Session/Token](/posts/interview/33-identity-cors/)：数据载体、会话状态和凭证分开。

## Q4：完整文章目录在哪里？

### 项目、Go 与数据库

| 文章 | 本轮标记 |
| --- | --- |
| [自我介绍与项目业务链路](/posts/interview/01-project-introduction/) | 待复测 |
| [context、并发名额与固定 worker](/posts/interview/02-context-workers/) | 重点不会 |
| [事务、行锁与防止优惠券超发](/posts/interview/03-transactions-locks/) | 重点不会 |
| [持久队列、SKIP LOCKED 与心跳恢复](/posts/interview/04-durable-tasks/) | 重点不会 |
| [requestId、业务唯一约束与 Outbox](/posts/interview/05-idempotency-outbox/) | 重点不会 |

### Agent、RAG 与协议

| 文章 | 本轮标记 |
| --- | --- |
| [Function Calling、工具校验与预算硬约束](/posts/interview/06-tools-budget/) | 重点不会 |
| [双 Agent、LangGraphGo 与工具执行顺序](/posts/interview/07-multi-agent-graph/) | 易混淆 |
| [SSE 分帧、工具参数分片与结束校验](/posts/interview/08-sse-tool-deltas/) | 重点不会 |
| [Agent 异常、上下文、评测与日志](/posts/interview/09-agent-reliability/) | 重点不会 |
| [澄清续接、短期记忆与长期偏好](/posts/interview/10-clarification-memory/) | 重点不会 |
| [织课 RAG 链路与重排模型选型](/posts/interview/11-rag-pipeline/) | 待核实 |
| [Embedding 与文档切分：不是越小越好](/posts/interview/12-rag-chunking/) | 易混淆 |
| [召回不足、生成幻觉与提示注入](/posts/interview/13-rag-quality-injection/) | 重点不会 |
| [MCP、Function Calling 与工具筛选](/posts/interview/14-mcp/) | 易混淆 |
| [A2A 任务委托与项目真实接入边界](/posts/interview/15-a2a/) | 重点不会 |
| [Docker 沙箱与代码测试版本绑定](/posts/interview/16-sandbox/) | 重点不会 |

### Redis 与缓存

| 文章 | 本轮标记 |
| --- | --- |
| [Redis、进程内 map 与缓存边界](/posts/interview/17-redis-role-types/) | 易混淆 |
| [缓存读写模式与数据库更新后的失效](/posts/interview/18-cache-patterns/) | 重点不会 |
| [缓存穿透、击穿与雪崩](/posts/interview/19-cache-failures/) | 重点不会 |
| [Redis 单线程与 Lua 原子执行](/posts/interview/20-lua-threading/) | 重点不会 |
| [固定窗口、滑动窗口与本地降级](/posts/interview/21-rate-limiting/) | 重点不会 |
| [TTL、过期清理与 LRU/LFU](/posts/interview/22-ttl-eviction/) | 重点不会 |
| [RDB 快照与 AOF 写操作日志](/posts/interview/23-persistence/) | 重点不会 |
| [分布式锁是有期限的执行资格](/posts/interview/24-distributed-locks/) | 重点不会 |
| [MGET、Pipeline、Lua 与两级缓存](/posts/interview/25-batching-caches/) | 重点不会 |
| [大 key、热 key 与 Redis 变慢排查](/posts/interview/26-redis-troubleshooting/) | 重点不会 |
| [INCR 超时与不安全重试](/posts/interview/27-redis-retry/) | 重点不会 |
| [主从复制、持久化与 Sentinel](/posts/interview/28-replication/) | 重点不会 |
| [Redis Cluster：key、槽与节点](/posts/interview/29-cluster/) | 重点不会 |
| [Pub/Sub 广播与可靠消息的区别](/posts/interview/30-pubsub-streams/) | 重点不会 |
| [商家缓存隔离与大模型回答缓存](/posts/interview/31-cache-keys-models/) | 易混淆 |

### 网络与身份基础

| 文章 | 本轮标记 |
| --- | --- |
| [HTTPS 请求链路、TCP/UDP 与连接复用](/posts/interview/32-network-basics/) | 易混淆 |
| [Cookie、Session、Token 与越权](/posts/interview/33-identity-cors/) | 重点不会 |

## Q5：还有哪些没有复习，不能被目录掩盖？

- **明确暂缓**：Go 语言基础与 SQL。
- **织课具体实现**：OnlyOffice 保存回调、文件 key 与版本、MinIO 与元数据、ConcurrentHashMap/CompletableFuture 请求合并。
- **Agent 待核实**：真实模型验收、RAG 模型与参数、评测数据与效果、长期记忆实际接入范围。
- **工程能力**：并发测试如何设计、race 能证明什么、浏览器闭环证据、部署与优雅退出。
- **个人经历**：实际困难与定位过程、团队协作与贡献、求职动机、实习安排及反问。
- **本轮中断题**：跨域/CORS 原题未作答；外部短信与本地事务原题未作答，后续只在可靠性讨论中解释。
- **Redis 未展开**：令牌桶只提到，Streams 只作机制对比，内部编码与完整高可用运维不算已学习。

## Q6：模拟流程还要怎样调整？

第一轮后半段连续死磕事务与幂等，已确认薄弱点仍不断换题确认，影响了覆盖面。这是提问节奏问题，不应全部归因于基础不足。

后续坚持一次一个问题；插问结束后明确原题是否已答；同一主题适度追问，确认缺口就记录并切换。详细教学与独立模拟分开，避免“刚讲完能复述”被误判成已经熟练。

原有学习笔记可配合阅读：[Lanagent 系列](/posts/lanagent/00-roadmap/)、[织课系列](/posts/织课/00-roadmap/)。本目录按真实问答定位薄弱点，不替代项目源码和实践。
