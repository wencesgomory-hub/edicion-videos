from pathlib import Path
import sherpa_onnx,soundfile as sf,numpy as np,json
r=Path('/workspace/rayban-02');m=Path('/workspace/models/spanish-ctc');rec=sherpa_onnx.OfflineRecognizer.from_nemo_ctc(model=str(m/'model.int8.onnx'),tokens=str(m/'tokens.txt'),num_threads=4)
a,sr=sf.read(r/'asr.wav',dtype='float32');out=[]
for st,en in [(st,min(148.033333,st+28)) for st in range(0,148,28)]:
 s=rec.create_stream();s.accept_waveform(sr,a[round(st*sr):round(en*sr)]);rec.decode_stream(s);x={'offset':st,'fin':en,'result':json.loads(str(s.result))};out.append(x);print(json.dumps(x,ensure_ascii=False),flush=True)
(r/'ctc.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
