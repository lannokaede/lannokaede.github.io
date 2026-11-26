---
title: VPS 自建代理与 DNS 排查
published: 2026-10-28
updated: 2026-11-24
description: 3x-ui 拆分多人订阅，以及 Clash Verge 覆盖 DNS 规则的排查记录。
image: /images/anime/bocchi-starry.webp
tags: [VPS, 自建代理, Xray, REALITY, Linux]
category: 技术笔记
draft: false
lang: zh_CN
---

连上代理后，IP 归属地和 WebRTC 都在美国，但浏览器测 DNS 还是出现了国内解析器，补完订阅里的 DNS 规则重新拉取也没变化。下面记一下这台机器的配置和排查结果。

## 服务器与端口

机器是 2 核 2 GB 的美国 VPS，系统 Ubuntu 22.04.5 LTS（x86_64），自己用之外还给三个朋友各分了一份。

面板用 [3x-ui](https://github.com/MHSanaei/3x-ui)，底层 Xray 走 VLESS / TCP / REALITY，flow 配 `xtls-rprx-vision`；客户端用 Clash Verge（Mihomo 内核）。TCP 443 跑 Xray 代理流量，Nginx 在 TCP 8443 提供 HTTPS 订阅入口。

面板只监听 `127.0.0.1:54321`，不暴露公网，需要进后台时本地开 SSH 隧道：

```bash
ssh -N -L 15432:127.0.0.1:54321 root@VPS_HOST
```

用完关掉终端即可断开。

## 多人独立订阅

我自己的账号不设上限，三个朋友每人每月 200 GiB（面板按上下行合计，填 `214748364800` 字节）。四人共用入口，节点凭证、订阅链接和流量计数完全分开。

分开后互不影响：某人跑满 200 GiB 只停他自己的账号；同一人在多设备导入同一订阅合并计费；规则模式下直连流量不扣额度。

三个朋友的账号每月 1 号自动清零，机器和面板时区统一为北京时间。测过跑满停用、到点清零恢复和过期续期，走的是 3x-ui 自带的[日历月续期逻辑](https://github.com/MHSanaei/3x-ui/blob/v3.11.0/internal/web/service/calendar_renew.go)。

## Clash Verge 的 DNS 覆盖问题

一开始以为是订阅里漏了 DNS 规则，补全并保留国内和局域网直连后重拉，依然泄漏。

后来直接看 Clash Verge 最终生效的运行态配置，里面有两行：

```yaml
tun:
  strict-route: false
```

原因是订阅虽然拉下来了，但 Clash Verge 合并本地 TUN 设置时把配置盖掉了。

在 Clash Verge 的 TUN 设置里打开严格路由，并检查本地 DNS 覆写开关是否覆盖了订阅策略。具体字段参考 Mihomo 的 [TUN 说明](https://wiki.metacubex.one/config/inbound/tun/)和 [DNS 配置页](https://wiki.metacubex.one/config/dns/)。

改完后还没重跑客户端检测，后续再连同分流规则一起核对。

## 证书续期与自动备份

Nginx 8443 用 Let's Encrypt 的 IP 证书，与 Xray REALITY 分开管理。

续期交给 systemd timer，每 6 小时检查一次；换新证书前先跑 `nginx -t`，通过再重载。手动模拟过续期和钩子触发。

面板的 SQLite 数据库每天北京时间 3:15 自动备份，保留 7 天。脚本调 SQLite backup API 导出并校验完整性，也做过恢复测试。查日志命令：

```bash
systemctl list-timers 'personal-vpn-*'
journalctl -u personal-vpn-cert-renew.service -n 30 --no-pager
journalctl -u personal-vpn-backup.service -n 30 --no-pager
```

## 后续补充

11 月中下旬又补了两项用法：

- **Windows 游戏进程直连**：在 Clash Verge Rev 2.5.10（开 TUN）里让《明日方舟》B 服 PC 端直连，只加外层启动器 `Games.exe` 不够，游戏本体是子进程 `Arknights.exe`，需要把两个完整路径一起写进 `prepend` 的 `PROCESS-PATH,...,DIRECT`。Mihomo API 确认规则已加载，但没进游戏抓实时连接验证。
- **给另一台服务器做出口**：11 月 23 日在另一台机器搭 [LibreChat](/posts/self-hosted-aichat/) 时直连拉不动镜像，把那台机器上的 `v2rayA`（本机 SOCKS5 `127.0.0.1:20170`、HTTP `20171`）切到了这台美国 VPS 的 VLESS 节点，Cloudflare 和 IPinfo 实测出口在美国。当天看资源余量：50 GB 根分区剩 40 GB，可用内存约 1,283 MiB（总量 1,963 MiB，未开 swap）。
