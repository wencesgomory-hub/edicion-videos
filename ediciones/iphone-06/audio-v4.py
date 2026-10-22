from pathlib import Path
from scipy.io import wavfile
import numpy as np,subprocess,json
r=Path('/workspace/iphone-06-v4');o=Path('/workspace/iphone-06-v3');sr,v=wavfile.read(o/'voice.wav');_,m=wavfile.read(o/'music.wav');_,fx=wavfile.read(o/'effects.wav');v=v.astype(float);m=m.astype(float);fx=fx.astype(float);N=len(v)
# Replace only the existing price-entry sound; leave the clock and other accents intact.
fx[round(3.20*sr):round(3.40*sr)]=0
_,sample=wavfile.read('/workspace/edicion-videos/materiales/audio/efectos-aislados-anuncio-v11.wav');j=round(15.2/1.12*sr);a=sample[j:j+round(.026*sr)].astype(float);a*=np.minimum(np.arange(len(a))/sr/.001,1)[:,None]*np.minimum((len(a)-np.arange(len(a)))/sr/.003,1)[:,None];a/=np.max(abs(a))+1e-12
events=[]
for at in [3.21,3.29,3.37,3.56,3.70,3.86,4.56,4.69,4.82]:
 i=round(at*sr);fx[i:i+len(a)]+=a*.095;events.append([at,'tecla seca',.095])
fade=np.minimum(np.arange(N)/sr/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1);wavfile.write(r/'mix-new.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32));wavfile.write(r/'effects-new.wav',sr,fx.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix-new.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master-new.wav')],check=True)
(r/'audio-cambios.json').write_text(json.dumps({'voz_musica':'Exactas V3 antes de mezcla','cambio':'Entrada de precios reemplazada por tecleo sincronizado a escritura; resto intacto','eventos':events},ensure_ascii=False,indent=2))
