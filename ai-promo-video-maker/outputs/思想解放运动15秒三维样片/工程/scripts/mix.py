"""原创 112 BPM 样片节奏带；无外部音乐素材，正式配乐待样片试听。"""
import os
import numpy as np
from audiolib import SR, SRC, Mix, timing, stereo, sub_boom, reverb

tm=timing(); beat=tm['beat']; drop=tm['drop']; mix=Mix(tm['duration'])
os.makedirs(SRC,exist_ok=True)
rng=np.random.default_rng(2026)
def pluck(freq,length=.65):
    t=np.arange(int(SR*length))/SR
    return stereo((np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*freq*2*t))*.13*np.exp(-t*6)*np.minimum(1,t*220))
chords=[[146.83,174.61,220,293.66],[116.54,146.83,174.61,233.08],[130.81,174.61,220,261.63],[130.81,164.81,196,261.63]]
for n in range(-29,28):
    at=drop+n*beat/2
    if at<0 or at>=15: continue
    c=chords[(n//8)%4]; freq=c[n%4]*(2 if n%3 else 1)
    mix.place(reverb(pluck(freq),seconds=1.0,wet=.2),at,gain=.65 if at<drop else 1,tag='music')
    if n%2==0:
        mix.place(sub_boom(.25,115,48,18),at,gain=.22 if at<drop else .4,tag='music')
    t=np.arange(int(SR*.07))/SR
    hat=stereo(rng.normal(size=len(t))*.035*np.exp(-t*75))
    mix.place(hat,at,gain=.5 if at<drop else 1,tag='music')
    if n%4==2:
        sn=stereo(rng.normal(size=len(t))*.12*np.exp(-t*32))
        mix.place(sn,at,gain=.35 if at<drop else .6,tag='music')
mix.place(sub_boom(1.6,78,30,3),drop,gain=.75)
for at in [drop+4*beat,drop+6*beat]: mix.place(reverb(pluck(880,.18),seconds=.7,wet=.4),at,gain=.6)
assert mix.duration==15 and np.isfinite(mix.buf).all()
mix.master(lufs=-14,true_peak=-1,end_fade=.3)
