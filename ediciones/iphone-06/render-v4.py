from pathlib import Path
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,subprocess,math,sys,shutil
k=int(sys.argv[1]);ad=5+k;r=Path('/workspace/iphone-06-v4');repo=Path('/workspace/edicion-videos');sr=48000
names={1:'595476B5-ADE7-4279-A5C3-DD7A85C1C6BF.MP4',2:'32BA7711-88BF-4354-BC1C-F5F855A87D88.MP4'}
source=repo/f'materiales/originales/iphone-{ad:02}'/names[k];D={1:15.766667,2:18.5}[k];N=round(D*sr)
_,v=wavfile.read('/workspace/iphone-06/voice.wav');_,m=wavfile.read('/workspace/iphone-06/music.wav');_,fx=wavfile.read('/workspace/iphone-06/effects.wav');v=v.astype(float);m=m.astype(float);fx=fx.astype(float);tt=np.arange(N)/sr;events=[]
def effect(*args):pass
if k==1:
 blocks=[(1.72,3.20,['GOMORY','IMPORTADOS'],'GOMORY','white','normal'),(3.20,6.02,['LOS MEJORES','PRECIOS','Y CALIDAD'],'PRECIOS','gold','typing'),(6.02,7.05,['IPHONES','SEMINUEVOS'],'SEMINUEVOS','white','normal'),(7.05,8.12,['Y TAMBIÉN','SELLADOS'],'SELLADOS','gold','normal'),(8.12,10.55,['ACCESORIOS','DE REGALO'],'DE REGALO','red','gift'),(10.55,12.22,['LO MÁS IMPORTANTE','GARANTÍA'],'GARANTÍA','green','guarantee'),(12.22,13.55,['MANDANOS','UN MENSAJE'],'UN MENSAJE','gold','cta'),(13.55,D,['TE ASESORAMOS','EN TU PRÓXIMO IPHONE'],'TE ASESORAMOS','white','cta')]
 hook=['LLEGÓ LA HORA','DE TU NUEVO IPHONE'];hook_end=1.72;hookcol='gold'
 for at,kind in [(3.2,'snap'),(6.02,'wood'),(7.05,'bubble'),(8.12,'bubble'),(8.42,'wood'),(10.55,'thud'),(12.22,'snap')]:effect(at,kind)
 cuts=[(0,1.72,1.04),(1.72,4.55,1.075),(4.55,6.02,1),(6.02,10.55,1.04),(10.55,12.22,1),(12.22,D,1.075)]
else:
 blocks=[(4.85,6.10,['ACÁ TENÉS','GARANTÍA'],'GARANTÍA','green','normal'),(6.10,6.95,['60 DÍAS','DE GARANTÍA'],'60 DÍAS','green','guarantee'),(6.95,7.65,['POR','ESCRITO'],'ESCRITO','white','normal'),(7.65,9.00,['FIRMADA','POR AMBAS PARTES'],'FIRMADA','green','normal'),(9.00,10.20,['EN LA COMPRA','DE TU EQUIPO'],'DE TU EQUIPO','white','normal'),(10.20,12.20,['¿ELEGÍS UN','SELLADO?'],'SELLADO?','gold','normal'),(12.20,14.52,['1 AÑO','DE GARANTÍA OFICIAL'],'1 AÑO','green','guarantee'),(14.52,15.60,['¿QUÉ ESTÁS','ESPERANDO?'],'ESPERANDO?','gold','cta'),(15.60,16.95,['MANDANOS','UN MENSAJE'],'UN MENSAJE','gold','cta'),(16.95,D,['TE ASESORAMOS','EN TU PRÓXIMO IPHONE'],'TE ASESORAMOS','white','cta')]
 hook=['¿MIEDO A QUE','TE ESTAFEN?'];hook_end=4.85;hookcol='red'
 for at,kind in [(4.85,'thud'),(6.10,'bubble'),(7.65,'wood'),(10.20,'snap'),(12.20,'thud'),(15.60,'bubble')]:effect(at,kind)
 cuts=[(0,1.55,1.04),(1.55,4.85,1.075),(4.85,9,1),(9,10.2,1.06),(10.2,14.52,1),(14.52,D,1.075)]
# Two crisp alternating ticks mark the time cue, while the existing onset retains body.
for at,freq,g in [(.025,2450,.20),(.25,1820,.16)]:
 u=np.arange(round(.035*sr))/sr;tick=(np.sin(2*np.pi*freq*u)+.32*np.sin(2*np.pi*freq*1.47*u))*np.exp(-u*175)*np.minimum(1,u/.0005)
 i=round(at*sr);fx[i:i+len(tick)]+=tick[:,None]*g;events.append([at,'tick-tock',g])
