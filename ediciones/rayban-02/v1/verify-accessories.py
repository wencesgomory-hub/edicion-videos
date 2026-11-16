from pathlib import Path
import sherpa_onnx,soundfile as sf,numpy as np,json
r=Path('/workspace/rayban-02');m=Path('/workspace/seminuevos-01/sherpa-onnx-whisper-small');a,sr=sf.read(r/'asr.wav',dtype='float32')
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=str(m/'small-encoder.int8.onnx'),decoder=str(m/'small-decoder.int8.onnx'),tokens=str(m/'small-tokens.txt'),language='es',num_threads=4,enable_segment_timestamps=True)
out=[]
for st in [81]:
 en=94;s=rec.create_stream();s.accept_waveform(sr,np.pad(a[round(st*sr):round(en*sr)],(0,sr)));rec.decode_stream(s);x={'offset':st,'fin':en,'result':json.loads(str(s.result))};out.append(x);print(json.dumps(x,ensure_ascii=False),flush=True);(r/'verificacion-accesorios.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
