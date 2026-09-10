# -*- coding: utf-8 -*-
"""
漫剧渲染器（竖屏 9:16）
-------------------------------------------------
镜头驱动：读取 漫剧脚本.json，每个镜头 = 一张图 + 一句台词 + 运镜。
自动：TTS配音 -> 按音频时长定时间轴 -> 对话框字幕 -> Ken Burns运镜 -> 合成音频 -> 输出 mp4。

配音引擎(脚本里 "engine" 字段)：
    offline  本机离线语音(免联网, 偏机械)         —— 当前默认
    edge     微软神经语音(自然, 需联网/代理)
    none     不配音, 仅字幕(每镜头固定时长)

用法:
    python manju.py                          # 用 漫剧脚本.json
    python manju.py --script 漫剧脚本.json --out output/manju.mp4
    python manju.py --engine edge            # 覆盖脚本里的引擎
"""
import argparse
import json
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio.v2 as imageio
import imageio_ffmpeg

FONTS_DIR = r"C:\Windows\Fonts"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ASSET_DIR = os.path.join("assets", "manju")
TMP = os.path.join("output", "_tmp")


def font(name, size):
    for c in (os.path.join(FONTS_DIR, name), name,
              os.path.join(FONTS_DIR, "msyh.ttc")):
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    raise RuntimeError("字体加载失败: " + name)


def wrap(text, fnt, max_w, draw):
    out = []
    for para in text.split("\n"):
        if not para:
            out.append("")
            continue
        line = ""
        for ch in para:
            if draw.textbbox((0, 0), line + ch, font=fnt)[2] > max_w and line:
                out.append(line)
                line = ch
            else:
                line += ch
        out.append(line)
    return out


def ease(t):
    return t * t * (3 - 2 * t)  # smoothstep


# ----------------------------------------------------------------- 配音
def synth(text, scene_voice, engine, out_wav):
    """生成配音 wav。返回 True/False(是否成功)。"""
    if engine == "none":
        return False
    try:
        if engine == "edge":
            import asyncio
            import edge_tts
            mp3 = out_wav[:-4] + ".mp3"

            async def go():
                await edge_tts.Communicate(text, scene_voice["edge"]).save(mp3)
            asyncio.run(go())
            subprocess.run([FFMPEG, "-y", "-i", mp3, "-ar", "44100",
                            "-ac", "2", out_wav], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        else:  # offline (pyttsx3 / SAPI Huihui)
            import pyttsx3
            e = pyttsx3.init()
            for v in e.getProperty("voices"):
                if "Huihui" in v.name or "Chinese" in v.name:
                    e.setProperty("voice", v.id)
                    break
            e.setProperty("rate", scene_voice.get("offline_rate", 160))
            raw = out_wav[:-4] + "_raw.wav"
            e.save_to_file(text, raw)
            e.runAndWait()
            # 统一成 44100/立体声
            subprocess.run([FFMPEG, "-y", "-i", raw, "-ar", "44100",
                            "-ac", "2", out_wav], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return os.path.getsize(out_wav) > 0
    except Exception as ex:
        print(f"  [配音失败,转无声] {type(ex).__name__}: {ex}")
        return False


def wav_dur(path):
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def pad_audio(in_wav, dur, out_wav):
    subprocess.run([FFMPEG, "-y", "-i", in_wav, "-af", "apad",
                    "-t", f"{dur:.3f}", "-ar", "44100", "-ac", "2", out_wav],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def silence(dur, out_wav):
    subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i",
                    "anullsrc=r=44100:cl=stereo", "-t", f"{dur:.3f}", out_wav],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ----------------------------------------------------------------- 画面
def cover(img, ow, oh):
    s = max(ow / img.width, oh / img.height)
    img = img.resize((int(img.width * s) + 1, int(img.height * s) + 1))
    l = (img.width - ow) // 2
    t = (img.height - oh) // 2
    return img.crop((l, t, l + ow, t + oh))


def ken_burns(oimg, motion, p, size):
    """从超采样大图里按运镜取一帧 (size)。p∈[0,1]。"""
    W, H = size
    OW, OH = oimg.size
    p = ease(p)
    if motion == "zoom_in":
        z = 1.0 + 0.18 * p
    elif motion == "zoom_out":
        z = 1.18 - 0.18 * p
    else:
        z = 1.08
    winw, winh = OW / z, OH / z
    if motion == "pan_right":
        x0 = (OW - winw) * p
    elif motion == "pan_left":
        x0 = (OW - winw) * (1 - p)
    else:
        x0 = (OW - winw) / 2
    y0 = (OH - winh) / 2
    crop = oimg.crop((int(x0), int(y0), int(x0 + winw), int(y0 + winh)))
    return crop.resize(size)


def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


def dialogue_layer(size, speaker, lines, name_f, text_f, accent):
    """底部对话框图层 (RGBA)。"""
    W, H = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pad, side = 44, 56
    name_h = d.textbbox((0, 0), "中", font=name_f)[3]
    line_h = d.textbbox((0, 0), "中", font=text_f)[3]
    lgap = 16
    content_h = name_h + 18 + len(lines) * (line_h + lgap)
    box_h = content_h + 2 * pad
    y1 = H - 130
    y0 = y1 - box_h
    rounded(d, (side, y0, W - side, y1), 28, (10, 10, 16, 205))
    # 说话人
    y = y0 + pad
    d.text((side + pad, y), speaker, font=name_f, fill=accent + (255,))
    y += name_h + 18
    # 台词
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=text_f)
        x = (W - (bb[2] - bb[0])) // 2
        d.text((x + 2, y + 2), ln, font=text_f, fill=(0, 0, 0, 170))
        d.text((x, y), ln, font=text_f, fill=(245, 245, 245, 255))
        y += line_h + lgap
    return layer


# ----------------------------------------------------------------- 视频片段
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}


