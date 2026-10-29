# 主题与素材来源

本博客基于 [Fuwari](https://github.com/saicaca/fuwari)，保留上游 MIT 许可证，见根目录 `LICENSE`。

当前博客头像使用与 GitHub 账号 `lannokaede` 相同的头像，以后可在 `src/config.ts` 修改 `profileConfig.avatar`。

以下保留 Fuwari 模板附带素材的图片来源说明，当前头像不使用这些模板图片：

- [Unsplash](https://unsplash.com/)
- [星と少女](https://www.pixiv.net/artworks/108916539)，作者 [Stella](https://www.pixiv.net/users/93273965)
- [Rabbit - v1.4 Showcase](https://civitai.com/posts/586908)，作者 [Rabbit_YourMajesty](https://civitai.com/user/Rabbit_YourMajesty)

上游演示文章已从博客内容中移除。博客文章的授权与主题代码的 MIT 许可证分开配置。
# 博客徽记

`src/assets/brand/field-notes.svg` 沿用用户指定的 ENDFIELD INDUSTRIES 图案，主字标为 LANNOKAEDE，下方小字为 FIELD NOTES。三角框架、等高线和中央图案保留原矢量路径。

参考用户仓库 `lannokaede/codex-theme-endfield` 的 `assets/endfield-industries.svg`，其上游为 [Yue-plus/endfield_icons](https://github.com/Yue-plus/endfield_icons/blob/2e8d430fb505a427ffbeb4a3d22aeb943e475302/svg/endfield-industries.svg)。对应 MIT 许可保存在 `src/assets/brand/LICENSE.endfield-icons`。游戏图案与商标的权利仍归各自权利人所有。

## 观测站视觉与动效

沿用 FIELD NOTES 的工业档案风格，参考 [Arwes](https://github.com/arwes/arwes) 的科幻仪表、分层入场和细线框表达；这部分以原生 CSS、SVG 和浏览器 API 实现，没有引入 Arwes 依赖或复制项目组件。Fuwari 的阅读布局、搜索与明暗模式继续保留。

- `src/components/FieldHero.astro`：等高线勘测面板、原有徽记、自动统计公开文章数量与最近发布日期。
- `src/styles/field-motion.css`：首页分层入场、约五秒后停止的扫描与环线、文章边框交互和手机排版。
- `src/components/FieldMotion.astro`：文章正文阅读进度、卡片进入视口动效、左下角动效开关。用户选择保存在本地；系统设置减少动态效果时优先遵循系统设置。关闭动效也会跳过已有开场动画。

文章卡片默认可见，浏览器不支持 IntersectionObserver 或 JavaScript 不可用时仍能阅读。文章阅读进度以正文相对视口的位置计算，不包含页脚。

