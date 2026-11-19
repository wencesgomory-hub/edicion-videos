from pathlib import Path
import json,re,shutil,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
r=Path('/workspace/rayban-02');repo=Path('/workspace/edicion-videos')
shutil.copytree(repo/'ediciones/rayban-01/v2/fonts',r/'fonts',dirs_exist_ok=True)
edl=[(0,18.15),(22.4,46.35),(52.4,61.4),(65.7,69.45),(71.9,79.9),(85.5,94.95),(95.2,102.55),(140,148.033333)]
clips=[];D=0
for a,b in edl:clips.append(dict(inicio_original=a,fin_original=b,inicio_montaje=round(D,6),duracion=round(b-a,6)));D+=b-a
(r/'montaje.json').write_text(json.dumps(dict(fuente='D8EB53EA-49A5-4D79-A8AD-B5872C04D7D1.mov',duracion_original=148.033333,duracion_montaje=D,velocidad=1,clips=clips),ensure_ascii=False,indent=2))
def remap(t):
 for c in clips:
  if c['inicio_original']<=t<c['fin_original']:return c['inicio_montaje']+t-c['inicio_original']
 return None
# Actual phrase times, checked against CTC word onsets and independent Whisper text.
rows=[(1.35,2.7,'Acá, en la cámara.'),(2.88,4.7,'El 1, el 0,5 también.'),(4.8,5.7,'Perfecto.'),(6,7.45,'No tiene manchitas, nada.'),(7.6,9.9,'La cámara, el zoom...'),(11.04,12.45,'Todo el enfoque, perfecto.'),(12.64,14.5,'Tiene muy buen zoom.'),(14.72,16.25,'Modo selfie también.'),(16.4,18.1,'Perfecto, nada.'),(22.56,24.8,'La linterna también, perfecto.'),(25.2,27.6,'También acá, en general,'),(27.6,28.7,'en información.'),(28.8,30.05,'Si acá no te salta nada'),(30.08,31.6,'de piezas e historial de servicios,'),(31.68,33.65,'quiere decir que no hay nada reemplazado,'),(33.76,35.6,'salvo la batería, que ya lo habíamos hablado.'),(36.24,36.95,'Esto acá.'),(37.2,39.35,'Batería: condición 100%.'),(39.44,40.7,'La anterior batería tenía'),(40.72,42.1,'1414 ciclos.'),(42.24,42.8,'Se reemplazó.'),(42.88,44.3,'Ahora empieza a guardar los ciclos.'),(44.48,46.35,'Después acá tenés el Face ID.'),(52.56,53.9,'También ves esto'),(53.92,55.6,'para que veas que funciona todo perfecto.'),(56.24,57.5,'Ya te empieza a tomar la cara'),(57.52,59.25,'y después vas a desbloquear'),(59.28,61.2,'todas las aplicaciones con la cara.'),(66.48,67.25,'Hola, hola.'),(67.36,68.2,'Hola, hola.'),(68.24,69.2,'Hola, hola.'),(72.8,73.8,'Todo perfecto.'),(74.08,75.4,'Yo voy a estarle sacando fotos.'),(75.52,76.4,'Yo me quedo la digital'),(76.48,77.55,'y vos te llevás la física.'),(77.6,79.7,'Por si hay alguna validación, lo que fuere.'),(85.76,87.65,'La funda.'),(87.92,89.8,'El cablecito, el cargador...'),(89.92,91.55,'Si te llega a fallar alguno,'),(91.6,92.25,'tenés garantía.'),(92.32,93.5,'Como el celu, no pasa nada.'),(93.6,94.95,'No hay problema, mandá un mensajito.'),(95.28,97.8,'Si te llegás a trabar en la configuración'),(97.92,99.55,'o lo que fuera, lo que sea,'),(99.68,100.8,'mandá mensaje, no pasa nada.'),(100.88,102.55,'Te doy una mano, no te preocupes.'),(140,141.35,'Ahí estaríamos, querido.'),(141.6,143.1,'Bueno, un gustazo.'),(143.28,144.95,'Cualquier cosita me avisás'),(145.36,147.5,'y lo vemos. No hay problema.')]
events=[]
for a,b,tx in rows:
 for c in clips:
  lo=max(a,c['inicio_original']);hi=min(b,c['fin_original'])
  if hi-lo>.12:events.append({'inicio':round(c['inicio_montaje']+lo-c['inicio_original'],3),'fin':round(c['inicio_montaje']+hi-c['inicio_original'],3),'texto':tx,'original':[a,b]})
