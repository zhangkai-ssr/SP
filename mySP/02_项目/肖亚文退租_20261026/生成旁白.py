import asyncio,json,re,subprocess,wave,hashlib
from pathlib import Path
import edge_tts
p=Path(__file__).resolve().parent
for folder in (p/'work',p/'audio',p/'output'):folder.mkdir(parents=True,exist_ok=True)
data=json.loads((p/'旁白稿.json').read_text(encoding='utf-8'))
async def make_one(index,text):
 f=p/'work'/f'voice-{index:02}.mp3'; meta=f.with_suffix('.json')
 boundaries=[]
 com=edge_tts.Communicate(text,'zh-CN-YunxiNeural',rate='-5%',boundary='WordBoundary')
 with f.open('wb') as stream:
  async for item in com.stream():
   if item['type']=='audio':stream.write(item['data'])
   elif item['type']=='WordBoundary':boundaries.append({k:item[k] for k in ('offset','duration','text')})
 assert f.stat().st_size>1000 and boundaries
 meta.write_text(json.dumps(boundaries,ensure_ascii=False),encoding='utf-8')
 print('VOICE',index,'OK',flush=True)
 return boundaries
async def main():
 for i,t in enumerate(data['paragraphs'],1): await asyncio.wait_for(make_one(i,t),60)
asyncio.run(main())
rate=48000;gap=.35;cursor=0.;records=[];cues=[]
raw=p/'work/narration-raw.wav'
with wave.open(str(raw),'wb') as whole:
 whole.setnchannels(1);whole.setsampwidth(2);whole.setframerate(rate)
 for i,t in enumerate(data['paragraphs'],1):
  mp3=p/'work'/f'voice-{i:02}.mp3'
  pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(mp3),'-ar',str(rate),'-ac','1','-f','s16le','-'])
  duration=len(pcm)/2/rate
  records.append({'id':i,'start':round(cursor,3),'end':round(cursor+duration,3),'text':t})
  events=json.loads(mp3.with_suffix('.json').read_text(encoding='utf-8'))
  current='';begin=None;end=None
  for e in events:
   start=cursor+e['offset']/1e7; stop=min(cursor+duration,cursor+(e['offset']+e['duration'])/1e7)
   if current and (len(current+e['text'])>18 or start-end>.45):
    cues.append({'start':begin,'end':end,'text':current});current='';begin=None
   if begin is None: begin=start
   current+=e['text'];end=stop
  if current:cues.append({'start':begin,'end':end,'text':current})
  whole.writeframes(pcm);whole.writeframes(b'\0'*int(rate*gap)*2)
  cursor+=duration+gap
assert 180<cursor<330,cursor
for i,c in enumerate(cues):
 assert c['start']<c['end']<=cursor
 if i: assert c['start']>=cues[i-1]['end']-.05
norm=lambda s:re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',s)
assert norm(''.join(c['text'] for c in cues))==norm(''.join(data['paragraphs']))
final=p/'audio/旁白_初稿.mp3'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000','-ac','2','-b:a','192k',str(final)],check=True)
def stamp(t):
 ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
 return f'{h:02}:{m:02}:{s:02},{ms:03}'
srt='\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(cues,1))+'\n'
(p/'output/字幕_初稿.srt').write_text(srt,encoding='utf-8')
(p/'旁白时间线.json').write_text(json.dumps({'duration':cursor,'paragraphs':records,'cues':cues,'voice':'zh-CN-YunxiNeural','rate':'-5%','engine':'edge-tts 7.3.1'},ensure_ascii=False,indent=2),encoding='utf-8')
print('VOICE_DURATION',round(cursor,3),'CUES',len(cues),'SHA256',hashlib.sha256(final.read_bytes()).hexdigest(),flush=True)
