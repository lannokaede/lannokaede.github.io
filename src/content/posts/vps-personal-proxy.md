---
title: 美国 VPS 自建代理记录
published: 2026-10-28
updated: 2026-10-28
description: 这台美国 VPS 上的 3x-ui、独立订阅和每月配额，以及一次 Clash Verge DNS 泄漏排查。
tags: [VPS, 自建代理, Xray, REALITY, Linux]
category: 技术笔记
draft: false
lang: zh_CN
---

代理已经连上了，网页出口和 WebRTC 检测也都指向美国，DNS 列表里却还有国内解析器。订阅里的配置补过一轮，重新拉取后，结果还是一样。

后来查到，Clash Verge 本地的 TUN 设置覆盖了订阅配置。服务器发下来的文件改了，客户端运行时用的还是旧值。

## 服务端

这是一台 2 核、2 GB 的美国 VPS，系统是 Ubuntu 22.04.5 LTS，x86_64。除了自己用，还给三个朋友各配了一份订阅。

服务端选了 [3x-ui](https://github.com/MHSanaei/3x-ui)，由它管理 Xray 和用户，协议用 VLESS / TCP / REALITY，flow 是 `xtls-rprx-vision`。电脑端用 Clash Verge，核心是 Mihomo。

Xray 直接使用 TCP 443。Nginx 另开了一个 HTTPS 订阅入口，放在 TCP 8443；客户端更新订阅时来这里取配置，平时的代理连接仍然走 443。

管理面板只监听 `127.0.0.1:54321`，没有公开到外网。要改配置，就从电脑开一个 SSH 隧道：

```bash
ssh -N -L 15432:127.0.0.1:54321 root@VPS_HOST
```

`VPS_HOST` 换成自己的服务器地址。连接保持着，再通过本地 15432 端口访问面板原来的管理路径。SSH 断开，这个临时入口也就关了。

## 每人一份订阅

我自己的用户没设软件流量上限，另外三个各有 200 GiB 月额度。三个用户用同一个代理入口，但连接身份分开，流量也分开记。

这样配完，某个人用完额度，只会停掉他自己的身份。手机和电脑如果导入同一份订阅，就合用这一份额度，不再按设备拆分。订阅链接也各发各的，没有让几个人共用主订阅。

面板里的流量按上传、下载之和统计，200 GiB 填的是 `214748364800` 字节。Clash Verge 在规则模式下会让部分连接直连，这些流量没有经过 VPS，不计入代理用量。自己这份所谓的“不限额”，也只是面板不设限，服务器厂商的流量套餐仍然有效。

普通用户配置为每月 1 日续期，服务器和面板都设成了北京时间。额度耗尽后的停用、续期后的清零和恢复，都做过测试；还模拟了过期后再补续期的情况，检查会不会一直留在停用状态。用的是 3x-ui 内置的[日历月续期功能](https://github.com/MHSanaei/3x-ui/blob/v3.11.0/internal/web/service/calendar_renew.go)。

## DNS 配置改了，为什么还没生效

初版订阅确实没有配完整的 DNS 策略，所以先补了订阅端。国内和局域网的直连规则保留，其余解析需要与代理规则配合。更新订阅后，检测页里仍然能看到国内解析器，问题没有就此消失。

继续检查 Clash Verge，发现实际运行配置里还是：

```yaml
tun:
  strict-route: false
```

本地 TUN 设置把订阅里的值覆盖了。于是服务器上的订阅文件是一份，客户端下载到的也是这一份，经过本地合并之后，交给 Mihomo 的又成了另一份。之前只查订阅内容，漏掉了最后一步。

这里要去 Clash Verge 的 TUN 设置里开严格路由，同时检查 DNS 覆写是否盖掉了订阅策略。继续刷新订阅不会改变本地的覆写选项。[Mihomo 的 TUN 文档](https://wiki.metacubex.one/config/inbound/tun/)里有 `strict-route` 的平台行为说明，DNS 各个解析器字段则在[另一页](https://wiki.metacubex.one/config/dns/)。

调整后的客户端检测还没补。复测时会连同分流规则一起看，确认哪些 DNS 请求原本就该直连。

## 证书和备份

订阅入口配的是 Let's Encrypt 的 IP 地址证书，给 Nginx 提供 HTTPS，和 REALITY 入口分开维护。

续期用 systemd timer，每六小时检查一次。实际换证后，先执行 Nginx 配置检查，再重载服务。续期模拟和重载钩子都跑过，免得证书文件换了，Nginx 还拿着旧的那张。

数据库每天北京时间凌晨 3:15 备份，保留最近七个日期。脚本通过 SQLite 的 backup API 生成备份，检查完整性，通过后才保存成当天的文件。恢复也试过一次。

这两个定时任务的名字一并留在这里，下次查日志方便些：

```bash
systemctl list-timers 'personal-vpn-*'
journalctl -u personal-vpn-cert-renew.service -n 30 --no-pager
journalctl -u personal-vpn-backup.service -n 30 --no-pager
```
