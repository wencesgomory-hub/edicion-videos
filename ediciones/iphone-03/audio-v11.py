from pathlib import Path
import numpy as np,json,subprocess
from scipy.io import wavfile
from scipy.signal import resample_poly
R=Path('/workspace/interior-03-v11');old=Path('/workspace/interior-03-v10');sr=48000
v=wavfile.read(old/'voice.wav')[1].astype(float);m=wavfile.read(old/'music.wav')[1].astype(float);fx=wavfile.read(old/'effects.wav')[1].astype(float);before=fx.copy();N=len(v)
# Remove the complete layered opening (sweep, tension, ding, long low tail).
fx[:round(.5*sr)]=0
_,bank=wavfile.read('/workspace/edicion-videos/materiales/audio/efectos-aislados-anuncio-v11.wav');start=round(7.67/1.12*sr);hit=bank[start:start+round(.14*sr)].astype(float)
if hit.ndim==1:hit=np.column_stack([hit,hit])
hit/=np.max(abs(hit))+1e-12
# A dry transient with a short low body, no ringing high note, echo or reverb.
t=np.arange(len(hit))/sr;body=(np.sin(2*np.pi*(57*t+30*.012*(1-np.exp(-t/.012))))+.26*np.sin(2*np.pi*123*t))*np.exp(-t*44)*np.minimum(1,t/.001)
x=hit*.40+body[:,None]*.15
endfade=np.minimum((len(x)-np.arange(len(x)))/sr/.008,1);x*=endfade[:,None]
i=round(.15*sr);fx[i:i+len(x)]+=x
assert np.array_equal(fx[round(.5*sr):],before[round(.5*sr):])
fade=np.minimum(np.arange(N)/sr/.025,1)*np.minimum((N-np.arange(N))/sr/.12,1)
wavfile.write(R/'mix.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
(R/'cambio-inicio.json').write_text(json.dumps({'efecto':'Golpe seco + cuerpo grave corto, sin ding, sin tensión estirada ni barrido sonoro inicial','inicio':.15,'duracion':.14,'voz_y_musica':'Componentes V10 idénticos, música conserva reducción del 10%','resto_efectos_sin_cambio_desde':.5},ensure_ascii=False,indent=2))
