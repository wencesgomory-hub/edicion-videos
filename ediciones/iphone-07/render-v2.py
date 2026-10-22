from pathlib import Path
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,subprocess,math,sys,shutil
k=int(sys.argv[1]);ad=5+k;r=Path('/workspace/iphone-07-v2');repo=Path('/workspace/edicion-videos');sr=48000
names={1:'595476B5-ADE7-4279-A5C3-DD7A85C1C6BF.MP4',2:'32BA7711-88BF-4354-BC1C-F5F855A87D88.MP4'}
source=repo/f'materiales/originales/iphone-{ad:02}'/names[k];D={1:15.766667,2:18.5}[k];N=round(D*sr)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-vn','-ac','1','-ar',str(sr),'-af','highpass=f=80,equalizer=f=360:t=q:w=0.9:g=-1.8,equalizer=f=3200:t=q:w=0.8:g=1.1,acompressor=threshold=0.16:ratio=1.7:attack=15:release=110:makeup=1.05,loudnorm=I=-14.5:TP=-1.5:LRA=8','-c:a','pcm_f32le',str(r/'voice-mono.wav')],check=True)
_,v=wavfile.read(r/'voice-mono.wav');v=v[:N].astype(float);v=np.pad(v,(0,max(0,N-len(v))));tt=np.arange(N)/sr;v*=1+(10**(1/20)-1)*np.clip((2.2-tt)/.6,0,1);v=np.column_stack([v,v])
_,bank=wavfile.read(repo/'materiales/audio/base-percusiva-iphone05-140.wav');offset=0 if k==1 else round(4*4*(60/140)*sr);m=bank[offset:offset+N].astype(float).copy();assert len(m)==N
m*=10**(-26.5/20)/(np.sqrt(np.mean(m*m))+1e-12);env=np.sqrt(uniform_filter1d(np.mean(v*v,axis=1),2400)+1e-12);m*=np.clip(1-env*1.2,.72,1)[:,None]
fx=np.zeros((N,2));_,sample=wavfile.read(repo/'materiales/audio/efectos-aislados-anuncio-v11.wav');refs={'thud':7.67/1.12,'snap':8.48/1.12,'wood':15.2/1.12,'bubble':16.7/1.12};events=[]
def add(x,at,g):
 if x.ndim==1:x=np.column_stack([x,x])
 i=round(at*sr);n=min(N-i,len(x))
 if n>0:fx[i:i+n]+=x[:n]*g

def effect(at,kind,g=.57):
 i=round(refs[kind]*sr);x=sample[i:i+round(.16*sr)].astype(float);x/=np.max(abs(x))+1e-12;add(x,at,g);events.append([at,kind,g])
# Compact opening hit and smooth tonal sweep, distinct from the music.
u=np.arange(round(.16*sr))/sr;phase=2*np.pi*(85*u+45*.012*(1-np.exp(-u/.012)));hit=(np.sin(phase)+.35*np.sin(2*phase))*np.exp(-u*30)*np.minimum(1,u/.0015);add(hit,.10,.54)
u=np.arange(round(.10*sr))/sr;sw=np.sin(2*np.pi*(650*u-200*u*u/.10))*np.sin(np.pi*u/.10)**2;add(sw,.025,.10)
if k==1:
 blocks=[(1.72,3.20,['GOMORY','IMPORTADOS'],'GOMORY','white','normal'),(3.20,4.55,['LOS MEJORES','PRECIOS'],'PRECIOS','gold','hero'),(4.55,6.02,['CALIDAD','EN TU CIUDAD'],'CALIDAD','gold','normal'),(6.02,7.05,['IPHONES','SEMINUEVOS'],'SEMINUEVOS','white','normal'),(7.05,8.12,['Y TAMBIÉN','SELLADOS'],'SELLADOS','gold','normal'),(8.12,10.55,['ACCESORIOS','DE REGALO'],'DE REGALO','gold','gift'),(10.55,12.22,['LO MÁS IMPORTANTE','GARANTÍA'],'GARANTÍA','green','guarantee'),(12.22,13.55,['MANDANOS','UN MENSAJE'],'UN MENSAJE','gold','cta'),(13.55,D,['TE ASESORAMOS','EN TU PRÓXIMO IPHONE'],'TE ASESORAMOS','white','cta')]
 hook=['LLEGÓ LA HORA','DE TU NUEVO IPHONE'];hook_end=1.72;hookcol='gold'
 for at,kind in [(3.2,'snap'),(6.02,'wood'),(7.05,'bubble'),(8.12,'bubble'),(8.42,'wood'),(10.55,'thud'),(12.22,'snap')]:effect(at,kind)
 cuts=[(0,1.72,1.04),(1.72,4.55,1.075),(4.55,6.02,1),(6.02,10.55,1.04),(10.55,12.22,1),(12.22,D,1.075)]
