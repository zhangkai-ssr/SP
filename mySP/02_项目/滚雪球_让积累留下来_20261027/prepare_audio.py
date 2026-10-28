"""为本片逐镜生成旁白，缓存已成功的分段。"""
import asyncio
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import edge_tts

ROOT = Path(__file__).parent


def cache_name(index, text, voice, rate):
    settings = json.dumps([text, voice, rate, edge_tts.__version__], ensure_ascii=False)
    digest = hashlib.sha256(settings.encode('utf-8')).hexdigest()[:12]
    return f'voice_{index:02}_{digest}'


async def main():
    (ROOT / 'work').mkdir(parents=True, exist_ok=True)
    story = json.loads((ROOT / 'storyboard.json').read_text(encoding='utf-8-sig'))
    semaphore = asyncio.Semaphore(3)

    async def synth(index, scene):
        async with semaphore:
            mp3 = ROOT / 'work' / (cache_name(index, scene['narration'], story['voice'], story['rate']) + '.mp3')
            wav = mp3.with_suffix('.wav')
            metadata = mp3.with_suffix('.json')
            if not (wav.exists() and metadata.exists()):
                for attempt in range(3):
                    try:
                        boundaries = []
                        with mp3.open('wb') as handle:
                            stream = edge_tts.Communicate(scene['narration'], story['voice'], rate=story['rate'], boundary='SentenceBoundary')
                            async for chunk in stream.stream():
                                if chunk['type'] == 'audio':
                                    handle.write(chunk['data'])
                                elif chunk['type'] == 'SentenceBoundary':
                                    boundaries.append({key: chunk[key] for key in ('text', 'offset', 'duration')})
                        assert mp3.stat().st_size > 1000, '语音为空'
                        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(mp3), '-ar', '48000', '-ac', '1', str(wav)], check=True)
                        metadata.write_text(json.dumps(boundaries, ensure_ascii=False), encoding='utf-8')
                        break
                    except Exception:
                        if attempt == 2:
                            raise
                        await asyncio.sleep(1 + attempt)
            with wave.open(str(wav), 'rb') as handle:
                duration = handle.getnframes() / handle.getframerate()
            assert duration > 1, f'旁白时长异常: {index}'
            print(f'AUDIO {index + 1:02}/{len(story["scenes"])} {duration:.2f}s', flush=True)
            return {'duration': duration, 'wav': wav.name, 'boundaries': json.loads(metadata.read_text(encoding='utf-8')), 'narration': scene['narration'], 'voice': story['voice'], 'rate': story['rate']}

    timing = await asyncio.gather(*(synth(i, s) for i, s in enumerate(story['scenes'])))
    assert len(timing) == len(story['scenes'])
    (ROOT / 'work' / 'audio_timing.json').write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding='utf-8')
    print('TOTAL_SPEECH_SECONDS', sum(t['duration'] for t in timing), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
