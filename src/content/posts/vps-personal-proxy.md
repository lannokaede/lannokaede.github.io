---
title: 美国 VPS 自建代理记录
published: 2026-10-28
updated: 2026-10-28
description: 用 3x-ui 和 Xray 搭了一个 VLESS + REALITY 节点，记一下订阅、流量限额和 DNS 泄漏的问题。
tags: [VPS, 自建代理, Xray, REALITY, Linux]
category: 技术笔记
draft: false
lang: zh_CN
---

最近在美国 VPS 上搭了个代理，自己用，也分给几个朋友。服务端用 3x-ui 管理，协议选了 VLESS + REALITY，电脑上用 Clash Verge。

节点搭好之后，又补了独立订阅、每月流量限额和自动续期。中间碰到一次 DNS 泄漏，查到最后发现订阅里的配置被客户端覆盖了。这篇主要记这些，具体地址和密钥就不贴了。

## 服务器和配置

机器是 2 核、2 GB 内存，系统为 Ubuntu 22.04.5 LTS，x86_64。上面还跑着其他服务。

目前这套配置是：

- 管理面板：3x-ui
- 代理核心：Xray
- 协议：VLESS，TCP 传输，REALITY，`xtls-rprx-vision`
- 客户端：Clash Verge / Mihomo
- 订阅 HTTPS 入口：Nginx

3x-ui 管用户、订阅和流量，代理流量由 Xray 处理。配置字段可以对照 [3x-ui](https://github.com/MHSanaei/3x-ui) 和 [Xray 文档](https://xtls.github.io/config/transport.html)查。

代理用 TCP 443，订阅入口用 TCP 8443。更新订阅只是下载配置，成功了也不代表节点一定能连上。排查时要分开看。

管理面板只监听 `127.0.0.1:54321`，需要访问时开 SSH 隧道：

```bash
# VPS_HOST 换成自己的服务器地址
ssh -N -L 15432:127.0.0.1:54321 root@VPS_HOST
```

然后通过本地 15432 端口和面板原来的管理路径访问，公网不用额外开放面板端口。

## 给朋友单独分订阅

我自己的身份没设软件流量上限，另外建了三个身份，每个每月 200 GiB。每个人拿自己的订阅，用完额度只停对应的身份。

这里要单独建用户，不能把同一条链接发给三个人。用同一身份连接的设备会合并计量，手机和电脑同时用也是一样。

200 GiB 对应 `214748364800` 字节，上传和下载加起来算。规则模式下直连的流量没经过服务器，不计入这个额度。自己的身份虽然不限额，VPS 厂商的套餐流量还是照算。

重置时间定在北京时间每月 1 日零点，到点清零普通用户的用量，恢复因额度耗尽被停用的身份。这部分额外写了维护逻辑。测试过耗尽后停用、重置后恢复，也确认了不会影响其他用户。

## DNS 泄漏

节点能用之后，我跑了一次检测。网页出口和 WebRTC 显示的都是美国服务器，DNS 结果里却有国内解析器。

先查订阅，初版确实缺了完整的 DNS 策略，补上后重新拉取。但问题还在。

再去看 Clash Verge 最终生效的配置，发现 TUN 的严格路由仍然是关的：

```yaml
tun:
  strict-route: false
```

订阅已经改了，Clash Verge 自己的 TUN 设置却把它覆盖回去了。继续刷新订阅没有用，需要在客户端的 TUN 设置里开启严格路由，同时检查 DNS 覆写有没有覆盖订阅策略。

这一段查的时候，容易一直盯着服务器发出来的 YAML。实际上本地还有配置合并，应该直接看客户端运行时用的那份。相关字段在 Mihomo 的 [TUN 文档](https://wiki.metacubex.one/config/inbound/tun/)和 [DNS 文档](https://wiki.metacubex.one/config/dns/)里。

目前定位到了这两处配置问题，调整后的客户端检测还需要补测。浏览器自己的加密 DNS、IPv6 和多网卡也可能影响结果，不能只根据出口 IP 判断。

## 证书和备份

订阅入口用了 Let's Encrypt 的 IP 地址证书，每六小时检查一次续期。这个证书给 Nginx 的 HTTPS 订阅入口用，与 REALITY 连接分开。

续期任务做过 dry-run，也检查过 Nginx 的配置和重载钩子，避免证书文件更新了，服务还在用旧证书。

数据库每天按服务器本地时间 03:15 备份，保留最近七个日期。用的是 SQLite 一致性备份，已经测试过恢复。

查服务状态和最近日志，用这几条就够了：

```bash
systemctl is-active x-ui nginx
systemctl list-timers --all
journalctl -u x-ui -n 50 --no-pager
```

订阅链接里带连接凭据，分享日志和截图时记得遮掉，也别把自己的链接交给不熟悉的在线订阅转换站。

暂时先用这套。服务端的计量、停用恢复和备份恢复都测过了，长时间的客户端稳定性还没专门测，等用一阵再补。