def ts(t,ass=False):
 n=round(t*(100 if ass else 1000));h,n=divmod(n,(360000 if ass else 3600000));m,n=divmod(n,(6000 if ass else 60000));s,n=divmod(n,(100 if ass else 1000));return f'{h}:{m:02}:{s:02}.{n:02}' if ass else f'{h:02}:{m:02}:{s:02},{n:03}'
def wrap(tx):
 words=tx.split()
 if len(tx)>31:
  mid=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))));words.insert(mid,r'\N')
 out=[]
 for w in words:
  clean=w.lower().strip('¿?¡!.,;:')
  col='7DEAA1' if clean in ['garantía','perfecto','ayuda'] else '59DAFF' if clean in ['cámara','cámaras','batería','ciclos','100%','1414','selfie','enfoque','zoom','digital','física'] else None
  out.append(r'{\c&H'+col+r'&}'+w+r'{\c&HFAFFFF&}' if col else w)
 return ' '.join(out)
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Base,GomoryMontserrat,68,&H00FAFFFF,&H0059DAFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.2,2,2,110,110,350,1
Style: Title,GomoryMontserratItalic,112,&H00FAFFFF,&H0059DAFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,5,90,90,0,1
Style: Chapter,GomoryMontserrat,59,&H00FAFFFF,&H0059DAFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,2,7,90,90,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
ass=[];srt=[]
for i,x in enumerate(events,1):
 a,b,tx=x['inicio'],x['fin'],x['texto'];ass.append(f'Dialogue: 0,{ts(a,True)},{ts(b,True)},Base,,0,0,0,,'+r'{\fad(15,30)\blur0.25\fscx102\fscy102\t(0,100,\fscx100\fscy100)}'+wrap(tx));srt.append(f'{i}\n{ts(a)} --> {ts(b)}\n{tx}\n')
def graphic(a,b,txt,style='Title',tags=''):
 ass.append(f'Dialogue: 2,{ts(a,True)},{ts(b,True)},{style},,0,0,0,,'+tags+txt)
for a,y,txt,size,col in [(.08,380,'NO COMPRES',110,'3322F0'),(.25,510,'UN IPHONE',126,'FAFFFF'),(.43,640,'SIN REVISAR ESTO',74,'59DAFF')]:
 graphic(a,3.1,txt,tags=r'{\pos(540,'+str(y)+r')\fs'+str(size)+r'\c&H'+col+r'&\fad(0,100)\fscx110\fscy110\t(0,120,\fscx100\fscy100)}')
graphic(3.2,6.8,'ENTREGA REAL · MAR DEL PLATA','Chapter',r'{\pos(90,200)\fs40\fad(60,100)}')
chapters=[(3.2,'01','CÁMARAS','Zoom · enfoque · selfie'),(remap(22.5),'02','LINTERNA','Probala también'),(remap(28.8),'03','HISTORIAL DE PIEZAS','Revisá la información'),(remap(37.2),'04','BATERÍA Y CICLOS','Reemplazo informado al cliente'),(remap(52.56),'05','FACE ID','Probalo antes de comprar'),(remap(66.48),'06','MICRÓFONO','Grabación de prueba'),(remap(74.08),'07','GARANTÍA','Tu copia, por escrito')]
for a,n,title,sub in chapters:
 graphic(a,a+2.6,n+' / '+title,'Chapter',r'{\move(65,320,90,320,0,150)\fad(25,100)}')
 graphic(a+.1,a+2.6,sub,'Chapter',r'{\pos(90,400)\fs37\c&H59DAFF&\fad(30,100)}')
