"""一次性分离同一音源的前 130 秒，避免分段推理的音色接缝。"""
from pathlib import Path
import importlib.util
import numpy as np
import soundfile as sf

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('separate',root/'scripts/separate-reference.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
samples,sr=sf.read(root/'audio-src/reference-full.wav',dtype='float32',always_2d=True)
assert len(samples)==130*sr
print('Separating 130 seconds in one continuous pass...',flush=True)
result=helper.create_offline_source_separation().process(sample_rate=sr,samples=np.ascontiguousarray(samples.T))
instrumental=result.stems[1].data.T
assert result.sample_rate==sr and instrumental.shape==samples.shape and np.isfinite(instrumental).all()
sf.write(root/'audio-src/reference-full-instrumental.wav',instrumental,sr,subtype='PCM_24')
print('130 seconds; continuous separation, no joins, loops or retiming.',flush=True)
