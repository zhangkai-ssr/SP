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
CHAPTERS = ['看见积累', '选对方向', '带着经验走', '允许再出发']


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


def book(d, x, y, scale=1):
    w, h = 17 * scale, 23 * scale
    d.rectangle((x, y, x + w, y + h), fill='#235f68', outline='#cbaa6b', width=max(1, int(scale)))
    d.line((x + 3 * scale, y + 2 * scale, x + 3 * scale, y + h - 2 * scale), fill='#7ac9b3', width=max(1, int(scale)))
    d.line((x + 6 * scale, y + 8 * scale, x + 13 * scale, y + 8 * scale), fill=GOLD, width=max(1, int(scale)))


def card(d, box, fill='#142c38'):
    d.rectangle(box, fill=fill, outline='#41636a', width=1)
    x0, y0, x1, y1 = box
    for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=GOLD)


def label(d, xy, text, size=24, color=WHITE, bold=False, anchor=None):
    d.text(xy, text, font=font(size, bold), fill=color, anchor=anchor, stroke_width=1, stroke_fill='#0c1c28')


def model_value(rounds):
    return 100 * 1.1 ** rounds


def ease(x):
    x = max(0, min(1, x))
    return x * x * (3 - 2 * x)


def snowball(d, x, y, radius, t):
    r = int(radius)
    d.ellipse((x-r, y+r-3, x+r+12, y+r+8), fill='#7e9fac')
    points = []
    for i in range(32):
        a = i * math.tau / 32
        points.append((round(x + r * math.cos(a)), round(y + r * math.sin(a))))
    d.polygon(points, fill='#f2fcf5', outline='#afcdd6')
    for i in range(7):
        a = i * 2.4 + t * .65
        rr = r * (.28 + .07 * (i % 4))
        px, py = round(x + math.cos(a) * rr), round(y + math.sin(a) * rr)
        d.rectangle((px-2,py-2,px+2,py+2), fill='#bcd8dd')
    d.line((x-r*.55,y-r*.55,x-r*.25,y-r*.75), fill='#ffffff', width=3)


