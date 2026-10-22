from pathlib import Path
from scipy.io import wavfile
import numpy as np,json,subprocess
r=Path('/workspace/iphone-05-v4');o=Path('/workspace/iphone-05-v3');sr,v=wavfile.read(o/'voice.wav');_,m=wavfile.read(o/'music.wav');_,fx=wavfile.read(o/'effects.wav');v=v.astype(float);m=m.astype(float);fx=fx.astype(float);N=len(v);t=np.arange(N)/sr
# One compact tonal entrance replaces the previous three stacked accents.
fx[:round(3.27*sr)]=0
u=np.arange(round(.16*sr))/sr;ph=2*np.pi*(90*u+35*.012*(1-np.exp(-u/.012)));hit=(np.sin(ph)+.32*np.sin(2*ph))*np.exp(-u*31)*np.minimum(1,u/.0015);i=round(.06*sr);fx[i:i+len(hit)]+=hit[:,None]*.53
fade=np.minimum(t/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('voice.wav',v),('music.wav',m),('effects.wav',fx),('mix.wav',(v+m+fx)*fade[:,None])]:wavfile.write(r/name,sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
(r/'audio-cambios.json').write_text(json.dumps({'voz':'igual V3','musica':'igual V3','eventos':[[.06,'golpe tonal breve',.53]],'resto_efectos':'igual V3 desde3.27s'},ensure_ascii=False,indent=2))
