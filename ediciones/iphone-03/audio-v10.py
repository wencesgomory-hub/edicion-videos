from pathlib import Path
import subprocess,json,types,math
import numpy as np
from scipy.io import wavfile
from PIL import Image,ImageDraw,ImageFont,ImageFilter
R=Path('/workspace/interior-03-v10');old=Path('/workspace/interior-03');repo=Path('/workspace/edicion-videos');sr=48000
cut=32/30;A=2.7;B=A+7.3;D=B+103/30;N=round(D*sr)
# Remove only the dead tail of the hook, leaving its completed phrase and start of movement.
_,v=wavfile.read('/workspace/interior-03-v3/voice-new.wav');v=v[:N].astype(float);v=np.pad(v,(0,max(0,N-len(v))));v=np.column_stack([v,v])
_,m=wavfile.read(repo/'materiales/audio/musica-base-anuncio-v11.wav');m=m[:N].astype(float)*2.9
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
# Reuse the earlier tension accent as a compact live-footage opening.
from scipy.signal import resample
_,intro=wavfile.read('/workspace/ad-v9/tension-intro.wav');intro=intro.astype(float)
if np.max(abs(intro))>2:intro/=32768
intro=resample(intro,round(.30*sr),axis=0);add(intro,0,.60)
# One bright ding backed by a deeper impact; no repeated metallic sequence.
t=np.arange(round(.23*sr))/sr
ding=(np.sin(2*np.pi*1174.66*t)+.30*np.sin(2*np.pi*2349.32*t))*np.exp(-t*29)*np.minimum(1,t/.001)
add(ding,.075,.23)
t=np.arange(round(.30*sr))/sr
low=np.sin(2*np.pi*(43*t+33*.035*(1-np.exp(-t/.035))))*np.exp(-t*20)*np.minimum(1,t/.002)
add(low,.085,.29)
# Firmer percussive bed follows the existing approved 142 BPM rhythm.
BPM=142;beat=60/BPM
for k in range(int(D/beat)+1):
 t=np.arange(round(.17*sr))/sr
 pulse=np.sin(2*np.pi*(49*t+70*.022*(1-np.exp(-t/.022))))*np.exp(-t*30)*.041
 if k%2:
  noise=sosfilt(butter(2,[900,6500],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(t)))
  pulse+=noise*np.exp(-t*65)*.012
 i=round(k*beat*sr);e=min(N,i+len(t))
 if e>i:m[i:e]+=pulse[:e-i,None]
# User requested exactly 10% less music amplitude; voice and effects are untouched.
previous_music=m.copy()
m*=0.90
assert np.max(abs(m-previous_music*.90))<1e-12
fade=np.minimum(np.arange(N)/sr/.025,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('music-before.wav',previous_music),('music.wav',m),('voice.wav',v),('effects.wav',fx)]:wavfile.write(R/name,sr,x.astype(np.float32))
old_mix=wavfile.read('/workspace/interior-03-v9/mix.wav')[1]
assert np.max(abs((v+previous_music+fx)*fade[:,None]-old_mix))<2e-7,'Preserve previous voice and effects'
(R/'verificacion-musica.json').write_text(json.dumps({'factor_amplitud':0.90,'reduccion_porcentaje':10,'cambio_dB':float(20*np.log10(.9)),'voz_y_fx_sin_modificar':True},indent=2))
wavfile.write(R/'mix.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
