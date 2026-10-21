from pathlib import Path
import numpy as np,json,subprocess
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
R=Path('/workspace/interior-03-final');old=Path('/workspace/interior-03-v10');sr=48000
_,v=wavfile.read(old/'voice.wav');v=v.astype(float);original_voice=v.copy();N=len(v)
# Rebuild the first second from raw source, avoiding WPE/spectral artefacts in the opening.
_,raw=wavfile.read('/workspace/interior-03/voice-0.wav');raw=raw[:sr].astype(float)
clean=sosfilt(butter(2,[95,6000],fs=sr,btype='bandpass',output='sos'),raw)
ref=np.sqrt(np.mean(v[round(.16*sr):round(.8*sr)]**2));level=np.sqrt(np.mean(clean[round(.16*sr):round(.8*sr)]**2));clean*=min(3,ref/(level+1e-12))
clean[:round(.115*sr)]=0
clean[:round(.16*sr)]*=np.clip((np.arange(round(.16*sr))/sr-.115)/.035,0,1)
blend=np.ones(sr);blend[round(.8*sr):]=np.linspace(1,0,sr-round(.8*sr))
v[:sr]=v[:sr]*(1-blend[:,None])+clean[:,None]*blend[:,None]
_,m=wavfile.read('/workspace/edicion-videos/materiales/audio/musica-base-anuncio-v11.wav');m=m[:N].astype(float)
_,fx=wavfile.read(old/'effects.wav');fx=fx.astype(float);fx[:round(.65*sr)]=0
# A short body-rich impact is audible on phone speakers, without noise/sweep/metallic layers.
q=np.arange(round(.18*sr))/sr;phase=2*np.pi*(82*q+44*.010*(1-np.exp(-q/.010)))
x=(np.sin(phase)+.38*np.sin(2*phase)+.12*np.sin(3*phase))*np.exp(-q*31)*np.minimum(1,q/.0012)
x*=np.minimum((len(x)-np.arange(len(x)))/sr/.007,1);x*=.46/(max(abs(x))+1e-12)
i=round(.10*sr);fx[i:i+len(x)]+=x[:,None]
t=np.arange(N)/sr;u=np.clip((t-.30)/.35,0,1);m*=((u*u)*(3-2*u))[:,None]
fade=np.minimum(t/.02,1)*np.minimum((N-np.arange(N))/sr/.12,1)
wavfile.write(R/'mix.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
assert np.array_equal(v[sr:],original_voice[sr:])
(R/'audio-final.json').write_text(json.dumps({'inicio_voz':'Primer segundo reconstruido de fuente cruda con filtro 95–6000Hz, sin WPE ni reducción espectral; cruce a voz aprobada 0.8–1.0s.','efecto':'Impacto tonal corto de 0.18s desde0.10s, con armónicos para audibilidad en teléfono, sin ruido/campana/cola de tensión.','musica':'Pista anterior sola a nivel bajo; entrada suave0.30–0.65s.','resto':'Voz desde1s y efectos desde0.65s preservados.'},ensure_ascii=False,indent=2))
