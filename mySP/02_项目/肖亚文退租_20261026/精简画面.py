from pathlib import Path
import json, subprocess

p = Path(__file__).resolve().parent
source = p / 'output/肖亚文退租_原剧解说_内部试剪.mp4'
target = p / 'output/肖亚文退租_精简画面版.mp4'

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))

before = probe(source)
video = next(s for s in before['streams'] if s['codec_type'] == 'video')
assert (video['width'], video['height']) == (1080, 1920), '输入版式已改变，需重新核对裁切坐标'
# shortcut: 固定修补此版本的左上角标识区域，更换片源或版式时须重定坐标。
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-threads', '2', '-i', str(source),
    '-vf', 'delogo=x=10:y=468:w=260:h=62:show=0,crop=1080:1350:0:210',
    '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-threads', '4', '-c:a', 'copy', '-movflags', '+faststart', str(target)], check=True)
after = probe(target)
video = next(s for s in after['streams'] if s['codec_type'] == 'video')
assert (video['width'], video['height'], video['r_frame_rate']) == (1080, 1350, '30/1')
assert abs(float(after['format']['duration']) - float(before['format']['duration'])) < .1
print(target, flush=True)
