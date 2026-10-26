from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]
t=json.loads((p/'src/timing.json').read_text(encoding='utf-8'))
assert t['width']==1920 and t['height']==1080 and t['fps']==30 and t['duration']==45, 'Approved 45-second 1080p30 contract not implemented'
scenes=list(t['scenes'].values())
assert scenes[0][0]==0 and scenes[-1][1]==45
assert all(a<b for a,b in scenes)
assert all(a[1]==b[0] for a,b in zip(scenes,scenes[1:]))
assert t['voice']['lines']==[], 'This film must have no API-generated voiceover'
assert len(list((p/'public/cases').glob('*.jpg')))==8, 'Eight distinct public case frames required'
print('PASS: approved timeline, contiguous scenes, no voiceover, eight case frames')
