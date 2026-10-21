from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.io import wavfile
import numpy as np,json,math,subprocess,hashlib
R=Path('/workspace/iphone-05');repo=Path('/workspace/edicion-videos');source=repo/'D4C459C6-A3C2-4BF0-94BE-C47B1EF21D57.MP4';D=35.016667;sr=48000;N=round(D*sr)
# Original pace and complete demonstration retained; no atempo, pitch or new jump cuts.
if not (R/'master.wav').exists():
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-vn','-ac','1','-ar','48000','-af','highpass=f=80,equalizer=f=360:t=q:w=0.9:g=-1.8,equalizer=f=3200:t=q:w=0.8:g=1.1,acompressor=threshold=0.16:ratio=1.7:attack=15:release=110:makeup=1.05,loudnorm=I=-18:TP=-3:LRA=8','-c:a','pcm_f32le',str(R/'voice.wav')],check=True)
 _,v=wavfile.read(R/'voice.wav');v=v[:N].astype(float);v=np.pad(v,(0,max(0,N-len(v))));v=np.column_stack([v,v])
 # Same 132 BPM arrangement as the latest ad, extended by complete bars rather than an abrupt loop.
 song=Path('/workspace/interior-03-cierre/audio.py').read_text();music_code=song[song.index('rng=np.random.default_rng(13221)'):song.index('# Controlled music level:')];music_code=music_code.replace('for bar in range(8):','for bar in range(math.ceil(D/(4*beat))+1):')
 from scipy.signal import butter,sosfilt
 exec(music_code,globals())
 m*=10**(-31/20)/(np.sqrt(np.mean(m*m))+1e-12)
 env=np.sqrt(np.convolve(np.mean(v*v,axis=1),np.ones(1800)/1800,mode='same')+1e-10);m*=np.clip(1-env*1.3,.72,1)[:,None]
 fx=np.zeros((N,2));_,bank=wavfile.read(repo/'materiales/audio/efectos-aislados-anuncio-v11.wav');bank=bank.astype(float);refs={'thud':7.67/1.12,'snap':8.48/1.12,'wood':15.2/1.12,'bubble':16.7/1.12};events=[]
 def effect(at,kind,g):
  i=round(refs[kind]*sr);x=bank[i:i+round(.18*sr)].copy();x/=np.max(abs(x))+1e-12;put(fx,x,at,g);events.append([at,kind,g])
 # Deliberate accents on message changes, not every subtitle.
 for at,k,g in [(1.35,'thud',.43),(4.12,'snap',.47),(7.58,'bubble',.48),(9.45,'wood',.44),(12.55,'snap',.42),(14.6,'bubble',.46),(18.05,'thud',.49),(22.0,'wood',.45),(24.1,'bubble',.47),(29.6,'thud',.48),(31.45,'bubble',.48),(31.72,'wood',.44),(32.65,'snap',.49)]:effect(at,k,g*1.26)
 # A compact onset: controlled air and low body, no sampled rustle or prolonged ding.
 t=np.arange(round(.14*sr))/sr;air=bp(rng.normal(size=len(t)),250,1900)*np.sin(np.pi*t/.14)**2;air=sosfilt(butter(2,1800,fs=sr,btype='lowpass',output='sos'),air);air/=max(abs(air))+1e-12;put(fx,air,.005,.095)
 t=np.arange(round(.16*sr))/sr;phase=2*np.pi*(79*t+43*.011*(1-np.exp(-t/.011)));hit=(np.sin(phase)+.3*np.sin(2*phase))*np.exp(-t*33)*np.minimum(1,t/.0015);hit/=max(abs(hit))+1e-12;put(fx,hit,.11,.27)
 # One money accent with the opening amount.
 t=np.arange(round(.13*sr))/sr;cash=(np.sin(2*np.pi*1318*t)+.22*np.sin(2*np.pi*1976*t))*np.exp(-t*44)*np.minimum(1,t/.002);put(fx,cash,7.65,.15)
 fade=np.minimum(np.arange(N)/sr/.012,1)*np.minimum((N-np.arange(N))/sr/.12,1)
 for name,x in [('music.wav',m),('effects.wav',fx),('mix.wav',(v+m+fx)*fade[:,None])]:wavfile.write(R/name,sr,x.astype(np.float32))
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
 print('AUDIO DONE',flush=True)
else:events=[]
F=repo/'materiales/fuentes/montserrat/Montserrat.ttf';I=repo/'materiales/fuentes/montserrat/Montserrat-Italic.ttf';WHITE=(255,255,250,255);GOLD=(255,224,90,255);GREEN=(71,235,143,255);RED=(227,30,41,255)
def font(size,italic=False,weight=850):
 f=ImageFont.truetype(str(I if italic else F),size);f.set_variation_by_axes([weight]);return f

