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


def book(d, x, y, scale=1):
    w, h = 17 * scale, 23 * scale
    d.rectangle((x, y, x + w, y + h), fill='#235f68', outline='#cbaa6b', width=max(1, int(scale)))
    d.line((x + 3 * scale, y + 2 * scale, x + 3 * scale, y + h - 2 * scale), fill='#7ac9b3', width=max(1, int(scale)))
    d.line((x + 6 * scale, y + 8 * scale, x + 13 * scale, y + 8 * scale), fill=GOLD, width=max(1, int(scale)))


def label(d, xy, text, size=24, color=WHITE, bold=False, anchor=None):
    d.text(xy, text, font=font(size, bold), fill=color, anchor=anchor, stroke_width=1, stroke_fill='#0c1c28')


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


@lru_cache(maxsize=4)
def backdrop(name):
    return Image.open(ROOT / 'assets' / (name+'.png')).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)


@lru_cache(maxsize=8)
def actor(pose):
    sheet=Image.open(ROOT/'assets/character_sheet.png').convert('RGBA')
    x,y=(pose%4)*sheet.width//4,(pose//4)*sheet.height//2
    cell=sheet.crop((x,y,x+sheet.width//4,y+sheet.height//2))
    cell=cell.crop(cell.getchannel('A').point(lambda v:255 if v>90 else 0).getbbox())
    height=410 if pose!=7 else 260
    return cell.resize((round(cell.width*height/cell.height),height),Image.Resampling.LANCZOS)


def place_actor(im,x,foot,pose,t,scale=1):
    a=actor(pose)
    if scale!=1: a=a.resize((round(a.width*scale),round(a.height*scale)),Image.Resampling.LANCZOS)
    im.paste(a,(round(x-a.width/2),round(foot-a.height+math.sin(t*1.8)*2)),a)


@lru_cache(maxsize=16)
def watch_art(r,silver):
    art=Image.open(ROOT/'assets/watch.png').convert('RGBA')
    if silver: art=ImageEnhance.Color(art).enhance(.12)
    scale=r/477
    return art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)


def watch(d,x,y,r,t,running=True,silver=False,open_case=False,surface=None,stopped_at=2):
    gold='#b9cbd0' if silver else '#efb84e'
    if surface is not None:
        art=watch_art(r,silver)
        surface.paste(art,(round(x-628*r/477),round(y-722*r/477)),art)
        r=r*.68
    else:
        d.ellipse((x-r-9,y-r-9,x+r+9,y+r+9),fill='#372918',outline=gold,width=7)
        d.ellipse((x-r,y-r,x+r,y+r),fill='#e8d6a5',outline='#88612c',width=5)
        d.ellipse((x-20,y-r-39,x+20,y-r-3),outline=gold,width=7)
    if open_case:
        d.ellipse((x-r,y-r,x+r,y+r),fill='#493423',outline=gold,width=4)
        for i,(dx,dy,rr) in enumerate([(-.38,-.24,.33),(.29,-.31,.29),(.0,.37,.38)]):
            gx,gy=x+r*dx,y+r*dy
            ang=t*(1 if i%2 else -1) if running else .2
            pts=[]
            for q in range(48):
                a=q*math.tau/48+ang; rad=r*rr*(1 if q%4<2 else .8)
                pts.append((gx+rad*math.cos(a),gy+rad*math.sin(a)))
            d.polygon(pts,fill='#aa762b',outline='#62401c')
            d.ellipse((gx-6,gy-6,gx+6,gy+6),fill='#ffe1a1')
        return
    for i in range(0 if surface is not None else 60):
        a=i*math.tau/60
        ra=r*.84; rb=r*(.71 if i%5==0 else .78)
        d.line((x+math.sin(a)*ra,y-math.cos(a)*ra,x+math.sin(a)*rb,y-math.cos(a)*rb),fill='#654b32',width=3 if i%5==0 else 1)
    for a,rr,width in [(1.8,r*.45,7),(.2,r*.65,5),((t if running else stopped_at)*1.6,r*.73,3)]:
        d.line((x,y,x+math.sin(a)*rr,y-math.cos(a)*rr),fill='#744521' if width>2 else '#c24532',width=width)
    d.ellipse((x-7,y-7,x+7,y+7),fill=gold)


def posture_watch(im,t,repaired):
    layer=Image.new('RGBA',(640,640))
    watch(ImageDraw.Draw(layer),320,370,174,t,repaired or t<3,surface=layer,stopped_at=3)
    # shortcut: 用纵向透视压缩表示平放与立起；需要真实机械视角时再采用三维模型。
    q=ease((t-1)/2)
    if repaired and t>5: q=1-ease((t-5)/2)
    height=round(640*(.48+.52*q))
    layer=layer.resize((640,height),Image.Resampling.LANCZOS)
    im.paste(layer,(320,510-round(544*height/640)),layer)


def note(d,x,y,t,mode='symptom'):
    d.rounded_rectangle((x-8,y-8,x+438,y+252),radius=6,fill='#4a2c1c')
    d.rectangle((x,y,x+430,y+244),fill='#e8d5a6',outline='#b99760',width=3)
    for yy in range(y+58,y+230,36): d.line((x+24,yy,x+406,yy),fill='#c6ad79',width=1)
    texts={'symptom':['维修记录 · 第 1 页','平放：能走','竖放：会停','换发条：无效'], 'answer':['补充 · 检查方法','先比较不同姿态','再定位异常位置','测试后，再合上表盖'], 'new':['维修记录 · 第 2 页','先问：什么时候停？','再试：换个方向呢？','旧方法，新问题'], 'life':['留下能再次使用的成果','错题：写清错误原因','代码：保留可运行实例','沟通：记下有效的提问']}[mode]
    for i,s in enumerate(texts):
        if i==0 or t>(i-1)*.75:
            d.text((x+25,y+18+i*53),s,font=font(23 if i else 25,True),fill='#493b2e')
    penx=x+340; peny=y+205
    d.line((penx,peny,penx+62,peny-77),fill='#234d54',width=9)
    d.polygon([(penx-5,peny),(penx+5,peny+5),(penx-6,peny+14)],fill='#54402a')


def draw_frame(scene,local_t,global_t,subtitle):
    k=scene['kind']; t=local_t
    outside=k in ('snow','finalsnow','tempt','choose','ending')
    wide=k in ('tired','question','bridge','practice','rest','resume','payoff')
    im=backdrop('street' if outside else 'workshop' if wide else 'bench').copy()
    # 镜头只对美术图层轻推近，字幕与记事本文字保持原尺寸。
    m=int(9*ease(min(t/8,1)))
    im=im.crop((m,m,W-m,H-m)).resize((W,H),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(im)
    if k in ('snow','finalsnow'):
        x=520+200*ease(t/9); r=42+35*ease(t/9)
        for j in range(10):
            xx=x-r-30-j*22
            d.ellipse((xx,606,xx+14,610),fill='#a2baca')
        place_actor(im,x-r-110,602,1+int(t*2)%2,t,.76)
        snowball(d,x,598-r,r,t)
    elif k in ('stop','repeat','test','repair','inspect','transfer'):
        if k=='transfer':
            watch(d,460,350,114,t,True,surface=im)
            watch(d,860,350,114,t,True,True,surface=im)
            label(d,(640,548),'外壳不同，先比较症状',32,GOLD,True,'mm')
        else:
            running= k=='repair' or (k=='stop' and t<2) or (k=='repeat' and t%4<2)
            if k in ('test','repair'): posture_watch(im,t,k=='repair')
            else: watch(d,640,347,168,t%4 if k=='repeat' else t,running,open_case=k=='inspect',surface=im)
            if k=='inspect':
                u=ease(t/3); x=int(830-120*u); y=int(250+36*u)
                d.ellipse((x-62,y-62,x+62,y+62),outline='#e4bb64',width=9)
                d.line((x+45,y+45,x+100,y+101),fill='#754322',width=17)
                d.arc((x-24,y-21,x+26,y+22),0,290,fill='#cc4938',width=6)
                label(d,(640,558),'之前跳过的检查',28,GOLD,True,'mm')
            if k in ('stop','repeat'):
                for i in range(3):
                    if t>i*.6:
                        xx=282+i*265
                        d.rectangle((xx,530,xx+185,573),fill='#e8d5a6',outline='#a57b3b',width=2)
                        d.text((xx+92,551),['修过一次','修过两次','修过三次'][i],font=font(22,True),fill='#493b2e',anchor='mm')
            if k in ('test','repair'):
                label(d,(640,554),('平放 → 竖放 → 停住' if k=='test' else '平放 ✓   竖放 ✓   继续走'),31,GOLD,True,'mm')
    elif k in ('notes','record','return','understand','life','reuse'):
        place_actor(im,295,615,4 if k!='understand' and t<5 else 5,t,.93)
        mode='answer' if k in ('record','understand','reuse') else 'new' if k=='return' else 'life' if k=='life' else 'symptom'
        note(d,585,285,t,mode)
        if k=='return': watch(d,1040,215,65,t,False,True,surface=im)
    elif k in ('tempt','choose'):
        place_actor(im,680,608,3 if k=='tempt' else 4,t,.82)
        d.rectangle((179,186,414,380),fill='#172f37',outline='#d4a447',width=5)
        for i in range(3):
            x=227+i*67
            d.line((x,254,x,342),fill='#d7aa5d',width=12)
            d.ellipse((x-15,230,x+15,260),outline='#fff0b5',width=6)
        label(d,(296,209),'新工具',25,GOLD,True,'mm')
        if k=='choose': label(d,(883,254),'它解决什么问题？',31,GOLD,True,'mm')
    elif k=='ending':
        shade=Image.new('RGB',(W,H),'#091c2b'); im=Image.blend(im,shade,.35); d=ImageDraw.Draw(im)
        place_actor(im,970,634,4,t,.95)
        label(d,(115,196),'《滚雪球》',39,GOLD,True)
        label(d,(108,265),'让积累',86,'#fff0ba',True)
        label(d,(108,360),'留下来',86,GOLD,True)
        label(d,(120,479),'做一次 · 看结果 · 留下来',27,WHITE,True)
    else:
        place_actor(im,470 if k!='tired' else 420,619,7 if k in ('rest','tired') else 3 if k=='question' else 4 if k in ('bridge','resume') else 6,t,1.02)
        if k=='question':
            note(d,710,330,0)
        elif k in ('bridge','resume','practice','payoff'):
            for i in range(1 if k=='bridge' else 4): book(d,774+i*46,439-i*5,2.2)
            watch(d,905,320,75,t,True,surface=im)
        elif k=='tired':
            for i in range(8):
                x=730+(i%4)*74;y=460+(i//4)*56
                d.ellipse((x-14,y-14,x+14,y+14),outline='#c69d50',width=5)
        if k=='rest':
            im=ImageEnhance.Brightness(im).enhance(.70-.18*ease(t/6)); d=ImageDraw.Draw(im)
            book(d,880,438,3)
    # 小标题代替大面积概念板；核心画面拥有完整的高度。
    top=Image.new('RGBA',(W,95),(8,20,28,0))
    td=ImageDraw.Draw(top)
    for yy in range(95): td.line((0,yy,W,yy),fill=(7,20,29,int(210*(1-yy/95))))
    im.paste(top,(0,0),top); d=ImageDraw.Draw(im)
    label(d,(32,19),'时间之外  /  《滚雪球》',20,GOLD,True)
    label(d,(W-32,22),scene['headline'],24,WHITE,True,'ra')
    overlay=Image.new('RGBA',(W,108),(5,15,23,230)); im.paste(overlay,(0,612),overlay); d=ImageDraw.Draw(im)
    if subtitle:
        lines=[subtitle[i:i+26] for i in range(0,len(subtitle),26)]
        assert len(lines)<=2
        for j,line in enumerate(lines):
            d.text((W//2,652+(j-(len(lines)-1)/2)*35),line,font=font(30,True),fill=WHITE,anchor='mm',stroke_width=2,stroke_fill='#08131e')
    label(d,(32,695),'原创虚构寓言 · 借用复利思路讨论学习',12,'#aebcc1')
    label(d,(W-32,695),'AI 辅助美术 / 合成旁白',12,'#aebcc1',anchor='ra')
    return im


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
    draw_frame(story['scenes'][0], 1.2, 1.2, '这块怀表，阿澈已经修好了三次。').save(ROOT / 'output/封面.png')
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
