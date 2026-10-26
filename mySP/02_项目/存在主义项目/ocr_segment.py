# -*- coding: utf-8 -*-
"""
从字幕条序列中检测"白字"变化，去重出每句代表帧，拼成几张长图供人工/模型转写。

用法:
    python ocr_segment.py --band output/ocr/band --out output/ocr/montage --fps 3
参数:
    --band     字幕条帧目录(里面是 b_*.png)
    --out      montage 输出目录
    --fps      抽帧帧率(用于把帧号换算成时间)
    --text-min 判定"有字幕"的最小白像素数(画面越宽越大)
    --per      每张长图放几句
"""
import os
import glob
import argparse
import numpy as np
from PIL import Image, ImageDraw


def white_mask(path, thr=180):
    im = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    m = (im[:, :, 0] > thr) & (im[:, :, 1] > thr) & (im[:, :, 2] > thr - 5)
    return m.astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--band", default="output/ocr/band")
    ap.add_argument("--out", default="output/ocr/montage")
    ap.add_argument("--fps", type=float, default=3.0)
    ap.add_argument("--text-min", type=int, default=600)
    ap.add_argument("--per", type=int, default=12)
    ap.add_argument("--change", type=float, default=0.35)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(a.band, "b_*.png")))
    if not files:
        raise SystemExit(f"没有找到字幕条帧: {a.band}")

    masks = [white_mask(f) for f in files]
    counts = np.array([m.sum() for m in masks])
    has_text = counts > a.text_min

    segments, cur = [], None
    for i in range(len(files)):
        if not has_text[i]:
            if cur is not None:
                segments.append((cur, i - 1)); cur = None
            continue
        if cur is None:
            cur = i; continue
        diff = np.logical_xor(masks[i], masks[i - 1]).sum()
        base = max(counts[i], counts[i - 1], 1)
        if diff / base > a.change:
            segments.append((cur, i - 1)); cur = i
    if cur is not None:
        segments.append((cur, len(files) - 1))

    reps = []
    for s, e in segments:
        if (e - s + 1) < 1:
            continue
        mid = (s + e) // 2
        reps.append((mid, mid / a.fps))
    print(f"检测到 {len(reps)} 个字幕段")

    band_h = Image.open(files[0]).height
    band_w = Image.open(files[0]).width
    PER, pad = a.per, 8
    for gi in range((len(reps) + PER - 1) // PER):
        chunk = reps[gi * PER:(gi + 1) * PER]
        H = len(chunk) * (band_h + pad) + pad
        canvas = Image.new("RGB", (band_w, H), (30, 30, 30))
        d = ImageDraw.Draw(canvas)
        y = pad
        for idx, t in chunk:
            canvas.paste(Image.open(files[idx]).convert("RGB"), (0, y))
            d.rectangle([0, y, band_w, y + band_h], outline=(80, 200, 120), width=2)
            d.text((12, y + 6), f"#{reps.index((idx, t)) + 1:02d}  {t:5.1f}s",
                   fill=(120, 255, 160))
            y += band_h + pad
        p = os.path.join(a.out, f"montage_{gi + 1:02d}.png")
        canvas.save(p)
        print("saved", p, f"({len(chunk)} 句)")
    print("done")


if __name__ == "__main__":
    main()