def text(tx,size,color=WHITE,italic=False,weight=850,maxw=900):
 f=font(size,italic,weight)
 if f.getlength(tx)>maxw:f=font(max(18,round(size*maxw/f.getlength(tx))),italic,weight)
 w=round(f.getlength(tx))+54;h=f.size+76;im=Image.new('RGBA',(w,h));sh=Image.new('RGBA',im.size);d=ImageDraw.Draw(sh);d.text((27,30),tx,font=f,fill=(0,0,0,220),stroke_width=2);sh=sh.filter(ImageFilter.GaussianBlur(4));d=ImageDraw.Draw(im);d.text((24,23),tx,font=f,fill=color);sh.alpha_composite(im);return sh

def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3

def place(out,im,x,y,q,en,scale=1,side=0):
 p=ease(q/.15);fade=min(clamp(q/.03),clamp(en/.06));sc=scale*(1.08-.08*p);pic=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.BICUBIC)
 pic.putalpha(pic.getchannel('A').point(lambda a:int(a*fade)));out.alpha_composite(pic,(round(x+(im.width-pic.width)/2+side*40*(1-p)),round(y+(im.height-pic.height)/2+20*(1-p))))

def centered(out,im,y,q,en,**kw):place(out,im,(1080-im.width)/2,y,q,en,**kw)
# Short phrases aligned approximately to ASR segments; emphasis changes with the message.
blocks=[
(0,1.32,['¿QUERÉS UN','IPHONE?'],'IPHONE?',GOLD,'hook'),
(1.32,2.45,['pero tenés miedo','A ELEGIR MAL'],'A ELEGIR MAL',RED,'warning'),
(2.45,3.27,['el mejor','CALIDAD / PRECIO'],'CALIDAD / PRECIO',GOLD,'normal'),
(3.27,4.10,['NOS PASÓ','A TODOS'],'A TODOS',WHITE,'normal'),
(4.10,5.08,['EN ESTE VIDEO'],'EN ESTE VIDEO',WHITE,'normal'),
(5.08,7.55,['3 OPCIONES','PARA ESTE AÑO'],'3 OPCIONES',GOLD,'hero'),
(7.55,9.43,['PRESUPUESTO','HASTA USD 400'],'HASTA USD 400',GOLD,'hero'),
(9.43,11.18,['LA MEJOR OPCIÓN','IPHONE 13'],'IPHONE 13',GOLD,'hero'),
(11.18,12.57,['un verdadero','CABALLITO DE BATALLA'],'CABALLITO DE BATALLA',WHITE,'normal'),
(12.57,14.58,['un poquito más','DE PRESUPUESTO'],'DE PRESUPUESTO',WHITE,'normal'),
(14.58,17.88,['ENTRE','USD 520 — 560'],'USD 520 — 560',GOLD,'hero'),
(17.88,19.42,['TE RECOMENDAMOS','IPHONE 14 PRO'],'IPHONE 14 PRO',GOLD,'hero'),
(19.42,21.82,['lo mejor','CALIDAD / PRECIO'],'CALIDAD / PRECIO',GOLD,'normal'),
(21.82,23.95,['junto al','IPHONE 15 PRO'],'IPHONE 15 PRO',GOLD,'hero'),
(23.95,25.52,['DESDE','USD 630'],'USD 630',GOLD,'hero'),
(25.52,26.82,['¿QUERÉS LLEVARTE','UNO DE ESTOS EQUIPOS?'],'UNO DE ESTOS EQUIPOS?',WHITE,'normal'),
(26.82,28.00,['la mejor','CALIDAD Y PRECIO'],'CALIDAD Y PRECIO',GOLD,'normal'),
(28.00,29.58,['DE LA CIUDAD'],'DE LA CIUDAD',WHITE,'normal'),
(29.58,31.40,['60 DÍAS','DE GARANTÍA'],'60 DÍAS',GREEN,'guarantee'),
(31.40,32.65,['ACCESORIOS','DE REGALO'],'DE REGALO',GOLD,'gift'),
(32.65,33.85,['MANDANOS','UN MENSAJE'],'UN MENSAJE',GOLD,'cta'),
(33.85,35.016667,['TE','ASESORAMOS'],'ASESORAMOS',WHITE,'cta')]
assets=[]
for st,en,lines,key,col,kind in blocks:
 ims=[]
 for line in lines:
  important=line==key
  size=(136 if kind in ['hook','hero','guarantee','cta'] else 106) if important else 67
  ims.append(text(line,size,col if important else WHITE,important,900 if important else 750,maxw=890))
 assets.append((st,en,ims,kind))
