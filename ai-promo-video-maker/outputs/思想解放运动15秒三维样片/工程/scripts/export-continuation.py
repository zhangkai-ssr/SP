"""将本轮渲染与指定伴奏合成兼容播放器的交付文件。"""
from pathlib import Path
import json
import subprocess
import sys
root=Path(__file__).resolve().parents[1]
complete='--full' in sys.argv
stem='思想解放运动_完整版' if complete else '思想解放运动_四理论续作'
raw=root/'out'/f'{stem}_原始.mp4'
dest=root/'out'/f'{stem}_交付.mp4'
t=json.loads((root/'src'/('full-timing.json' if complete else 'body-timing.json')).read_text(encoding='utf-8'))
r=subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(raw)],check=True,capture_output=True,text=True,encoding='utf-8')
v=next(s for s in json.loads(r.stdout)['streams'] if s['codec_type']=='video')
assert int(v['nb_frames'])==t['durationFrames']
full=v.get('color_range')=='pc' or v['pix_fmt'].startswith('yuvj')
vf=f"scale=in_range={'pc' if full else 'tv'}:out_range=tv:out_color_matrix=bt709,format=yuv420p"
subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-i',str(root/'public/audio'/('full.wav' if complete else 'continuation.wav')),'-map','0:v:0','-map','1:a:0','-vf',vf,'-c:v','libx264','-preset','slow','-b:v','14M','-maxrate','18M','-bufsize','28M','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-af','volume=-1dB' if complete else 'anull','-c:a','aac','-b:a','192k','-ar','48000','-t',str(t['durationFrames']/30),'-movflags','+faststart',str(dest)],check=True)
print(dest)
