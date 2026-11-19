from pathlib import Path
import sherpa_onnx,soundfile as sf,numpy as np,json
r=Path('/workspace/rayban-02');m=Path('/workspace/models/whisper-large-v3');rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=str(m/'large-v3-encoder.int8.onnx'),decoder=str(m/'large-v3-decoder.int8.onnx'),tokens=str(m/'large-v3-tokens.txt'),language='es',num_threads=6,enable_segment_timestamps=True)
a,sr=sf.read(r/'asr.wav',dtype='float32');out=[]
for start,end in [(0,26)]:
 s=rec.create_stream();s.accept_waveform(sr,np.pad(a[round(start*sr):round(end*sr)],(0,sr)));rec.decode_stream(s);x={'offset':start,'fin':end,'result':json.loads(str(s.result))};out.append(x);print(json.dumps(x,ensure_ascii=False),flush=True);(r/'transcript-large.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
