"""本片专用：像素图层动画、语音字幕与原创轻配乐合成。"""
import argparse
import bisect
import json
import math
import re
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).parent
W, H, FPS = 1280, 720, 24
GOLD, TEAL, WHITE = '#f5c979', '#62cec2', '#f1efe6'
BG, SPRITES = None, []
CHAPTERS = ['时间的价格', '找到专长', '让作品复制', '把时间拿回来']


def validate_audio(story, timings):
    if len(story['scenes']) != len(timings):
        raise ValueError('镜头数与旁白数不一致，请运行 prepare_audio.py')
    for scene, audio in zip(story['scenes'], timings):
        expected = (scene['narration'], story['voice'], story['rate'])
        actual = (audio.get('narration'), audio.get('voice'), audio.get('rate'))
        if actual != expected:
            raise ValueError('分镜文案或声音设置已变化，请运行 prepare_audio.py')


def make_timeline(durations):
    if not durations or any(not math.isfinite(d) or d <= 0 for d in durations):
        raise ValueError('语音时长必须为正数')
    result, cursor = [], 0.0
    for duration in durations:
        end = cursor + duration + 0.35
        result.append({'start': cursor, 'end': end, 'speech_end': cursor + duration})
        cursor = end
    return result


@lru_cache(maxsize=32)
def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc', size)


