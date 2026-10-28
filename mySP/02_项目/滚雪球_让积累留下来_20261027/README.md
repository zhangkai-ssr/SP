# 滚雪球 · 让积累留下来

用户确认主题：《滚雪球》：把复利用在普通人的生活里。沿用《纳瓦尔宝典·把时间拿回来》的像素角色和普通话旁白，以22镜头讲述原创虚构人物阿澈学习绘画、留下记录、修正方法的过程。

## 制作入口

- `storyboard.json`：文案、镜头类型、章节与文字标签，是本片事实源。
- `解说稿.md`、`分镜表.md`：可审看的文案与按真实音频回填的时间表。
- `prepare_audio.py`：沿用原项目音频生成，缓存关联文案/声音/语速/工具版本。
- `render.py --preview`：实际旁白的15秒样片与6张关键帧。
- `render.py`：完整候选片、SRT、分镜联系表。
- `test_render.py`：模型算术、确定性/动态图层、时间线/过期音频拒绝。
- `assets/`：旧项目角色/工坊资产及原始生成记录；其余道具程序绘制。
- `work/`：语音WAV/时间信息/QA；`audio/`：临时混音；`output/`：候选结果。

## 运行与离线恢复

Python 3.12，Pillow 12.2.0，NumPy 2.4.4，edge-tts 7.3.1；本机FFmpeg/ffprobe与Windows微软雅黑字体。要求见requirements.txt。新配音需联网；有工程包中的22段WAV和audio_timing.json时，重新渲染不请求语音服务。

```powershell
python test_render.py
python prepare_audio.py
python render.py --preview
python render.py
```

已有匹配音频时跳过prepare_audio.py。视频1280×720、24fps，保留系列既有规格。时间轴从旁白真实时长生成，镜头间留0.35秒。字幕基于服务句时间，句内按字数分配，未逐字强制对齐。数学固定比例只作假设演示。默认本地候选交付，不含发布和剪映草稿。

跨项目方法见[像素讲书视频创作流程](../../docs/像素讲书视频_创作流程.md)。精确媒体检查以本项目质检记录为准。
