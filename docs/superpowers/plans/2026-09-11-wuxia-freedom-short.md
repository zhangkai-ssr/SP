# “乘风入山海”同类型短片 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 解析用户提供的 33 秒国风动画参考片，并在不复用其画面、角色、音轨或原句的前提下，制作一条约 30 秒、16:9 的原创同类型短片。

**Architecture:** 复用仓库现有 `02_项目/存在主义项目/manju.py` 渲染器，以项目级 JSON 驱动 6 张原创插画、离线中文旁白、程序化原创 BGM、字幕和 Ken Burns 运镜。项目目录保存事实源与素材，正式交付目录保存成片、封面、制作说明、来源记录和 QA 结果。

**Tech Stack:** Python 3.12、Pillow、NumPy、imageio、imageio-ffmpeg、pyttsx3、OpenAI ImageGen、FFmpeg/ffprobe。

## Global Constraints

- 参考视频只用于结构和节奏分析，不复制其画面、角色、音轨、字幕原句或可识别 IP。
- 输出规格为 1920×1080、30 fps、H.264/AAC、约 25–40 秒。
- 优先复用现有渲染器，不新增第三套视频框架。
- 正式交付前必须验证编码、时长、音轨、黑帧、静音、字幕可读性、素材来源和 SHA-256。

---

### Task 1: 固化参考片分析与原创分镜

**Files:**
- Create: `02_项目/乘风入山海_20260911/参考视频分析.md`
- Create: `02_项目/乘风入山海_20260911/漫剧脚本.json`
- Create: `02_项目/乘风入山海_20260911/README.md`

**Interfaces:**
- Consumes: 参考片 ffprobe 数据、2 秒间隔接触表、镜头变化时间点。
- Produces: `漫剧脚本.json`，字段与现有 `manju.py` 的 `build(cfg, out_path, engine_override)` 接口一致。

- [x] **Step 1: 写入参考片结构分析**

记录 33.23 秒、1920×1080、30 fps、H.264/AAC、暖橙/青色国风、Q版主角、风雨转折、底部字幕和约 6 段叙事结构；明确只抽象结构。

- [x] **Step 2: 写入原创脚本配置**

使用 2 张标题卡与 6 个正文镜头；正文依次为醒来、规则、风雨、受阻、领悟和突破，旁白均为新写句子；配置 `size=[1920,1080]`、`fps=30`、`engine=offline`、`bgm=../存在主义项目/bgm/ambient.wav`。

- [x] **Step 3: 写入复现说明**

说明在项目目录运行 `python ..\存在主义项目\manju.py --script 漫剧脚本.json --out output\乘风入山海.mp4`，并列出依赖、素材位置和交付边界。

### Task 2: 生成一致角色的原创视觉素材

**Files:**
- Create: `02_项目/乘风入山海_20260911/assets/manju/01.png`
- Create: `02_项目/乘风入山海_20260911/assets/manju/02.png`
- Create: `02_项目/乘风入山海_20260911/assets/manju/03.png`
- Create: `02_项目/乘风入山海_20260911/assets/manju/04.png`
- Create: `02_项目/乘风入山海_20260911/assets/manju/05.png`
- Create: `02_项目/乘风入山海_20260911/assets/manju/06.png`
- Create: `02_项目/乘风入山海_20260911/素材来源与版权.md`

**Interfaces:**
- Consumes: 固定角色设定“银蓝短发、琥珀眼、墨青斗篷的原创青年行旅者”。
- Produces: 6 张无文字、无水印、16:9 国风动画插画，供 `assets/manju/<image>` 加载。

- [x] **Step 1: 生成角色定调镜头**

生成行旅者立于晨雾山崖、远望云海的宽景，作为后续角色参考。

- [x] **Step 2: 生成五个叙事镜头**

保持角色服饰、发色和面部特征一致，分别生成微笑近景、纸鹤飞行、穿越暴雨、雨中古城墙前停步、冲出云层迎向朝阳。

- [x] **Step 3: 记录素材来源**

逐图记录由 OpenAI ImageGen 在本任务中新生成，并记录未使用第三方图片、品牌、公众人物或原视频帧。

### Task 3: 渲染、质检并形成正式交付

**Files:**
- Create: `02_项目/乘风入山海_20260911/output/乘风入山海.mp4`（过程输出，Git 忽略）
- Create: `03_交付/乘风入山海_20260911/output/乘风入山海.mp4`
- Create: `03_交付/乘风入山海_20260911/封面.jpg`
- Create: `03_交付/乘风入山海_20260911/完整文案与字幕.md`
- Create: `03_交付/乘风入山海_20260911/制作说明.md`
- Create: `03_交付/乘风入山海_20260911/素材来源与版权.md`
- Create: `03_交付/乘风入山海_20260911/QA报告.md`

**Interfaces:**
- Consumes: 项目 JSON、6 张插画、现有渲染器与原创程序化 BGM。
- Produces: 可播放 MP4 和带 SHA-256 的完整交付包。

- [x] **Step 1: 渲染成片**

在项目目录执行现有渲染器并使用离线中文语音；若旁白引擎失败，则保留字幕与 BGM 并在 QA 中如实记录。

- [x] **Step 2: 执行自动质检**

用 ffprobe 验证 H.264/AAC、1920×1080、30 fps、25–40 秒；用 FFmpeg `blackdetect` 与 `silencedetect` 检查异常黑帧和长静音，并生成 12 帧接触表。

- [x] **Step 3: 执行视觉质检**

检查接触表中的角色一致性、字幕安全区、构图、黑边和明显生成瑕疵；若不合格则修图或调整配置后重新渲染。

- [x] **Step 4: 复制正式交付并记录摘要**

只复制最终成片与必需文档到 `03_交付/乘风入山海_20260911`，保留项目事实源；计算成片 SHA-256 并写入 QA 报告。
