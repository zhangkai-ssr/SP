"""本片音轨：曲库配乐＋轻量镜头提示音，不调用生成类 API。"""
from audiolib import Mix, load, flick, blip, timing

TM = timing()
mix = Mix(TM["duration"])
music = load("music.mp3")
mix.place(music, 0, gain=0.9, fade_in=0.12, fade_out=1.15, tag="music")
for name, (start, end) in TM["scenes"].items():
    if start > 0:
        mix.place(flick(length=0.07, gain=0.15), start-0.05, gain=0.35)
for at in (2.1, 2.4, 9.4, 25.1, 25.5, 25.9):
    mix.place(blip(freq=1100, length=0.05, gain=0.1), at, gain=0.18)
for at in range(29,36):
    mix.place(flick(length=0.04, gain=0.1), at-0.02, gain=0.2)
mix.master()