def winter(t):
    im = Image.new('RGB', (640,360), '#325f77')
    d = ImageDraw.Draw(im)
    for y in range(360):
        d.line((0,y,640,y), fill=(48+y//5,89+y//5,112+y//6))
    d.ellipse((490,45,550,105),fill='#ffe7ae')
    for shift,color,height in ((0,'#688d9e',95),(70,'#89abb5',142)):
        dx = math.sin(t*.09)*5
        d.polygon([(dx-80,270),(dx+70+shift,height),(dx+156+shift,225),(dx+270+shift,height+14),(dx+410+shift,258),(700,280)],fill=color)
        d.polygon([(dx+48+shift,height+30),(dx+70+shift,height),(dx+95+shift,height+42),(dx+72+shift,height+28)],fill='#e2edf0')
    d.polygon([(0,265),(110,247),(270,272),(400,251),(640,272),(640,360),(0,360)], fill='#d2e4e4')
    for i in range(14):
        x = (i*113+17+math.sin(t*.5+i)*5)%640
        y = (i*59+t*(4+i%3))%280
        d.rectangle((x,y,x+2,y+2),fill='#e4f4ed')
    return im


def arrow(d, a, b, t):
    d.line((*a,*b),fill=TEAL,width=3)
    u = (t*.27)%1
    x,y = a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u
    d.ellipse((x-4,y-4,x+4,y+4),fill=GOLD)
    d.polygon([(b[0],b[1]),(b[0]-10,b[1]-6),(b[0]-10,b[1]+6)],fill=TEAL)


def draw_frame(scene, local_t, global_t, subtitle):
    kind, chapter, step = scene['kind'],scene['chapter'],scene.get('step',0)
    t = local_t
    im = winter(global_t)
    d = ImageDraw.Draw(im)
    overlay_labels = []
    if kind in ('snow','reset','final'):
        x = 330 + 70*ease((t%8)/8)
        radius = (22 + min(25,step*1.2)) + 8*ease((t%8)/8)
        if kind == 'reset':
            radius = 18+15*ease((t%4)/4)
            x = 350+45*ease((t%4)/4)
            for i in range(4):
                book(d,400+i*29,240-i%2*9,1)
        person(im,x-radius-48,285,1+int(t*2.4)%2,t,1.05)
        snowball(d,x,278-radius,radius,t)
        for i in range(6):
            xx = x-radius-75-i*23
            d.rectangle((xx,287,xx+7,289),fill='#a4bdc3')
        if kind == 'final':
            d.line((430,120,430,270),fill='#977650',width=4)
            d.polygon([(434,123),(509,133),(434,157)],fill=GOLD)
            book(d,487,244,1.2)
        overlay_labels=[(1000,290,scene['labels'][0],28),(1000,334,scene['labels'][-1],23)]
    elif kind == 'compare':
        for x in (55,351):
            card(d,(x,105,x+234,278),'#254858')
        snowball(d,174,225,23+8*ease((t%4)/4),t)
        snowball(d,470,221,28+15*ease(min(t,8)/8),t)
        arrow(d,(301,190),(333,190),t)
        overlay_labels=[(344,260,'重复',35),(936,260,'积累',35),(344,553,scene['labels'][0],22),(936,553,scene['labels'][1],22)]
    elif kind == 'formula':
        card(d,(44,100,597,290),'#193744')
        for i,value in enumerate((100,110,121)):
            x = 103+i*172
            bar = (value/121)*87*ease(t/1.4)
            d.rectangle((x-25,253-bar,x+25,253),fill=GOLD if i==2 else '#76b6b5')
            overlay_labels.append((x*2,290,str(round(value*ease(t/1.4))),42))
            overlay_labels.append((x*2,540,('初始','第 1 轮','第 2 轮')[i],20))
            if i<2: arrow(d,(x+42,198),(x+113,198),t+i)
        overlay_labels += [(640,220,'假设每轮固定 +10% · 不是收益预测',24)]
    elif kind == 'notebook':
        person(im,105,292,4,t,1)
        card(d,(220,108,580,278),'#e7debd')
        d.line((398,117,398,269),fill='#b9aa85',width=2)
        for i in range(5):
            y = 141+i*24
            length=105*ease((t-i*.4)/1.2)
            d.line((241,y,241+length,y),fill='#536e70',width=2)
            if t>i*.4+.7:
                d.line((421,y,427,y+6,439,y-5),fill='#43857d',width=3)
                d.line((450,y,450+70*ease((t-i*.4-.7)),y),fill='#7d8d78',width=2)
        snowball(d,169,263,20,t)
        overlay_labels=[(620,224,scene['labels'][0],24),(981,224,scene['labels'][1],24)]
    elif kind == 'feedback':
        person(im,130,292,3 if int(t)%5<3 else 5,t,1.05)
        pts=[(284,147),(492,147),(388,260)]
        for i,(x,y) in enumerate(pts):
            xx,yy=pts[(i+1)%3]
            d.line((x,y,xx,yy),fill='#458b91',width=3)
            u=(t*.23+i/3)%1
            d.rectangle((x+(xx-x)*u-3,y+(yy-y)*u-3,x+(xx-x)*u+3,y+(yy-y)*u+3),fill=GOLD)
            card(d,(x-44,y-26,x+44,y+26),'#214655')
            overlay_labels.append((x*2,y*2,scene['labels'][i],25))
    elif kind == 'paths':
        d.polygon([(230,310),(294,250),(400,214),(553,190),(580,215),(427,242),(326,274),(291,310)],fill='#f5f0cd')
        d.polygon([(230,310),(290,220),(245,160),(265,145),(327,220),(291,310)],fill='#a6bec8')
        person(im,210,289,3,t,1.02)
        snowball(d,321+45*ease((t%7)/7),263-12*ease((t%7)/7),24,t)
        d.line((495,115,495,212),fill='#785c41',width=4)
        card(d,(448,120,566,149),'#284f5c')
        overlay_labels=[(1010,270,scene['labels'][1],19),(505,337,scene['labels'][0],20)]
    elif kind == 'bridge':
        d.polygon([(0,275),(205,270),(236,360),(0,360)],fill='#6a8b98')
        d.polygon([(424,268),(640,260),(640,360),(393,360)],fill='#6a8b98')
        d.rectangle((190,272,445,281),fill='#a18662')
        for x in range(194,445,16):
            d.line((x,273,x,280),fill='#d2c09b',width=2)
        d.line((195,240,440,240),fill='#b1a486',width=2)
        for x in (199,278,357,437): d.line((x,236,x,278),fill='#96775b',width=3)
        x=250+90*ease((t%8)/8)
        person(im,x-38,274,1+int(t*2)%2,t,.9)
        snowball(d,x+28,248,25,t)
        overlay_labels=[(640,224,scene['labels'][0],31),(640,272,scene['labels'][1],24)]
    elif kind == 'workshop':
        im=ImageEnhance.Brightness(BG).enhance(.94)
        d=ImageDraw.Draw(im)
        person(im,205,295,4 if int(t)%6<3 else 6,t,1.12)
        card(d,(350,108,565,277),'#254857')
        for i in range(3):
            yy=131+i*43
            book(d,373,yy,1.2)
            d.line((410,yy+9,410+115*ease((t-i*.5)/1.5),yy+9),fill=GOLD,width=3)
            d.line((410,yy+17,489,yy+17),fill='#79aaa9',width=2)
        overlay_labels=[(914,555,scene['labels'][0],21)]
    else:
        raise ValueError(f'未知镜头类型: {kind}')

    # 小幅平滑推近只作用于场景，文字仍在独立安全区内。
    margin=round(2+2*math.sin(global_t*.12))
    im=im.crop((margin,margin,640-margin,360-margin)).resize((640,360),Image.Resampling.NEAREST)
    out=im.resize((W,H),Image.Resampling.NEAREST)
    draw=ImageDraw.Draw(out)
    draw.rectangle((0,0,W,61),fill='#122936')
    label(draw,(32,16),'时间之外',22,GOLD,True)
    for i,text in enumerate(CHAPTERS):
        x=284+i*237
        label(draw,(x,20),f'0{i+1}  {text}',18,GOLD if i==chapter else '#94adb3',i==chapter)
        if i==chapter: draw.rectangle((x,55,x+176,59),fill=GOLD)
    draw.rectangle((0,62,W,167),fill='#254858')
    draw.rectangle((35,83,43,126),fill=GOLD)
    label(draw,(65,80),scene['headline'],35,WHITE,True)
    label(draw,(68,137),'THE SNOWBALL  /  生活里的积累 · 原创寓言',14,'#c1d5d4')
    for x,y,text,size in overlay_labels:
        label(draw,(x,y),text,size,WHITE,True,'mm')
    draw.rectangle((0,615,W,H),fill='#122936')
    if subtitle:
        lines=[subtitle[i:i+26] for i in range(0,len(subtitle),26)]
        assert len(lines)<=2,'字幕超出安全区'
        for j,line in enumerate(lines):
            draw.text((W//2,651+(j-(len(lines)-1)/2)*37),line,font=font(29,True),fill=WHITE,anchor='mm',stroke_width=2,stroke_fill='#08131e')
    label(draw,(32,693),'虚构故事 · 复利思路，不是人生增长公式',12,'#9cb4ba')
    label(draw,(W-32,693),'普通话合成旁白 / AI辅助角色美术',12,'#9cb4ba',anchor='ra')
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
    parser.add_argument('--preview', action='store_true', help='输出带旁白的开头15秒样片和六张关键帧')
    args = parser.parse_args()
    story = json.loads((ROOT / 'storyboard.json').read_text(encoding='utf-8-sig'))
    timings = json.loads((ROOT / 'work/audio_timing.json').read_text(encoding='utf-8'))
    validate_audio(story, timings)
    timeline = make_timeline([item['duration'] for item in timings])
    cues = subtitle_cues(story, timings, timeline)
    load_assets()
    (ROOT / 'work/timeline.json').write_text(json.dumps({'scenes': timeline, 'cues': cues}, ensure_ascii=False, indent=2), encoding='utf-8')
    srt = '\n\n'.join(f'{i + 1}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}' for i, c in enumerate(cues))
    (ROOT / 'output/让积累留下来.srt').write_text(srt + '\n', encoding='utf-8-sig')
    indices = [0, 1, 4, 6, 8, 11, 12, 15, 20]
    contact = Image.new('RGB', (1280, 720), '#0d1b25')
    for position, index in enumerate(indices):
        preview = draw_frame(story['scenes'][index], 2.6, timeline[index]['start'] + 2.6, split_subtitle(story['scenes'][index]['narration'])[0])
        preview = preview.resize((420, 236), Image.Resampling.LANCZOS)
        contact.paste(preview, ((position % 3) * 428, (position // 3) * 241))
    contact.save(ROOT / 'output/分镜联系表.jpg', quality=95)
    draw_frame(story['scenes'][0], 1.2, 1.2, '让今天的努力，成为明天的起点').save(ROOT / 'output/封面.png')
    audio = make_audio(timings, timeline)
    total = min(15, timeline[-1]['end']) if args.preview else timeline[-1]['end']
    target = ROOT / ('output/开头15秒样片.mp4' if args.preview else 'output/滚雪球_让积累留下来.mp4')
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
    if args.preview:
        for number, second in enumerate((0, 2.5, 5, 7.5, 10, 12.5)):
            index = min(len(timeline)-1, bisect.bisect_right(scene_ends, second))
            ci = bisect.bisect_right(cue_starts, second)-1
            subtitle = cues[ci]['text'] if ci >= 0 and second < cues[ci]['end'] else ''
            draw_frame(story['scenes'][index], second-timeline[index]['start'], second, subtitle).save(ROOT / f'output/样片关键帧_{number+1:02}.png')
    print('RENDER_OK', target, total, flush=True)


if __name__ == '__main__':
    main()
