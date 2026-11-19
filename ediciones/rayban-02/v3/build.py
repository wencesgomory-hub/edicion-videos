from pathlib import Path
import shutil,json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
from PIL import ImageFont
r=Path('/workspace/rayban-02-v3');old=Path('/workspace/rayban-02-v2');repo=Path('/workspace/edicion-videos')
for n in ['montaje.json','chapters.json','subtitulos.srt','captions.json']:shutil.copy2(old/n,r/n)
shutil.copytree(old/'fonts',r/'fonts',dirs_exist_ok=True)
chapters=json.loads((r/'chapters.json').read_text())
s=(old/'subtitulos.ass').read_text();lines=s.splitlines();lines=[l for l in lines if not(l.startswith('Dialogue: 2,') and (',Chapter,' in l and (' / ' in l or '\\pos(90,400)' in l)))]
def ts(t):
 n=round(t*100);m,n=divmod(n,6000);sec,n=divmod(n,100);return f'0:{m:02}:{sec:02}.{n:02}'
def ev(a,b,tx,tags,style='Title'):
 lines.append(f'Dialogue: 3,{ts(a)},{ts(b)},{style},,0,0,0,,'+tags+tx)
for i,(a,n,title,sub) in enumerate(chapters):
 end=a+2.65;font='GomoryMontserratItalic' if i%2==0 else 'GomoryMontserrat';col='7DEAA1' if title=='GARANTÍA' else '59DAFF' if title in ['LINTERNA','BATERÍA Y CICLOS'] else 'FAFFFF'
 labels=[title]
 if title=='HISTORIAL DE PIEZAS':labels=['HISTORIAL','DE PIEZAS']
 if title=='BATERÍA Y CICLOS':labels=['BATERÍA','Y CICLOS']
 size=126 if len(labels)==1 else 112
 for j,tx in enumerate(labels):
  f=ImageFont.truetype(str(r/'fonts'/(font+'.ttf')),size);sz=min(size,round(size*850/max(1,f.getlength(tx))))
  y=640+j*115 if len(labels)==2 else 680
  if i%3==0:entry=f'\\move(440,{y},540,{y},0,180)\\fscx106\\fscy106\\t(0,180,\\fscx100\\fscy100)'
  elif i%3==1:entry=f'\\pos(540,{y})\\fscx82\\fscy82\\t(0,130,\\fscx105\\fscy105)\\t(130,240,\\fscx100\\fscy100)'
  else:entry=f'\\move(540,{y+55},540,{y},0,180)\\blur2\\t(0,160,\\blur0)'
  ev(a+j*.07,end,tx,'{'+entry+f'\\fn{font}\\fs{sz}\\c&H{col}&\\bord2.5\\shad3\\fad(0,140)'+'}')
 ev(a,end,'PASO '+n+' / REVISIÓN',r'{\pos(540,515)\fs36\fnGomoryMontserrat\c&HEAEAEA&\fad(25,100)}')
 ev(a+.13,end,sub,r'{\pos(540,855)\fs39\fnGomoryMontserrat\c&HFAFFFF&\fad(50,120)}')
 # Clean gold rule, not a large opaque card.
 ev(a+.05,end,r'{\p1}m 0 0 l 140 0 l 140 5 l 0 5{\p0}',r'{\an7\pos(470,910)\bord0\shad0\c&H59DAFF&\fad(60,120)}')
(r/'subtitulos.ass').write_text('\n'.join(lines)+'\n')
sr,v=wavfile.read('/workspace/rayban-02/voz-editada.wav');v=v.astype(float);N=len(v);t=np.arange(N)/sr;D=N/sr
rng=np.random.default_rng(1503);bed=np.zeros_like(v);fx=np.zeros_like(v)
def add(dst,x,at,g):
 i=round(at*sr)
 if i<0 or i>=N:return
 if x.ndim==1:x=np.column_stack([x,x])
 k=min(len(x),N-i);dst[i:i+k]+=x[:k]*g
