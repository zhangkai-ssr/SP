"""检查实际成片并从成片提取审阅帧，避免交付与预览不一致。"""
import json
import subprocess
import sys
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[1]
stem=sys.argv[1] if len(sys.argv)>1 else '思想解放运动_15秒三维样片'
movie=root/'out'/f'{stem}_交付.mp4'
full='--full' in sys.argv
extended='--body' in sys.argv or full
cfg=json.loads((root/'src'/('full-timing.json' if full else 'body-timing.json')).read_text(encoding='utf-8')) if extended else None
expected_frames=cfg['durationFrames'] if extended else 450
expected_duration=expected_frames/30
def run(args):
    return subprocess.run(args,check=True,capture_output=True,text=True,encoding='utf-8').stdout
meta=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
video=next(s for s in meta['streams'] if s['codec_type']=='video')
audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
assert (video['width'],video['height'])==(1920,1080)
assert video['r_frame_rate']=='30/1' and int(video['nb_frames'])==expected_frames
assert video['codec_name']=='h264' and video['pix_fmt']=='yuv420p'
assert abs(float(meta['format']['duration'])-expected_duration)<.05
assert audio['channels']==2
assert audio['sample_rate']=='48000'
decode=subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0 and not decode.stderr.strip(),decode.stderr
dest=root/'out'/f'{stem}_关键帧'; dest.mkdir(exist_ok=True)
times=[0,3,6.65,8.55,11.8,14.9]
if extended: times=[3,cfg['titleFrame']/30+.2,13,16,18.5,23,29.5,36,41.5]
if full: times=[3,cfg['titleFrame']/30+.5]+[(s+75)/30 for s in cfg['starts'][:-1]]+[(cfg['starts'][-1]+12)/30,expected_duration-1]
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
sheet=Image.new('RGB',(1440,314*((len(times)+2)//3)),'#101b28')
for i,t in enumerate(times):
    target=dest/f'{i+1:02d}_{t:05.2f}秒.jpg'
    run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1','-q:v','2',str(target)])
    im=Image.open(target).convert('RGB'); assert im.size==(1920,1080)
    im.thumbnail((480,270)); x=(i%3)*480; y=(i//3)*314
    sheet.paste(im,(x,y)); ImageDraw.Draw(sheet).text((x+12,y+278),f'{i+1:02d} / {t:.2f} s',font=font,fill='#e9dcc4')
sheet.save(root/'out'/f'{stem}_关键帧预览.jpg',quality=95)
analysis=subprocess.run(['ffmpeg','-hide_banner','-i',str(movie),'-vf','blackdetect=d=0.1:pix_th=0.03:pic_th=0.98','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,encoding='utf-8')
assert analysis.returncode==0
assert 'black_start:' not in analysis.stderr, 'Unexpected near-black interval'
summary=analysis.stderr.rsplit('Summary:',1)[-1]
integrated=float(re.search(r'I:\s+(-?[\d.]+) LUFS',summary).group(1))
peak=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS',summary).group(1))
assert peak<0, f'Audio clipping: {peak}'
if extended: assert -16<integrated< -12, integrated
(root/'out'/f'{stem}_成片检测.txt').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n'+analysis.stderr,encoding='utf-8')
print(json.dumps({'duration':meta['format']['duration'],'frames':video['nb_frames'],'size':[video['width'],video['height']],'video':video['codec_name'],'audio':audio['codec_name'],'bit_rate':video.get('bit_rate'),'decode':'PASS','near_black_intervals':0,'keyframes':len(times),'LUFS':integrated,'true_peak_dBFS':peak},ensure_ascii=False))
