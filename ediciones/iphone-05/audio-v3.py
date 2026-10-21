from pathlib import Path
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d
import numpy as np,json,subprocess
R=Path('/workspace/iphone-05-v3');old=Path('/workspace/iphone-05');sr,v=wavfile.read(old/'voice.wav');N=round(35.016667*sr);v=v[:N].astype(float);t=np.arange(N)/sr
# Global voice lift, with a restrained extra emphasis across the hook.
g=10**(3.5/20)*(1+(10**(1.5/20)-1)*np.clip((4.1-t)/.7,0,1));v*=g;v=np.column_stack([v,v])
_,m=wavfile.read('/workspace/edicion-videos/materiales/audio/musica-base-anuncio-v11.wav');m=m[:N].astype(float);m*=10**(-26.5/20)/(np.sqrt(np.mean(m*m))+1e-12)
# Add controlled low-end on the approved 142 BPM pulse, no hiss or paper texture.
beat=60/142
for k in range(int(N/sr/beat)):
 at=.08+k*beat;i=round(at*sr);u=np.arange(round(.14*sr))/sr
 phase=2*np.pi*(56*u+68*.014*(1-np.exp(-u/.014)));kick=(np.sin(phase)+.13*np.sin(2*phase))*np.exp(-u*34)*np.minimum(1,u/.0015);n=min(len(kick),N-i)
 if n>0:m[i:i+n]+=kick[:n,None]*.065
energy=np.sqrt(uniform_filter1d(np.mean(v*v,axis=1),size=2400)+1e-12);duck=np.clip(1-energy*1.45,.68,1);m*=duck[:,None]
_,fx=wavfile.read('/workspace/iphone-05-v2/effects.wav');fx=fx.astype(float)*10**(3/20)
# Remove the old sparse hook events and land a compact, strong introduction.
fx[:round(3.27*sr)]=0
_,bank=wavfile.read('/workspace/edicion-videos/materiales/audio/efectos-aislados-anuncio-v11.wav');refs={'thud':7.67/1.12,'snap':8.48/1.12,'wood':15.2/1.12,'bubble':16.7/1.12};events=[]
def add(x,at,g):
 if x.ndim==1:x=np.column_stack([x,x])
 i=round(at*sr);n=min(len(x),N-i)
 if n>0:fx[i:i+n]+=x[:n]*g

def effect(at,kind,g):
 i=round(refs[kind]*sr);x=bank[i:i+round(.16*sr)].astype(float);x/=np.max(abs(x))+1e-12;add(x,at,g);events.append([at,kind,g])
# Punch and tactile reveal, without repeating bell hits.
u=np.arange(round(.18*sr))/sr;ph=2*np.pi*(85*u+52*.012*(1-np.exp(-u/.012)));hit=(np.sin(ph)+.35*np.sin(2*ph))*np.exp(-u*28)*np.minimum(1,u/.0015);add(hit,.025,.45)
effect(.08,'thud',.55);effect(.40,'bubble',.48);effect(.80,'wood',.34)
fade=np.minimum(t/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('voice.wav',v),('music.wav',m),('effects.wav',fx),('mix.wav',(v+m+fx)*fade[:,None])]:wavfile.write(R/name,sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
(R/'audio-cambios.json').write_text(json.dumps({'voz_global_db_sobre_v1':3.5,'voz_gancho_db_sobre_v1':5,'efectos_db_sobre_v2':3,'musica':'Stem aprobado V11 a -26.5dB RMS antes de ducking, refuerzo grave142BPM, sustituye base132BPM rechazada','eventos':events,'cierre':'sincronía V2 conservada','velocidad':1},ensure_ascii=False,indent=2))
