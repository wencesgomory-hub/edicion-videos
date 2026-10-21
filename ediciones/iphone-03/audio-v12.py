from pathlib import Path
import numpy as np,json,subprocess
from scipy.io import wavfile
R=Path('/workspace/interior-03-v12');old=Path('/workspace/interior-03-v10');sr=48000
_,v=wavfile.read(old/'voice.wav');_,m=wavfile.read(old/'music.wav');_,fx=wavfile.read(old/'effects.wav');v=v.astype(float);m=m.astype(float);fx=fx.astype(float);N=len(v)
_,base=wavfile.read('/workspace/edicion-videos/materiales/audio/musica-base-anuncio-v11.wav');m=base[:N].astype(float).copy()
origm=m.copy();origfx=fx.copy()
# No added sound effect under BASTA. Remove all prior introductory FX layers.
fx[:round(.65*sr)]=0
# Let the voice lead; music returns smoothly to the lower original-stem level by 0.65 s.
t=np.arange(N)/sr;envelope=np.clip((t-.20)/.45,0,1);envelope=envelope*envelope*(3-2*envelope);m*=envelope[:,None]
# Short tonal low impact, with no noise layer or sampled thud.
q=np.arange(round(.16*sr))/sr
phase=2*np.pi*(58*q+42*.012*(1-np.exp(-q/.012)))
fum=(np.sin(phase)+.22*np.sin(2*phase))*np.exp(-q*35)*np.minimum(1,q/.0018)
fum*=np.minimum((len(fum)-np.arange(len(fum)))/sr/.008,1)
fum*=.32/(np.max(abs(fum))+1e-12)
i=round(.14*sr);fx[i:i+len(fum)]+=fum[:,None]
assert np.array_equal(fx[round(.65*sr):],origfx[round(.65*sr):])
assert np.array_equal(m[round(.65*sr):],origm[round(.65*sr):])
fade=np.minimum(t/.025,1)*np.minimum((N-np.arange(N))/sr/.12,1)
wavfile.write(R/'mix.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i','/workspace/edicion-videos/videos/anuncio-iphone-03-v11.mp4','-i',str(R/'master.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-t',str(N/sr),'-movflags','+faststart','/workspace/edicion-videos/videos/anuncio-iphone-03-v12.mp4'],check=True)
(R/'cambio.json').write_text(json.dumps({'voz':'Sin cambio','imagen':'V11 copiada sin recodificar','inicio':'Fum grave de 0.16 s desde0.14 s, sin ruido, ding ni reverberación añadida; música entra desde0.20 hasta0.65 s','desde_0_65':'Pista anterior sola, sin percusión reforzada, con nivel considerablemente menor que V10; efectos posteriores conservados','duracion':N/sr},ensure_ascii=False,indent=2));print('DONE',flush=True)
