---
title: LanAgent：Go 写的本地 Agent
published: 2026-10-30
updated: 2026-11-24
description: 用 Go 写的个人 Agent 工具，记录 MCP 拆分、工具调用、断点续跑和本地记忆。
image: /images/anime/kon-practice.webp
tags: [LanAgent, Go, Agent Harness, MCP, SQLite, Milvus]
category: 项目复盘
draft: false
lang: zh_CN
---

用 Go 写了个个人用的 Agent 宿主 [LanAgent](https://github.com/lannokaede/LanAgent)，平时用来查 Go 文档、刷题和跑验证代码。

终端 CLI 和独立 MCP 服务共用这一套宿主。知识库导了 17 份 Go 官方文档，按 512 字符、64 重叠切出 1,206 个片段；代码测试放在本地 Docker 容器里跑，不直接碰宿主机环境。

## 检索与入库拆成 MCP

文档检索和入库拆成了单独的 MCP 服务，入口做鉴权和并发控制，队列满直接拒绝。

检索走同步返回；入库涉及切分、算向量和写库，耗时较长，改成异步任务，先返回任务编号再查进度。

## 工具循环与上下文裁剪

外层 ReAct 循环用 LangGraphGo 编排。宿主层限制了最大轮次和预算上限，工具按白名单放行，参数执行前校验 JSON Schema；文件类工具默认只读，写操作需要显式开启。

请求先走规则路由，能直接回答的跳过工具循环；不确定的再交给小分类模型，按严格 JSON Schema 输出，分类失败或格式异常时退回默认路径。

长对话需要裁剪历史。按条数硬截断容易把 `tool_call` 和对应的工具返回拆散导致接口报错，后来改成按完整的“调用 + 返回”消息组删除；历史摘要调用失败时也退回整组裁剪。

## 并发队列与流式重试

SSE 流式和非流式请求共用同一套调用封装，限制在途并发数和等待队列，满载直接报错。

退避重试前会先释放并发槽位，下一轮再重新排队，避免慢请求占死池子。SSE 流式输出在发出第一个数据包后不再自动重试，防止拼接乱码；11 月中旬补了校验，非流式接口返回不完整响应也会直接拒绝。

## 断点续跑

模型节点和工具节点每次流转都会把 Checkpoint 和执行 ID 落盘，中断后拿原会话 ID 恢复，已完成的节点直接复用旧结果。后面修 bug 时补了两处：替换 Checkpoint 后显式持久化会话目录，Checkpoint 写入失败时停止后台 research worker。

可能修改外部状态、但本地未记录回执的调用，恢复时会用参数哈希向工具服务查执行收据：有收据直接复用，查不到则把会话停在待核对状态，避免重复写操作。

做过一次本地代理故障注入测试：模型刚调完 `read_file` 后，上游连续返回三次 HTTP 503。重试耗尽后任务暂停，拿原会话 ID 恢复跑完，日志里 `read_file` 只执行了一次。[验收记录](https://github.com/lannokaede/LanAgent/blob/main/docs/harness-validation.md)在仓库文档里。

## 本地记忆同步

记忆正文和版本号存在 SQLite，语义检索用外部 Milvus（按需开启）。

修改或删除记忆时，SQLite 在同一事务里写入新正文、新版本号和待同步记录，后台任务持租约刷到 Milvus。因为向量库同步存在延迟，召回结果不会直接进上下文，而是拿记录 ID 回查 SQLite，过滤掉版本号不一致或已删除的数据。