graphic(D-5,D-.3,'GUARDÁ ESTA GUÍA',tags=r'{\pos(540,470)\fs76\fad(90,150)}')
graphic(D-4.8,D-.3,'ANTES DE COMPRAR TU IPHONE',tags=r'{\pos(540,560)\fs44\c&H59DAFF&\fad(90,150)}')
(r/'subtitulos.ass').write_text(head+'\n'.join(ass));(r/'subtitulos.srt').write_text('\n'.join(srt));(r/'captions.json').write_text(json.dumps(events,ensure_ascii=False,indent=2));(r/'chapters.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2))
# Audio edits match video exactly; preserve original speaking speed and dynamics.
sr,v=wavfile.read(r/'voice.wav');parts=[]
for c in clips:
 x=v[round(c['inicio_original']*sr):round(c['fin_original']*sr)].astype(float);n=round(.004*sr);x[:n]*=np.linspace(0,1,n)[:,None];x[-n:]*=np.linspace(1,0,n)[:,None];parts.append(x)
v=np.concatenate(parts);N=round(D*sr);v=v[:N];v=np.pad(v,((0,max(0,N-len(v))),(0,0)));t=np.arange(N)/sr
ms,m=wavfile.read(repo/'materiales/audio/musica-base-anuncio-v11.wav');m=m.astype(float)
if m.dtype.kind=='i':m/=32768
if ms!=sr:m=resample_poly(m,sr,ms)
if m.ndim==1:m=np.column_stack([m,m])
# 64 beats at142BPM, selected from the existing approved instrumental.
L=min(len(m),round(64*60/142*sr));m=m[:L];m/=np.sqrt(np.mean(m*m))+1e-12
music=m[np.arange(N)%L];level=np.where(t<3.1,10**(-30/20),10**(-37/20));level*=np.minimum(t/.06,1)*np.minimum((D-t)/.4,1);music*=level[:,None]
fx=np.zeros_like(v)
def add(x,at,g):
 i=round(at*sr)
 if x.ndim==1:x=np.column_stack([x,x])
 n=min(len(x),N-i);fx[i:i+n]+=x[:n]*g
u=np.arange(round(.19*sr))/sr;p=2*np.pi*(70*u+45*.014*(1-np.exp(-u/.014)));impact=(np.sin(p)+.25*np.sin(2*p))*np.exp(-u*25)*np.minimum(1,u/.002)
add(impact,.08,.42)
u=np.arange(round(.075*sr))/sr
pop=np.sin(2*np.pi*(410*u-900*u*u))*np.exp(-u*65)*np.minimum(1,u/.001)
click=np.sin(2*np.pi*1700*u)*np.exp(-u*130)*np.minimum(1,u/.001)
low=np.sin(2*np.pi*160*u)*np.exp(-u*55)*np.minimum(1,u/.001)
for i,(a,n,title,sub) in enumerate(chapters):add([pop,click,low][i%3],a,.13 if i%3 else .20)
# A single clear confirmation at the completed FaceID demo, not repeated dings.
u=np.arange(round(.20*sr))/sr;chime=(np.sin(2*np.pi*880*u)+.2*np.sin(2*np.pi*1320*u))*np.exp(-u*22)*np.minimum(u/.003,1);add(chime,remap(60.9),.075)
for name,a in [('voz-editada',v),('musica',music),('efectos',fx),('mix',v+music+fx)]:wavfile.write(r/(name+'.wav'),sr,a.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
print('DURATION',D,'CAPTIONS',len(events),flush=True)