else:
 blocks=[(4.85,6.10,['ACÁ TENÉS','GARANTÍA'],'GARANTÍA','green','normal'),(6.10,6.95,['60 DÍAS','DE GARANTÍA'],'60 DÍAS','green','guarantee'),(6.95,7.65,['POR','ESCRITO'],'ESCRITO','white','normal'),(7.65,9.00,['FIRMADA','POR AMBAS PARTES'],'FIRMADA','green','normal'),(9.00,10.20,['EN LA COMPRA','DE TU EQUIPO'],'DE TU EQUIPO','white','normal'),(10.20,12.20,['¿ELEGÍS UN','SELLADO?'],'SELLADO?','gold','normal'),(12.20,14.52,['1 AÑO','DE GARANTÍA OFICIAL'],'1 AÑO','green','guarantee'),(14.52,15.60,['¿QUÉ ESTÁS','ESPERANDO?'],'ESPERANDO?','gold','cta'),(15.60,16.95,['MANDANOS','UN MENSAJE'],'UN MENSAJE','gold','cta'),(16.95,D,['TE ASESORAMOS','EN TU PRÓXIMO IPHONE'],'TE ASESORAMOS','white','cta')]
 hook=['¿MIEDO A QUE','TE ESTAFEN','COMPRANDO UN IPHONE?'];hook_end=4.85;hookcol='red'
 for at,kind in [(4.85,'thud'),(6.10,'bubble'),(7.65,'wood'),(10.20,'snap'),(12.20,'thud'),(15.60,'bubble')]:effect(at,kind)
 cuts=[(0,1.55,1.04),(1.55,4.85,1.075),(4.85,9,1),(9,10.2,1.06),(10.2,14.52,1),(14.52,D,1.075)]
fade=np.minimum(tt/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('voice.wav',v),('music.wav',m),('effects.wav',fx),('mix.wav',(v+m+fx)*fade[:,None])]:wavfile.write(r/name,sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
shutil.copy('/workspace/iphone-07/master.wav',r/'master.wav')
F=repo/'materiales/fuentes/montserrat/Montserrat.ttf';I=repo/'materiales/fuentes/montserrat/Montserrat-Italic.ttf';colors={'white':(255,255,250,255),'gold':(255,224,90,255),'green':(71,235,143,255),'red':(245,24,35,255)}
def text(tx,size,color='white',italic=False,weight=850,maxw=870):
 def font(size):
  f=ImageFont.truetype(str(I if italic else F),size);f.set_variation_by_axes([weight]);return f
 f=font(size)
 if f.getlength(tx)>maxw:f=font(round(size*maxw/f.getlength(tx)))
 im=Image.new('RGBA',(round(f.getlength(tx))+54,f.size+76));sh=Image.new('RGBA',im.size);d=ImageDraw.Draw(sh);d.text((27,30),tx,font=f,fill=(0,0,0,220),stroke_width=2);sh=sh.filter(ImageFilter.GaussianBlur(4));d=ImageDraw.Draw(im);d.text((24,23),tx,font=f,fill=colors[color]);sh.alpha_composite(im);return sh

def ease(q):return 1-(1-max(0,min(1,q)))**3

def place(out,im,y,q,en,hard=False):
 p=ease(q/.15);sc=1.08-.08*p;pic=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.BICUBIC);alpha=min(1,en/.07)*(1 if hard else min(1,(q+.02)/.04));pic.putalpha(pic.getchannel('A').point(lambda a:round(a*max(0,alpha))));out.alpha_composite(pic,(round((1080-pic.width)/2),round(y+(im.height-pic.height)/2)))
