---
title: VPS 自建代理与 DNS 排查
published: 2026-10-28
updated: 2026-11-24
description: 用 3x-ui 拆分多人独立订阅，排查 Clash Verge 覆盖 DNS 规则，以及证书和备份自动化。
image: /images/anime/bocchi-starry.webp
tags: [VPS, 自建代理, Xray, REALITY, Linux]
category: 技术笔记
draft: false
lang: zh_CN
---

## 服务器与端口配置

VPS 配置为 2 核 2 GB，系统 Ubuntu 22.04.5 LTS（`x86_64`）。面板使用 [3x-ui](https://github.com/MHSanaei/3x-ui)，底层 Xray 走 VLESS / TCP / REALITY，flow 配 `xtls-rprx-vision`；客户端使用 Clash Verge（Mihomo 内核）。

端口按用途分开：TCP `443` 跑 Xray 代理流量，Nginx 在 TCP `8443` 提供 HTTPS 订阅入口。管理面板只监听 `127.0.0.1:54321`，不直接暴露公网，需要进后台时通过本地 SSH 隧道访问：

```bash
ssh -N -L 15432:127.0.0.1:54321 root@VPS_HOST
```

用完关掉终端即可断开隧道。

## 多人独立订阅

同一入口下拆了 4 份独立订阅，各自拥有独立的节点凭证、订阅链接和流量计数。自用账号不设面板上限，另外 3 个账号每人每月 200 GiB（面板按上下行合计，填 `214748364800` 字节）。

这样拆分后互不干扰：某个账号跑满额度只会单独停用，同一人在多台设备导入同一订阅会合并计费，客户端开规则模式时直连流量不计入额度。3 个限额账号按北京时间每月 1 日自动清零，走 3x-ui 自带的[日历月续期逻辑](https://github.com/MHSanaei/3x-ui/blob/v3.11.0/internal/web/service/calendar_renew.go)，满额停用、到点清零恢复和过期续期都已经测试通过。

## Clash Verge DNS 覆盖排查

代理连通后，IP 归属地和 WebRTC 都显示在美国，但浏览器测 DNS 依然出现国内解析器，补全订阅里的 DNS 规则重新拉取也没有变化。

后来直接查看 Clash Verge 最终生效的运行态配置，发现里面有两行覆盖项：

```yaml
tun:
  strict-route: false
```

订阅本身已经拉下来了，但在合并本地 TUN 设置时被客户端配置盖掉了。解决办法是在 Clash Verge 的 TUN 设置里打开严格路由，同时检查本地 DNS 覆写开关有没有覆盖订阅策略，具体字段可以参考 Mihomo 的 [TUN 说明](https://wiki.metacubex.one/config/inbound/tun/)和 [DNS 配置页](https://wiki.metacubex.one/config/dns/)。改完后还没重新跑客户端检测，后续会和分流规则一起核对。

## 证书续期与自动备份

Nginx `8443` 使用 Let's Encrypt 的 IP 证书，与 Xray REALITY 分开维护。续期交给 systemd timer，每 6 小时检查一次，换新证书前先跑 `nginx -t`，确认配置正常再重载 Nginx；手动模拟过续期与钩子触发。

面板的 SQLite 数据库每天北京时间 3:15 自动备份一次，保留最近 7 天。脚本直接调用 SQLite 的 backup API 导出并校验完整性，也做过恢复测试。查看定时任务和日志的命令如下：

```bash
systemctl list-timers 'personal-vpn-*'
journalctl -u personal-vpn-cert-renew.service -n 30 --no-pager
journalctl -u personal-vpn-backup.service -n 30 --no-pager
```
