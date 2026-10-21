from pathlib import Path
import subprocess,json,types,math
import numpy as np
from scipy.io import wavfile
from PIL import Image,ImageDraw,ImageFont,ImageFilter
R=Path('/workspace/interior-03-v6');old=Path('/workspace/interior-03');repo=Path('/workspace/edicion-videos');sr=48000
cut=32/30;A=2.7;B=A+7.3;D=B+103/30;N=round(D*sr)
# Remove only the dead tail of the hook, leaving its completed phrase and start of movement.
_,v=wavfile.read('/workspace/interior-03-v3/voice-new.wav');v=v[:N].astype(float);v=np.pad(v,(0,max(0,N-len(v))));v=np.column_stack([v,v])
_,m=wavfile.read(repo/'materiales/audio/musica-base-anuncio-v11.wav');m=m[:N].astype(float)*2.35
_,bank=wavfile.read(repo/'materiales/audio/efectos-aislados-anuncio-v11.wav');fx=np.zeros((N,2));refs={'thud':7.67/1.12,'snap':8.48/1.12,'wood':15.2/1.12,'bubble':16.7/1.12};ev=[]
def add(x,t,g):
 i=round(t*sr)
 if i<0:x=x[-i:];i=0
 e=min(N,i+len(x));x=x[:e-i]*g
 if x.ndim==1:x=x[:,None]
 if e>i:fx[i:e]+=x

def accent(t,kind,g):
 i=round(refs[kind]*sr);x=bank[i:i+round(.18*sr)].astype(float);x/=max(np.max(abs(x)),1e-9);add(x,t,g);ev.append([t,kind,g])
for t,k,g in [(.09,'thud',.58),(1.65,'snap',.36),(A,'thud',.48),(A+1.05,'snap',.39),(A+2.10,'wood',.48),(A+3.38,'snap',.44),(A+4.32,'thud',.48),(A+5.05,'bubble',.64),(A+6.10,'snap',.35),(B,'thud',.43),(B+.82,'snap',.47)]:accent(t,k,g)
accent(A+5.27,'snap',.62)
accent(A+5.50,'wood',.58)
# Actual air transition already used in the approved earlier ad.
_,air=wavfile.read('/workspace/ad-v9/fx.wav');air=air.astype(float)
if np.max(abs(air))>2:air/=32768
start=round((1.05/1.12-.12)*sr);whoosh=air[start:start+round(.18*sr)];whoosh/=max(np.max(abs(whoosh)),1e-9)
for t in [A,B]:add(whoosh,t-.12,.19)
# A short air sweep and low hit follow the entering beam of light.
from scipy.signal import butter,sosfilt
rng=np.random.default_rng(505)
t=np.arange(round(.20*sr))/sr
sw=sosfilt(butter(2,[700,8000],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(t)))*np.sin(np.pi*t/.20)**2
sw/=max(abs(sw));add(sw,0,.22)
add(sw,A+4.32-.10,.14)
add(sw,B-.10,.14)
# One positive check accent, no repeating run of metallic dings.
t=np.arange(round(.13*sr))/sr
check=(np.sin(2*np.pi*880*t)+.35*np.sin(2*np.pi*1320*t))*np.exp(-t*43)*np.minimum(1,t/.002)
add(check,A+5.32,.16)
fade=np.minimum(np.arange(N)/sr/.025,1)*np.minimum((N-np.arange(N))/sr/.12,1)
wavfile.write(R/'mix.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
