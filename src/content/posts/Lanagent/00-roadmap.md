---
title: LanAgent 的工具调用与会话恢复
published: 2026-10-30
updated: 2026-11-20
description: 我用 Go 写的个人 Agent Harness，记录工具调用的限制、请求中断后的恢复和本地记忆。
image: /images/anime/kon-practice.webp
tags: [LanAgent, Go, Agent Harness, MCP, SQLite]
category: 项目复盘
draft: false
lang: zh_CN
---

LanAgent 是我用 Go 写的个人 Agent Harness。平时从终端输入任务，LangGraphGo 跑模型和工具之间的循环。我在宿主里管工具的权限、调用次数和会话状态。资料检索、面试练习和代码验证都接在这套工具接口上。

## 工具调用

普通问题可以直接回答。任务需要读文件或查资料时，才进工具循环。宿主会核对工具名、白名单和参数格式，也会限制模型轮次和工具调用次数。文件操作默认只读，写入要单独开启。资料检索和入库做成了独立的 MCP 服务，入库这种耗时操作会先返回任务编号，之后再查进度。

## 中断后的会话恢复

工具执行前会写一条标记，拿到结果后再把结果存下来。恢复时，有结果就接着用。遇到可能已经写入、但本地没存到结果的调用，先核对工具服务的执行收据。查不到收据时就把任务停在待核对状态。

我在验收时用代理模拟了模型接口连续返回三次 503，故障发生在文件已经读完之后。重试用完后任务停下，再恢复原会话，前后日志里只出现了一次 `read_file`。[验收记录](https://github.com/lannokaede/LanAgent/blob/main/docs/harness-validation.md)

## 本地记忆

记忆正文和版本存在 SQLite，Milvus 可以按需启用，用来做语义检索。改一条记忆时，SQLite 会在同一个事务里保存新版本和待同步记录。向量索引可能还没更新，召回后会再查 SQLite，把旧版本和已经删掉的记录滤掉。

[项目代码与使用说明](https://github.com/lannokaede/LanAgent)
