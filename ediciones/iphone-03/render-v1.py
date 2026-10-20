from pathlib import Path
import json,subprocess,math,types
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
from PIL import Image,ImageDraw,ImageFont,ImageFilter
R=Path('/workspace/interior-03');repo=Path('/workspace/edicion-videos');sources=json.loads((R/'sources.json').read_text());sr=48000
F='/usr/share/fonts/openai-sans/OpenAISans-Bold.woff2';C='/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf';I='/usr/share/fonts/opentype/urw-base35/NimbusSans-BoldItalic.otf'
frames=[113,219,103];dur=[n/30 for n in frames];D=sum(dur);N=round(D*sr);o1=dur[0];o2=sum(dur[:2]);G=(255,222,65);CY=(74,225,247);RED=(255,65,67);WHITE=(255,255,251)
# Keep every source clip in its original order and at 1x. Only CFR frame rounding.
for j,(a,n) in enumerate(zip(sources,frames)):
 subprocess.run(['ffmpeg','-v','error','-y','-i',a['path'],'-vf','fps=30,scale=1080:1920:flags=lanczos,setsar=1,eq=contrast=1.065:brightness=-0.003:saturation=1.075:gamma=1.035,colorbalance=rs=-0.009:bs=0.012:rh=0.012:bh=-0.008,unsharp=5:5:0.25:3:3:0','-frames:v',str(n),'-an','-c:v','libx264','-preset','fast','-crf','15','-threads','4',str(R/f'clip-{j}.mp4')],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',a['path'],'-vn','-af',f'apad,atrim=duration={dur[j]}','-ac','1','-ar','48000','-c:a','pcm_f32le',str(R/f'voice-{j}.wav')],check=True)
print('SOURCES PREPARED',flush=True)
v=np.concatenate([wavfile.read(R/f'voice-{j}.wav')[1] for j in range(3)]);wavfile.write(R/'voice-raw.wav',sr,v.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'voice-raw.wav'),'-af','highpass=f=85,afftdn=nf=-23,equalizer=f=190:t=q:w=0.8:g=1.7,equalizer=f=3000:t=q:w=1:g=1.8,acompressor=threshold=0.12:ratio=2:attack=8:release=90:makeup=1.2,loudnorm=I=-16:TP=-3:LRA=7','-ar','48000','-c:a','pcm_f32le',str(R/'voice.wav')],check=True)
v=wavfile.read(R/'voice.wav')[1].astype(float)[:N];v=np.pad(v,(0,max(0,N-len(v))));v=np.column_stack([v,v])
_,m=wavfile.read(repo/'materiales/audio/musica-base-anuncio-v11.wav');m=m[:N].astype(float)
# Stronger approved 142 BPM music with audible drums; no rejected 120 BPM bed.
m*=2.45
rng=np.random.default_rng(303);dr=np.zeros(N);B=60/142
for k in range(int(D/B)+1):
 t=np.arange(round(.16*sr))/sr;i=round(k*B*sr);pulse=np.sin(2*np.pi*(49*t+70*.022*(1-np.exp(-t/.022))))*np.exp(-t*29)*.043
 if k%2:pulse+=sosfilt(butter(2,[1100,7600],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(t)))*np.exp(-t*60)*.013
 e=min(N,i+len(t))
 if e>i:dr[i:e]+=pulse[:e-i]
m+=dr[:,None];fx=np.zeros((N,2));events=[]
_,bank=wavfile.read(repo/'materiales/audio/efectos-aislados-anuncio-v11.wav');bank=bank.astype(float)
refs={'thud':7.67/1.12,'snap':8.48/1.12,'wood':15.2/1.12,'bubble':16.7/1.12,'low-pop':24.86/1.12}
def add(x,at,g):
 i=round(at*sr)
 if i<0:x=x[-i:];i=0
 e=min(N,i+len(x));x=x[:e-i]*g
 if x.ndim==1:x=x[:,None]
 if e>i:fx[i:e]+=x

def effect(at,kind,g=.53):
 i=round(refs[kind]*sr);x=bank[i:i+round(.18*sr)].copy();x/=np.max(abs(x))+1e-12;add(x,at,g);events.append([at,kind,g])
