---
title: VPS 自建代理与 DNS 排查
published: 2026-10-28
updated: 2026-11-24
description: 3x-ui 多人独立订阅、Clash Verge DNS 覆写排查与证书/备份自动化配置。
image: /images/anime/bocchi-starry.webp
tags: [VPS, 自建代理, Xray, REALITY, Linux]
category: 技术笔记
draft: false
lang: zh_CN
---

## 服务器与端口

美国 VPS（2 核 2 GB，Ubuntu 22.04.5 LTS `x86_64`）。面板使用 [3x-ui](https://github.com/MHSanaei/3x-ui)，底层 Xray 协议为 VLESS / TCP / REALITY（flow `xtls-rprx-vision`），客户端为 Clash Verge（Mihomo 内核）。

- TCP `443`：Xray 代理流量。
- TCP `8443`：Nginx HTTPS 订阅入口。
- 面板仅监听 `127.0.0.1:54321`，管理时走本地 SSH 隧道：

```bash
ssh -N -L 15432:127.0.0.1:54321 root@VPS_HOST
```

## 多人独立订阅

共 4 份独立配置（共用入口，凭证、订阅链接与流量计数独立）：自用账号不设面板上限，另外 3 个账号每人每月 200 GiB（上下行合计 `214748364800` 字节）。满额仅停用对应账号，同账号多设备合并计费，规则模式直连不扣额度。

3 个限额账号按北京时间每月 1 日自动清零，走 3x-ui 的[日历月续期逻辑](https://github.com/MHSanaei/3x-ui/blob/v3.11.0/internal/web/service/calendar_renew.go)，已验证满额停用、清零恢复与过期续期。

## Clash Verge DNS 覆盖排查

现象：代理连通后 IP 与 WebRTC 均显示美国，但 DNS 测试仍出现国内解析器，补全订阅 DNS 规则重拉无效。

排查：检查 Clash Verge 最终生效的运行态配置，存在如下覆盖项：

```yaml
tun:
  strict-route: false
```

订阅规则在合并本地 TUN 设置时被覆盖。处理方式：在 Clash Verge TUN 设置中开启严格路由，并检查本地 DNS 覆写开关是否覆盖订阅策略（参考 Mihomo [TUN](https://wiki.metacubex.one/config/inbound/tun/) 与 [DNS](https://wiki.metacubex.one/config/dns/) 文档）。修改后尚未重跑客户端检测。

## 证书续期与数据库备份

- **证书**：Nginx 8443 使用 Let's Encrypt IP 证书，systemd timer 每 6 小时检查续期，换证前执行 `nginx -t` 通过后再 reload；已手动模拟续期与钩子触发。
- **备份**：3x-ui SQLite 数据库每日北京时间 3:15 通过 SQLite backup API 导出并校验完整性，保留 7 天，已做恢复测试。

```bash
systemctl list-timers 'personal-vpn-*'
journalctl -u personal-vpn-cert-renew.service -n 30 --no-pager
journalctl -u personal-vpn-backup.service -n 30 --no-pager
```

## 后续补充

- **Windows 游戏进程直连**：Clash Verge Rev 2.5.10（TUN 模式）配置《明日方舟》B 服 PC 端直连时，外层启动器为 `Games.exe`，游戏本体为子进程 `Arknights.exe`，需将两者完整路径一并写入 `prepend` 的 `PROCESS-PATH,...,DIRECT`。Mihomo API 确认规则已加载，未进游戏抓实时连接验证。
- **跨服务器出口**：另一台服务器直连拉取 Docker 镜像受阻时，将该机 `v2rayA`（本机 SOCKS5 `127.0.0.1:20170` / HTTP `20171`）切至本机 VLESS 节点，Cloudflare 与 IPinfo 实测出口均为美国。当天本机资源余量：50 GB 根分区剩 40 GB，可用内存约 1,283 MiB（总量 1,963 MiB，未开 swap）。
