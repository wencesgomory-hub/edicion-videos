from pathlib import Path
from scipy.io import wavfile
import numpy as np,subprocess,json
r=Path('/workspace/iphone-07-v4');o=Path('/workspace/iphone-07');sr,v=wavfile.read(o/'voice.wav');_,m=wavfile.read(o/'music.wav');_,fx=wavfile.read(o/'effects.wav');v=v.astype(float);m=m.astype(float);fx=fx.astype(float);N=len(v)
_,sample=wavfile.read('/workspace/edicion-videos/materiales/audio/efectos-aislados-anuncio-v11.wav');refs={'wood':15.2/1.12,'bubble':16.7/1.12,'thud':7.67/1.12};events=[]
for at,kind,dur,g in [(.10,'wood',.035,.10),(.24,'wood',.035,.10),(.40,'wood',.035,.10),(3.,'bubble',.16,.38),(3.65,'thud',.13,.28)]:
 i=round(refs[kind]*sr);a=sample[i:i+round(dur*sr)].astype(float);a*=np.minimum(np.arange(len(a))/sr/.0015,1)[:,None]*np.minimum((len(a)-np.arange(len(a)))/sr/.004,1)[:,None];a/=np.max(abs(a))+1e-12;j=round(at*sr);fx[j:j+len(a)]+=a*g;events.append([at,kind,g])
fade=np.minimum(np.arange(N)/sr/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1)
wavfile.write(r/'effects-new.wav',sr,fx.astype(np.float32));wavfile.write(r/'mix-new.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix-new.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master-new.wav')],check=True)
(r/'audio-cambios.json').write_text(json.dumps({'voz_musica':'V1 exactas antes de mezcla','efectos_nuevos':events,'resto':'Sin cambios'},ensure_ascii=False,indent=2))
