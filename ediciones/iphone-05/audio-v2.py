from pathlib import Path
from scipy.io import wavfile
import numpy as np,json,subprocess
R=Path('/workspace/iphone-05-v2');old=Path('/workspace/iphone-05');sr,v=wavfile.read(old/'voice.wav');v=v.astype(float)[:round(35.016667*sr)];N=len(v);t=np.arange(N)/sr
# Focused opening lift, smooth return to accepted level; no pitch/tempo processing.
g=1+(10**(3/20)-1)*np.clip((4.1-t)/.7,0,1);v*=g
v=np.column_stack([v,v]);_,m=wavfile.read(old/'music.wav');m=m.astype(float);m*= (1-(1-10**(-2/20))*np.clip((3.6-t)/.5,0,1))[:,None]
_,fx=wavfile.read(old/'effects.wav');fx=fx.astype(float)*10**(1/20);fx[round(25.4*sr):]=0
_,bank=wavfile.read('/workspace/edicion-videos/materiales/audio/efectos-aislados-anuncio-v11.wav');refs={'thud':7.67/1.12,'snap':8.48/1.12,'wood':15.2/1.12,'bubble':16.7/1.12};events=[]
def put(x,at,g):
 if x.ndim==1:x=np.column_stack([x,x])
 i=round(at*sr);n=min(len(x),N-i)
 if n>0:fx[i:i+n]+=x[:n]*g

def effect(at,kind,g):
 i=round(refs[kind]*sr);x=bank[i:i+round(.16*sr)].astype(float);x/=np.max(abs(x))+1e-12;put(x,at,g);events.append([at,kind,g])
for at,k,g in [(2.45,'thud',.44),(5.08,'bubble',.39),(5.28,'wood',.28),(27.45,'wood',.38),(30.7,'snap',.40),(31.3,'thud',.56),(32.18,'bubble',.54),(32.62,'wood',.39),(33.25,'snap',.55),(34.3,'bubble',.43)]:effect(at,k,g)
fade=np.minimum(t/.012,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('voice.wav',v),('music.wav',m),('effects.wav',fx),('mix.wav',(v+m+fx)*fade[:,None])]:wavfile.write(R/name,sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
(R/'audio-cambios.json').write_text(json.dumps({'voz_inicial_db':3,'rampa_voz_s': [3.4,4.1],'musica_intro_db':-2,'musica_resto':'igual V1','efectos_db':1,'eventos':events,'cierre':'FX previos desde25.4s retirados y sustituidos por entradas realineadas','velocidad':1},ensure_ascii=False,indent=2))
