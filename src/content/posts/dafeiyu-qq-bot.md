---
title: 大肥鱼 QQ 机器人记录
published: 2026-10-28
updated: 2026-11-24
description: 基于 AstrBot 与 NapCat 搭建 QQ 机器人的部署方式，以及群聊、表情包、记忆和视频抽帧的处理。
image: /images/anime/bocchi-school.webp
tags: [QQ机器人, AstrBot, NapCat, 大肥鱼, Docker]
category: 技术笔记
draft: false
lang: zh_CN
---

## 部署方式

服务运行在 OpenCloudOS 9.4 上，核心是两个容器：[AstrBot](https://github.com/AstrBotDevs/AstrBot)（`v4.29.1`）和 NapCat（`v4.18.41`），镜像都锁定了 digest。NapCat 负责挂接 QQ，通过 OneBot 11 反向 WebSocket 把消息推给 AstrBot，经过插件和模型处理后再返回回复。每次变更配置或升级前，会备份 Compose 文件、AstrBot 数据卷和 QQ 登录目录。

聊天和记忆整理接入 OpenAI 兼容网关（DeepSeek），管理面板放在 Nginx 后面走 HTTPS，后端端口只监听回环地址。日常在 `/opt/astrbot` 下查看状态主要用这三条命令：

```bash
docker compose ps
docker compose logs --tail 100 astrbot
docker logs --tail 100 napcat
```

## 群聊触发与人设配置

群聊回复最初用 AstrBot 自带的随机搭话，后来换成 [Chat Plus](https://github.com/Him666233/astrbot_plugin_group_chat_plus) 统一判断触发时机（初始概率 0.15），并关掉了自带的随机触发。私聊仍走原生流程；群聊上下文保留最近 30 条消息和 20 轮对话。

人设参考社区的[大肥鱼人格文件](https://github.com/whyever77/dafeiyu-astrbot/blob/main/persona/大肥鱼-人格.md)做了精简，去掉了未接入的语音和生图能力描述，闲聊长度压在 1–3 句，并按发言人区分称呼。修改时需要注意 AstrBot 默认人格和 Chat Plus 里的人格必须两边同步更新，只改一处群聊不会生效。

## 表情包与接口兼容

表情包模块使用 `meme_manager`，预导入图片后补好描述和向量，按最近对话和人设选图，单次最多发一张；自动收图只对指定群开启，加了采样率、冷却时间和去重限制。

发图方式改成了 Base64 传输，因为 AstrBot 和 NapCat 分属两个容器，传递本地文件路径经常互相不可见。另外遇到过上游网关不支持强制 tool 调用参数的问题，在插件外围加了异常捕获，报错时自动回退到插件内置的 JSON 逻辑，并补了回归测试；后续升级 `meme_manager` 时需要留意补丁是否保留。

## 长期记忆长度截断

长期记忆用的是 [LivingMemory](https://github.com/lxfight-s-Astrbot-Plugins/astrbot_plugin_livingmemory)，本地 CPU 跑 `BAAI/bge-small-zh-v1.5`（512 维，仅监听回环地址）提供向量检索。

早期短文本测试都正常，记忆积累变长后本地向量接口开始拒收请求。排查发现向量接口上限写死了 2000 字符，而 LivingMemory 聚合出的文本会达到 4000 字符。把接口上限放宽到 4000 字符后不再报错，但 `bge-small-zh-v1.5` 模型本身仍按 512 tokens 截断，超长文本后半段不会被编码进向量，后续还需要在入库前做分段。

## 视频抽帧与插件顺序

视频识别基于 [LLM 综合增强](https://github.com/Foolllll-J/astrbot_plugin_llm_enhancement)的媒体模块封装了一层精简入口，对普通视频、引用视频和合并转发视频调用 FFmpeg 抽帧，纯文本消息直接跳过。

刚接入时遇到一个插件顺序问题：Chat Plus 在发请求前会重写上下文，如果媒体解析排在它前面，抽帧得到的画面描述容易被冲掉。把媒体解析挪到上下文重写之后，画面信息就能稳定保留下来。

验证时用 FFmpeg 合成了一段 8 秒短片（红球移向蓝方块），直接发送、引用和合并转发三条路径都通过了真实模型测试。目前只做抽帧和画面文字，没有接语音识别；超时会自动截断，解析失败时直接说明没看清。QQ 登录态偶尔会因为安全限制（如返回 `168`）或凭据过期失效，容器运行正常时也需要注意检查登录状态。
