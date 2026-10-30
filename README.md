# SP 视频工作区

本仓库对应本地 `D:\sp`，按现有目录层级保存以下项目。

| 目录 | 内容 | 来源 |
|---|---|---|
| [mySP](mySP/README.md) | 自有视频工具、项目、交付与研究资料 | 原 SP 仓库内容 |
| [AUTO](AUTO/README.md) | 社交平台自动上传工具 | [social-auto-upload](https://github.com/dreammis/social-auto-upload) |
| [NarratoAI](NarratoAI/README.md) | AI 视频创作工具 | [NarratoAI](https://github.com/linyqh/NarratoAI) |
| [PV](PV/README.md) | Pixelle Video 视频生成工具 | [Pixelle-Video](https://github.com/ATH-MaaS/Pixelle-Video) |
| [ai-promo-video-maker](ai-promo-video-maker/README.md) | 产品宣传视频制作器 | [ai-promo-video-maker](https://github.com/liyupi/ai-promo-video-maker) |
| [vibe-knowledge-video](vibe-knowledge-video/README.md) | 知识短视频创作规范、Canvas 模板与渲染脚本 | [vibe-knowledge-video](https://github.com/xiazhuo123456789/vibe-knowledge-video) |

原 SP 仓库历史保留，原根目录内容现位于 `mySP/`。各第三方项目保留自己的许可证与说明。

`vibe-knowledge-video/` 收录上游 `e28759c5f4876c3e5e68444b3ed57e1c1991df18`（v2.4.0）的完整文件快照；原许可证、致谢与研究资料的使用说明均予保留。该项目偏重知识讲解与分镜设计，`ai-promo-video-maker/` 提供产品宣传工作流和 Remotion 工程，两者可按题材选用。

统一提交和推送时，在 `D:\sp` 根目录操作。子项目原有的 Git 元数据保留在本地，不上传到本仓库；远端保存完整文件，不使用 Git 子模块。

遵循各项目原有忽略规则，不提交虚拟环境、依赖目录、缓存、本地密钥与已忽略的生成物。前端 `.env.development` 和 `.env.production` 为不含密钥的构建配置，保留在仓库中。

## 知识视频账号发布素材

[《思想解放运动》完整版与工程](ai-promo-video-maker/outputs/思想解放运动15秒三维样片/README.md)：123.1 秒、16 个理论、1080p 三维动画。源码与时间线保存在仓库，原画质视频及含配乐的可编辑工程包通过 Release 下载。

[账号发布素材](ai-promo-video-maker/outputs/思想解放运动15秒三维样片/账号发布素材/README.md)：专业版头像、初版三维头像、竖版封面、主页介绍、视频发布文案与昵称候选。

## 自宣片示例

[产品宣传视频制作器 · 工具自宣片](ai-promo-video-maker/outputs/工具自宣片/使用说明.md)：45秒1080p成片、可编辑工程、素材来源和质检记录。该示例按用户要求单独入库，其他输出仍保持忽略；依赖、缓存、独立配乐和系统字体不入库，恢复步骤见示例说明。
