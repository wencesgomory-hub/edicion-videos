from pathlib import Path
from PIL import ImageFont
import json,subprocess,math
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
r=Path('/workspace/work/14pro-vs-15');repo=Path('/workspace/edicion-videos');D=68.1
fonts=r/'fonts';fonts.mkdir(exist_ok=True)
for suffix in ['', '-Italic']:
 font=TTFont(repo/f'materiales/fuentes/montserrat/Montserrat{suffix}.ttf');font=instantiateVariableFont(font,{'wght':850},inplace=True)
 fam='GomoryCompareItalic' if suffix else 'GomoryCompare'
 for n in font['name'].names:
  if n.nameID in [1,4,6,16]:n.string=fam.encode(n.getEncoding())
 font.save(fonts/(fam+'.ttf'))
def ts(t):
 n=round(t*100);m,n=divmod(n,6000);s,c=divmod(n,100);return f'0:{m:02}:{s:02}.{c:02}'
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Base,GomoryCompare,73,&H00FAFFFF,&H005ADFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,2,5,95,95,0,1
Style: Hero,GomoryCompareItalic,132,&H00FAFFFF,&H005ADFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,3,5,95,95,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
rows=[];cues=[]
white='FAFFFF';gold='5ADFFF';red='3024ED'
def event(a,b,tx,x=540,y=1370,size=73,color=white,style='Base',layer=1,extra='',anim='pop'):
 # Keep all editorial text below the presenter's face.
 if y>=1000:y=min(1650,y+105)
 if not tx.startswith('{'):
  font=ImageFont.truetype(str(fonts/('GomoryCompareItalic.ttf' if style=='Hero' else 'GomoryCompare.ttf')),size)
  maxw=880 if x==540 else 420
  width=font.getlength(tx)
  if width>maxw:size=round(size*maxw/width)
 tags=rf'{{\pos({x},{y})\fs{size}\c&H{color}&\fad(30,90)'
 if anim=='pop':tags+=r'\fscx108\fscy108\t(0,140,\fscx100\fscy100)'
 if anim=='slide':tags=tags.replace(r'\pos('+str(x)+','+str(y)+')',rf'\move({x-65},{y},{x},{y},0,180)')
 tags+=extra+'}'
 rows.append(f'Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{tags}{tx}')
 cues.append(dict(start=a,end=b,text=tx.replace(r'\N',' '),size=size))
def label(a,b,tx,y=240):event(a,b,tx,y=240,size=44,color=gold,anim='slide')
def duo(a,b,top,bottom,col=gold):
 event(a,b,top,y=1280,size=65,anim='slide');event(a+.10,b,bottom,y=1420,size=111,color=col,style='Hero')
# Opening: unobstructed face, fast three-part hierarchy over the table.
event(.08,2.42,'LA PREGUNTA QUE MÁS ME HACEN',y=240,size=49,color=white,anim='slide')
event(.12,4.28,'14 PRO',x=335,y=1300,size=139,color=gold,style='Hero')
event(.24,4.28,'VS',x=765,y=1300,size=69,color=red)
event(.38,4.28,'IPHONE 15',y=1470,size=127,style='Hero')
event(2.5,4.28,'¿CUÁL CONVIENE?',y=240,size=57)
duo(4.3,6.9,'BUSCÁS','CALIDAD / PRECIO')
duo(6.9,9.85,'DOS OPCIONES','¿CUÁL ELEGÍS?')
label(9.92,12.15,'SU PRIMERA ELECCIÓN')
event(10.02,12.15,'IPHONE 15',y=1360,size=145,color=gold,style='Hero')
# Factual graphics follow the actual spoken order.
label(12.16,15.63,'IPHONE 15 · DISEÑO Y CONEXIÓN')
event(12.18,13.55,'MÁS LIVIANO',y=1310,size=102,style='Hero',color=gold)
event(12.3,13.55,'171 g  /  14 Pro: 206 g',y=1435,size=45)
event(13.55,15.63,'USB-C',y=1310,size=150,color=gold,style='Hero')
event(13.65,15.63,'14 Pro: Lightning',y=1460,size=48)
label(16.48,18,'EN RENDIMIENTO')
event(16.5,18,'A16 BIONIC',y=1320,size=119,color=gold,style='Hero')
event(16.6,18,'EL MISMO CHIP EN LOS DOS',y=1450,size=43)
duo(18.57,20.72,'UNA GENERACIÓN','MÁS NUEVO')
label(20.78,25.5,'AHORA, LO QUE OFRECE EL PRO')
event(20.86,25.5,'14 PRO',y=1320,size=156,color=gold,style='Hero')
event(22.4,25.5,'TAMBIÉN TIENE SUS VENTAJAS',y=1470,size=43)
# Frequency comparison, clear distinction from chip performance.
label(25.55,32.14,'01 / PANTALLA',y=1080)
event(25.62,32.14,'14 PRO',x=290,y=1200,size=54,color=gold)
event(25.74,32.14,'120',x=290,y=1335,size=152,color=gold,style='Hero')
event(25.84,32.14,'HASTA 120 Hz',x=290,y=1460,size=38,color=gold)
event(28.02,32.14,'15 BASE',x=790,y=1200,size=54)
event(28.12,32.14,'60',x=790,y=1335,size=152,style='Hero')
event(28.22,32.14,'60 Hz',x=790,y=1460,size=38)
event(29.78,32.14,'MÁS REFRESCOS POR SEGUNDO',y=1580,size=39)
label(32.6,38.1,'02 / CÁMARAS')
event(32.68,35,'14 PRO',y=1265,size=56,color=gold)
event(32.78,35,'3 CÁMARAS',y=1400,size=121,color=gold,style='Hero')
event(35,38.1,'TELEOBJETIVO',y=1260,size=76,style='Hero')
event(35.1,38.1,'3× ÓPTICO',y=1405,size=125,color=gold,style='Hero')
label(38.15,42.32,'CÁMARA PRINCIPAL')
event(38.22,42.32,'48 MP',y=1305,size=154,color=gold,style='Hero')
event(38.35,42.32,'EN AMBOS MODELOS',y=1445,size=45)
event(40.65,42.32,'Igual resolución ≠ cámaras idénticas',y=1540,size=30)
label(42.65,47.15,'03 / DISEÑO · OPINIÓN PERSONAL')
event(42.72,47.15,'¿DOS O TRES',y=1300,size=88,style='Hero')
event(42.83,47.15,'CÁMARAS?',y=1420,size=126,color=gold,style='Hero')
# Keep presenter's changing recommendation legible; avoid unverified verbatim subtitles.
label(47.2,53.5,'LA DECISIÓN NO ES TAN OBVIA')
event(47.3,53.5,'DEPENDE DE LO',y=1310,size=76,style='Hero')
event(47.45,53.5,'QUE PRIORIZÁS',y=1430,size=101,color=gold,style='Hero')
label(54.1,62.1,'SU ELECCIÓN FINAL')
event(54.15,56.15,'14 PRO',y=1330,size=165,color=gold,style='Hero')
# Summary grows item by item as it is mentioned.
event(56.2,62.1,'3 CÁMARAS',y=1230,size=77,color=gold,style='Hero')
event(57.1,62.1,'TELEOBJETIVO 3×',y=1345,size=67,style='Hero')
event(58.1,62.1,'HASTA 120 Hz',y=1460,size=77,color=gold,style='Hero')
event(62.55,66.3,'¿VOS CON CUÁL',y=1255,size=89,style='Hero')
event(62.68,66.3,'TE QUEDÁS?',y=1380,size=123,color=gold,style='Hero')
event(63.2,66.3,'14 PRO  /  15 BASE',y=1520,size=43)
event(66.35,D,'LOS DOS AL',y=1270,size=69)
event(66.45,D,'MISMO PRECIO',y=1410,size=115,color=gold,style='Hero')
# Subtle rule under chapter labels, white edge flash on key transitions only.
for a,b in [(12.16,15.63),(16.48,18),(20.78,25.5),(25.55,32.14),(32.6,38.1),(38.15,42.32),(42.65,47.15),(54.1,62.1)]:
 y=300
 event(a,b,r'{\p1}m 0 0 l 130 0 l 130 4 l 0 4{\p0}',x=475,y=y,size=1,color=gold,layer=0,anim='none',extra=r'\an7\bord0\shad0')