assets=[]
for st,en,lines,key,col,kind in blocks:
 ims=[text(line,(132 if kind in ['hero','guarantee','cta'] else 108) if line==key else 67,col if line==key else 'white',line==key,900 if line==key else 750) for line in lines];assets.append((st,en,ims,kind))
hookims=[text(hook[0],104,'white',False),text(hook[1],116,hookcol,True,900),text(hook[2],68,'white',False,800)]
grad=Image.new('RGBA',(1080,800));gd=ImageDraw.Draw(grad)
for y in range(800):gd.line((0,y,1080,y),fill=(0,0,0,round(100*math.sin(math.pi*y/900)**1.3)))
def frame(t):
 out=Image.new('RGBA',(1080,1920));out.alpha_composite(grad,(0,880));d=ImageDraw.Draw(out)
 if .10<=t<hook_end:
  for j,im in enumerate(hookims):place(out,im,890+145*j,t-.10,hook_end-t,True)
  d.line((450,1330,630,1330),fill=colors[hookcol],width=4)
 if .08<=t<.34:
  a=round(25*math.sin(math.pi*(t-.08)/.26));out.alpha_composite(Image.new('RGBA',out.size,(255,239,218,a)))
 for st,en,ims,kind in assets:
  if st<=t<en:
   y=1050
   for j,im in enumerate(ims):place(out,im,y,max(0,t-st-j*.025),en-t);y+=im.height-45
   if kind in ['guarantee','gift'] and t-st>.1:d.line([(855,1000),(883,1028),(938,969)],fill=colors['green'],width=12,joint='curve')
 return out
for t in [.4,D*.5,D-1]:frame(t).save(r/f'overlay-{t:.2f}.png')
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(r/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(round(D*30)):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0;print('GRAPHICS DONE',ad,flush=True)
filters=['[0:v]fps=30,split='+str(len(cuts))+''.join(f'[s{i}]' for i in range(len(cuts)))]
for i,(a,b,z) in enumerate(cuts):
 w=int(1080/z)//2*2;h=int(1920/z)//2*2;filters.append(f'[s{i}]trim=start_frame={round(a*30)}:end_frame={round(b*30)},setpts=PTS-STARTPTS,crop={w}:{h}:(iw-ow)/2:(ih-oh)*0.25,scale=1080:1920:in_range=pc:out_range=tv:flags=lanczos,setsar=1[v{i}]')
filters.append(''.join(f'[v{i}]' for i in range(len(cuts)))+f'concat=n={len(cuts)}:v=1:a=0,eq=contrast=1.045:brightness=0.008:saturation=1.025:gamma=1.055[base]');filters.append('[base][1:v]overlay=shortest=1,format=yuv420p[v]')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-i',str(r/'graphics.mov'),'-i',str(r/'master.wav'),'-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[v]','-map','2:a','-t',str(D),'-c:v','libx264','-preset','fast','-crf','15','-threads','2','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/f'videos/anuncio-iphone-{ad:02}-v2.mp4')],check=True)
(r/'montaje.json').write_text(json.dumps({'fuente':str(source.relative_to(repo)),'duracion':D,'velocidad':1,'gancho':hook,'bloques':blocks,'encuadres':cuts,'efectos':events,'timings':'Estimaciones de alineación mediante ASR segmentado y ventanas cortas; no timestamps exactos de palabras.','musica':'Base percusiva140BPM, segmento por compases; ducking para voz','voz':'EQ y compresión moderadas, objetivo -14.5LUFS antes de mezcla; sin pitch, atempo o WPE.','nota':'Revisión localizada: agregar COMPRANDO UN IPHONE al gancho, manteniendo TE ESTAFEN rojo. Mezcla originalV1 copiada exacta; resto visual y condiciones intactos.'},ensure_ascii=False,indent=2));print('DONE',ad,flush=True)
