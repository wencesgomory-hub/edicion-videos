from pathlib import Path
import numpy as np,json,subprocess
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
R=Path('/workspace/seminuevos-01-v8');s=json.loads((R/'edit.json').read_text());sr=48000;N=round(s['duration']*sr);rng=np.random.default_rng(6120);B=.5
_,v=wavfile.read('/workspace/seminuevos-01-v4/voice.wav');v=np.concatenate([v[:round(6.4*sr)],v[round(6.6*sr):]])[:N].astype(float)
v=np.concatenate([v[:round((745/30)*sr)],np.zeros(round((.9)*sr)),v[round((745/30)*sr):]])[:N]
if v.ndim==1:v=np.column_stack([v,v])
m=np.zeros((N,2));fx=np.zeros_like(m);events=[]
def add(buf,x,at,g,pan=0):
 i=round(at*sr)
 if i<0:x=x[-i:];i=0
 e=min(N,i+len(x))
 if e>i:buf[i:e,0]+=x[:e-i]*g*(1-pan*.15);buf[i:e,1]+=x[:e-i]*g*(1+pan*.15)
def filt(x,lo,hi):return sosfilt(butter(2,[lo,hi],fs=sr,btype='bandpass',output='sos'),x)
def kick():
 t=np.arange(round(.24*sr))/sr;return np.sin(2*np.pi*(49*t+70*.02*(1-np.exp(-t/.02))))*np.exp(-t*25)+.10*rng.normal(size=len(t))*np.exp(-t*200)
def clap():
 t=np.arange(round(.15*sr))/sr;return filt(rng.normal(size=len(t)),850,6500)*np.exp(-t*47)+.28*np.sin(2*np.pi*185*t)*np.exp(-t*43)
roots=[45,45,41,43];chords=[[57,60,64],[57,60,64],[53,57,60],[55,59,62]]
for bar in range(16):
 at=bar*4*B
 for q in [0,1.5,2,3.25]:
  for pan in [-.1,.1]:add(m,kick(),at+q*B,.21,pan)
 for q in [1,3]:add(m,clap(),at+q*B,.11)
 for h in range(8):
  t=np.arange(round(.05*sr))/sr;hat=filt(rng.normal(size=len(t)),5800,10500)*np.exp(-t*100);add(m,hat,at+h*B/2+(.016 if h%2 else 0),.027 if h%2 else .018,(-1 if h%2 else 1))
 for q,semitone in [(0,0),(.75,0),(1.5,12),(2,0),(2.75,0),(3.5,7)]:
  t=np.arange(round(.24*sr))/sr;f=440*2**((roots[bar%4]-12+semitone-69)/12);bass=(np.sin(2*np.pi*f*t)+.36*np.sin(4*np.pi*f*t)+.16*np.sin(6*np.pi*f*t))*np.minimum(1,t/.008)*np.exp(-t*12);add(m,bass,at+q*B,.22)
 # Low soft chord body; no bell, arpeggio, metallic stab or bright repeated note.
 t=np.arange(round(.78*sr))/sr;env=np.minimum(1,t/.06)*np.exp(-t*4)
 chord=sum(np.sin(2*np.pi*(440*2**((note-69)/12))*t) for note in chords[bar%4])/3*env
 add(m,chord,at+.25*B,.035,-.3);add(m,chord,at+2.25*B,.03,.3)
m*=10**(-28.8/20)/(np.sqrt(np.mean(m*m))+1e-12)
env=np.sqrt(np.convolve(np.mean(v*v,axis=1),np.ones(1800)/1800,mode='same')+1e-9);m*=np.clip(.95-env*2,.65,.95)[:,None]
def hit(kind):
 t=np.arange(round(.18*sr))/sr;attack=np.minimum(1,t/.0015)
 if kind.startswith('pop'):
  pitch={'pop':1.,'pop-high':1.18,'pop-low':.83}.get(kind,1.);x=np.sin(2*np.pi*(180*pitch*t+650*pitch*.012*(1-np.exp(-t/.012))))*np.exp(-t*35)*attack
 elif kind=='click':x=filt(rng.normal(size=len(t)),900,6500)*np.exp(-t*145)*attack
 else:x=np.sin(2*np.pi*(55*t+70*.016*(1-np.exp(-t/.016))))*np.exp(-t*27)*attack+.15*filt(rng.normal(size=len(t)),700,4500)*np.exp(-t*110)
 return x/(max(abs(x))+1e-12)
def effect(at,kind,g):add(fx,hit(kind),at,g);events.append(dict(at=at,kind=kind,gain=g))
effect(.07,'pop',.25)
price=s['precio_dolar']['inicio'];t=np.arange(round(.20*sr))/sr;cash=(np.sin(2*np.pi*1568*t)+.22*np.sin(2*np.pi*2093*t))*np.exp(-t*29);add(fx,cash,price,.21);events.append(dict(at=price,kind='cash',gain=.21))
first=7.30;effect(first,'pop',.46)
second=next(c[0] for c in s['captions'] if c[3]=='SEMINUEVOS');effect(second,'pop-low',.42) # One accent when the box is visibly raised, not before the demonstration.
# Dry broadband plops: no pitched oscillator or beep.
pop_rng=np.random.default_rng(8020)
for j,(name,label,at) in enumerate(s['accessories']):
 t=np.arange(round(.105*sr))/sr
 noise=pop_rng.normal(size=len(t))
 body=filt(noise,120+j*55,1650+j*500)
 air=filt(noise,1800,7000)*.20
 x=(body+air)*np.minimum(1,t/.0007)*np.exp(-t*(55+j*8))
 x/=max(abs(x))+1e-12
 add(fx,x,at,.55);events.append(dict(at=at,kind='pop-seco-'+name,gain=.55))
red=next(c[0] for c in s['accents'] if c[2]=='red');effect(red,'impact',.35)
for key,c in s['cards'].items():effect(c[2],'pop' if key=='sellados' else 'impact',.37)
st=s['cards']['60-dias'][2];t=np.arange(round(.25*sr))/sr;brush=filt(rng.normal(size=len(t)),1200,5000)*np.sin(np.pi*t/.25)**2;brush/=max(abs(brush));add(fx,brush,st,.045)
cta=next(c[0] for c in s['captions'] if c[3]=='MENSAJE');effect(cta,'click',.35)
assert sum(6.4<=e['at']<9.1 for e in events)==2,'Solo dos acentos diferentes al mostrar los equipos.'
# Original recording of boxes falling/caught, not a replacement hit.
subprocess.run(['ffmpeg','-v','error','-y','-ss','2.0','-t','0.9','-i','/workspace/edicion-videos/IMG_6242.MOV','-vn','-ac','1','-ar','48000','-af','highpass=f=110,afade=t=in:d=0.008,afade=t=out:st=0.82:d=0.08','-c:a','pcm_f32le',str(R/'cajas-original.wav')],check=True)
_,original=wavfile.read(R/'cajas-original.wav')
add(fx,original,745/30,1.0);events.append(dict(at=745/30,kind='cajas-audio-original',gain=1.0))
fade=np.minimum(np.arange(N)/sr/.07,1)*np.minimum((N-np.arange(N))/sr/.16,1)
for name,x in [('music.wav',m*fade[:,None]),('effects.wav',fx),('mix.wav',(v*1.03*.65+m+fx)*fade[:,None])]:wavfile.write(R/name,sr,x.astype(np.float32))
(R/'eventos-sonido.json').write_text(json.dumps(events,indent=2)+'\n')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.80:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True);print('AUDIO DONE: pops restaurados, dos acentos en equipos, música +1.5 dB, cajas completas.',flush=True)