fade=np.minimum(tt/.008,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('voice.wav',v),('music.wav',m),('effects.wav',fx),('mix.wav',(v+m+fx)*fade[:,None])]:wavfile.write(r/name,sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
shutil.copy('/workspace/iphone-06-v4/master-new.wav',r/'master.wav')
F=repo/'materiales/fuentes/montserrat/Montserrat.ttf';I=repo/'materiales/fuentes/montserrat/Montserrat-Italic.ttf';colors={'white':(255,255,250,255),'gold':(255,224,90,255),'green':(71,235,143,255),'red':(245,24,35,255)}
def text(tx,size,color='white',italic=False,weight=850,maxw=870):
 def font(size):
  f=ImageFont.truetype(str(I if italic else F),size);f.set_variation_by_axes([weight]);return f
 f=font(size)
 if f.getlength(tx)>maxw:f=font(round(size*maxw/f.getlength(tx)))
 im=Image.new('RGBA',(round(f.getlength(tx))+54,f.size+76));sh=Image.new('RGBA',im.size);d=ImageDraw.Draw(sh);d.text((27,30),tx,font=f,fill=(0,0,0,220),stroke_width=2);sh=sh.filter(ImageFilter.GaussianBlur(4));d=ImageDraw.Draw(im);d.text((24,23),tx,font=f,fill=colors[color]);sh.alpha_composite(im);sh.info['prefixes']=[round(24+f.getlength(tx[:i]))+8 for i in range(len(tx)+1)];return sh

def ease(q):return 1-(1-max(0,min(1,q)))**3

def place(out,im,y,q,en,hard=False):
 p=ease(q/.15);sc=1.08-.08*p;pic=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.BICUBIC);alpha=min(1,en/.07)*(1 if hard else min(1,(q+.02)/.04));pic.putalpha(pic.getchannel('A').point(lambda a:round(a*max(0,alpha))));out.alpha_composite(pic,(round((1080-pic.width)/2),round(y+(im.height-pic.height)/2)))
def gift_line():
 label=text('DE REGALO',132,'red',True,900,maxw=690)
 ef=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',109)
 emoji=Image.new('RGBA',(160,160));ed=ImageDraw.Draw(emoji);ed.text((0,0),'🎁',font=ef,embedded_color=True)
 box=emoji.getbbox();emoji=emoji.crop(box).resize((96,96),Image.Resampling.LANCZOS)
 im=Image.new('RGBA',(1000,label.height));x=(1000-label.width-108)//2;im.alpha_composite(label,(x,0));im.alpha_composite(emoji,(x+label.width+12,37));return im
assets=[]
for st,en,lines,key,col,kind in blocks:
 ims=([text('LOS MEJORES',67,'white',False,750),text('PRECIOS',132,'gold',True,900),text('Y CALIDAD',112,'gold',True,900)] if kind=='typing' else [text(line,(132 if kind in ['hero','guarantee','cta'] else 108) if line==key else 67,col if line==key else 'white',line==key,900 if line==key else 750) for line in lines])
 if kind=='gift':ims[1]=gift_line()
 assets.append((st,en,ims,kind))
hookims=[text(hook[0],110,'gold',False,900),text(hook[1],78,'gold',True,850)]
grad=Image.new('RGBA',(1080,800));gd=ImageDraw.Draw(grad)
for y in range(800):gd.line((0,y,1080,y),fill=(0,0,0,round(100*math.sin(math.pi*y/900)**1.3)))
def type_line(im,q,duration):
 if q<0:return None
 prefixes=im.info['prefixes'];n=min(len(prefixes)-1,math.floor(max(0,q)/duration*(len(prefixes)-1)))
 if n==len(prefixes)-1:return im
 pic=im.copy();mask=Image.new('L',pic.size,0);md=ImageDraw.Draw(mask);md.rectangle((0,0,prefixes[n],pic.height),fill=255)
 from PIL import ImageChops
 pic.putalpha(ImageChops.multiply(pic.getchannel('A'),mask));return pic
def frame(t):
 out=Image.new('RGBA',(1080,1920));out.alpha_composite(grad,(0,880));d=ImageDraw.Draw(out)
 if .10<=t<hook_end:
  for im,yy in zip(hookims,[1250,1400]):place(out,im,yy,t-.10,hook_end-t,True)
 if .08<=t<.34:
  a=round(25*math.sin(math.pi*(t-.08)/.26));out.alpha_composite(Image.new('RGBA',out.size,(255,239,218,a)))
 for st,en,ims,kind in assets:
  if st<=t<en:
   y=1050
   for j,im in enumerate(ims):
    if kind=='typing':
     starts=[3.20,3.55,4.55];pic=type_line(im,t-starts[j],[.28,.48,.46][j])
     if pic is not None:place(out,pic,y,.2,en-t,True)
    else:place(out,im,y,max(0,t-st-j*.025),en-t)
    y+=im.height-45
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
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-i',str(r/'graphics.mov'),'-i',str(r/'master.wav'),'-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[v]','-map','2:a','-t',str(D),'-c:v','libx264','-preset','fast','-crf','15','-threads','2','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/f'videos/anuncio-iphone-{ad:02}-v4.mp4')],check=True)
(r/'montaje.json').write_text(json.dumps({'fuente':str(source.relative_to(repo)),'duracion':D,'velocidad':1,'gancho':hook,'bloques':blocks,'encuadres':cuts,'efectos':events,'timings':'Estimaciones de alineación mediante ASR segmentado y ventanas cortas; no timestamps exactos de palabras.','musica':'Base percusiva140BPM, segmento por compases; ducking para voz','voz':'EQ y compresión moderadas, objetivo -14.5LUFS antes de mezcla; sin pitch, atempo o WPE.','nota':'Sustituye bloques sueltos por LOS MEJORES / PRECIOS / Y CALIDAD con escritura progresiva; el texto previo permanece visible al agregarse CALIDAD. Sonidos de tecleo localizados. DE REGALO rojo y emoji🎁 al lado. Gancho reloj y resto de V3 conservados; anuncio07 intacto.'},ensure_ascii=False,indent=2));print('DONE',ad,flush=True)
