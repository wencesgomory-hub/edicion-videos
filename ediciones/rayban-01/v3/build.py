from pathlib import Path
import json, shutil, subprocess
import numpy as np
from scipy.io import wavfile
from PIL import Image,ImageDraw,ImageFont,ImageFilter
r=Path('/workspace/rayban-01-v3'); old=Path('/workspace/rayban-01-v2')
shutil.copytree(old/'fonts',r/'fonts',dirs_exist_ok=True)
# Phrase starts and ends reviewed against independent Spanish CTC token timestamps.
rows=[(0,2.15,'Tiene una rayita acá...'),(2.15,3,'¿Eh?'),(3,4.9,'Esta rayita...'),(4.9,6,'¿Cuál?'),(15.05,16.6,'¿Esto es cámara?'),(17.4,18.95,'Un desastre cómo contestan...'),(19.4,19.95,'Vos...'),(20.48,21.65,'Te contestan muy crudo...'),(21.92,22.95,'Que te contestan...'),(23.2,24.85,'Y no tienen un proceso claro.'),(25,25.65,'Claro.'),(26,27.85,'Cuando me mandaste para reservarlo...'),(28,30.55,'Sí, sí, sí.'),(31.55,32.65,'Tratamos de manejar...'),(32.8,34.3,'Sí, el tema es que...'),(36.48,38.15,'La cámara, fijate que...'),(38.96,40.65,'Es una locura'),(40.72,43.4,'lo que la cámara está haciendo.'),(44.8,46.05,'Y la batería también'),(46.05,46.95,'dura una locura.'),(47.2,48.35,'Al ser Max, también'),(48.35,49.7,'dura un montonazo.'),(52.9,54.35,'Acá arriba.'),(54.8,56.55,'Y ahí va.'),(56.8,58.7,'Cualquier cosa de la configuración'),(58.72,59.5,'o lo que sea,'),(59.68,61.1,'que te trabes o algo,'),(61.2,62.35,'me mandás un mensajito.'),(62.64,63.7,'Eso no pasa nada.'),(63.84,64.8,'Te lo dejo acá.'),(64.88,66.1,'Si querés, metelo acá adentro.'),(67.28,68.1,'La bolsita.'),(68.24,69.7,'Te guardo acá la garantía.'),(71.92,74,'La fundita.'),(75.12,76,'Ahí entró.'),(79.2,80.1,'Bueno, señor.'),(80.24,80.95,'Un gustazo.'),(81.12,81.75,'Nos estamos viendo.'),(81.76,83.1,'Y cualquier cosita me decís.'),(83.2,84.473,'Dale, dale.')]
# Reuse approved typography, replacing timing data instead of proportionally splitting sentences.
src=(old/'captions.py').read_text();src=src[src.index('def stamp'):];src=src[:src.index('ass=[];srt=[]')]+src[src.index('ass=[];srt=[]'):]
events=[dict(inicio=a,fin=b,texto=t) for a,b,t in rows]
exec(src,globals())
(r/'captions.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
# Compact hook lower in frame: leave client's face unobscured. Keep product visible after 3s.
for name,tx,size,y,col in [('titulo','CASI PIERDO',108,1070,(255,255,250,255)),('venta','ESTA VENTA',108,1190,(255,255,250,255)),('error','POR ESTE ERROR EN LA CÁMARA',46,1320,(245,24,35,255))]:
 f=ImageFont.truetype(str(r/'fonts/GomoryMontserrat.ttf'),size);im=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(im);w=d.textlength(tx,font=f);d.text(((1080-w)/2,y),tx,font=f,fill=col,stroke_width=3,stroke_fill=(0,0,0,225));im.save(r/(name+'.png'))
# No continuous synthetic drone; one clean impact and brief camera-like click, then original conversation.
sr,v=wavfile.read(r/'voice.wav');v=v.astype(float);fx=np.zeros_like(v)
def add(x,at,g):
 if x.ndim==1:x=np.column_stack([x,x])
 i=round(at*sr);n=min(len(x),len(fx)-i);fx[i:i+n]+=x[:n]*g
u=np.arange(round(.22*sr))/sr
p=2*np.pi*(65*u+55*.014*(1-np.exp(-u/.014)))
x=(np.sin(p)+.28*np.sin(2*p))*np.exp(-u*23)*np.minimum(u/.002,1)
add(x,.10,.45);add(x,5.5,.18)
# Short dry click, no rustling or sustained background effect.
u=np.arange(round(.035*sr))/sr;add(np.sin(2*np.pi*1400*u)*np.exp(-u*160),.34,.075)
wavfile.write(r/'effects.wav',sr,fx.astype(np.float32));wavfile.write(r/'mix.wav',sr,(v+fx).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
