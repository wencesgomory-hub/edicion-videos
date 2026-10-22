from pathlib import Path
from scipy.io import wavfile
import numpy as np,subprocess,json
r=Path('/workspace/iphone-06-v5');sr,v=wavfile.read('/workspace/iphone-06-v3/voice.wav');_,m=wavfile.read('/workspace/iphone-06-v3/music.wav');_,fx=wavfile.read('/workspace/iphone-06-v4/effects-new.wav');v=v.astype(float);m=m.astype(float);fx=fx.astype(float);N=len(v);fx[:round(.70*sr)]=0;events=[]
for at,freq,g in [(.025,2450,.34),(.18,1820,.30),(.33,2450,.34),(.48,1820,.28)]:
 u=np.arange(round(.035*sr))/sr;x=(np.sin(2*np.pi*freq*u)+.32*np.sin(2*np.pi*freq*1.47*u))*np.exp(-u*175)*np.minimum(1,u/.0005);i=round(at*sr);fx[i:i+len(x)]+=x[:,None]*g;events.append([at,'reloj',g])
u=np.arange(round(.18*sr))/sr;ph=2*np.pi*(88*u+46*.01*(1-np.exp(-u/.01)));hit=(np.sin(ph)+.46*np.sin(2*ph)+.26*np.sin(4*ph))*np.exp(-u*29)*np.minimum(1,u/.0012);i=round(.10*sr);fx[i:i+len(hit)]+=hit[:,None]*.68
u=np.arange(round(.17*sr))/sr;ding=(np.sin(2*np.pi*1396.91*u)+.25*np.sin(2*np.pi*2095.36*u))*np.exp(-u*30)*np.minimum(1,u/.002);i=round(15.52*sr);n=min(len(ding),N-i);fx[i:i+n]+=ding[:n,None]*.28;events.append([15.52,'ding tilde',.28])
fade=np.minimum(np.arange(N)/sr/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1);wavfile.write(r/'effects-new.wav',sr,fx.astype(np.float32));wavfile.write(r/'mix-new.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix-new.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master-new.wav')],check=True)
(r/'audio-cambios.json').write_text(json.dumps({'voz_musica':'Conservadas','tecleo':'Conservado V4','cambios':'Intro tic-tac más presente y golpe con armónicos, ding final15.52s','eventos':events},ensure_ascii=False,indent=2))