for at,k,g in [(0,'thud',.63),(.62,'snap',.50),(1.9,'bubble',.47),(o1,'thud',.57),(o1+1.0,'snap',.49),(o1+2.18,'wood',.55),(o1+3.40,'bubble',.55),(o1+4.35,'thud',.56),(o1+5.10,'bubble',.57),(o1+5.38,'snap',.50),(o1+6.1,'low-pop',.48),(o2,'snap',.56),(o2+.83,'bubble',.55)]:effect(at,k,g)
for at in [o1,o2]:
 t=np.arange(round(.14*sr))/sr;x=sosfilt(butter(2,[650,6500],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(t)));x*=np.sin(np.pi*t/.14)**2;x/=np.max(abs(x));add(x,at-.10,.22)
fade=np.minimum(np.arange(N)/sr/.012,1)*np.minimum((N-np.arange(N))/sr/.10,1)
wavfile.write(R/'mix.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
# Designed typography varies by message, not a single subtitle preset.
def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3
def text(txt,size,color=WHITE,font=F,stroke=2):
 f=ImageFont.truetype(font,size)
 if f.getlength(txt)>880:f=ImageFont.truetype(font,max(18,int(size*880/f.getlength(txt))))
 b=f.getbbox(txt);w=int(f.getlength(txt))+50;h=b[3]-b[1]+60;im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im);d.text((25,24-b[1]),txt,font=f,fill=color,stroke_width=stroke,stroke_fill=(8,10,15,230));return im

def place(out,im,y,q,side=0,scale=1,angle=0):
 p=ease(q/.17);sc=(.86+.14*p)*scale;im=im.resize((max(1,round(im.width*sc)),max(1,round(im.height*sc))),Image.Resampling.BICUBIC)
 if angle:im=im.rotate(angle*(1-p),Image.Resampling.BICUBIC,expand=True)
 x=(1080-im.width)/2+side*100*(1-p);out.alpha_composite(im,(int(x),int(y+42*(1-p))))

def label(txt,col=CY):
 im=text(txt,76,col,C);bg=Image.new('RGBA',(im.width+32,im.height+18));d=ImageDraw.Draw(bg);d.rounded_rectangle((1,1,bg.width-2,bg.height-2),radius=14,fill=(8,12,19,237),outline=(*col,230),width=2);bg.alpha_composite(im,(16,9));return bg
caps=[(.58,1.83,'¿HASTA CUÁNDO?',WHITE,C,107),(1.83,3.50,'CAMBIAR TU IPHONE',CY,C,126),(o1,o1+1.00,'VENÍ CON NOSOTROS',WHITE,F,77),(o1+1.,o1+2.10,'SIN EXCUSAS',RED,C,134),(o1+2.10,o1+3.38,'MEJORES PRECIOS',G,I,111),(o1+3.38,o1+4.32,'MEJOR CALIDAD',CY,C,123),(o1+4.32,o1+5.05,'GARANTÍA',WHITE,C,139),(o1+5.05,o1+6.10,'ACCESORIOS DE REGALO',G,C,103),(o1+6.10,o2,'¿QUÉ MÁS PODÉS PEDIR?',WHITE,I,82),(o2,o2+.82,'NO ESPERES MÁS',RED,C,118),(o2+.82,o2+1.95,'MANDANOS UN MENSAJE',CY,C,104),(o2+1.95,D,'TU PRÓXIMO EQUIPO',WHITE,I,103)]
rendered=[(st,en,text(tx,sz,col,font),tx) for st,en,tx,col,font,sz in caps]
basta=text('BASTA.',245,RED,C,3)
# Real product close-up selected from the user's library, decorative card only.
subprocess.run(['ffmpeg','-v','error','-y','-ss','1','-i',str(repo/'materiales/productos/iphonecontenido.mp4'),'-frames:v','1',str(R/'producto.jpg')],check=True)
phone=Image.open(R/'producto.jpg').convert('RGBA');phone.thumbnail((245,390),Image.Resampling.LANCZOS)
photos=[]
for name in ['cable','funda']:
 ph=Image.open(repo/f'materiales/graficos/accesorios-ilustrativos/{name}.png').convert('RGBA');ph.thumbnail((205,205),Image.Resampling.LANCZOS);photos.append(ph)

