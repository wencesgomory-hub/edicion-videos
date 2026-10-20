from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
R=Path('/workspace/seminuevos-01-v5');B=Path('/workspace/seminuevos-01-v4');s=json.loads((B/'edit.json').read_text());old=next(x for x in s['accents'] if x[2]=='red')[0]
s['accents']=[[16.40,16.97,'red'] if x[2]=='red' else x for x in s['accents']];s['insertos']=[];s['revision']='V5: quitar ambos insertos y conservar toma original; cruz y sonido negativo en réplicas.';s['cruz_timing']='Estimación de alineación visual/fonética: salida 16.40–16.97 s, correspondiente al final de la frase réplicas; no al inicio de la frase anterior.';(R/'edit.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
for name in ['clip-0.mp4','clip-1.mp4','clip-2.mp4','clip-3.mp4','cable.png','funda.png','cargador.png','dolar.png']:
 p=R/name
 if not p.exists():p.symlink_to(B/name)
p=R/'graphics.py';p.write_text((B/'graphics.py').read_text().replace("R=Path('/workspace/seminuevos-01-v4')","R=Path('/workspace/seminuevos-01-v5')"))
# Relocate only the red confirmation cue; preserve the approved mix and music exactly elsewhere.
sr,x=wavfile.read(B/'mix-referencia.wav');x=x.copy();t=np.arange(int(.1*sr))/sr;cue=np.sin(2*np.pi*330*t)*np.sin(np.pi*t/.1)**2*.22*2.0*.65
for at,g in [(old,-1),(16.40,1)]:
 i=int(at*sr);x[i:i+len(cue)]+=cue[:,None]*g
wavfile.write(R/'mix.wav',sr,x.astype(np.float32));subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.80:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
