"""保留已审阅前四段，在同一连续音乐上延长至十六段。"""
from pathlib import Path
import json
import numpy as np
import soundfile as sf
from scipy.signal import stft,find_peaks,resample_poly
root=Path(__file__).resolve().parents[1]
base=json.loads((root/'src/body-timing.json').read_text(encoding='utf-8'))
x,sr=sf.read(root/'audio-src/reference-full-instrumental.wav')
x=resample_poly(x.mean(axis=1),1,2);sr//=2
_,t,z=stft(x,fs=sr,nperseg=1024,noverlap=768,boundary=None)
flux=np.maximum(0,np.diff(np.log1p(np.abs(z)*100),axis=1)).sum(axis=0);t=t[1:]
flux/=np.convolve(flux,np.ones(171)/171,'same')+1e-6
peaks,_=find_peaks(flux,distance=int(.18/(t[1]-t[0])),prominence=.12)
def snap(target,radius=.16):
 p=peaks[np.abs(t[peaks]-target)<radius]
 return float(t[max(p,key=lambda j:flux[j]-.7*abs(t[j]-target)/radius)]) if len(p) else target
beat=base['beat'];offset=.066
starts=base['starts']+[round(snap(offset+(28+12*i)*beat)*30) for i in range(5,17)]
ends=base['demoEnds']+[round(snap(offset+(36+12*i)*beat)*30) for i in range(4,16)]
beats=base['beatFrames']+[round(snap(offset+i*beat,.075)*30) for i in range(len(base['beatFrames']),237)]
cfg={**base,'count':16,'starts':starts,'demoEnds':ends,'beatFrames':beats,'durationFrames':round((offset+232*beat)*30),'musicStatus':'user_reference_full_separated'}
assert len(starts)==17 and all(a<b for a,b in zip(starts,starts[1:]))
assert all(starts[i]+95<ends[i]<starts[i+1]-30 for i in range(16))
assert cfg['durationFrames']/30<130 and beats[-1]>cfg['durationFrames']
(root/'src/full-timing.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'duration':cfg['durationFrames']/30,'scene_seconds':[round(n/30,2) for n in starts]},ensure_ascii=False))
