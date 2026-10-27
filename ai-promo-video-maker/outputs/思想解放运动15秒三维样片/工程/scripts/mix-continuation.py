"""指定伴奏原速连续使用；只调响度与首尾淡入淡出。"""
import json
import sys
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
full='--full' in sys.argv
cfg=json.loads((root/'src'/('full-timing.json' if full else 'body-timing.json')).read_text(encoding='utf-8'))
duration=cfg['durationFrames']/cfg['fps']
source=root/'audio-src'/('reference-full-instrumental.wav' if full else 'reference-instrumental.wav')
dest=root/'public/audio'/('full.wav' if full else 'continuation.wav')
assert source.is_file() and (120<duration<130 if full else 40<duration<50)
fade=f'afade=t=in:st=0:d=0.06,afade=t=out:st={duration-.6}:d=0.6'
base=['ffmpeg','-hide_banner','-i',str(source),'-t',str(duration)]
target='I=-14:TP=-1.5:LRA=11'
r=subprocess.run(base+['-af',f'{fade},loudnorm={target}:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
s=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
norm=f"loudnorm={target}:measured_I={s['input_i']}:measured_TP={s['input_tp']}:measured_LRA={s['input_lra']}:measured_thresh={s['input_thresh']}:offset={s['target_offset']}:linear=true"
subprocess.run(base+['-v','error','-y','-af',f'{fade},{norm}','-ar','48000','-c:a','pcm_s16le',str(dest)],check=True)
print(f'{duration}s; original source at 0s, speed 1.0; target -14 LUFS / -1.5 dBTP')
