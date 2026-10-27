# 《思想解放运动》完整版与可编辑工程

16 个理论、四组主题、三维白色角色、深蓝文字穿梭开场与连续配乐。成片为 **1920×1080 / 30 fps / 123.1 秒 / 3693 帧**，没有旁白。

## 下载

[Release：thought-liberation-20261027-v1](https://github.com/zhangkai-ssr/SP/releases/tag/thought-liberation-20261027-v1)

- [完整版 MP4](https://github.com/zhangkai-ssr/SP/releases/download/thought-liberation-20261027-v1/thought-liberation-full.mp4)：原交付文件，H.264、AAC、BT.709，约 118 MB；未为上传重新压缩。
- [可编辑工程 ZIP](https://github.com/zhangkai-ssr/SP/releases/download/thought-liberation-20261027-v1/thought-liberation-project.zip)：项目说明、完整源码、锁文件、时间线、所需画面、已混配音乐、用于重新对齐的分离伴奏，以及头像与封面。
- [SHA256SUMS.txt](https://github.com/zhangkai-ssr/SP/releases/download/thought-liberation-20261027-v1/SHA256SUMS.txt)：校验上述两个下载文件。Windows 可用 `Get-FileHash -Algorithm SHA256 -LiteralPath '下载文件路径'` 比对。

Release 附件使用英文文件名，避免 GitHub 改写中文下载名；工程包内部仍使用中文目录。仓库保存可审阅源码和预览图；大型成片及配乐随 Release 交付。工程包没有 `node_modules`、缓存、系统字体文件、原始参考视频或参考 PDF。字体在本机生成，步骤如下。

![完整分镜预览](完整分镜预览.jpg)

## 恢复工程（Windows）

本次在 Windows 上验证。需要 Node.js 22 或更高版本、Python 3.10 或更高版本、可从命令行调用的 FFmpeg/ffprobe，以及系统中文字体（微软雅黑、宋体、楷体）。如果在其他系统使用，先在 `fonts.json` 中配置已安装的等效字体；更换字体可能改变字形与版式。

1. 下载并解压工程 ZIP，在其中的 `思想解放运动/工程` 目录打开终端。Git 克隆得到的工程不含 WAV，也需从同版本 ZIP 复制 `public/audio` 和 `audio-src`。
2. 安装依赖并生成字体：

```powershell
npm ci --no-audit --no-fund
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/fonts.py
```

3. 检查与预览：

```powershell
npm test
npm run lint
.\.venv\Scripts\python.exe scripts/check_assets.py
npm run still:full
npm run dev
```

在 Remotion Studio 选择 **FullFilm**。该合成默认不嵌入音轨，因为最终导出会统一混入 `public/audio/full.wav`；需要实时试听时，在合成属性中将 `withAudio` 设为 `true`。

4. 导出完整版：

```powershell
npm run render:full
.\.venv\Scripts\python.exe scripts/export-continuation.py --full
.\.venv\Scripts\python.exe scripts/qa-sample.py 思想解放运动_完整版 --full
```

交付文件位于 `工程/out/思想解放运动_完整版_交付.mp4`。`render:full` 使用已有 `FullFilm` 时间线渲染无声画面；导出脚本加入连续配乐、下调 1 dB、编码 AAC，并设置兼容播放器的像素格式和色彩标记。

`npm run render:1080`、`render:preview`、`mix` 和网页入口仍属于早期 15 秒 `Promo` 样片，不能代替上述完整版流程。`BodyPreview` 为四理论版，当前交付以 `FullFilm` 为准。

## 编辑与音乐

- `工程/src/BodyPreview.tsx`：统一舞台、角色、卡片墙及转场。
- `工程/src/TheoryProps.tsx`：后十二个理论的三维道具。
- `工程/src/full-timing.json`：完整时间线与节拍落点。
- `工程/src/Promo.tsx`：三维文字开场。
- `工程/fonts.json`：字体配置；改文字后重新运行 `scripts/fonts.py`。

ZIP 内的 `public/audio/full.wav` 已完成混音，可直接用于导出；前四理论与早期样片对应 `continuation.wav`、`mix.wav`。重新测节拍或混音时，安装 `soundfile`（`.\.venv\Scripts\python.exe -m pip install soundfile`），再运行：

```powershell
.\.venv\Scripts\python.exe scripts/align-full.py
.\.venv\Scripts\python.exe scripts/mix-continuation.py --full
```

这两步会覆盖时间线或混音，只有主动修改配乐时才需要执行。ZIP 含 `audio-src/reference-full-instrumental.wav` 和四理论版用的 `reference-instrumental.wav`。原始视频、分离模型和中间文件不打包；人声分离相关脚本仅保留制作过程，需要自行准备输入与可选环境，正常渲染无需运行。

## 记录与发布素材

- [完整版说明](完整版说明.md)及[完整成片验收记录](完整版验收记录.md)
- [入库验证记录](入库验证记录.md)
- [需求确认及修改沿革](需求确认.md)、[调研笔记](调研笔记.md)
- [头像、竖版封面与发布文案](账号发布素材/README.md)

音乐来自用户指定参考视频的伴奏分离；没有额外的曲库授权声明。原交付做过自动音频检查和画面抽帧，未做人耳全片试听，可能仍有细微分离痕迹。工程包不分发系统字体文件，需要按上述步骤在本机生成。
