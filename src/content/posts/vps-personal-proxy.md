---
title: 美国 VPS 的订阅配置和 DNS 排查
published: 2026-10-28
updated: 2026-11-21
description: 给自己和三个朋友配了独立订阅，顺手记下流量配额和 Clash Verge 里的 DNS 排查过程。
image: /images/anime/bocchi-starry.webp
tags: [VPS, 自建代理, Xray, REALITY, Linux]
category: 技术笔记
draft: false
lang: zh_CN
---

代理明明已经连上了，IP 归属地和 WebRTC 检测也都显示在美国，可浏览器一测 DNS，列表里还是飘着几个国内解析器。回头把订阅文件里的 DNS 策略补了一遍，重新拉取之后结果依然没变。

## 服务端怎么搭的

服务器是一台 2 核 2 GB 的美国 VPS，系统跑 Ubuntu 22.04.5 LTS（x86_64）。除了自己用，还顺便给三个朋友各分了一份配置。

管理面板选了 [3x-ui](https://github.com/MHSanaei/3x-ui)，底层 Xray 走 VLESS / TCP / REALITY，flow 配的是 `xtls-rprx-vision`。电脑客户端用 Clash Verge，内核是 Mihomo。

端口上做了个简单分工：Xray 代理流量直接占 TCP 443，Nginx 另外在 TCP 8443 开了一个 HTTPS 订阅入口。平时翻出去走 443，只有客户端更新订阅时才找 8443 拉配置。

管理面板只监听 `127.0.0.1:54321`，不直接暴露到公网。要改配置的时候，本地开条 SSH 隧道连上去就行：

```bash
ssh -N -L 15432:127.0.0.1:54321 root@VPS_HOST
```

把 `VPS_HOST` 换成服务器地址，保持终端不断，浏览器访问本地 15432 端口就能进后台。隧道一关，入口也跟着断掉。

## 每人单独一份订阅

我自己用的账号没在面板里设限，另外三个朋友各给了每月 200 GiB 额度。四个人走同一个代理入口，但节点凭证和订阅链接各自独立，流量也是分开记的。

这样拆开以后，谁先把自己的 200 GiB 用完，面板只会停掉他那一个账号，不影响别人；同一个人要是手机和电脑都导了同一份订阅，就合着扣这一份流量。

面板算流量是上传加下载的总和，200 GiB 填的是 `214748364800` 字节。如果客户端开了规则模式，直连网站不经过 VPS，这部分自然不计费。当然我这份“不限额”只是面板不管，VPS 自带的月流量包还是卡着的。

三个朋友的账号设了每月 1 日自动重置，服务器和面板时区都统一调成了北京时间。为了确认不会出岔子，还专门测过额度耗尽停用、到点清零恢复，以及过期之后再补续期的流程，走的是 3x-ui 自带的[日历月续期逻辑](https://github.com/MHSanaei/3x-ui/blob/v3.11.0/internal/web/service/calendar_renew.go)。

## Clash Verge 覆写掉 DNS 的坑

刚开始我以为是订阅文件漏了 DNS 规则，于是照着补了一轮，保留国内和局域网直连，结果重拉订阅后还是照样泄漏。

后来去翻 Clash Verge 实际生效的运行配置，才看到里面还躺着一行：

```yaml
tun:
  strict-route: false
```

问题就出在这：订阅确实把新配置拉下来了，但 Clash Verge 合并本地 TUN 设置时又把配置盖回去了。一开始我只盯着下载下来的 YAML 看，没看 Mihomo 最终吞进去的那份运行态配置，白折腾一圈。

解决方式是在 Clash Verge 的 TUN 设置里打开严格路由，顺便检查本地的 DNS 覆写开关是不是把订阅里的策略全顶掉了。只要本地覆写还开着，外面订阅刷多少遍都没用。具体字段行为可以参考 Mihomo 文档里的 [TUN 说明](https://wiki.metacubex.one/config/inbound/tun/)和 [DNS 配置页](https://wiki.metacubex.one/config/dns/)。

改完还没重跑一遍客户端检测，等有空再连同分流规则一起核对，顺便确认哪些域名原本就该直接走本地解析。

## 证书续期和自动备份

Nginx 8443 端口用的是一张 Let's Encrypt 的 IP 证书，跟 Xray 的 REALITY 分开维护。

续期交给 systemd timer，每六小时跑一次检查；真换了新证书，会先跑 `nginx -t` 校验配置，过了再重载 Nginx，免得证书换完服务还拿着旧的。手动模拟过一轮续期和钩子触发，确认能正常切过去。

面板的 SQLite 数据库每天北京时间凌晨 3:15 自动备份一次，保留最近七天。脚本里直接调 SQLite 的 backup API 导副本，校验完整性通过才落成当天文件，也拿备份文件试过一次恢复。

把两个定时任务的查询命令留在这里，后面真出问题方便直接翻日志：

```bash
systemctl list-timers 'personal-vpn-*'
journalctl -u personal-vpn-cert-renew.service -n 30 --no-pager
journalctl -u personal-vpn-backup.service -n 30 --no-pager
```
