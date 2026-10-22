from pathlib import Path
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import numpy as np,json,subprocess
r=Path('/workspace/iphone-05-v5');o=Path('/workspace/iphone-05-v4');sr,v=wavfile.read(o/'voice.wav');_,music=wavfile.read(o/'music.wav');_,fx=wavfile.read(o/'effects.wav');v=v.astype(float);music=music.astype(float);fx=fx.astype(float);N=len(v);D=N/sr;intro=round(3.27*sr)
# Change the attack and arrangement of the opening, not its overall level.
x=music[:intro].copy();extra=np.zeros_like(x);beat=60/142
for k in range(8):
 i=round((.08+k*beat)*sr);u=np.arange(round(.16*sr))/sr
 ph=2*np.pi*(60*u+82*.012*(1-np.exp(-u/.012)));kick=(np.sin(ph)+.36*np.sin(2*ph)+.18*np.sin(3*ph))*np.exp(-u*30)*np.minimum(1,u/.001)
 n=min(len(kick),intro-i)
 if n>0:extra[i:i+n]+=kick[:n,None]*.085
 if k%2:
  u=np.arange(round(.07*sr))/sr
  snap=(np.sin(2*np.pi*180*u)+.4*np.sin(2*np.pi*320*u))*np.exp(-u*65)*np.minimum(1,u/.0008);n=min(len(snap),intro-i)
  if n>0:extra[i:i+n]+=snap[:n,None]*.08
shaped=np.tanh((x+extra)*3)/3
shaped*=np.sqrt(np.mean(x*x))/(np.sqrt(np.mean(shaped*shaped))+1e-12)
blend=np.minimum((intro-np.arange(intro))/sr/.22,1);music[:intro]=shaped*blend[:,None]+x*(1-blend[:,None])
fx[:intro]=0
# A smooth short tonal sweep into one body impact; no rustling sample or repeated ding.
u=np.arange(round(.11*sr))/sr;sweep=np.zeros_like(u)
for j in range(5):
 ph=2*np.pi*((470+85*j)*u-(110+15*j)*u*u/.11);sweep+=np.sin(ph)/(j+2)
sweep*=np.sin(np.pi*u/.11)**2;sweep/=np.max(abs(sweep))+1e-12
i=round(.025*sr);fx[i:i+len(sweep)]+=sweep[:,None]*.13
u=np.arange(round(.17*sr))/sr;ph=2*np.pi*(83*u+49*.010*(1-np.exp(-u/.010)));hit=(np.sin(ph)+.38*np.sin(2*ph)+.15*np.sin(3*ph))*np.exp(-u*30)*np.minimum(1,u/.0013);i=round(.10*sr);fx[i:i+len(hit)]+=hit[:,None]*.54
# A single clean ting on the green budget label, not a repeating bell pattern.
u=np.arange(round(.16*sr))/sr;ting=(np.sin(2*np.pi*1318.51*u)+.24*np.sin(2*np.pi*1977.77*u))*np.exp(-u*31)*np.minimum(1,u/.002)
i=round(12.57*sr);fx[i:i+len(ting)]+=ting[:,None]*.25
fade=np.minimum(np.arange(N)/sr/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,a in [('voice.wav',v),('music.wav',music),('effects.wav',fx),('mix.wav',(v+music+fx)*fade[:,None])]:wavfile.write(r/name,sr,a.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
(r/'audio-cambios.json').write_text(json.dumps({'voz':'igual V4','musica':'Intro0–3.27s con percusión y armónicos más firmes, RMS igualado a V4; resto idéntico','eventos':[[.025,'barrido tonal suave',.13],[.10,'golpe con cuerpo',.54],[12.57,'ting presupuesto',.25]],'resto_efectos':'igual V4 desde3.27s salvo ting12.57s pedido por usuario'},ensure_ascii=False,indent=2))