beat=60/136
# New original instrumental: dry drums, syncopated bass, no lounge melody/chords.
for k in range(int(D/beat)+1):
 at=k*beat;bar=k//4
 u=np.arange(round(.19*sr))/sr;p=2*np.pi*(49*u+70*.012*(1-np.exp(-u/.012)));kick=(np.sin(p)+.18*np.sin(2*p))*np.exp(-u*30)*np.minimum(u/.0015,1)
 if k%4 in [0,2] or (bar%4==3 and k%4==3):add(bed,kick,at,.58)
 if k%4 in [1,3]:
  u=np.arange(round(.095*sr))/sr;noise=rng.normal(size=len(u));noise=sosfilt(butter(2,[950,6500],fs=sr,btype='bandpass',output='sos'),noise);snare=(.32*np.sin(2*np.pi*180*u)+.32*noise)*np.exp(-u*65)*np.minimum(u/.001,1);add(bed,snare,at,.55)
 if k%2==0 or bar%4==2:
  root=[55,55,65.406,49][bar%4];u=np.arange(round(.28*sr))/sr;bass=(np.sin(2*np.pi*root*u)+.28*np.sin(4*np.pi*root*u))*np.minimum(u/.008,1)*np.exp(-u*10);add(bed,bass,at+(.5*beat if k%4==2 else 0),.24)
 # Short closed percussion taps only; no continuous hiss/shaker.
 if bar%4 in [1,3]:
  u=np.arange(round(.025*sr))/sr;tap=np.sin(2*np.pi*2800*u)*np.exp(-u*200)*np.minimum(u/.001,1);add(bed,tap,at+.5*beat,.09)
bed/=np.sqrt(np.mean(bed**2))+1e-12
level=np.full(N,10**(-32.5/20));level[t<3.1]=10**(-28/20);level[(t>=51.1)&(t<54.85)]=10**(-44/20);level[t>=79.65]=10**(-31/20)
# Brief musical breaks before several new checks, then the rhythm returns.
for a in [18.25,24.55,32.95,42.26,57.03]:
 level[(t>=a-.14)&(t<a+.08)]*=.30
music=bed*level[:,None];music*=np.minimum(t/.015,1)[:,None]*np.minimum((D-t)/.18,1)[:,None]
events=[]
def hit(x,at,g,name):add(fx,x,at,g);events.append([at,name,g])
def pop(f=520):
 u=np.arange(round(.14*sr))/sr;p=2*np.pi*(80*u+(f-80)*.008*(1-np.exp(-u/.008)));return (np.sin(p)+.3*np.sin(2*p))*np.exp(-u*43)*np.minimum(u/.0015,1)
u=np.arange(round(.42*sr))/sr;p=2*np.pi*(43*u+25*.028*(1-np.exp(-u/.028)));deep=(np.sin(p)+.48*np.sin(2*p)+.22*np.sin(3*p))*np.exp(-u*13)*np.minimum(u/.003,1);hit(deep,.08,.58,'impacto profundo43Hz y armonicos')
hit(pop(340),.25,.18,'golpe breve texto');hit(pop(600),.43,.24,'pop cierre gancho')
for i,(a,n,title,sub) in enumerate(chapters):
 if i%4==0:x=pop(540);kind='pop seco'
 elif i%4==1:
  u=np.arange(round(.16*sr))/sr;x=(np.sin(2*np.pi*740*u)+.2*np.sin(2*np.pi*1110*u))*np.exp(-u*36)*np.minimum(u/.002,1);kind='blink tonal corto'
 elif i%4==2:
  u=np.arange(round(.065*sr))/sr;x=(np.sin(2*np.pi*1250*u)+.35*np.sin(2*np.pi*2300*u))*np.exp(-u*95)*np.minimum(u/.001,1);kind='tack seco'
 else:
  u=np.arange(round(.23*sr))/sr;x=(np.sin(2*np.pi*990*u)+.25*np.sin(2*np.pi*1485*u))*np.exp(-u*24)*np.minimum(u/.002,1);kind='cling corto'
 hit(x,a,[.39,.30,.34,.25,.37,.29,.33][i],kind+' / '+title)
hit(pop(630),50.6,.15,'confirmacion FaceID');hit(pop(430),82.68,.23,'guardar guia')
for name,x in [('musica',music),('efectos',fx),('mix',v+music+fx)]:wavfile.write(r/(name+'.wav'),sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.84:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
(r/'sonido.json').write_text(json.dumps({'musica':'Composicion nueva original136BPM, bateria seca y bajo sincopado; sin stemsV11/V2','voz':'StemV1 exacto antes del limitador; natural1x','eventos':events},ensure_ascii=False,indent=2))
p=(old/'render.py').read_text().replace('rayban-02-v2','rayban-02-v3').replace('revision-v2.mp4','revision-v3.mp4');(r/'render.py').write_text(p)
print('BUILD V3 LISTO',flush=True)
