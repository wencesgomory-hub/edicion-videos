from pathlib import Path
import subprocess,json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
R=Path('/workspace/seminuevos-01-v11');repo=Path('/workspace/edicion-videos');sr=48000
_,mix=wavfile.read('/workspace/seminuevos-01-v10/mezcla.wav');mix=mix.astype(float);N=len(mix);D=N/sr
_,music=wavfile.read('/workspace/seminuevos-01-v9/musica.wav');music=music.astype(float)[:N]*10**(3/20)
fade=np.minimum(np.arange(N)/sr/.02,1)*np.minimum((N-np.arange(N))/sr/.14,1)
# +2.5 dB over V10: same approved track, voice and effects stay in place.
mix+=music*(10**(2.5/20)-1)*fade[:,None]
drums=np.zeros(N);rng=np.random.default_rng(11142);B=60/142
for beat in range(int(D/B)+1):
 at=beat*B;i=round(at*sr);t=np.arange(round(.15*sr))/sr
 kick=np.sin(2*np.pi*(49*t+70*.022*(1-np.exp(-t/.022))))*np.exp(-t*29)
 pulse=kick*.032
 if beat%2:
  noise=sosfilt(butter(2,[1100,7600],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(t)))
  pulse+=noise*np.exp(-t*65)*.010
 e=min(N,i+len(t))
 if e>i:drums[i:e]+=pulse[:e-i]
mix+=drums[:,None]*fade[:,None]
wavfile.write(R/'mezcla.wav',sr,mix.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mezcla.wav'),'-af','alimiter=limit=0.84:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
s=json.loads(Path('/workspace/seminuevos-01-v10/montaje.json').read_text());s.update(version='v11',revision='Música +2.5 dB respecto de V10, refuerzo de bombo/caja a 142 BPM y ajuste suave de contraste/color/luminosidad. Voz, textos, efectos y cortes conservados.',salida='videos/anuncio-seminuevos-mdp-01-v11.mp4');(R/'montaje.json').write_text(json.dumps(s,ensure_ascii=False,indent=2))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/'videos/anuncio-seminuevos-mdp-01-v10.mp4'),'-i',str(R/'master.wav'),'-map','0:v:0','-map','1:a:0','-vf','eq=contrast=1.035:brightness=0.003:saturation=1.05:gamma=1.025','-t',str(D),'-c:v','libx264','-preset','fast','-crf','14','-threads','4','-c:a','aac','-b:a','256k','-movflags','+faststart',str(repo/s['salida'])],check=True)
print('V11 DONE',flush=True)