# Lower frame contrast support, leaving the speaker's face clear.
grad=Image.new('RGBA',(1080,870));gd=ImageDraw.Draw(grad)
for y in range(870):gd.line((0,y,1080,y),fill=(0,0,0,round(116*math.sin(math.pi*y/1000)**1.3)))
glow=Image.new('RGBA',(1080,360));gg=ImageDraw.Draw(glow)
for r in range(500,0,-5):gg.ellipse((540-r,180-r*.16,540+r,180+r*.16),fill=(255,236,178,5))
glow=glow.filter(ImageFilter.GaussianBlur(20))
def frame(t):
 out=Image.new('RGBA',(1080,1920));out.alpha_composite(grad,(0,900));d=ImageDraw.Draw(out)
 # Restrained light entries on opening and recommendation/guarantee transitions.
 for at in [0.04,5.08,9.43,17.88,21.82,29.58,32.65]:
  q=t-at
  if 0<=q<.24:
   g=glow.copy();strength=math.sin(math.pi*q/.24);g.putalpha(g.getchannel('A').point(lambda a:round(a*5*strength)));out.alpha_composite(g,(0,980))
 for st,en,ims,kind in assets:
  if st<=t<en:
   yy=1050 if kind in ['hero','hook','guarantee','cta'] else 1090
   for j,im in enumerate(ims):
    centered(out,im,yy,max(.02,t-st+.04-j*.025),en-t,side=(-1 if j%2==0 else 1));yy+=im.height-47
   if kind=='warning':
    # Subtle red border pulse, no cartoon symbol and no full red mask.
    a=round(45*(.5+.5*math.sin((t-st)*8)));d.line((80,1370,1000,1370),fill=(*RED[:3],a+70),width=5)
   if kind=='hero':
    p=ease((t-st)/.3);d.line((390,1445,390+round(300*p),1445),fill=GOLD,width=4)
   if kind in ['guarantee','gift']:
    q=ease((t-st)/.22);pts=[(866,1020),(890,1044),(944,985)]
    if q>.5:d.line(pts,fill=GREEN,width=12,joint='curve')
 return out
for t in [.6,1.8,5.8,8.3,10.3,15.4,18.7,22.7,24.7,30.4,31.9,34.2]:frame(t).save(R/f'overlay-{t}.png')
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(round(D*30)):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0;print('GRAPHICS DONE',flush=True)
# Small framing changes around the explanation, leaving hand-held product moments uncropped.
z="if(between(t,1.32,4.10)+between(t,5.08,7.55)+between(t,12.57,14.58)+between(t,25.52,29.58)+gte(t,32.65),1.075,1)"
vf=f"fps=30,crop=w='trunc(iw/({z})/2)*2':h='trunc(ih/({z})/2)*2':x='(iw-ow)/2':y='(ih-oh)*0.25',scale=1080:1920:in_range=pc:out_range=tv:flags=lanczos,setsar=1,eq=contrast=1.045:brightness=0.008:saturation=1.025:gamma=1.055"
# crop w/h expressions cannot evaluate t dynamically: use fixed split sections instead.
segments=[(0,1.32,1),(1.32,4.1,1.075),(4.1,5.08,1),(5.08,7.55,1.075),(7.55,12.57,1),(12.57,14.58,1.075),(14.58,25.52,1),(25.52,29.58,1.075),(29.58,32.65,1),(32.65,D,1.075)]
filters=['[0:v]fps=30,split=10'+''.join(f'[s{i}]' for i in range(10))]
for i,(a,b,z) in enumerate(segments):
 w=int(1080/z)//2*2;h=int(1920/z)//2*2
 filters.append(f'[s{i}]trim=start_frame={round(a*30)}:end_frame={round(b*30)},setpts=PTS-STARTPTS,crop={w}:{h}:(iw-ow)/2:(ih-oh)*0.25,scale=1080:1920:in_range=pc:out_range=tv:flags=lanczos,setsar=1[v{i}]')
filters.append(''.join(f'[v{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=1:a=0,eq=contrast=1.045:brightness=0.008:saturation=1.025:gamma=1.055[base]')
filters.append('[base][1:v]overlay=shortest=1,format=yuv420p[v]')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-i',str(R/'graphics.mov'),'-i',str(R/'master.wav'),'-filter_complex_threads','4','-filter_complex',';'.join(filters),'-map','[v]','-map','2:a','-t',str(D),'-c:v','libx264','-preset','fast','-crf','15','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/'videos/anuncio-iphone-05-v1.mp4')],check=True)
(R/'montaje.json').write_text(json.dumps({'fuente':source.name,'duracion':D,'velocidad':1,'bloques':blocks,'encuadres':segments,'efectos':events,'timings':'Estimación de alineación a partir de transcripciones por segmentos y frames; no son timestamps exactos de palabras.','referencia':'referencia-principal-iphone-05.mp4','audio':'Voz con EQ/compresión moderadas, música132BPM y FX variados +2dB; sin WPE ni cambio de velocidad o tono.','nota':'Sin descuento añadido; no trasladar automáticamente ofertaUSD30 de otro anuncio.'},ensure_ascii=False,indent=2));print('DONE',flush=True)
