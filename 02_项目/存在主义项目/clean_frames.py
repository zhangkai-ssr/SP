# -*- coding: utf-8 -*-
"""
从源视频 6b69 抽取氛围空镜，擦掉烧录文字（顶部标题渐隐黑 + 底部字幕带暗化），
存成可直接用于 manju.py 的竖屏背景图 assets/manju/real_*.png
"""
import os
import subprocess
import numpy as np
from PIL import Image
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = "源视频/6b69976223e191af2ffe673d5dacdab6.mp4"
OUT = "assets/manju"
TMP = "output/grab"
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# (时间秒, 输出名, 说明)
SHOTS = [
    (8,   "real_hand_orange", "橙光伸手"),
    (42,  "real_hand_forest", "红调森林伸手"),
    (70,  "real_forest",      "迷雾森林"),
    (115, "real_tree_wide",   "蓝树远景"),
    (132, "real_tree",        "蓝色发光树"),
    (152, "real_smoke",       "红烟焰火"),
]


def erase_text(img):
    """顶部标题渐隐黑 + 底部字幕带暗化。"""
    W, H = img.size
    base = img.convert("RGB")
    arr = np.asarray(base).astype(np.float32)

    # 顶部：全黑覆盖标题，再渐隐过渡
    top_full, top_fade = 320, 440
    for y in range(top_fade):
        a = 1.0 if y < top_full else (1 - (y - top_full) / (top_fade - top_full))
        arr[y, :, :] *= (1 - a)

    # 底部字幕带：暗化到几乎全黑，彻底盖掉白字幕(对话框还会再盖一层)
    b0, b1 = 1290, 1620
    for y in range(b0, min(b1, H)):
        d = min(y - b0, b1 - y) / 70.0
        a = min(max(d, 0.0), 1.0) * 0.96
        arr[y, :, :] *= (1 - a)

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


for t, name, desc in SHOTS:
    raw = os.path.join(TMP, f"_raw_{name}.png")
    subprocess.run([FF, "-ss", str(t), "-i", SRC, "-frames:v", "1", "-y", raw,
                    "-hide_banner", "-loglevel", "error"], check=True)
    img = Image.open(raw).convert("RGB")
    if img.size != (1080, 1920):
        img = img.resize((1080, 1920))
    out = os.path.join(OUT, name + ".png")
    erase_text(img).save(out)
    print(f"[OK] {out}  ({desc})")
print("done")
