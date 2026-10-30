---
title: "面试复习 33｜Cookie、Session、Token 与越权"
published: 2026-10-30
description: "把数据携带方式、服务端会话与凭证分开；跨域题保留为未作答。"
tags: [面试复习, HTTP鉴权, 重点不会]
category: 面试复习
draft: false
lang: zh_CN
---

[← 面试复习总目录](/posts/interview/00-index/)

> **复习标记：重点不会** · 本文按真实模拟对话整理。“当时回答”与“我的追问”为原话摘录或明确标注的归纳；参考答案是整理后的解释，不表示已独立掌握。

把数据携带方式、服务端会话与凭证分开；跨域题保留为未作答。

## Q1：Cookie、Session、Token 是什么关系？

**当时回答**：Cookie 和 Session 本质差不多，前者是前端用户画像，后者是后端登录态；Token 用来鉴权。

### A：三者不是同一种东西

| 概念 | 作用 |
| --- | --- |
| Cookie | 浏览器保存并按规则自动携带的数据 |
| Session | 服务端维护的会话状态 |
| Token | 客户端提交、由服务端验证的凭证 |

常见 Session 登录：服务端保存登录会话，Cookie 只携带 Session ID，后续用它查询身份。Token 也可以通过 Cookie 或 Authorization 请求头传递，不是互斥方案。

Cookie 不是用户画像。Session 也不要求保存在当前进程内，可以使用共享存储。

---

## Q2：前端传 user_id，就能查该用户资料吗？

**当时回答正确**：不行，要鉴权，确认权限。

### A：从可信凭证确认身份，再校验目标数据权限

前端参数可被修改。已登录不代表有权访问任意对象；按当前用户、商家归属或明确授权读取，避免水平越权。

项目当前使用演示身份与签名 Cookie，不是完整真实账户体系，不能说已经实现 JWT/RBAC。

---

## Q3：跨域限制由谁实施，CORS 做什么？

**状态：最后提出的问题，随后结束模拟，未作答。**

### A：待复习补充，不计为已考会

浏览器同源策略限制页面脚本读取不满足规则的跨源资源。同源通常要求协议、主机与端口一致。CORS 通过响应头声明允许哪些跨源访问；某些请求会先发 OPTIONS 预检。

跨域不等于请求一定没到服务器，CORS 也不是服务端鉴权，不能用它阻止所有非浏览器客户端。

Cookie 属性、CSRF、预检细节还没有系统练习。后续按个人要求维持概念层次，不扩成网络底层专项。

**复测**：分别解释“知道你是谁”和“允许你看这条数据”；不把 CORS 当作登录安全机制。

---

**核对资料**

- [MDN：Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [MDN：CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)

---

[返回总目录，选择下一个知识点 →](/posts/interview/00-index/)
