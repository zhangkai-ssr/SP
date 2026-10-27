"""从已分离的指定伴奏测节拍；整段音频不变速，画面落点吸附实际起音。"""
from pathlib import Path
import json
import numpy as np
import soundfile as sf
from scipy.signal import stft, find_peaks, resample_poly

root=Path(__file__).resolve().parents[1]
x,sr=sf.read(root/'audio-src/reference-instrumental.wav')
x=resample_poly(x.mean(axis=1),1,2); sr=sr//2
t,_,z=None,None,None
_,t,z=stft(x,fs=sr,nperseg=1024,noverlap=768,boundary=None)
flux=np.maximum(0,np.diff(np.log1p(np.abs(z)*100),axis=1)).sum(axis=0)
t=t[1:]; flux=flux/(np.convolve(flux,np.ones(171)/171,'same')+1e-6)
best=(-1,0,0)
for period in np.arange(.515,.55,.00015):
 for phase in np.arange(0,period,.006):
  grid=np.arange(phase,60,period); grid=grid[(grid>4)&(grid<55)]
  score=np.mean(np.interp(grid,t,flux))
  if score>best[0]: best=(score,period,phase)
score,beat,offset=best
peaks,_=find_peaks(flux,distance=int(.18/(t[1]-t[0])),prominence=.12)
def snap(target,radius=.16):
 p=peaks[np.abs(t[peaks]-target)<radius]
 return float(t[max(p,key=lambda p:flux[p]-.7*abs(t[p]-target)/radius)]) if len(p) else float(target)
# 每段 12 拍，前 8 拍演示，后 4 拍回总览再推近下一张。
starts=[round(snap(offset+(28+12*i)*beat)*30) for i in range(5)]
ends=[round(snap(offset+(36+12*i)*beat)*30) for i in range(4)]
title=round(snap(offset+16*beat)*30)
wall=round(snap(offset+20*beat)*30)
beats=[round(snap(offset+i*beat,.075)*30) for i in range(84)]
timing=dict(fps=30,introFrames=starts[0],starts=starts,demoEnds=ends,count=4,durationFrames=starts[-1]+64,titleFrame=title,wallFrame=wall,beat=round(float(beat),6),beatFrames=beats,musicStatus='user_reference_separated',timingStatus='measured_onset_aligned')
(root/'src/body-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(a<b for a,b in zip(starts,starts[1:]))
assert all(starts[i]<ends[i]<starts[i+1] for i in range(4))
assert timing['durationFrames']/30<len(x)/sr
print(json.dumps({'bpm':60/beat,'offset':offset,'score':score,'scene_seconds':[f/30 for f in starts],'title':title/30},indent=2))
