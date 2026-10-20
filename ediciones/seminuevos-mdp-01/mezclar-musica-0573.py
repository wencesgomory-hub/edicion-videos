from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly,butter,sosfilt
import subprocess,json
R=Path('/workspace/seminuevos-01-v4');s=json.loads((R/'edit.json').read_text());sr=48000;N=round(s['duration']*sr)
_,v=wavfile.read(R/'voice.wav');v=v.astype(float)
if v.ndim==1:v=np.column_stack([v,v])
_,fx=wavfile.read(R/'effects.wav');fx=fx.astype(float)
fs,m=wavfile.read(R/'music-reference/instrumental.wav');m=resample_poly(m.astype(float),160,147,axis=0);m=m[int(.5*sr):int(.5*sr)+N];m=np.pad(m,((0,max(0,N-len(m))),(0,0)))[:N]
m=sosfilt(butter(2,[75,13500],fs=sr,btype='bandpass',output='sos'),m,axis=0)
# Tame unrelated peaks left by the reference SFX before setting the background level.
rms=np.sqrt(np.mean(m*m));m=rms*3*np.tanh(m/(rms*3+1e-12));m*=10**(-33/20)/(np.sqrt(np.mean(m*m))+1e-12)
v=np.pad(v,((0,max(0,N-len(v))),(0,0)))[:N];fx=np.pad(fx,((0,max(0,N-len(fx))),(0,0)))[:N]
env=np.sqrt(np.convolve(np.mean(v*v,axis=1),np.ones(1200)/1200,mode='same')+1e-9);m*=np.clip(.85-env*2,.5,.85)[:,None]
fade=np.minimum(np.arange(N)/sr/.06,1)*np.minimum((N-np.arange(N))/sr/.18,1)
wavfile.write(R/'musica-extraida-0573.wav',sr,(m*fade[:,None]).astype(np.float32));wavfile.write(R/'mix-referencia.wav',sr,((v*1.03+m+fx*2.0)*.65*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix-referencia.wav'),'-af','alimiter=limit=0.80:level=false:latency=true','-c:a','pcm_f32le',str(R/'master-referencia.wav')],check=True);print('MIX DONE',flush=True)
