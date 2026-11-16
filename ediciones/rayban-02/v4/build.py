from pathlib import Path
import shutil,json,subprocess
from PIL import ImageFont
from scipy.io import wavfile
import numpy as np
r=Path('/workspace/rayban-02-v4');old=Path('/workspace/rayban-02-v3');repo=Path('/workspace/edicion-videos')
for n in ['montaje.json','subtitulos.srt']:shutil.copy2(old/n,r/n)
shutil.copytree(old/'fonts',r/'fonts',dirs_exist_ok=True)
s=(old/'subtitulos.ass').read_text();lines=[l for l in s.splitlines() if 'ENTREGA REAL · MAR DEL PLATA' not in l]
tx='MAR DEL PLATA';f=ImageFont.truetype(str(r/'fonts/GomoryMontserrat.ttf'),76);x=round((1080-f.getlength(tx))/2)
def ts(t):
 n=round(t*100);m,n=divmod(n,6000);sec,n=divmod(n,100);return f'0:{m:02}:{sec:02}.{n:02}'
starts=[3.2+i*.065 for i in range(len(tx))]
for i,a in enumerate(starts):
 b=starts[i+1] if i+1<len(starts) else 6.8
 lines.append(f'Dialogue: 4,{ts(a)},{ts(b)},Chapter,,0,0,0,,'+r'{\an7\pos('+str(x)+r',195)\fnGomoryMontserrat\fs76\c&H3322F0&\bord2.5\shad2}'+tx[:i+1])
(r/'subtitulos.ass').write_text('\n'.join(lines)+'\n')
sr,a=wavfile.read(old/'master.wav');a=a.astype(float);fx=np.zeros_like(a);rng=np.random.default_rng(1604)
for ch,at in zip(tx,starts):
 if ch==' ':continue
 u=np.arange(round(.027*sr))/sr
 noise=rng.normal(size=len(u));tick=(.42*noise+.32*np.sin(2*np.pi*760*u))*np.exp(-u*180)*np.minimum(1,u/.0006)
 i=round(at*sr);fx[i:i+len(u)]+=(tick*.12)[:,None]
wavfile.write(r/'tecleo.wav',sr,fx.astype(np.float32));wavfile.write(r/'mix.wav',sr,(a+fx).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
p=(old/'render.py').read_text().replace('rayban-02-v3','rayban-02-v4').replace('revision-v3.mp4','revision-v4.mp4');(r/'render.py').write_text(p)
(r/'cambio.json').write_text(json.dumps({'texto':tx,'color':'rojo RGB240/34/51','posicion':[x,195],'tamano':76,'inicio':3.2,'fin':6.8,'entrada':'letra por letra cada65ms, sonido en caracteres no espacios','base':'V3 completa, conservada'},ensure_ascii=False,indent=2))
