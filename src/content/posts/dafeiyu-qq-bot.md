---
title: 大肥鱼 QQ 机器人记录
published: 2026-10-28
updated: 2026-11-24
description: AstrBot + NapCat 搭的 QQ 机器人，记录群聊、表情包、记忆和视频识别。
image: /images/anime/bocchi-school.webp
tags: [QQ机器人, AstrBot, NapCat, 大肥鱼, Docker]
category: 技术笔记
draft: false
lang: zh_CN
---

给大肥鱼加视频识别时查了发给模型的原始消息，发现群里发过去的视频传到模型只剩 `[视频]` 两个字——部分路径拿到文件地址后没有继续抽帧，模型根本看不到画面。

大肥鱼是挂在 QQ 上的机器人，人设基于社区的[大肥鱼人格文件](https://github.com/whyever77/dafeiyu-astrbot/blob/main/persona/大肥鱼-人格.md)改的，底层用 AstrBot 配 NapCat。这里记一下部署和几个模块踩过的问题。

## 部署方式

服务器系统是 OpenCloudOS 9.4，跑两个容器：[AstrBot](https://github.com/AstrBotDevs/AstrBot)（`v4.29.1`）和 NapCat（`v4.18.41`），镜像都锁了 digest。NapCat 负责挂 QQ，走 OneBot 11 反向 WebSocket 把消息推给 AstrBot。改动配置或升级前会备份 Compose 文件、AstrBot 数据卷和 QQ 登录目录。

聊天和记忆整理接 OpenAI 兼容网关（DeepSeek），服务器只管消息接入、插件和一个小向量模型。面板挂在 Nginx 后面走 HTTPS，后端端口仅绑回环地址。`/opt/astrbot` 下常用查看命令：

```bash
docker compose ps
docker compose logs --tail 100 astrbot
docker logs --tail 100 napcat
```

## 群聊插话与人设

最初用 AstrBot 自带随机搭话（15%），后来换成 [Chat Plus](https://github.com/Him666233/astrbot_plugin_group_chat_plus) 控制群聊触发（初始概率 0.15），关掉自带随机。私聊走原生流程；群聊带最近 30 条消息和 20 轮上下文。

改人设时要注意 AstrBot 默认人格和 Chat Plus 里的人格得同步改，只改一处群里不会生效。

回复风格做了删减：闲聊压在一到三句，去掉复述和每句固定带语气词的规则，删掉没接入的语音和生图描述，群里按发言人区分称呼。

## 表情包与网关兼容

表情包插件用 `meme_manager`，导入一批图并补好描述和向量，按最近对话和人设选图，单次最多发一张。自动收图只对指定群开启，配了采样率、冷却和去重。

发图改成 Base64 传输，因为 AstrBot 和 NapCat 在两个容器里，本地路径经常互不可见。

另外遇到过网关不兼容强制 tool 调用参数的问题，在插件外加了异常捕获，报错时回退到插件自带的 JSON 逻辑，并补了测试。后续升级 `meme_manager` 时需要核对这个补丁还在不在。

## 长期记忆长度截断

长期记忆用 [LivingMemory](https://github.com/lxfight-s-Astrbot-Plugins/astrbot_plugin_livingmemory)，本地 CPU 跑 `BAAI/bge-small-zh-v1.5`（512 维，仅监听回环地址）做向量检索。

早期短文本测试正常，记忆变长后本地向量接口开始拒收。排查发现接口上限写死 2000 字符，而 LivingMemory 聚合出的文本会到 4000 字符。

把接口上限改到 4000 字符后不再报错，但 `bge-small-zh-v1.5` 本身按 512 tokens 截断，超长文本后半段不会进入向量，后续还需要在入库前分段。

## 视频抽帧与插件顺序

视频识别基于 [LLM 综合增强](https://github.com/Foolllll-J/astrbot_plugin_llm_enhancement)的媒体模块包了一层精简入口。普通视频、引用视频和合并转发视频都会先交给 FFmpeg 抽帧；纯文本跳过。

最初挂上去时，Chat Plus 会在发请求前重写上下文，把排在它前面的视频描述冲掉。把媒体解析挪到重写之后，问题解决。

测试时用 FFmpeg 合成了一段 8 秒短片（红球移向蓝方块），直接发、引用和合并转发三条链路都跑通了真实模型。目前只做抽帧和画面文字，没接语音识别；超时会截断，读失败直接说明没看清。

## QQ 登录掉线

QQ 登录态比较容易掉：遇过扫码后返回 `168`（账号安全限制），也遇过凭据过期快捷登录被拒。容器正常运行不代表登录态还活着。

10 月 28 日装完视频插件后 QQ 卡在等待扫码状态，服务端短片测试通过，但没往真实群里发过实测消息。

## 下线记录

11 月 23 日准备在这台机器上搭 [LibreChat](/posts/self-hosted-aichat/)，当时根分区只剩约 12 GB、可用内存 1.68 GiB，于是把 NapCat、AstrBot 及对应的后台服务和 Nginx 配置卸掉了。

卸载后根分区回到约 17 GiB，可用内存 2.51 GiB，原有配置和数据打包留了约 4.2 GiB 本地备份。真实群聊的视频测试也就没继续补。
