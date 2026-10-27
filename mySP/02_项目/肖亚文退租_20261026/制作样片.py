from pathlib import Path
import json,math,subprocess,wave,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
W=P/'work'; OUT=P/'output'; SRC=P/'assets/source/退租候选.mp4'
V=json.loads((P/'旁白时间线.json').read_text(encoding='utf-8'))
for folder in (W,OUT,P/'audio/bgm'):folder.mkdir(parents=True,exist_ok=True)
SPECS=[
 ('意外的赔偿','退租，为什么反而拿到赔偿？',[186,198,223,236]),
 ('接手一家公司','先弄清：你现在代表谁',[25,42,66,122]),
 ('这辆车属于谁','使用方便，不等于权属清楚',[0,8,46,53]),
 ('接手之前的那本账','借来的资源，也需要交代',[74,81,92,113]),
 ('退租的转折','先沟通，再处理具体约定',[86,98,110,186]),
 ('钱的流向变了','重新连接三方的需要',[188,205,212,225]),
 ('肖亚文多问了一句','先弄清：这笔好处从哪来',[186,197,232,238]),
 ('三方各有需要','场地 · 费用 · 关系',[78,94,207,220]),
 ('她的动作很具体','身份 → 沟通 → 追问',[28,95,123,185]),
 ('换个人，还会这样吗','把故事里的条件看完整',[82,115,208,229]),
 ('第一件值得学的事','把资产、借用和情面分清',[9,44,76,118]),
 ('第二件值得学的事','接受方便之前，问清原因',[186,193,210,233]),
 ('第三件值得学的事','决定，要能向别人交代',[30,52,105,116]),
 ('再回到这场退租','机会背后，也有人情与责任',[92,186,200,237]),
 ('把问题留给自己','你正在使用谁的资源？',[36,121,186,237]),
]
assert len(SPECS)==len(V['paragraphs'])==15
assert 180<V['duration']<300
FONT='C:/Windows/Fonts/msyh.ttc'; BOLD='C:/Windows/Fonts/msyhbd.ttc'
def ft(n,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def centered(d,text,y,size,fill,bold=False):
 font=ft(size,bold); box=d.textbbox((0,0),text,font=font);x=(1080-(box[2]-box[0]))/2
 assert x>=54,(text,size,x)
 d.text((x,y),text,font=font,fill=fill)
def plate(i):
 title,insight,_=SPECS[i]
 yy=np.linspace(0,1,1920)[:,None,None];top=np.array([23,29,40])[None,None,:];bot=np.array([10,14,21])[None,None,:]
 arr=np.repeat((top*(1-yy)+bot*yy).astype('uint8'),1080,axis=1)
 im=Image.fromarray(arr);d=ImageDraw.Draw(im)
 d.rounded_rectangle((78,136,337,189),radius=8,fill='#2a303b')
 d.text((96,146),'天道 · 人物故事',font=ft(28),fill='#D8BD83')
 d.text((850,148),f'{i+1:02} / 15',font=ft(26),fill='#8A929E')
 centered(d,'肖亚文退租',228,76,'#F5F1E9',True)
 centered(d,title,336,39,'#B5BDC8')
 d.rectangle((0,449,1079,1064),fill='#080B10');d.line((0,449,1080,449),fill='#D1AE70',width=2)
 d.text((80,1110),'这一段，值得多想一步',font=ft(28),fill='#D1AE70')
 # 保留原剧画幅和来源标识，关键观点另置在画面外。
 if len(insight)>17:
  split=insight.find('，')+1 if '，' in insight else len(insight)//2
  centered(d,insight[:split],1192,51,'#F2EEE5',True);centered(d,insight[split:],1264,51,'#F2EEE5',True)
 else:centered(d,insight,1220,51,'#F2EEE5',True)
 d.line((96,1364,984,1364),fill='#343C49',width=1)
 d.text((80,1570),'画面含来源字幕 · 下方为原创解说字幕',font=ft(23),fill='#8A929E')
 d.rectangle((80,1655,1000,1658),fill='#343C49');d.rectangle((80,1655,80+round(920*(i+1)/15),1658),fill='#D1AE70')
 d.text((80,1700),'本地试剪 · 素材发布授权待核对',font=ft(25),fill='#A5ADB7')
 d.text((80,1748),'画面：《天道》｜片段：懂壹点人情世故',font=ft(23),fill='#8A929E')
 im.save(W/f'plate-{i:02}.png')
def ass_time(t):
 cs=round(max(0,t)*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100)
 return f'{h}:{m:02}:{s:02}.{cs:02}'
def subtitles(i,start,end):
 header='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Main,Microsoft YaHei,50,&H00F5F5F5,&H000000FF,&H00100B08,&H00000000,0,0,0,0,100,100,0,0,1,2,1,5,70,70,10,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
 lines=[]
 for c in V['cues']:
  if c['start']>=start-.02 and c['start']<end:
   text=c['text'].replace('{','').replace('}','')
   lines.append(f'Dialogue: 0,{ass_time(c["start"]-start)},{ass_time(min(c["end"],end)-start)},Main,,0,0,0,,{{\\an5\\pos(540,1468)}}{text}')
 (W/f'sub-{i:02}.ass').write_text(header+'\n'.join(lines)+'\n',encoding='utf-8-sig')

records=[]
for i,(rec,spec) in enumerate(zip(V['paragraphs'],SPECS)):
 start=rec['start'];end=V['paragraphs'][i+1]['start'] if i<14 else V['duration'];duration=end-start
 plate(i);subtitles(i,start,end)
 cuts=[{'source_start':t,'duration':duration/4} for t in spec[2]]
 # 避开来源中穿插的上传者解读镜头，只选已核对的剧情对白区间。
 assert all((0<=c['source_start'] and c['source_start']+c['duration']<=128) or (185<=c['source_start'] and c['source_start']+c['duration']<=248) for c in cuts)
 records.append({'id':i+1,'start':start,'end':end,'title':spec[0],'insight':spec[1],'source':'assets/source/退租候选.mp4','cuts':cuts})
manifest={'width':1080,'height':1920,'fps':30,'duration':V['duration'],'status':'internal_preview','source_audio_used':False,'scenes':records}
(P/'storyboard.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# 一个镜头片段放在完整画幅内；全部来源音轨关闭，避免叠入他人的解说。
for i,rec in enumerate(records):
 target=W/f'part-{i:02}.mp4';dur=rec['end']-rec['start']
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']
 for cut in rec['cuts']:cmd+=['-threads','2','-ss',str(cut['source_start']),'-t',str(cut['duration']),'-i',str(SRC)]
 cmd+=['-loop','1','-framerate','30','-i',str(W/f'plate-{i:02}.png')]
 filters=[f'[{n}:v]setpts=PTS-STARTPTS,fps=30,scale=1080:608,setsar=1[v{n}]' for n in range(4)]
 filters+=['[v0][v1][v2][v3]concat=n=4:v=1:a=0[story]','[4:v][story]overlay=0:452:shortest=1[framed]',f'[framed]ass=work/sub-{i:02}.ass[out]']
 cmd+=['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[out]','-an','-t',str(dur),'-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-r','30','-threads','4',str(target)]
 subprocess.run(cmd,cwd=P,check=True)
 print('RENDER',i+1,'/',15,flush=True)

# 本地合成轻量氛围音垫，无第三方曲库素材。
rate=48000;seconds=V['duration'];n=int(seconds*rate);bed=np.zeros(n,dtype=np.float32)
chords=[(110,130.8128,164.8138),(87.3071,110,130.8128),(130.8128,164.8138,195.9977),(97.9989,123.4708,146.8324)]
for start in range(0,math.ceil(seconds),12):
 count=min(rate*12,n-start*rate)
 if count<=0:break
 t=np.arange(count,dtype=np.float32)/rate;env=np.minimum(t/2,1)*np.minimum((count/rate-t)/2,1)
 segment=sum(np.sin(2*np.pi*freq*t)*np.exp(-t/8) for freq in chords[(start//12)%4])/3
 bed[start*rate:start*rate+count]+=segment*env*.022
bed*=np.minimum(np.arange(n)/rate/3,1)*np.minimum((n-np.arange(n))/rate/3,1)
with wave.open(str(P/'audio/bgm/氛围音垫.wav'),'wb') as f:
 f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes((bed*32767).astype('<i2').tobytes())
(W/'concat.txt').write_text(''.join(f"file 'part-{i:02}.mp4'\n" for i in range(15)),encoding='utf-8')
final=OUT/'肖亚文退租_原剧解说_内部试剪.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(W/'concat.txt'),'-i',str(P/'audio/旁白_初稿.mp3'),'-i',str(P/'audio/bgm/氛围音垫.wav'),'-filter_complex','[1:a][2:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9[a]','-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',str(seconds),'-movflags','+faststart',str(final)],check=True)
print('FINAL',final,'SHA256',hashlib.sha256(final.read_bytes()).hexdigest(),flush=True)
