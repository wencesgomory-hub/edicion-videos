from pathlib import Path
import numpy as np,json,subprocess
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
R=Path('/workspace/interior-03-cierre');sr=48000
# Reuse exactly the voice reconstruction the user approved, without reprocessing it.
p=Path('/workspace/interior-03-final/audio.py').read_text().split('_,m=wavfile.read')[0]
p=p.replace("R=Path('/workspace/interior-03-final')","R=Path('/workspace/interior-03-cierre')");scope={};exec(p,scope);v=scope['v'];N=len(v);D=N/sr
rng=np.random.default_rng(13221);beat=60/132;m=np.zeros((N,2))
def bp(x,lo,hi):return sosfilt(butter(2,[lo,hi],fs=sr,btype='bandpass',output='sos'),x)
def put(buf,x,at,g,pan=0):
 i=round(at*sr)
 if i<0:x=x[-i:];i=0
 e=min(N,i+len(x))
 if e<=i:return
 if x.ndim==1:x=np.column_stack([x*(1-pan*.2),x*(1+pan*.2)])
 buf[i:e]+=x[:e-i]*g
start=.12
# New driving instrumental: four-on-floor kick, firm backbeat and syncopated bass.
for k in range(int(D/beat)+1):
 at=start+k*beat;t=np.arange(round(.22*sr))/sr
 phase=2*np.pi*(49*t+78*.019*(1-np.exp(-t/.019)))
 kick=(np.sin(phase)+.17*np.sin(2*phase))*np.exp(-t*27)*np.minimum(1,t/.0012)
 knock=np.sin(2*np.pi*173*t)*np.exp(-t*110)*.14
 put(m,kick+knock,at,.30)
 if k%2:
  t=np.arange(round(.12*sr))/sr
  n=bp(rng.normal(size=len(t)),900,6500)
  clap=n*(np.exp(-t*58)+.38*np.exp(-abs(t-.012)*280))*np.minimum(1,t/.001)
  put(m,clap,at,.085)
 # Quiet offbeat hats; no rattling layer at the opening.
 if at>.6:
  t=np.arange(round(.045*sr))/sr;hat=bp(rng.normal(size=len(t)),6500,10500)*np.exp(-t*120)
  put(m,hat,at+beat/2,.013,(-1 if k%2 else 1))
for bar in range(8):
 at=start+bar*4*beat
 root=[42,42,45,40][bar%4];freq=440*2**((root-69)/12)
 for q in [.5,1.25,1.75,2.5,3.25,3.75]:
  t=np.arange(round(.22*sr))/sr
  bass=(np.sin(2*np.pi*freq*t)+.47*np.sin(4*np.pi*freq*t)+.22*np.sin(6*np.pi*freq*t))*np.minimum(1,t/.008)*np.exp(-t*14)
  put(m,bass,at+q*beat,.16)
 # Soft, clipped minor chord stabs, subordinate to the drums and speech.
 for q in [.75,2.75]:
  t=np.arange(round(.21*sr))/sr;stab=np.zeros_like(t)
  for note in [root+24,root+27,root+31]:
   f=440*2**((note-69)/12)
   stab+=np.sin(2*np.pi*f*t)+.16*np.sin(4*np.pi*f*t)
  stab=stab/3*np.minimum(1,t/.008)*np.exp(-t*22)
  put(m,stab,at+q*beat,.025,.5 if bar%2 else -.5)
# Controlled music level: present, with voice taking priority.
m*=10**(-29/20)/(np.sqrt(np.mean(m*m))+1e-12)
_,fx=wavfile.read('/workspace/interior-03-v10/effects.wav');fx=fx.astype(float);fx[:round(.65*sr)]=0
# Smooth low/mid air sweep, no crackling/transient noise texture.
t=np.arange(round(.19*sr))/sr
raw=rng.normal(size=len(t));air=bp(raw,260,2200)
air=sosfilt(butter(2,1900,fs=sr,btype='lowpass',output='sos'),air)
air*=np.sin(np.pi*t/.19)**2;air/=max(abs(air))+1e-12
put(fx,air,.005,.18)
t=np.arange(round(.17*sr))/sr;phase=2*np.pi*(78*t+44*.011*(1-np.exp(-t/.011)))
hit=(np.sin(phase)+.30*np.sin(2*phase))*np.exp(-t*30)*np.minimum(1,t/.0014)
hit*=np.minimum((len(hit)-np.arange(len(hit)))/sr/.008,1);hit/=max(abs(hit))+1e-12
put(fx,hit,.12,.38)
fade=np.minimum(np.arange(N)/sr/.015,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('voice.wav',v),('music.wav',m),('effects.wav',fx),('mix.wav',(v+m+fx)*fade[:,None])]:wavfile.write(R/name,sr,x.astype(np.float32))
assert np.array_equal(v,scope['v'])
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
(R/'audio-cierre.json').write_text(json.dumps({'voz':'Reconstrucción aprobada de final, exactamente igual antes de mezcla','musica':'Nueva composición instrumental de132BPM, bombo4/4, bajo sincopado y percusión; normalizada a -29dB RMS antes de mezcla','intro':'Barrido de aire filtrado suave0.005–0.195s y golpe grave0.12–0.29s, separados de la voz','efectos_desde0_65':'Conservados'},ensure_ascii=False,indent=2))
