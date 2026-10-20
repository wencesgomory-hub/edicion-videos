from pathlib import Path
import subprocess,json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
R=Path('/workspace/seminuevos-01');s=json.loads((R/'edit.json').read_text());sr=48000;N=int(s['duration']*sr)
voice=[]
for i in range(4):
 fs,x=wavfile.read(R/f'voice-{i}.wav');voice.append(x.astype(np.float32)/32768)
x=np.concatenate(voice);wavfile.write(R/'voice-raw.wav',sr,x)
af='highpass=f=85,afftdn=nr=5:nf=-38,agate=threshold=0.0035:ratio=1.3:range=0.8:attack=8:release=140,equalizer=f=160:t=q:w=0.9:g=1,equalizer=f=350:t=q:w=0.9:g=-1.5,equalizer=f=3400:t=q:w=0.8:g=1.6,deesser=i=0.15:m=0.4:f=0.5,acompressor=threshold=0.1:ratio=2:attack=8:release=100:makeup=1.15,loudnorm=I=-15:TP=-1.5:LRA=7'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'voice-raw.wav'),'-af',af,'-ar','48000','-c:a','pcm_f32le',str(R/'voice.wav')],check=True)
def load(p):
 _,v=wavfile.read(p);v=v.astype(float)/(32768 if v.dtype==np.int16 else 1)
 if v.ndim==1:v=np.stack([v,v],axis=1)
 return np.pad(v,((0,max(0,N-len(v))),(0,0)))[:N]
v=load(R/'voice.wav');music=load('/workspace/anuncio-interior-02-v2/musica-electronica-142.wav');music*=10**(-33/20)/(np.sqrt(np.mean(music**2))+1e-9)
fx=np.zeros((N,2));rng=np.random.default_rng(6236)
def add(x,at,g,pan=0):
 i=int(at*sr)
 if i<0:x=x[-i:];i=0
 e=min(N,i+len(x))
 if e>i:fx[i:e,0]+=x[:e-i]*g*(1-pan*.25);fx[i:e,1]+=x[:e-i]*g*(1+pan*.25)
def sound(kind,p=1):
 t=np.arange(int(.21*sr))/sr;noise=rng.normal(size=len(t));att=np.minimum(1,t/.0015)
 if kind=='pop':x=np.sin(2*np.pi*(180*p*t+780*p*.012*(1-np.exp(-t/.012))))*np.exp(-t*34)*att+.08*noise*np.exp(-t*150)
 elif kind=='snap':x=sosfilt(butter(2,[1200,8500],fs=sr,btype='bandpass',output='sos'),noise)*np.exp(-t*110)*att+.25*np.sin(2*np.pi*410*t)*np.exp(-t*90)
 elif kind=='wood':x=(np.sin(2*np.pi*620*p*t)+.4*np.sin(2*np.pi*1130*p*t))*np.exp(-t*100)*att+.15*noise*np.exp(-t*180)
 else:x=np.sin(2*np.pi*(90*t+3*(1-np.exp(-t*60))))*np.exp(-t*35)*att+.12*noise*np.exp(-t*160)
 return x/(max(abs(x))+1e-9)
for i,c in enumerate(s['clips']):add(sound('thud'),c['output_start'],.35)
selected=[0,1,3,5,7,8,10,11,12,13,14,16,18,19,21]
for j,idx in enumerate(selected):
 if idx>=len(s['captions']):continue
 st,en,_,_=s['captions'][idx];kind=['pop','snap','wood'][j%3];add(sound(kind,.85+.12*(j%4)),st,.34 if kind!='wood' else .30,(-1 if j%2 else 1)*.65)
for k,(title,sub,st,en) in s['cards'].items():
 add(sound('pop',.78 if k=='60-dias' else 1.1),st,.48)
 t=np.arange(int(.22*sr))/sr;add((np.sin(2*np.pi*1175*t)+.2*np.sin(2*np.pi*1762*t))*np.exp(-t*24),st+.03,.12)
for st,en,kind in s['accents']:
 if kind=='red':
  t=np.arange(int(.1*sr))/sr;add(np.sin(2*np.pi*330*t)*np.sin(np.pi*t/.1)**2,st,.22)
# Music stays quiet; slight reduction below active voice. No repeated transition sweep.
rms=np.sqrt(np.convolve(np.mean(v*v,axis=1),np.ones(1200)/1200,mode='same')+1e-9);music*=np.clip(.85-rms*2,.5,.85)[:,None]
fade=np.minimum(np.arange(N)/sr/.05,1)*np.minimum((N-np.arange(N))/sr/.14,1)
for name,a in [('music.wav',music),('effects.wav',fx),('mix-pre.wav',(v*1.03+music+fx)*fade[:,None])]:wavfile.write(R/name,sr,a.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix-pre.wav'),'-af','alimiter=limit=0.87:level=false:latency=true,volume=0.65','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
print('AUDIO DONE',N/sr,flush=True)
