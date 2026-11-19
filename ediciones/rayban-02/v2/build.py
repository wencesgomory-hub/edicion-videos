from pathlib import Path
import json,shutil,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly,sosfilt,butter
r=Path('/workspace/rayban-02-v2');old=Path('/workspace/rayban-02');repo=Path('/workspace/edicion-videos')
for n in ['montaje.json','chapters.json','subtitulos.srt','captions.json']:shutil.copy2(old/n,r/n)
shutil.copytree(old/'fonts',r/'fonts',dirs_exist_ok=True)
s=(old/'subtitulos.ass').read_text().replace(r'\fs110',r'\fs132').replace(r'\fs126',r'\fs142').replace(r'\fs74',r'\fs88').replace(r'\fscx110\fscy110\t(0,120,\fscx100\fscy100)',r'\fscx118\fscy118\t(0,150,\fscx100\fscy100)').replace(r'\move(65,320,90,320,0,150)\fad(25,100)',r'\move(55,320,90,320,0,130)\fad(0,100)\fscx112\fscy112\t(0,160,\fscx100\fscy100)')
(r/'subtitulos.ass').write_text(s)
sr,v=wavfile.read(old/'voz-editada.wav');v=v.astype(float);N=len(v);t=np.arange(N)/sr;D=N/sr
rng=np.random.default_rng(1502)
def bed(name):
 ms,x=wavfile.read(repo/'materiales/audio'/name);x=x.astype(float)
 if x.ndim==1:x=np.column_stack([x,x])
 if ms!=sr:x=resample_poly(x,sr,ms)
 L=min(len(x),round(64*60/142*sr));x=x[:L];x/=np.sqrt(np.mean(x*x))+1e-12
 return x[np.arange(N)%L]
base=bed('musica-base-anuncio-v11.wav');perc=bed('base-percusiva-142.wav');thin=sosfilt(butter(2,350,fs=sr,btype='highpass',output='sos'),base,axis=0);thin/=np.sqrt(np.mean(thin**2))+1e-12
sections=[(0,3.1,0.85,0.3,0,-27.5),(3.1,18.15,1,.2,0,-31.5),(18.15,24.55,0,1,0,-32),(24.55,32.95,0,.55,.55,-33),(32.95,42.1,1,.4,0,-31),(42.1,51.1,.5,.6,0,-32),(51.1,54.85,0,.5,.5,-42),(54.85,62.85,1,.15,0,-31.5),(62.85,72.3,0,1,0,-32),(72.3,79.65,.8,.3,0,-32.5),(79.65,D,1,.35,0,-30.5)]
music=np.zeros_like(v);weight=np.zeros(N)
for a,b,g,p,h,db in sections:
 env=np.clip((t-a+.12)/.24,0,1)*np.clip((b+.12-t)/.24,0,1);x=g*base+p*perc+h*thin;x/=np.sqrt(np.mean(x*x))+1e-12;music+=x*(env*10**(db/20))[:,None];weight+=env
music/=np.maximum(weight,1)[:,None]
fx=np.zeros_like(v);events=[]
def add(x,at,g,name):
 i=round(at*sr)
 if x.ndim==1:x=np.column_stack([x,x])
 n=min(len(x),N-i);fx[i:i+n]+=g*x[:n];events.append({'tiempo':at,'efecto':name,'ganancia':g})
def pop(freq,decay=48,d=.13):
 u=np.arange(round(d*sr))/sr;phase=2*np.pi*(65*u+(freq-65)*.009*(1-np.exp(-u/.009)));return (np.sin(phase)+.28*np.sin(phase*2))*np.exp(-u*decay)*np.minimum(u/.0015,1)
add(pop(270,23,.3),.08,.57,'impacto grave inicial')
add(pop(600,60,.09),.25,.23,'acento seco segunda linea')
add(pop(420,50,.12),.43,.29,'pop tercera linea')
chapters=json.loads((r/'chapters.json').read_text())
for i,(at,n,title,sub) in enumerate(chapters):
 add(pop([540,360,700,440,620,310,490][i],40+i%3*7),at,[.38,.34,.37,.38,.35,.32,.38][i],'pop '+title)
 # brief upper transient lends definition without repeated metallic bells
 u=np.arange(round(.035*sr))/sr;tick=np.sin(2*np.pi*(1800+90*i)*u)*np.exp(-u*150)*np.minimum(u/.001,1);add(tick,at+.008,.045,'ataque '+title)
add(pop(760,60,.09),50.6,.18,'confirmacion FaceID')
add(pop(450,55,.1),82.68,.24,'guardar guia')
for e in events:
 at=e['tiempo'];duck=1-.27*np.exp(-np.maximum(t-at,0)/.14)*(t>=at)*(t<at+.6);music*=duck[:,None]
fade=np.minimum(t/.015,1)*np.minimum((D-t)/.15,1);music*=fade[:,None]
for name,x in [('musica',music),('efectos',fx),('mix',v+music+fx)]:wavfile.write(r/(name+'.wav'),sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.84:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
(r/'sonido.json').write_text(json.dumps({'voz':'StemV1 exacto, a1x, sin nuevos filtros','secciones_musicales':sections,'efectos':events},ensure_ascii=False,indent=2))
p=(old/'render.py').read_text().replace("r=Path('/workspace/rayban-02')","r=Path('/workspace/rayban-02-v2')").replace('revision-v1.mp4','revision-v2.mp4')
p=p.replace('subtitles=filename=',"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.10:t=fill:enable=between(t\\\\,0.43\\\\,0.49),subtitles=filename=")
(r/'render.py').write_text(p)
print('AUDIO Y TITULOS LISTOS',flush=True)
