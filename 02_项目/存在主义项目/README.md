# 存在主义的回归 · 短视频项目

围绕「存在主义」主题的竖屏漫剧短片项目：从口播视频提取文案，再生成带配音/字幕/运镜的成片。

## 目录结构
```
存在主义项目\
├─ manju.py            漫剧渲染器（配音+时间轴+对话框+Ken Burns运镜+合成）
├─ gen_assets.py       氛围占位插画生成器（10张场景图）
├─ ocr_segment.py      烧录字幕提取工具（白字变化检测去重）
├─ 漫剧脚本.json        分镜剧本（改这个换内容）
├─ 存在主义文案.md       从源视频提取整理的完整文案 + 逐句字幕
├─ assets\manju\       场景占位图 01~10.png（换成AI插画即可覆盖）
├─ output\             成片输出
│   └─ 存在主义短片.mp4   当前成品（62s / 1080×1920 / 带配音）
└─ 源视频\
    └─ 6b69...mp4       文案来源口播视频（存在主义主题，2:53）
```

## 用法（在本文件夹内运行）

```powershell
# 1) 生成占位插画（首次或改了 gen_assets.py 后）
python gen_assets.py

# 2) 渲染成片
python manju.py --out output\存在主义短片.mp4

# 3) 覆盖引擎（可选）：offline=离线音 / edge=微软神经音(需联网代理) / none=只字幕
python manju.py --engine edge
```

## 配音说明
- 默认 `offline`：Windows 自带 `Huihui` 离线中文语音，免联网、偏机械。
- `edge`：微软神经语音（自然），但当前网络访问 `speech.platform.bing.com` 的 TLS 被拦截，需挂代理后可用。改 `漫剧脚本.json` 里的 `"engine": "edge"` 即可。

## 升级方向
1. **画面**：用即梦/Liblib/Midjourney 出真插画，按同名覆盖 `assets\manju\01~10.png`。
2. **配乐**：`漫剧脚本.json` 的 `"bgm"` 填音乐路径，自动混入。
3. **配音**：挂代理换 edge-tts，或接国内云语音（讯飞/豆包，需 API key）。

## 文案提取流程（ocr_segment.py）
源视频是烧录字幕（无独立字幕轨），提取步骤：
1. ffmpeg 按 3fps 裁底部字幕条；
2. `ocr_segment.py` 用"近白像素掩膜"做变化检测，去重出每句代表帧，拼成长图；
3. 人工/模型逐句转写 → 整理进 `存在主义文案.md`。
