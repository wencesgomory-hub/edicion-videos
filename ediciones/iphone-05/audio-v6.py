from pathlib import Path
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
from scipy.ndimage import uniform_filter1d
import numpy as np,json,subprocess
r=Path('/workspace/iphone-05-v6');o=Path('/workspace/iphone-05-v5');sr,v=wavfile.read(o/'voice.wav');_,fx=wavfile.read(o/'effects.wav');_,previous=wavfile.read(o/'music.wav');v=v.astype(float);fx=fx.astype(float);N=len(v);D=N/sr;music=np.zeros((N,2));rng=np.random.default_rng(14691);beat=60/140
# New dark percussive instrumental: tight broken drums and syncopated bass.
# No lounge chords, piano melody, bells, or material from the rejected bed.
def add(x,at,g,pan=0):
 i=round(at*sr)
 if i>=N:return
 if i<0:x=x[-i:];i=0
 n=min(len(x),N-i)
 if x.ndim==1:x=np.column_stack([x*(1-.18*pan),x*(1+.18*pan)])
 music[i:i+n]+=x[:n]*g

def band(x,lo,hi):return sosfilt(butter(2,[lo,hi],fs=sr,btype='bandpass',output='sos'),x)
for bar in range(int(np.ceil(D/(beat*4)))):
 start=.10+bar*4*beat
 # Firm kick pattern with occasional offbeat pickup.
 for q in ([0,1.5,2,3.25] if bar%2==0 else [0,.75,2,2.75,3.5]):
  u=np.arange(round(.21*sr))/sr;phase=2*np.pi*(51*u+98*.016*(1-np.exp(-u/.016)))
  kick=(np.sin(phase)+.20*np.sin(2*phase))*np.exp(-u*25)*np.minimum(1,u/.0008)
  attack=np.sin(2*np.pi*185*u)*np.exp(-u*160)*.20
  add(kick+attack,start+q*beat,.47 if q in [0,2] else .36)
 for q in [1,3]:
  u=np.arange(round(.13*sr))/sr;noise=band(rng.normal(size=len(u)),1100,7800)
  envelope=np.exp(-u*43)+.38*np.exp(-abs(u-.012)*330)
  body=np.sin(2*np.pi*186*u)*np.exp(-u*44)
  snare=(.34*noise*envelope+.40*body)*np.minimum(1,u/.0007)
  add(snare,start+q*beat,.28)
 # Closed hats, lightly swung and panned; avoid continuous shaker wash.
 for k in range(8):
  if bar%4==3 and k==7:continue
  u=np.arange(round(.032*sr))/sr;hat=band(rng.normal(size=len(u)),6500,11500)*np.exp(-u*140)*np.minimum(1,u/.0005)
  add(hat,start+(k*.5+(.025 if k%2 else 0))*beat,.028 if k%2 else .019,(-1 if k%2 else 1))
 # Monophonic bass riff with harmonics audible on phone speakers.
 notes=[38,38,41,36];root=notes[(bar//2)%4]
 pattern=[(.25,root,.22),(1.75,root,.16),(2.5,root+12,.14),(3.5,root,.18)]
 for q,note,length in pattern:
  u=np.arange(round(length*sr))/sr;f=440*2**((note-69)/12)
  bass=np.sin(2*np.pi*f*u)+.48*np.sin(4*np.pi*f*u)+.28*np.sin(6*np.pi*f*u)+.12*np.sin(8*np.pi*f*u)
  bass=np.tanh(bass*1.2)*np.minimum(1,u/.006)*np.minimum(1,(length-u)/.025)*np.exp(-u*5)
  add(bass,start+q*beat,.22)
 # A muted percussive accent at the turnaround, not a lead melody.
 if bar%2:
  u=np.arange(round(.07*sr))/sr;rim=np.sin(2*np.pi*900*u)*np.exp(-u*100)*np.minimum(1,u/.0007)
  add(rim,start+3.75*beat,.035,.6)
# Keep the same overall bed level, with speech priority and a clean tail.
energy=np.sqrt(uniform_filter1d(np.mean(v*v,axis=1),2400)+1e-12);music*=np.clip(1-energy*1.3,.70,1)[:,None]
t=np.arange(N)/sr;music*=np.minimum(t/.045,1)[:,None]*np.minimum((D-t)/.20,1)[:,None]
music*=np.sqrt(np.mean(previous.astype(float)**2))/(np.sqrt(np.mean(music*music))+1e-12)
fade=np.minimum(t/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('voice.wav',v),('music.wav',music),('effects.wav',fx),('mix.wav',(v+music+fx)*fade[:,None])]:wavfile.write(r/name,sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
(r/'cambio.json').write_text(json.dumps({'cambio':'Solo música','musica':'Nueva composición percusiva140BPM, batería quebrada y bajo sincopado, sin acordes lounge ni melodía de teclado. RMS igualado a V5 después de ducking.','voz':'Stem exacto V5','efectos':'Stem exacto V5','imagen':'Copia de flujo V5 sin recodificar','duracion':D},ensure_ascii=False,indent=2))