def frame(t):
 out=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(out)
 # Local gradient lets big lettering read without darkening the face.
 for y in range(1110,1690):
  a=int(112*math.sin(math.pi*(y-1110)/580)**1.3);d.line((0,y,1080,y),fill=(4,7,12,a))
 if t<.62:
  q=t;d.rectangle((0,0,1080,1920),fill=(255,35,43,int(27*(1-clamp(q/.62)))));place(out,basta,1190,q,scale=1.08,angle=-5)
  d.rectangle((130,1490,950,1500),fill=(*RED,235))
 for st,en,im,tx in rendered:
  if st<=t<en:
   y=1310
   if tx in ['MEJOR CALIDAD','ACCESORIOS DE REGALO']:y=1335
   if tx=='GARANTÍA':
    d.rounded_rectangle((100,1245,980,1460),radius=18,fill=(6,15,18,240),outline=(61,239,151,255),width=4)
   place(out,im,y,t-st,side=1 if int(st*10)%2 else -1,angle=3)
 if 1.9<=t<3.5:
  # Cyan moving focus marks highlight subject without a forced zoom.
  q=ease((t-1.9)/.2);d.line((125,350,125,280,230,280),fill=(*CY,int(210*q)),width=6);d.line((850,980,955,980,955,905),fill=(*CY,int(210*q)),width=6)
 if o1+3.38<=t<o1+4.32:
  q=ease((t-o1-3.38)/.16);x=int(760+120*(1-q));y=820
  d.rounded_rectangle((x-12,y-12,x+phone.width+12,y+phone.height+12),radius=19,fill=(8,16,23,242),outline=(*CY,255),width=3);out.alpha_composite(phone,(x,y))
 if o1+5.05<=t<o1+6.10:
  for j,ph in enumerate(photos):
   q=ease((t-o1-5.05-j*.13)/.14)
   if q<=0:continue
   x=290+j*280;y=int(1060+45*(1-q));d.rounded_rectangle((x-15,y-15,x+220,y+220),radius=19,fill=(10,14,20,238),outline=(*G,255),width=2);out.alpha_composite(ph,(x,y))
 if o2+.82<=t<D:
  q=ease((t-o2-.82)/.2);d.rounded_rectangle((160,1535,920,1607),radius=36,fill=(36,198,231,int(220*q)));d.text((540,1550),'GOMORY IMPORTADOS',font=ImageFont.truetype(F,36),fill=(5,13,20,255),anchor='mt')
 return out
for t in [.22,2.3,o1+2.5,o1+3.7,o1+5.5,o2+1.2]:frame(t).save(R/f'overlay-{t:.2f}.png')
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(sum(frames)):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0
print('GRAPHICS DONE',flush=True)
f='[0:v]setsar=1[a];[1:v]setsar=1[b];[2:v]setsar=1[c];[a][b][c]concat=n=3:v=1:a=0[base];[base][3:v]overlay=shortest=1,format=yuv420p[v]'
cmd=['ffmpeg','-v','error','-y']
for j in range(3):cmd+=['-i',str(R/f'clip-{j}.mp4')]
cmd+=['-i',str(R/'graphics.mov'),'-i',str(R/'master.wav'),'-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','4:a','-t',str(D),'-c:v','libx264','-preset','fast','-crf','15','-threads','4','-c:a','aac','-b:a','256k','-movflags','+faststart',str(repo/'videos/anuncio-iphone-03-v1.mp4')]
(R/'montaje.json').write_text(json.dumps({'fuentes':sources,'frames':frames,'duracion':D,'velocidad':1,'recortes_adicionales':False,'captions':caps,'sonidos':events,'referencia':'Anuncio meta V11 de ayer; no seminuevos de hoy','imagenes':['iphonecontenido','ilustrativo-cable','ilustrativo-funda'],'nota':'Captions de énfasis, no transcripción literal completa; no se añade duración de garantía no mencionada.'},ensure_ascii=False,indent=2));subprocess.run(cmd,check=True);print('FINAL DONE',flush=True)
