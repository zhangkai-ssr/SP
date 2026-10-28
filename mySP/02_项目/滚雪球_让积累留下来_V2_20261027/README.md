# 滚雪球：让积累留下来 · V2

用户反馈 V1 内容及封面不如《把时间拿回来》生动，本版重写为同一角色阿澈的修表寓言，重新生成竖版封面、两张场景背景与无指针怀表美术，保留已有角色和工坊。旧版保留。

24 镜头，约 227.4 秒，1280×720、24fps；普通话合成旁白。表面、指针、人物、记录页与字幕独立合成。2D 图层动画，不是全动作角色表演或三维机械仿真。

## 本地复现

Windows Python 3.12、FFmpeg、微软雅黑。安装 requirements.txt。运行 `python test_render.py` 不需要配音缓存。首次从 Git 克隆后先运行 `python prepare_audio.py` 生成配音，再运行 `python render.py --preview` 或 `python render.py`。已有匹配的 work/ 中 WAV、audio_timing.json 时可跳过配音；旁白改变时须重新生成。

assets/ 是美术与来源；storyboard.json 是分镜；work/ 是音频缓存和质检日志；audio/ 是混音；output/ 是候选片。工程包保留现有 WAV，可离线合成；不分发字体。

Git 保存源工程、分镜、素材及检查记录；成片和配音缓存按项目规则不提交。用户已授权提交 PR 并合入，视频尚未发布。具体来源与检查边界见素材来源.md、质检记录.md。