def clip_loop_frames(path, size):
    """无限循环地产出 clip 的每一帧（已 cover 到 size 的 PIL RGB）。
    clip 比镜头短就循环播放，比镜头长就只用到所需帧数。"""
    while True:
        rd = imageio.get_reader(path)
        empty = True
        for fr in rd:
            empty = False
            yield cover(Image.fromarray(fr).convert("RGB"), size[0], size[1])
        rd.close()
        if empty:                       # 读不到帧，兜底一张纯色，避免死循环
            yield Image.new("RGB", size, (20, 20, 28))


def compose_subtitle(bg_rgba, dlg, fi, fade_f):
    """把字幕图层（带淡入）叠到背景上，返回可写入的 RGB ndarray。"""
    a = min(fi / fade_f, 1.0) if fade_f else 1.0
    layer = dlg
    if a < 1:
        al = dlg.split()[3].point(lambda v: int(v * a))
        layer = dlg.copy()
        layer.putalpha(al)
    return np.asarray(Image.alpha_composite(bg_rgba, layer).convert("RGB"))


def title_layer(size, main, sub, main_f, sub_f, measure):
    """片头/片尾标题卡图层：主标题(大) + 副标题(小)，居中。"""
    W, H = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    main_lines = wrap(main, main_f, int(W * 0.86), measure)
    sub_lines = wrap(sub, sub_f, int(W * 0.78), measure) if sub else []
    mh = d.textbbox((0, 0), "中", font=main_f)[3]
    sh = d.textbbox((0, 0), "中", font=sub_f)[3]
    gap_ms = 40
    total = (len(main_lines) * (mh + 20)
             + (gap_ms + len(sub_lines) * (sh + 14) if sub_lines else 0))
    y = (H - total) // 2 - 40
    for ln in main_lines:
        bb = d.textbbox((0, 0), ln, font=main_f)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        d.text((x + 3, y + 3), ln, font=main_f, fill=(0, 0, 0, 180))
        d.text((x, y), ln, font=main_f, fill=(245, 243, 235, 255))
        y += mh + 20
    if sub_lines:
        # 分隔线
        ly = y + gap_ms // 2
        d.line([(W // 2 - 60, ly), (W // 2 + 60, ly)],
               fill=(220, 200, 150, 200), width=2)
        y += gap_ms
        for ln in sub_lines:
            bb = d.textbbox((0, 0), ln, font=sub_f)
            x = (W - (bb[2] - bb[0])) // 2 - bb[0]
            d.text((x + 2, y + 2), ln, font=sub_f, fill=(0, 0, 0, 150))
            d.text((x, y), ln, font=sub_f, fill=(225, 215, 190, 255))
            y += sh + 14
    return layer


# ----------------------------------------------------------------- 主流程
def build(cfg, out_path, engine_override):
    W, H = cfg.get("size", [1080, 1920])
    fps = cfg.get("fps", 30)
    engine = engine_override or cfg.get("engine", "offline")
    tail_pad = cfg.get("tail_pad", 0.6)
    voices = cfg.get("voices", {})
    size = (W, H)
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    name_f = font("msyhbd.ttc", 46)
    text_f = font("msyhbd.ttc", 60)
    title_main_f = font("msyhbd.ttc", 92)
    title_sub_f = font("msyh.ttc", 44)
    measure = ImageDraw.Draw(Image.new("RGB", size))
    max_text_w = W - 2 * (56 + 44)

    print(f"配音引擎: {engine} | 共 {len(cfg['scenes'])} 个镜头")

    writer = imageio.get_writer(
        out_path, fps=fps, codec="libx264", quality=8,
        macro_block_size=None, ffmpeg_log_level="error",
        output_params=["-pix_fmt", "yuv420p"])

    audio_parts = []
    OW, OH = int(W * 1.18), int(H * 1.18)

    for idx, sc in enumerate(cfg["scenes"], 1):
        is_card = sc.get("type") == "title"
        sv = voices.get(sc.get("speaker", ""), {})
        accent = tuple(sv.get("color", [255, 255, 255]))

        # 1) 配音 / 时长
        if is_card:
            ok = False
            scene_dur = float(sc.get("dur", 3.2))
        else:
            wav = os.path.join(TMP, f"v{idx:02d}.wav")
            ok = synth(sc["text"].replace("\n", "，"), sv, engine, wav)
            adur = wav_dur(wav) if ok else 0.0
            scene_dur = max(adur + tail_pad, 2.2)

        # 2) 音轨(标题卡与无配音镜头补静音)
        part = os.path.join(TMP, f"a{idx:02d}.wav")
        if ok:
            pad_audio(wav, scene_dur, part)
        else:
            silence(scene_dur, part)
        audio_parts.append(part)

        n = max(int(scene_dur * fps), 1)
        fade_f = int(0.4 * fps)

        # 3a) 片头/片尾标题卡
        if is_card:
            img = sc.get("image", "")
            ip = os.path.join(ASSET_DIR, img) if img else ""
            if os.path.isfile(ip):
                oimg = cover(Image.open(ip).convert("RGB"), OW, OH)
            else:
                oimg = Image.new("RGB", (OW, OH), (14, 14, 20))
            tlayer = title_layer(size, sc.get("main", ""), sc.get("sub", ""),
                                 title_main_f, title_sub_f, measure)
            fin, fout = int(0.6 * fps), int(0.5 * fps)
            for fi in range(n):
                p = fi / max(n - 1, 1)
                frame = ken_burns(oimg, "zoom_in", p, size).convert("RGBA")
                if fi < fin:
                    a = fi / fin
                elif fi > n - fout:
                    a = max((n - fi) / fout, 0.0)
                else:
                    a = 1.0
                lay = tlayer
                if a < 1:
                    al = tlayer.split()[3].point(lambda v: int(v * a))
                    lay = tlayer.copy()
                    lay.putalpha(al)
                writer.append_data(
                    np.asarray(Image.alpha_composite(frame, lay).convert("RGB")))
            print(f"  镜头 {idx:02d}/{len(cfg['scenes'])}  时长 {scene_dur:4.1f}s  "
                  f"无声  [标题卡]  '{sc.get('main', '')[:12]}'")
            continue

        # 3b) 普通镜头：背景(clip优先/image回退) + 字幕
        clip = sc.get("clip", "")
        image = sc.get("image", "")
        clip_path = os.path.join(ASSET_DIR, clip) if clip else ""
        img_path = os.path.join(ASSET_DIR, image) if image else ""
        use_video = (os.path.splitext(clip)[1].lower() in VIDEO_EXTS
                     and os.path.isfile(clip_path))
        lines = wrap(sc["text"], text_f, max_text_w, measure)
        dlg = dialogue_layer(size, sc["speaker"], lines, name_f, text_f, accent)

        if use_video:
            gen = clip_loop_frames(clip_path, size)
            for fi in range(n):
                frame = next(gen).convert("RGBA")
                writer.append_data(compose_subtitle(frame, dlg, fi, fade_f))
            kind = "视频"
        else:
            if os.path.isfile(img_path):
                oimg = cover(Image.open(img_path).convert("RGB"), OW, OH)
            else:
                oimg = Image.new("RGB", (OW, OH), (20, 20, 28))
            for fi in range(n):
                p = fi / max(n - 1, 1)
                frame = ken_burns(oimg, sc.get("motion", "zoom_in"),
                                  p, size).convert("RGBA")
                writer.append_data(compose_subtitle(frame, dlg, fi, fade_f))
            kind = "占位待clip" if clip else "静图"
        print(f"  镜头 {idx:02d}/{len(cfg['scenes'])}  时长 {scene_dur:4.1f}s  "
              f"{'配音' if ok else '无声'}  [{kind}]  '{sc['text'][:12]}...'")

    writer.close()
    silent_video = out_path[:-4] + "_silent.mp4"
    os.replace(out_path, silent_video)

    # 4) 合并所有配音轨
    full_audio = os.path.join(TMP, "full.wav")
    listf = os.path.join(TMP, "list.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for p in audio_parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listf,
                    "-c", "copy", full_audio], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5) 混入 BGM(可选) 并封装
    bgm = cfg.get("bgm", "")
    if bgm and os.path.isfile(bgm):
        subprocess.run([FFMPEG, "-y", "-i", silent_video, "-i", full_audio,
                        "-stream_loop", "-1", "-i", bgm, "-filter_complex",
                        "[2:a]volume=0.22[bg];[1:a][bg]amix=inputs=2:duration=first[a]",
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", out_path],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run([FFMPEG, "-y", "-i", silent_video, "-i", full_audio,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", out_path],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(silent_video)
    print(f"[OK] 漫剧已生成: {out_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--script", default="漫剧脚本.json")
    p.add_argument("--out", default="output/manju.mp4")
    p.add_argument("--engine", default="", help="覆盖脚本引擎: offline/edge/none")
    a = p.parse_args()
    with open(a.script, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    build(cfg, a.out, a.engine or "")


if __name__ == "__main__":
    main()
