# -*- coding: utf-8 -*-
"""
文字动画短视频生成器（竖屏 9:16）
-------------------------------------------------
读取文案文件，逐句生成"淡入 + 上移"动画，可选图片虚化背景与背景音乐，
输出抖音/视频号常见的 1080x1920 竖屏 mp4。

用法:
    python make_video.py                      # 用默认 script.txt 出片
    python make_video.py --script my.txt      # 指定文案
    python make_video.py --assets assets      # 指定背景图目录
    python make_video.py --bgm bgm/music.mp3  # 指定背景音乐
    python make_video.py --hold 2.8 --font msyhbd.ttc

文案格式（script.txt）:
    用「空行」分隔每一张卡片(card)；同一卡片内的换行会原样保留。
    以 # 开头的行视为注释，忽略。
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import imageio.v2 as imageio
import imageio_ffmpeg  # noqa: F401  (确保自带 ffmpeg 被打包)

FONTS_DIR = r"C:\Windows\Fonts"


# --------------------------------------------------------------------------- #
# 文案解析
# --------------------------------------------------------------------------- #
def parse_script(path):
    """把文案文件解析成卡片列表，每张卡片是一段文字。"""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    cards, buf = [], []
    for line in raw.splitlines():
        if line.strip().startswith("#"):
            continue
        if line.strip() == "":
            if buf:
                cards.append("\n".join(buf).strip())
                buf = []
        else:
            buf.append(line.rstrip())
    if buf:
        cards.append("\n".join(buf).strip())
    return [c for c in cards if c]


# --------------------------------------------------------------------------- #
# 字体 / 排版
# --------------------------------------------------------------------------- #
def load_font(name, size):
    """按名字加载字体，找不到就回退到微软雅黑。"""
    candidates = [name, os.path.join(FONTS_DIR, name),
                  os.path.join(FONTS_DIR, "msyh.ttc")]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    raise RuntimeError(f"无法加载字体: {name}")


def wrap_text(text, font, max_width, draw):
    """按像素宽度对中文/混排文本自动换行（保留原有的手动换行）。"""
    out_lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            out_lines.append("")
            continue
        line = ""
        for ch in paragraph:
            test = line + ch
            w = draw.textbbox((0, 0), test, font=font)[2]
            if w > max_width and line:
                out_lines.append(line)
                line = ch
            else:
                line = test
        out_lines.append(line)
    return out_lines


# --------------------------------------------------------------------------- #
# 背景
# --------------------------------------------------------------------------- #
def make_gradient(size, top=(24, 26, 38), bottom=(8, 8, 14)):
    """生成一张竖直渐变背景，作为没有图片时的兜底。"""
    w, h = size
    grad = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / max(h - 1, 1)
        grad[y, :] = [int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)]
    return Image.fromarray(grad, "RGB")


def prepare_background(img_path, size, blur=18, darken=0.45):
    """把一张图片处理成"铺满 + 虚化 + 压暗"的背景，突出文字。"""
    w, h = size
    img = Image.open(img_path).convert("RGB")
    # 等比缩放后居中裁剪到目标比例 (cover)
    scale = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1))
    left = (img.width - w) // 2
    top = (img.height - h) // 2
    img = img.crop((left, top, left + w, top + h))
    img = img.filter(ImageFilter.GaussianBlur(blur))
    # 压暗
    overlay = Image.new("RGB", size, (0, 0, 0))
    img = Image.blend(img, overlay, darken)
    return img


# --------------------------------------------------------------------------- #
# 单帧渲染
# --------------------------------------------------------------------------- #
def render_text_layer(size, lines, font, line_gap, color, shadow):
    """把整段文字渲染到一张透明 RGBA 图层，返回图层与其高度。"""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    heights = [draw.textbbox((0, 0), ln or "中", font=font)[3] for ln in lines]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = (h - total_h) // 2

    for ln, lh in zip(lines, heights):
        bbox = draw.textbbox((0, 0), ln, font=font)
        lw = bbox[2] - bbox[0]
        x = (w - lw) // 2 - bbox[0]
        if shadow:
            draw.text((x + 3, y + 3), ln, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), ln, font=font, fill=color)
        y += lh + line_gap
    return layer


def ease_out(t):
    """缓出曲线，让动画收尾更自然。"""
    return 1 - (1 - t) ** 3


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def build(args):
    size = (args.width, args.height)
    fps = args.fps

    cards = parse_script(args.script)
    if not cards:
        sys.exit(f"文案为空: {args.script}")
    print(f"共 {len(cards)} 张卡片，开始渲染…")

    font = load_font(args.font, args.font_size)
    color = (255, 255, 255, 255)

    # 收集背景图
    bg_images = []
    if args.assets and os.path.isdir(args.assets):
        exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
        bg_images = sorted(
            os.path.join(args.assets, f)
            for f in os.listdir(args.assets)
            if f.lower().endswith(exts)
        )
    print(f"背景图 {len(bg_images)} 张" if bg_images else "无背景图，使用渐变兜底")

    fade = args.fade            # 淡入/淡出时长(秒)
    hold = args.hold            # 停留时长(秒)
    slide_px = args.slide       # 上移像素

    writer = imageio.get_writer(
        args.out, fps=fps, codec="libx264", quality=8,
        macro_block_size=None, ffmpeg_log_level="error",
        output_params=["-pix_fmt", "yuv420p"],
    )

    measure = ImageDraw.Draw(Image.new("RGB", size))
    max_text_w = int(size[0] * 0.84)

    try:
        for idx, card in enumerate(cards):
            # 背景
            if bg_images:
                bg = prepare_background(bg_images[idx % len(bg_images)], size,
                                        blur=args.blur, darken=args.darken)
            else:
                bg = make_gradient(size)
            bg_rgba = bg.convert("RGBA")

            # 文字图层
            lines = wrap_text(card, font, max_text_w, measure)
            text_layer = render_text_layer(size, lines, font, args.line_gap,
                                           color, args.shadow)

            total = fade + hold + fade
            n_frames = max(int(total * fps), 1)
            for fi in range(n_frames):
                t = fi / fps
                if t < fade:                      # 淡入
                    p = ease_out(t / fade)
                    alpha = p
                    dy = int((1 - p) * slide_px)
                elif t < fade + hold:             # 停留
                    alpha, dy = 1.0, 0
                else:                             # 淡出
                    p = (t - fade - hold) / fade
                    alpha, dy = max(1 - p, 0.0), 0

                frame = bg_rgba.copy()
                if alpha > 0:
                    layer = text_layer
                    if dy:
                        layer = Image.new("RGBA", size, (0, 0, 0, 0))
                        layer.paste(text_layer, (0, -dy), text_layer)
                    if alpha < 1:
                        a = layer.split()[3].point(lambda v: int(v * alpha))
                        layer = layer.copy()
                        layer.putalpha(a)
                    frame = Image.alpha_composite(frame, layer)

                writer.append_data(np.asarray(frame.convert("RGB")))
            print(f"  卡片 {idx + 1}/{len(cards)} 完成 ({n_frames} 帧)")
    finally:
        writer.close()

    print(f"[OK] 视频已生成(无声): {args.out}")

    # 合成背景音乐
    if args.bgm and os.path.isfile(args.bgm):
        mux_audio(args.out, args.bgm)


def mux_audio(video_path, bgm_path):
    """用自带 ffmpeg 把背景音乐合进视频（音频随视频长度裁剪）。"""
    import subprocess
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out = os.path.splitext(video_path)[0] + "_bgm.mp4"
    cmd = [ffmpeg, "-y", "-i", video_path, "-i", bgm_path,
           "-map", "0:v", "-map", "1:a", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k", "-shortest", out]
    print("合成背景音乐…")
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[OK] 带音乐版本: {out}")


def main():
    p = argparse.ArgumentParser(description="文字动画短视频生成器")
    p.add_argument("--script", default="script.txt", help="文案文件")
    p.add_argument("--assets", default="assets", help="背景图目录(可空)")
    p.add_argument("--bgm", default="", help="背景音乐文件(可空)")
    p.add_argument("--out", default="output/video.mp4", help="输出文件")
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--font", default="msyhbd.ttc", help="字体文件名")
    p.add_argument("--font-size", type=int, default=72)
    p.add_argument("--line-gap", type=int, default=24)
    p.add_argument("--hold", type=float, default=2.4, help="每句停留秒数")
    p.add_argument("--fade", type=float, default=0.5, help="淡入/淡出秒数")
    p.add_argument("--slide", type=int, default=48, help="入场上移像素")
    p.add_argument("--blur", type=int, default=18, help="背景虚化强度")
    p.add_argument("--darken", type=float, default=0.45, help="背景压暗 0~1")
    p.add_argument("--shadow", action="store_true", default=True)
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    build(args)


if __name__ == "__main__":
    main()
