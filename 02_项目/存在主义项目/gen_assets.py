# -*- coding: utf-8 -*-
"""
为「存在主义的回归」生成 10 张氛围占位图（1080x1920）。
真正出片时用 AI 绘图(即梦/Liblib等)产出的插画替换 assets/manju/ 下同名文件即可。
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
OUT = os.path.join("assets", "manju")
os.makedirs(OUT, exist_ok=True)


def gradient(top, bottom):
    g = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / (H - 1)
        g[y, :] = [int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)]
    return Image.fromarray(g, "RGB")


def figure(draw, cx, ground, scale=1.0, color=(12, 12, 16)):
    """一个孤独的人影剪影。"""
    h = int(360 * scale)
    head_r = int(46 * scale)
    top = ground - h
    # 身体（梯形）
    bw_top, bw_bot = int(70 * scale), int(130 * scale)
    draw.polygon([(cx - bw_top, top + head_r), (cx + bw_top, top + head_r),
                  (cx + bw_bot, ground), (cx - bw_bot, ground)], fill=color)
    # 头
    draw.ellipse([cx - head_r, top - head_r, cx + head_r, top + head_r], fill=color)


def stars(draw, n=120, seed=0):
    # 伪随机（不用 random，避免环境限制）
    x = seed * 9301 + 49297
    for _ in range(n):
        x = (x * 9301 + 49297) % 233280
        px = x % W
        x = (x * 9301 + 49297) % 233280
        py = (x % (H * 6)) // 10
        x = (x * 9301 + 49297) % 233280
        r = 1 + x % 3
        draw.ellipse([px, py, px + r, py + r], fill=(230, 230, 245))


def base(top, bottom, ground_color=(10, 10, 14)):
    img = gradient(top, bottom).convert("RGB")
    d = ImageDraw.Draw(img)
    ground = int(H * 0.78)
    d.rectangle([0, ground, W, H], fill=ground_color)
    return img, d, ground


def scene01():  # 信息洪流 / 喧嚣
    img, d, g = base((40, 44, 66), (14, 16, 26))
    for i in range(0, W, 26):
        d.line([(i, 0), (i + 120, g)], fill=(60, 66, 96), width=1)
    figure(d, W // 2, g, 1.0)
    return img

def scene02():  # 自我提问 / 一束光
    img, d, g = base((20, 22, 34), (8, 9, 16))
    d.polygon([(W//2-160, 0), (W//2+160, 0), (W//2+60, g), (W//2-60, g)],
              fill=(54, 60, 92))
    figure(d, W // 2, g, 1.0, color=(8, 8, 12))
    return img

def scene03():  # 哲人 / 黎明
    img, d, g = base((196, 150, 96), (60, 44, 40))
    d.ellipse([W//2-150, g-520, W//2+150, g-220], fill=(245, 210, 150))
    figure(d, W // 2, g, 1.05, color=(30, 22, 20))
    return img

def scene04():  # 赋予意义 / 双色地平线
    img, d, g = base((70, 90, 120), (20, 26, 40))
    d.ellipse([W//2-110, g-440, W//2+110, g-220], fill=(255, 238, 200))
    figure(d, int(W*0.5), g, 1.0)
    return img

def scene05():  # 自由的重量 / 门
    img, d, g = base((34, 30, 44), (12, 10, 18))
    dw, dh = 300, 560
    d.rectangle([W//2-dw//2, g-dh, W//2+dw//2, g], fill=(18, 16, 24),
                outline=(150, 140, 120), width=6)
    d.rectangle([W//2-dw//2+24, g-dh+24, W//2+dw//2-24, g-24],
                fill=(245, 236, 210))
    figure(d, W // 2, g, 0.9, color=(10, 10, 12))
    return img

def scene06():  # 西西弗斯 / 山
    img, d, g = base((150, 120, 110), (40, 32, 34))
    d.polygon([(W//2-520, g), (W//2+120, g-760), (W//2+560, g)],
              fill=(64, 54, 52))
    d.ellipse([W//2-30, g-300, W//2+90, g-180], fill=(28, 24, 24))  # 巨石
    figure(d, W//2-70, g-150, 0.7, color=(20, 16, 16))
    return img

def scene07():  # 清醒 / 破晓
    img, d, g = base((120, 140, 150), (30, 40, 52))
    for r in range(700, 0, -90):
        c = 150 + (700 - r) // 8
        d.ellipse([W//2-r, g-r//2-180, W//2+r, g+r//2-180],
                  outline=(min(c, 255), min(c, 250), 220), width=2)
    figure(d, W // 2, g, 1.0)
    return img

def scene08():  # 转身 / 回归 / 暖光
    img, d, g = base((58, 70, 92), (18, 22, 34))
    d.ellipse([W//2-200, g-560, W//2+200, g-160], fill=(250, 220, 170))
    d.ellipse([W//2-130, g-490, W//2+130, g-230], fill=(255, 240, 205))
    figure(d, W // 2, g, 1.0, color=(14, 12, 16))
    return img

def scene09():  # 属于你 / 星空旷野
    img, d, g = base((16, 18, 40), (6, 7, 16))
    stars(d, 160, seed=7)
    figure(d, W // 2, g, 1.0, color=(10, 10, 18))
    return img

def scene10():  # 向死而生 / 朝阳之路
    img, d, g = base((230, 170, 110), (70, 46, 50))
    d.ellipse([W//2-170, g-360, W//2+170, g-20], fill=(255, 226, 160))
    d.polygon([(W//2-40, g), (W//2+40, g), (W//2+260, H), (W//2-260, H)],
              fill=(120, 86, 66))
    figure(d, W // 2, g, 1.0, color=(28, 18, 16))
    return img


scenes = [scene01, scene02, scene03, scene04, scene05,
          scene06, scene07, scene08, scene09, scene10]

for i, fn in enumerate(scenes, 1):
    img = fn().filter(ImageFilter.GaussianBlur(0.6))
    path = os.path.join(OUT, f"{i:02d}.png")
    img.save(path)
    print("saved", path)
print("done")
