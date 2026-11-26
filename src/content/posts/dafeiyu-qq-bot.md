---
title: 大肥鱼 QQ 机器人记录
published: 2026-10-28
updated: 2026-11-24
description: AstrBot + NapCat 部署配置，以及群聊、表情包、记忆截断与视频抽帧处理记录。
image: /images/anime/bocchi-school.webp
tags: [QQ机器人, AstrBot, NapCat, 大肥鱼, Docker]
category: 技术笔记
draft: false
lang: zh_CN
---

## 部署架构

系统为 OpenCloudOS 9.4，运行两个容器：[AstrBot](https://github.com/AstrBotDevs/AstrBot)（`v4.29.1`）与 NapCat（`v4.18.41`），镜像均锁定 digest。NapCat 通过 OneBot 11 反向 WebSocket 将消息推送至 AstrBot。变更或升级前备份 Compose 文件、AstrBot 数据卷和 QQ 登录目录。

聊天与记忆整理接入 OpenAI 兼容网关（DeepSeek），管理面板经 Nginx 反代走 HTTPS，后端端口仅绑回环地址。`/opt/astrbot` 下常用状态命令：

```bash
docker compose ps
docker compose logs --tail 100 astrbot
docker logs --tail 100 napcat
```

## 群聊触发与人设

群聊由 [Chat Plus](https://github.com/Him666233/astrbot_plugin_group_chat_plus) 控制触发（初始概率 0.15），关闭 AstrBot 原生随机搭话；私聊走原生流程。群聊上下文保留最近 30 条消息、20 轮对话。

人设基于社区[大肥鱼人格文件](https://github.com/whyever77/dafeiyu-astrbot/blob/main/persona/大肥鱼-人格.md)修改。AstrBot 默认人格与 Chat Plus 人格需同步更新，仅改一处群聊不生效。提示词中去掉未接入的语音/生图能力描述，限制闲聊长度在 1–3 句并按发言人区分称呼。

## 表情包与接口兼容

- 表情包插件为 `meme_manager`，预导入图片并补充描述与向量，单次最多发 1 张；自动收图仅对指定群开启，配置采样率、冷却与去重。
- 发送图片改用 Base64，规避 AstrBot 与 NapCat 跨容器本地路径不可见问题。
- 网关不支持插件强制 tool 调用参数时，外层捕获异常并回退到插件内置 JSON 逻辑，补充回归测试（升级 `meme_manager` 需复核补丁）。

## 长期记忆长度截断

长期记忆使用 [LivingMemory](https://github.com/lxfight-s-Astrbot-Plugins/astrbot_plugin_livingmemory)，本地 CPU 运行 `BAAI/bge-small-zh-v1.5`（512 维，仅监听回环地址）。

问题：向量接口上限写死 2000 字符，LivingMemory 聚合文本可达 4000 字符，导致长记忆写入被拒。将接口上限提高到 4000 字符后不再报错，但 `bge-small-zh-v1.5` 本身按 512 tokens 截断，超长文本后半段未进入向量，后续需在入库前分段。

## 视频抽帧与插件顺序

视频解析基于 [LLM 综合增强](https://github.com/Foolllll-J/astrbot_plugin_llm_enhancement)的媒体模块封装精简入口，对普通视频、引用视频与合并转发视频调用 FFmpeg 抽帧，纯文本跳过。

问题：Chat Plus 在发请求前会重写上下文，导致排在其前面的媒体描述被清除。调整媒体解析顺序至上下文重写之后恢复正常。

验证：用 FFmpeg 合成 8 秒测试短片（红球移向蓝方块），直接发送、引用和合并转发三条路径均通过真实模型验证。当前仅做抽帧与画面文字，未接语音识别，超时自动截断。

## 登录态与下线

QQ 登录态遇过扫码返回 `168`（账号安全限制）及凭据过期拒登。10 月 28 日装完视频插件后卡在待扫码状态，未做真实群聊发消息验证。

11 月 23 日因服务器资源紧张（当时根分区剩余约 12 GB，可用内存 1.68 GiB），卸载了 NapCat、AstrBot 及对应服务与 Nginx 配置。卸载后根分区剩余约 17 GB，可用内存 2.51 GiB，原有配置和数据打包保留约 4.2 GiB 本地备份。
