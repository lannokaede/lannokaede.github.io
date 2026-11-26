---
title: LanAgent：Go 写的本地 Agent
published: 2026-10-30
updated: 2026-11-24
description: Go 个人 Agent 宿主设计：MCP 拆分、工具权限、并发队列、断点续跑与本地记忆。
image: /images/anime/kon-practice.webp
tags: [LanAgent, Go, Agent Harness, MCP, SQLite, Milvus]
category: 项目复盘
draft: false
lang: zh_CN
---

[LanAgent](https://github.com/lannokaede/LanAgent) 是用 Go 写的本地 Agent 宿主，终端 CLI 与独立 MCP 服务共用同一套调度核心。知识库导入 17 份 Go 官方文档，按 512 字符、64 重叠切分 1,206 个片段；代码测试在本地 Docker 容器内隔离执行。

## MCP 服务拆分

文档检索与入库拆分为独立 MCP 服务，入口统一做鉴权与并发控制，队列满直接拒绝：

- 检索：同步返回。
- 入库：含切分、向量化与写库，改为异步任务，先返回任务 ID 再轮询状态。

## 工具循环与上下文裁剪

- 外层 ReAct 循环基于 LangGraphGo。宿主层限制最大轮次与预算上限，工具走白名单，参数执行前校验 JSON Schema；文件类工具默认只读，写操作需显式放行。
- 路由先过规则层，可直接回答的跳过工具循环；不确定请求交小分类模型按严格 JSON Schema 输出，异常时退回默认路径。
- 历史裁剪按完整“工具调用 + 返回”消息组删除，避免按条截断拆散 `tool_call` 导致接口报错；摘要失败时同样回退到整组裁剪。

## 并发队列与流式重试

- SSE 流式与非流式共用调用封装，限制在途并发数与等待队列，满载立即返回错误。
- 退避重试前先释放并发槽位，下一轮重新排队，防止慢请求占满池子。
- SSE 发出首个数据包后不再自动重试；11 月中旬补充校验，非流式接口返回不完整响应直接拒绝。

## 断点续跑

模型节点与工具节点每次流转都会落盘 Checkpoint 和执行 ID，中断后凭原会话 ID 恢复并复用已完成节点。后续修复补了两项落盘规则：替换 Checkpoint 后显式持久化会话目录；Checkpoint 写入失败时停止后台 research worker。

可能修改外部状态且本地未记录回执的调用，恢复时按参数哈希向工具服务查询执行收据：存在收据直接复用，查不到则暂停在待核对状态，不自动重放写操作。

本地代理故障注入验证：模型调用 `read_file` 后上游连续返回三次 HTTP 503，重试耗尽暂停，凭原会话 ID 恢复完成，日志确认 `read_file` 仅执行一次（[验收记录](https://github.com/lannokaede/LanAgent/blob/main/docs/harness-validation.md)）。

## SQLite 与 Milvus 记忆同步

记忆正文与版本号存 SQLite，语义检索用外部 Milvus（按需开启）。修改或删除时，SQLite 单事务写入新正文、新版本号与待同步记录，后台任务持租约同步到 Milvus。召回结果不直接注入上下文，按记录 ID 回查 SQLite，过滤版本号不一致或已删除条目。