def load_assets():
    global BG, SPRITES
    BG = Image.open(ROOT / 'assets/workshop.png').convert('RGB').resize((640, 360), Image.Resampling.NEAREST)
    sheet = Image.open(ROOT / 'assets/character_sheet.png').convert('RGBA')
    assert sheet.getchannel('A').getextrema()[0] == 0, '角色表需要透明背景'
    SPRITES = []
    for index in range(8):
        x, y = (index % 4) * sheet.width // 4, (index // 4) * sheet.height // 2
        cell = sheet.crop((x, y, x + sheet.width // 4, y + sheet.height // 2))
        bounds = cell.getchannel('A').point(lambda v: 255 if v > 90 else 0).getbbox()
        assert bounds, f'角色帧为空: {index}'
        cell = cell.crop(bounds)
        height = 115 if index != 7 else 80
        SPRITES.append(cell.resize((round(cell.width * height / cell.height), height), Image.Resampling.NEAREST))


def person(im, x, foot, pose=0, t=0, scale=1):
    sprite = SPRITES[pose]
    if scale != 1:
        sprite = sprite.resize((round(sprite.width * scale), round(sprite.height * scale)), Image.Resampling.NEAREST)
    y = int(foot - sprite.height + math.sin(t * 2.2) * 1.5)
    d = ImageDraw.Draw(im)
    d.ellipse((x - sprite.width * 0.38, foot - 2, x + sprite.width * 0.38, foot + 5), fill='#0a1722')
    im.paste(sprite, (int(x - sprite.width / 2), y), sprite)


def gear(d, x, y, radius, phase, color=GOLD):
    points = []
    for i in range(48):
        angle = i * math.tau / 48 + phase
        r = radius * (1 if i % 4 in (0, 1) else 0.82)
        points.append((int(x + math.cos(angle) * r), int(y + math.sin(angle) * r)))
    d.polygon(points, fill=color)
    d.ellipse((x - radius * .55, y - radius * .55, x + radius * .55, y + radius * .55), fill='#17333c')
    d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)


def clock(d, x, y, radius, t):
    d.ellipse((x - radius - 4, y - radius - 4, x + radius + 4, y + radius + 4), fill='#80583b')
    d.ellipse((x - radius, y - radius, x + radius, y + radius), fill='#e6cf98', outline=GOLD, width=2)
    for i in range(12):
        a = i * math.tau / 12
        d.line((x + math.sin(a) * radius * .82, y - math.cos(a) * radius * .82,
                x + math.sin(a) * radius * .91, y - math.cos(a) * radius * .91), fill='#463b36', width=2)
    for angle, length, width in ((t * .9, .75, 2), (t * .075 + 1, .48, 4)):
        d.line((x, y, x + math.sin(angle) * radius * length, y - math.cos(angle) * radius * length), fill='#33424b', width=width)
    d.ellipse((x - 3, y - 3, x + 3, y + 3), fill='#ca714f')


def book(d, x, y, scale=1):
    w, h = 17 * scale, 23 * scale
    d.rectangle((x, y, x + w, y + h), fill='#235f68', outline='#cbaa6b', width=max(1, int(scale)))
    d.line((x + 3 * scale, y + 2 * scale, x + 3 * scale, y + h - 2 * scale), fill='#7ac9b3', width=max(1, int(scale)))
    d.line((x + 6 * scale, y + 8 * scale, x + 13 * scale, y + 8 * scale), fill=GOLD, width=max(1, int(scale)))


def city(im, t, harbor=False):
    d = ImageDraw.Draw(im)
    for y in range(360):
        d.line((0, y, 640, y), fill=(12 + y // 24, 22 + y // 20, 43 + y // 15))
    for i in range(38):
        x, y = (i * 173 + 67) % 640, 43 + (i * 71) % 128
        shade = int(130 + 65 * math.sin(t * .7 + i))
        d.rectangle((x, y, x + 1, y + 1), fill=(shade, shade, 155))
    d.ellipse((502, 67, 540, 105), fill='#f2dca6')
    d.ellipse((492, 59, 531, 98), fill='#101d32')
    for i in range(19):
        x = i * 37 - 15
        roof = 142 + ((i * 47) % 48)
        d.rectangle((x, roof, x + 31, 241), fill=('#203445' if i % 2 else '#1a2c40'))
        d.polygon([(x - 2, roof), (x + 15, roof - 11), (x + 33, roof)], fill='#2b3d4d')
        for wx in range(x + 6, x + 28, 10):
            for wy in range(roof + 8, 236, 15):
                d.rectangle((wx, wy, wx + 3, wy + 6), fill=('#bd985d' if (wx + wy + i) % 3 else '#355064'))
    if harbor:
        d.rectangle((0, 241, 640, 313), fill='#163d4c')
        for i in range(44):
            x = int((i * 73 + t * (4 + i % 3)) % 660) - 10
            y = 246 + (i * 11) % 60
            d.line((x, y, x + 6 + i % 18, y), fill=('#396471' if i % 3 else '#726a48'), width=1)
        d.rectangle((0, 298, 640, 360), fill='#16252e')
        d.rectangle((0, 295, 640, 299), fill='#5c6660')
        for x in range(0, 640, 36):
            d.rectangle((x, 300, x + 2, 360), fill='#263d44')
    else:
        d.rectangle((0, 241, 640, 360), fill='#13262f')
        for y in (260, 280, 300):
            d.line((0, y, 640, y), fill='#29404a')


def card(d, box, fill='#142c38'):
    d.rectangle(box, fill=fill, outline='#41636a', width=1)
    x0, y0, x1, y1 = box
    for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=GOLD)


def label(d, xy, text, size=24, color=WHITE, bold=False, anchor=None):
    d.text(xy, text, font=font(size, bold), fill=color, anchor=anchor, stroke_width=1, stroke_fill='#0c1c28')


def draw_frame(scene, local_t, global_t, subtitle):
    kind, chapter = scene['kind'], scene['chapter']
    if kind in ('workshop', 'queue', 'skill'):
        im = ImageEnhance.Brightness(BG).enhance(.65)
    else:
        im = Image.new('RGB', (640, 360), '#0f2634')
        city(im, global_t, harbor=kind == 'harbor')
    d = ImageDraw.Draw(im)
    t = local_t
    if kind == 'workshop':
        pose = (6, 3, 4, 5)[int(global_t / 8) % 4]
        person(im, 199, 296, pose, t, 1.22)
        card(d, (350, 108, 563, 257))
        book(d, 431, 141, 2.7)
        for i in range(11):
            x, y = 357 + (i * 29) % 200, 260 - ((t * 13 + i * 23) % 150)
            d.rectangle((x, y, x + 1, y + 1), fill='#8a8957')
    elif kind == 'clock':
        clock(d, 430, 188, 76, t + global_t * .13)
        person(im, 160, 290, 1 + int(t * 3) % 2, t, 1.1)
        d.line((200, 279, 540, 279), fill='#476269', width=3)
        for i in range(24):
            x = 217 + i * 13
            d.rectangle((x, 273, x + 8, 280), fill=GOLD if i < 24 - int(t) % 24 else '#284650')
    elif kind == 'queue':
        d.rectangle((36, 265, 601, 278), fill='#3a3b37', outline='#97754b', width=2)
        for i in range(10):
            x = int((i * 66 - t * 17) % 595) + 20
            d.rectangle((x, 239, x + 29, 262), fill='#c3af82', outline='#5b584d')
            d.line((x + 5, 245, x + 23, 245), fill='#788a7d', width=2)
        person(im, 315, 291, 6, t, 1.1)
        clock(d, 513, 160, 30, t * 2)
    elif kind == 'balance':
        card(d, (55, 112, 269, 278))
        card(d, (371, 112, 585, 278))
        clock(d, 162, 174, 42, t)
        book(d, 450, 138, 3)
        for x in range(288, 358, 18):
            d.polygon([(x, 185), (x + 10, 195), (x, 205)], fill=GOLD if (int(t * 3) + x // 18) % 3 else '#3e666d')
    elif kind == 'skill':
        person(im, 159, 293, 3 if int(t) % 5 < 3 else 5, t, 1.2)
        for x, y, r in ((387, 172, 40), (460, 155, 28), (483, 215, 34)):
            gear(d, x, y, r, t * (.3 if x == 387 else -.4))
        d.line((332, 253, 544, 253), fill=TEAL, width=2)
        for i in range(7):
            d.rectangle((343 + i * 28, 257, 358 + i * 28, 264), fill=GOLD if i <= int(t) % 8 else '#213a42')
    elif kind == 'blueprint':
        d.rectangle((0, 35, 640, 305), fill='#112d3c')
        for x in range(0, 640, 16):
            d.line((x, 35, x, 305), fill='#1b3a48')
        for y in range(35, 306, 16):
            d.line((0, y, 640, y), fill='#1b3a48')
        person(im, 128, 292, 4 if int(t) % 6 < 3 else 5, t, 1.13)
        for i, (x, y) in enumerate(((280, 135), (432, 135), (432, 234), (280, 234))):
            if i:
                previous = ((280, 135), (432, 135), (432, 234))[i - 1]
                d.line((previous[0] + 33, previous[1], x, y), fill='#7bbfb4', width=2)
            card(d, (x - 40, y - 25, x + 40, y + 25), '#244653' if t > i * .7 else '#172f3b')
            gear(d, x, y, 12, t * .4 + i, GOLD if t > i * .7 else '#49616b')
    elif kind == 'factory':
        d.rectangle((0, 36, 640, 307), fill='#122c36')
        for x in range(0, 640, 32):
            d.line((x, 36, x, 307), fill='#1d3740')
        d.rectangle((208, 244, 588, 259), fill='#34434b', outline='#89a0a1')
        for i in range(13):
            x = int(213 + (i * 32 + t * 27) % 371)
            d.line((x, 247, x - 8, 255), fill='#75837d', width=2)
        d.rectangle((232, 132, 335, 240), fill='#42626a', outline=GOLD, width=2)
        d.rectangle((244, 149, 322, 188), fill='#153b43')
        d.rectangle((250, 203, 319, 213), fill='#0a1b26')
        gear(d, 283, 169, 12, t)
        for i in range(5):
            x = 323 + ((t * 27 + i * 57) % 243)
            book(d, x, 220, .9)
        person(im, 135, 292, 5 if int(t) % 4 else 4, t, 1.05)
        for i in range(3):
            gear(d, 263 + i * 48, 282, 13, t * (.6 if i % 2 else -.6))
    elif kind == 'network':
        nodes = [(313, 186), (450, 121), (548, 202), (438, 273), (233, 275), (220, 122)]
        for index, (x, y) in enumerate(nodes[1:]):
            d.line((313, 186, x, y), fill='#3f7d83', width=2)
            u = (t * .22 + index / 5) % 1
            px, py = 313 + (x - 313) * u, 186 + (y - 186) * u
            d.rectangle((px - 3, py - 3, px + 3, py + 3), fill=GOLD)
        for i, (x, y) in enumerate(nodes):
            d.ellipse((x - 23, y - 23, x + 23, y + 23), fill='#1b404b', outline=TEAL, width=2)
            book(d, x - 8, y - 11)
        person(im, 111, 291, 5, t, .98)
    elif kind == 'garden':
        d.rectangle((0, 274, 640, 300), fill='#34483e')
        d.rectangle((174, 162, 184, 275), fill='#927451')
        for i in range(16):
            angle = i * 2.4
            x, y = 179 + math.cos(angle) * (29 + i % 4 * 7), 150 + math.sin(angle) * (28 + i % 3 * 9)
            d.rectangle((x - 16, y - 14, x + 16, y + 14), fill=('#37674f', '#4c8560', '#72a574')[i % 3])
            if i % 4 == 0:
                d.rectangle((x + 4, y + 3, x + 9, y + 8), fill=GOLD)
        person(im, 95, 292, 4, t, .9)
        card(d, (313, 115, 587, 271))
        points = [(337, 242), (367, 231), (397, 233), (427, 207), (457, 214), (487, 175), (517, 179), (551, 145)]
        visible = min(len(points), 2 + int(t * 1.1))
        d.line(points[:visible], fill=TEAL, width=3)
        for x, y in points[:visible]:
            d.rectangle((x - 3, y - 3, x + 3, y + 3), fill=GOLD)
    elif kind == 'harbor':
        person(im, 209 + math.sin(t * .15) * 8, 300, 0 if scene['headline'] == '你想留下什么？' else 1 + int(t * 2) % 2, t, 1.13)
        x = 395 + math.sin(t * .15) * 30
        d.polygon([(x, 261), (x + 46, 261), (x + 36, 272), (x + 12, 272)], fill='#9f7856')
        d.line((x + 24, 222, x + 24, 263), fill='#c6ad7d', width=2)
        d.polygon([(x + 21, 225), (x + 21, 257), (x + 2, 255)], fill='#d4c391')
    else:
        raise ValueError(f'未知镜头类型: {kind}')

    out = im.resize((W, H), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, W, 62), fill='#101f2d')
    label(draw, (34, 16), '时间之外', 22, GOLD, True)
    for i, text in enumerate(CHAPTERS):
        x = 292 + i * 228
        label(draw, (x, 20), f'0{i + 1}  {text}', 18, GOLD if i == chapter else '#68808b', i == chapter)
        if i == chapter:
            draw.rectangle((x, 56, x + 172, 59), fill=GOLD)
    # 顶部留给章节，底部留给字幕；核心图形位于两者之间。
    draw.rectangle((35, 83, 49, 129), fill=GOLD)
    label(draw, (68, 82), scene['headline'], 34, WHITE, True)
    label(draw, (70, 133), 'THE ALMANACK OF NAVAL RAVIKANT  /  原创寓言', 13, '#b3c6c3')
    if kind == 'workshop':
        label(draw, (914, 449), '纳瓦尔宝典', 21, GOLD, True, 'mm')
        label(draw, (914, 479), '读书 · 创作 · 选择', 15, '#a6bab6', anchor='mm')
    elif kind == 'clock':
        label(draw, (320, 256), '24H', 58, GOLD, True, 'mm')
        label(draw, (320, 306), '一天的时间预算', 21, '#b5c7c2', anchor='mm')
    elif kind == 'balance':
        label(draw, (324, 493), '每次重新投入', 24, GOLD, True, 'mm')
        label(draw, (956, 493), '留下可用的作品', 24, TEAL, True, 'mm')
    elif kind == 'skill':
        label(draw, (858, 571), '兴趣  ×  经验  ×  真实需求', 23, GOLD, True, 'mm')
    elif kind == 'blueprint':
        for text, xy in zip(('观察', '判断', '验证', '记录'), ((560, 332), (864, 332), (864, 530), (560, 530))):
            label(draw, xy, text, 19, GOLD, True, 'mm')
    elif kind == 'factory':
        label(draw, (920, 334), '一次创造', 31, GOLD, True, 'mm')
        label(draw, (920, 376), '多次使用', 24, '#9abebc', anchor='mm')
    elif kind == 'garden':
        label(draw, (904, 575), '技能 / 作品 / 信任的积累示意', 17, '#b2c4bb', anchor='mm')
    elif kind == 'harbor':
        label(draw, (860, 377), '把时间拿回来', 42, GOLD, True, 'mm')
        label(draw, (860, 436), '从一份真正有用的作品开始', 23, '#afc6bf', anchor='mm')

    draw.rectangle((0, 615, W, H), fill='#101f2d')
    if subtitle:
        lines = [subtitle[i:i + 26] for i in range(0, len(subtitle), 26)]
        assert len(lines) <= 2, '字幕超出安全区'
        for j, line in enumerate(lines):
            draw.text((W // 2, 651 + (j - (len(lines) - 1) / 2) * 37), line, font=font(29, True), fill=WHITE, anchor='mm', stroke_width=2, stroke_fill='#08131e')
    label(draw, (32, 693), '虚构故事 · 观点解读', 12, '#81989e')
    label(draw, (W - 32, 693), '普通话合成旁白  /  AI辅助美术', 12, '#81989e', anchor='ra')
    return out


def split_subtitle(text):
    parts = [x for x in re.split(r'(?<=[，。！？：；])', text) if x]
    result, line = [], ''
    for part in parts:
        if line and len(line + part) > 24:
            result.append(line)
            line = ''
        while len(part) > 24:
            result.append(part[:24])
            part = part[24:]
        line += part
    if line:
        result.append(line)
    return result


def subtitle_cues(story, timings, timeline):
    cues = []
    for scene, audio, timing in zip(story['scenes'], timings, timeline):
        boundaries = audio['boundaries']
        assert boundaries, '缺少语音时间信息，不生成猜测时间轴'
        for boundary_index, boundary in enumerate(boundaries):
            begin = timing['start'] + boundary['offset'] / 10_000_000
            end = min(timing['speech_end'], begin + boundary['duration'] / 10_000_000)
            if boundary_index + 1 < len(boundaries):
                end = min(end, timing['start'] + boundaries[boundary_index + 1]['offset'] / 10_000_000)
            pieces = split_subtitle(boundary['text'])
            total = sum(len(p) for p in pieces)
            cursor = begin
            for part in pieces:
                stop = min(end, cursor + (end - begin) * len(part) / total)
                if stop > cursor:
                    cues.append({'start': cursor, 'end': stop, 'text': part})
                cursor = stop
    assert all(c['end'] > c['start'] for c in cues)
    assert all(a['end'] <= b['start'] + .015 for a, b in zip(cues, cues[1:])), '字幕时间轴重叠'
    return cues


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    return f'{milliseconds // 3600000:02}:{milliseconds // 60000 % 60:02}:{milliseconds // 1000 % 60:02},{milliseconds % 1000:03}'


def make_audio(timings, timeline):
    sr = 48000
    length = math.ceil(timeline[-1]['end'] * sr)
    mix = np.zeros(length, dtype=np.float32)
    for audio, timing in zip(timings, timeline):
        with wave.open(str(ROOT / 'work' / audio['wav']), 'rb') as handle:
            assert handle.getframerate() == sr and handle.getnchannels() == 1
            samples = np.frombuffer(handle.readframes(handle.getnframes()), dtype='<i2').astype(np.float32) / 32768
        start = round(timing['start'] * sr)
        count = min(len(samples), length - start)
        mix[start:start + count] += samples[:count] * .85
    # 原创稀疏琶音，音量低于旁白；不使用第三方音乐文件。
    for beat, midi in enumerate(([57, 64, 69, 64, 53, 60, 65, 60, 60, 67, 72, 67, 55, 62, 67, 62] * 30)):
        start = round(beat * 1.6 * sr)
        if start >= length:
            break
        n = min(int(2.7 * sr), length - start)
        t = np.arange(n, dtype=np.float32) / sr
        frequency = 440 * 2 ** ((midi - 69) / 12)
        envelope = (1 - np.exp(-t * 8)) * np.exp(-t * 1.7)
        note = (np.sin(math.tau * frequency * t) + .18 * np.sin(math.tau * frequency * 2 * t)) * envelope * .009
        mix[start:start + n] += note
    fade = min(sr * 2, length)
    mix[-fade:] *= np.linspace(1, 0, fade)
    assert np.max(np.abs(mix)) < 1, '混音削波'
    path = ROOT / 'audio/mix.wav'
    with wave.open(str(path), 'wb') as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sr)
        handle.writeframes((mix * 32767).astype('<i2').tobytes())
    return path


def main():
    for directory in ('work', 'audio', 'output'):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true', help='只导出联系表和六秒动画预览')
    args = parser.parse_args()
    story = json.loads((ROOT / 'storyboard.json').read_text(encoding='utf-8-sig'))
    timings = json.loads((ROOT / 'work/audio_timing.json').read_text(encoding='utf-8'))
    validate_audio(story, timings)
    timeline = make_timeline([item['duration'] for item in timings])
    cues = subtitle_cues(story, timings, timeline)
    load_assets()
    (ROOT / 'work/timeline.json').write_text(json.dumps({'scenes': timeline, 'cues': cues}, ensure_ascii=False, indent=2), encoding='utf-8')
    srt = '\n\n'.join(f'{i + 1}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}' for i, c in enumerate(cues))
    (ROOT / 'output/把时间拿回来.srt').write_text(srt + '\n', encoding='utf-8-sig')
    indices = [0, 1, 2, 7, 10, 12, 15, 19, 24]
    contact = Image.new('RGB', (1280, 720), '#0d1b25')
    for position, index in enumerate(indices):
        preview = draw_frame(story['scenes'][index], 2.6, timeline[index]['start'] + 2.6, split_subtitle(story['scenes'][index]['narration'])[0])
        preview = preview.resize((420, 236), Image.Resampling.LANCZOS)
        contact.paste(preview, ((position % 3) * 428, (position // 3) * 241))
    contact.save(ROOT / 'output/分镜联系表.jpg', quality=95)
    draw_frame(story['scenes'][0], 1.2, 1.2, '让今天的努力，成为明天的起点').save(ROOT / 'output/封面.png')
    if args.preview:
        target = ROOT / 'work/animation_preview.mp4'
        command = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', str(target)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        try:
            for i in range(FPS * 6):
                scene_index = 1 if i < FPS * 3 else 12
                process.stdin.write(draw_frame(story['scenes'][scene_index], (i / FPS) % 3, i / FPS, '时间有限，创造可以被反复使用的作品').tobytes())
        finally:
            process.stdin.close()
        assert process.wait() == 0
        print('PREVIEW_OK', len(cues), 'subtitle cues', flush=True)
        return
    audio = make_audio(timings, timeline)
    total = timeline[-1]['end']
    target = ROOT / 'output/纳瓦尔宝典_把时间拿回来.mp4'
    command = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(audio), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-threads', '6', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-movflags', '+faststart', '-t', f'{total:.4f}', str(target)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    scene_ends = [s['end'] for s in timeline]
    cue_starts = [c['start'] for c in cues]
    frames = math.ceil(total * FPS)
    try:
        for frame_index in range(frames):
            time = frame_index / FPS
            index = min(len(timeline) - 1, bisect.bisect_right(scene_ends, time))
            cue_index = bisect.bisect_right(cue_starts, time) - 1
            subtitle = cues[cue_index]['text'] if cue_index >= 0 and time < cues[cue_index]['end'] else ''
            frame = draw_frame(story['scenes'][index], time - timeline[index]['start'], time, subtitle)
            progress = ImageDraw.Draw(frame)
            progress.rectangle((0, 716, int(W * time / total), 719), fill=GOLD)
            process.stdin.write(frame.tobytes())
            if frame_index % (FPS * 15) == 0:
                print(f'RENDER {time:.0f}/{total:.1f}s', flush=True)
    finally:
        process.stdin.close()
    assert process.wait() == 0, '视频编码失败'
    print('RENDER_OK', target, total, flush=True)


if __name__ == '__main__':
    main()
