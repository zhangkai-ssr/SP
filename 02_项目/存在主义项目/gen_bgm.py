# -*- coding: utf-8 -*-
"""
合成一段无版权氛围 BGM（小调和声铺底，柔和），供漫剧循环使用。
纯正弦/三角波合成，可商用、无版权问题。输出 bgm/ambient.wav
"""
import os
import math
import numpy as np

SR = 44100
os.makedirs("bgm", exist_ok=True)

# 音名 -> 频率
def f(n):
    names = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    name, octv = n[0], int(n[1])
    semis = names[name] + (octv - 4) * 12
    return 440.0 * (2 ** (semis / 12.0))

# 进行：Am - F - C - G（忧郁但有归向感），每和弦 8 秒
progression = [
    ["A2", "A3", "C4", "E4"],
    ["F2", "F3", "A3", "C4"],
    ["C3", "C4", "E4", "G4"],
    ["G2", "G3", "B3", "D4"],
]
CHORD = 8.0
total = CHORD * len(progression)
t = np.linspace(0, total, int(SR * total), endpoint=False)

def soft_voice(freq, t, detune=0.0):
    """一个柔和的声部：基波 + 轻微泛音 + 慢速颤音。"""
    w = 2 * math.pi * freq * (1 + detune)
    sig = (np.sin(w * t)
           + 0.25 * np.sin(2 * w * t)
           + 0.12 * np.sin(3 * w * t))
    trem = 0.85 + 0.15 * np.sin(2 * math.pi * 0.12 * t)  # 慢颤音
    return sig * trem

# 逐和弦合成，和弦间做交叉淡化
left = np.zeros_like(t)
right = np.zeros_like(t)
xf = int(SR * 1.2)  # 交叉淡化样本数
for i, chord in enumerate(progression):
    seg = np.zeros_like(t)
    segR = np.zeros_like(t)
    s0 = int(i * CHORD * SR)
    s1 = int((i + 1) * CHORD * SR)
    tt = t[s0:s1] - t[s0]
    chord_sig = np.zeros_like(tt)
    chord_sigR = np.zeros_like(tt)
    for j, note in enumerate(chord):
        amp = 0.9 if j == 0 else 0.6   # 根音稍强
        chord_sig += amp * soft_voice(f(note), tt, detune=+0.0008)
        chord_sigR += amp * soft_voice(f(note), tt, detune=-0.0008)
    # 和弦内的轻微起伏包络
    env = 0.7 + 0.3 * np.sin(math.pi * tt / CHORD)
    left[s0:s1] += chord_sig * env
    right[s0:s1] += chord_sigR * env

# 简单低通（滑动平均），让声音更暖、去毛刺
def lowpass(x, k=24):
    c = np.cumsum(np.insert(x, 0, 0))
    return (c[k:] - c[:-k]) / k

left = lowpass(left)
right = lowpass(right)
m = max(np.max(np.abs(left)), np.max(np.abs(right)))
left, right = left / m * 0.5, right / m * 0.5  # 适度音量

stereo = np.stack([left, right], axis=1)
pcm = (stereo * 32767).astype(np.int16)

import wave
with wave.open("bgm/ambient.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"[OK] BGM 已生成: bgm/ambient.wav  ({total:.0f}s, 可循环)")
