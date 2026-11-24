---
title: 美国 VPS 分给三个朋友共用，顺手查了个 Clash Verge DNS 泄漏
published: 2026-10-28
updated: 2026-11-24
description: 给自己和三个朋友拆了独立订阅和 200 GiB 月额度，顺带记一下排查 Clash Verge 偷偷盖掉 DNS 规则的过程。
image: /images/anime/bocchi-starry.webp
tags: [VPS, 自建代理, Xray, REALITY, Linux]
category: 技术笔记
draft: false
lang: zh_CN
---

代理明明连着，查 IP 归属地和 WebRTC 也都在美国，结果浏览器一测 DNS，列表里还是挂着几个国内解析器。回头把订阅里的 DNS 策略补了一圈重拉，结果纹丝不动。

## 服务器和端口是怎么分的

机器是台 2 核 2 GB 的美国 VPS，系统跑 Ubuntu 22.04.5 LTS（x86_64），除了自己用，顺手给三个朋友也各分了一套。

面板选了 [3x-ui](https://github.com/MHSanaei/3x-ui)，底层 Xray 走 VLESS / TCP / REALITY，flow 配 `xtls-rprx-vision`；电脑客户端用 Clash Verge（Mihomo 内核）。端口分工挺简单：TCP 443 给 Xray 跑代理流量，Nginx 另外在 TCP 8443 开个 HTTPS 订阅入口，平时走 443，更新订阅才找 8443。

管理面板只绑在 `127.0.0.1:54321`，不直接露在公网上。要进后台改东西的时候，本地开条 SSH 隧道凑合就行：

```bash
ssh -N -L 15432:127.0.0.1:54321 root@VPS_HOST
```

把 `VPS_HOST` 换成机器地址，终端别关，浏览器打开本地 15432 端口就能进。用完把隧道一掐，入口跟着就断了。

## 四个人拆四份订阅

我自己那份在面板里没设限，三个朋友每人每月给了 200 GiB（面板按上传加下载算，填的是 `214748364800` 字节）。四个人共用同一个入口，节点凭证、订阅链接和流量计数全分开。

拆开之后省心不少：谁先跑满 200 GiB，面板只停他一个人的号，不连累别人；同一个人手机电脑都导同一份订阅，就合着扣这一份。客户端开规则模式的话，直连网站不走 VPS，自然也不扣额度。当然我自己所谓“不限额”只是面板不管，VPS 本身的月流量包还是卡在那的。

三个朋友的账号设了每月 1 号自动清零，机器和面板时区统一调成了北京时间。之前特意把额度跑满停用、到点清零恢复、过期再续期都试了一轮，走的是 3x-ui 自带的[日历月续期逻辑](https://github.com/MHSanaei/3x-ui/blob/v3.11.0/internal/web/service/calendar_renew.go)，没出岔子。

## Clash Verge 把 DNS 规则偷偷盖掉了

一开始以为是自己订阅文件漏写 DNS 规则，老老实实补了一遍、留好国内和局域网直连，重拉订阅再测，照样泄漏。

后来把 Clash Verge 实际生效的运行态配置翻出来一看，里面赫然躺着两行：

```yaml
tun:
  strict-route: false
```

破案了——订阅确实把新配置拉下来了，但 Clash Verge 合并本地 TUN 设置时又给盖回去了。我一开始光盯着下载下来的 YAML 看，压根没翻 Mihomo 最终吞进去的那份配置，白绕了一圈。

解决办法就是在 Clash Verge 的 TUN 设置里把严格路由打开，顺手看看本地的 DNS 覆写开关是不是把订阅策略全顶掉了。本地覆写还开着的话，外面订阅刷再多遍都没用。具体字段可以看 Mihomo 的 [TUN 说明](https://wiki.metacubex.one/config/inbound/tun/)和 [DNS 配置页](https://wiki.metacubex.one/config/dns/)。

不过改完之后还没重跑客户端检测，等有空再连着分流规则一起核一遍，顺便理清哪些域名本来就该走本地解析。

## 证书续期和数据库自动备份

Nginx 8443 用的是一张 Let's Encrypt 的 IP 证书，跟 Xray 的 REALITY 分开管。

续期扔给 systemd timer，每六小时查一次；真换了新证书会先跑 `nginx -t`，过了再重载 Nginx，免得证书换了服务还拿着旧的。手动模拟过一轮续期和钩子触发，能正常切过去。

面板的 SQLite 数据库每天北京时间凌晨 3:15 自动备一次，留最近七天。脚本直接调 SQLite 的 backup API 导副本，校验完整性通过才落盘，也拿备份文件试过一次恢复。把查日志的三条命令顺手记这儿，省得后面出事到处翻：

```bash
systemctl list-timers 'personal-vpn-*'
journalctl -u personal-vpn-cert-renew.service -n 30 --no-pager
journalctl -u personal-vpn-backup.service -n 30 --no-pager
```

## 后面顺手多出来的两个用法

11 月中下旬，这台机器和 Clash Verge 又顺手补了两笔记录：

- **Windows 下给游戏加进程直连**：在 Clash Verge Rev 2.5.10（开着 TUN）里想让《明日方舟》B 服 PC 端绕过代理，一开始只把 `Games.exe` 加进了本地订阅规则覆写的 `PROCESS-PATH,...,DIRECT`，后来一看它只是外层启动进程，真正跑游戏本体的是子进程 `Arknights.exe`，得把两个完整路径一块加进 `prepend`。Mihomo API 确认规则都加载进去了，不过当时没进游戏抓实时连接验证命中。
- **给另一台服务器当美国出口**：11 月 23 日在另一台机器上搭自用 [LibreChat](/posts/self-hosted-aichat/) 时，官方镜像直连拉不动，干脆把那台机器上的 `v2rayA`（本机 SOCKS5 `127.0.0.1:20170` 和 HTTP `20171`）直接切到了这台美国 VPS 的 VLESS 节点，Cloudflare 和 IPinfo 实测出口都在美国。顺手看了眼 11 月 23 日这台 VPS 的资源余量：50 GB 根分区还剩 40 GB，内存可用约 1,283 MiB（总量 1,963 MiB，没开 swap），带这些个人服务绰绰有余。