(r/'base.ass').write_text(head+'\n'.join(rows));(r/'rotulos.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2))
# Audio: original speed, modest corrective EQ/leveling; no voice pitch changes.
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'original.mp4'),'-vn','-af','highpass=f=85,lowpass=f=11500,acompressor=threshold=0.14:ratio=2:attack=15:release=130:makeup=1.2,loudnorm=I=-16:TP=-2:LRA=9','-ar','48000','-ac','2','-c:a','pcm_f32le',str(r/'voice.wav')],check=True)
sr,v=wavfile.read(r/'voice.wav');N=min(len(v),round(D*sr));v=v[:N].astype(float);t=np.arange(N)/sr
ms,m=wavfile.read(repo/'materiales/audio/musica-base-anuncio-v11.wav');scale=32768 if m.dtype.kind=='i' else 1;m=m.astype(float)/scale
if ms!=sr:m=resample_poly(m,sr,ms)
if m.ndim==1:m=np.column_stack([m,m])
# Loop an exact 64-beat phrase, crossfade the join so it stays discreet.
L=min(len(m),round(64*60/142*sr));m=m[:L];m/=max(np.sqrt(np.mean(m*m)),1e-8);music=m[np.arange(N)%L]
# Lower the instrumental for detailed comparisons; pause it before the verdict.
level=np.ones(N)*10**(-32/20);level[t<4.28]=10**(-28/20);level[(t>=25.55)&(t<42.32)]=10**(-35/20);level[(t>=52.58)&(t<54.1)]=0;level[t>=62.55]=10**(-30/20)
level*=np.minimum(t/.12,1)*np.minimum((D-t)/.25,1);music*=level[:,None]
fx=np.zeros_like(v)
def add(x,at,g):
 i=round(at*sr);n=min(len(x),N-i)
 if n>0:fx[i:i+n]+=x[:n,None]*g
u=np.arange(round(.16*sr))/sr;ph=2*np.pi*(58*u+55*.012*(1-np.exp(-u/.012)));hit=(np.sin(ph)+.3*np.sin(2*ph))*np.exp(-u*27)*np.minimum(1,u/.002);add(hit,.12,.34)
for j,at in enumerate([12.16,16.48,20.78,25.55,28.02,32.6,35,38.15,42.65,54.1,62.55,66.35]):
 u=np.arange(round(.075*sr))/sr;freq=[350,190,820][j%3];x=np.sin(2*np.pi*(freq*u+150*u*np.exp(-u/.02)))*np.exp(-u*(65 if j%3 else 48))*np.minimum(1,u/.001);add(x,at,[.17,.19,.10][j%3])
for name,x in [('music.wav',music),('effects.wav',fx),('mix.wav',v+music+fx)]:wavfile.write(r/name,sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.87:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
print('Base gráfica y mezcla preparadas',flush=True)
