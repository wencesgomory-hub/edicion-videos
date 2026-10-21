from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.io import wavfile
import numpy as np,json,math,subprocess,hashlib
from PIL import ImageChops
CUT=0.4
R=Path('/workspace/iphone-04-v2');repo=Path('/workspace/edicion-videos');source=repo/'86F3673D-C971-40E3-ACC4-CF51DB8EE3E4.MP4';D=29.3;sr=48000;N=round(D*sr)
# Original pace and complete demonstration retained; no atempo, pitch or new jump cuts.
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
# Price changes have varied accents, not a repeated bell on every number.
for at,k,g in [(3.24,'thud',.40),(5.72,'bubble',.43),(10.02,'snap',.40),(13.35,'wood',.42),(16.96,'bubble',.41),(20.25,'snap',.35),(23.68,'bubble',.43),(25.02,'thud',.43),(26.70,'bubble',.45),(26.96,'snap',.40),(27.18,'wood',.38),(27.78,'thud',.40)]:effect(at,k,g)
# A compact onset: controlled air and low body, no sampled rustle or prolonged ding.
t=np.arange(round(.14*sr))/sr;air=bp(rng.normal(size=len(t)),250,1900)*np.sin(np.pi*t/.14)**2;air=sosfilt(butter(2,1800,fs=sr,btype='lowpass',output='sos'),air);air/=max(abs(air))+1e-12;put(fx,air,.005,.095)
t=np.arange(round(.16*sr))/sr;phase=2*np.pi*(79*t+43*.011*(1-np.exp(-t/.011)));hit=(np.sin(phase)+.3*np.sin(2*phase))*np.exp(-t*33)*np.minimum(1,t/.0015);hit/=max(abs(hit))+1e-12;put(fx,hit,.11,.27)
# Secondary tactile accents sync to model/amount stagger, never a repeated ding.
for st,kind in [(3.24,'snap'),(5.72,'wood'),(10.02,'bubble'),(13.35,'snap'),(16.96,'thud')]:effect(st+.24,kind,.20)
# One money accent with the opening amount.
t=np.arange(round(.13*sr))/sr;cash=(np.sin(2*np.pi*1318*t)+.22*np.sin(2*np.pi*1976*t))*np.exp(-t*44)*np.minimum(1,t/.002);put(fx,cash,.85,.12)
fade=np.minimum(np.arange(N)/sr/.012,1)*np.minimum((N-np.arange(N))/sr/.12,1)
for name,x in [('music.wav',m),('effects.wav',fx),('mix.wav',(v+m+fx)*fade[:,None])]:wavfile.write(R/name,sr,x.astype(np.float32))
# Remove Sabés que from voice, music and effects; restore the approved short opening accent.
_,fullmix=wavfile.read(R/'mix.wav');newmix=fullmix[round(CUT*sr):].copy();newmix[:round(.30*sr)]+=fx[:round(.30*sr)]
newmix[:round(.004*sr)]*=np.linspace(0,1,round(.004*sr))[:,None]
wavfile.write(R/'mix-cut.wav',sr,newmix.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix-cut.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
print('AUDIO DONE',flush=True)
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
prices=[(3.24,5.52,'13',370),(5.72,9.63,'14 PRO',550),(10.02,13.28,'15 PRO',650),(13.35,16.78,'15 PRO MAX',760),(16.96,20.12,'16 PRO',800)]
price_assets={}
for st,en,model,amount in prices:
 im=Image.new('RGBA',(1000,470));title=text('IPHONE '+model,89,(191,232,243,255) if model in ['14 PRO','16 PRO'] else WHITE,False,900,maxw=880);im.alpha_composite(title,((1000-title.width)//2,0));money=text('$'+str(amount),202,GOLD,False,900,maxw=730);unit=text('USD',49,WHITE,False,800);group=money.width+unit.width-15;xx=(1000-group)//2;im.alpha_composite(money,(xx,130));im.alpha_composite(unit,(xx+money.width-12,267));price_assets[model]=im
hook1=text('¿SABÉS QUE...?',128,WHITE,True,900);con=text('CON SOLO',73,WHITE,False,750);money=text('USD 370',184,GOLD,False,900);first_a=text('tu primer',82,WHITE,False,700);first_b=text('IPHONE',148,WHITE,True,900)
offer_title=text('TU PRIMER IPHONE',96,WHITE,True,900,maxw=920)
offer_small=text('CON SOLO',66,WHITE,False,750)
offer_price=text('USD 370',183,GOLD,False,900)
# Caption blocks after the actual product/price demonstration.
caps=[(20.25,21.55,['MAR DEL PLATA','Y ALREDEDORES'],'MAR DEL PLATA',WHITE),(21.55,22.45,['aprovechá','CALIDAD'],'CALIDAD',GOLD),(22.45,23.55,['y','PRECIO'],'PRECIO',GOLD),(23.68,24.82,['mandanos','un MENSAJE'],'MENSAJE',GOLD),(26.70,27.68,['accesorios de','REGALO'],'REGALO',RED),(27.78,29.3,['¿qué más estás','ESPERANDO?'],'ESPERANDO?',RED)]
cap_assets=[]
for st,en,lines,key,col in caps:
 ims=[text(line,112 if key in line else 71,col if key in line else WHITE,key in line,900 if key in line else 700) for line in lines];cap_assets.append((st,en,ims))
gar1=text('60 DÍAS',164,GREEN,False,900);gar2=text('DE GARANTÍA',84,WHITE,True,850)
grad=Image.new('RGBA',(1080,700));gd=ImageDraw.Draw(grad)
for y in range(700):gd.line((0,y,1080,y),fill=(0,0,0,round(95*math.sin(math.pi*y/700)**1.5)))
# The light accent remains subtle and localized, never a red crossing stripe.
glow=Image.new('RGBA',(1080,420));gg=ImageDraw.Draw(glow)
for r in range(470,0,-6):gg.ellipse((540-r,210-r*.16,540+r,210+r*.16),fill=(255,246,217,round(2+2*(1-r/470))))
glow=glow.filter(ImageFilter.GaussianBlur(18))
def check(out,t,st):
 q=ease((t-st)/.18);d=ImageDraw.Draw(out);pts=[(812,1015),(854,1058),(943,948)]
 if q<.4:
  z=q/.4;d.line([pts[0],(round(812+42*z),round(1015+43*z))],fill=GREEN,width=15)
 else:
  z=(q-.4)/.6;d.line([pts[0],pts[1],(round(854+89*z),round(1058-110*z))],fill=GREEN,width=15,joint='curve')
def frame(t):
 t+=CUT
 out=Image.new('RGBA',(1080,1920));out.alpha_composite(grad,(0,920))
 if CUT+.02<=t<CUT+.30:
  power=math.sin(math.pi*(t-CUT-.02)/.28);im=glow.copy();im.putalpha(im.getchannel('A').point(lambda a:min(75,round(a*14*power))));out.alpha_composite(im,(0,850))
 if CUT<=t<3.18:
  q=t-CUT+.06
  centered(out,offer_title,985,q,3.18-t)
  centered(out,offer_small,1120,q,3.18-t)
  centered(out,offer_price,1205,q,3.18-t)
 for st,en,model,amount in prices:
  if st<=t<en:
   q=t-st;im=price_assets[model]
   top=im.crop((0,0,1000,130));bottom=im.crop((0,130,1000,470))
   # A short gloss passes through the glyphs only.
   if .18<=q<.68:
    gloss=Image.new('RGBA',bottom.size);gd=ImageDraw.Draw(gloss);x=round(-180+1400*((q-.18)/.5));alpha=round(170*math.sin(math.pi*(q-.18)/.5))
    gd.polygon([(x,0),(x+100,0),(x-40,340),(x-140,340)],fill=(255,255,255,alpha))
    gloss.putalpha(ImageChops.multiply(gloss.getchannel('A'),bottom.getchannel('A')));bottom.alpha_composite(gloss)
   place(out,top,40,1000,q,en-t,side=-1)
   place(out,bottom,40,1130,max(0,q-.045),en-t,side=1)
   if q<.067:out.alpha_composite(Image.new('RGBA',(1080,1920),(245,250,255,16)))
   # Thin expanding rule gives each amount a clean graphic landing, without a panel.
   p=ease(q/.23);d=ImageDraw.Draw(out);d.line((355,1417,355+round(370*p),1417),fill=GOLD,width=5)
 for st,en,ims in cap_assets:
  if st<=t<en:
   yy=1110-sum(im.height-42 for im in ims)/2
   for j,im in enumerate(ims):centered(out,im,yy,max(0,t-st-j*.025),en-t,side=1 if j%2 else -1);yy+=im.height-42
 if 25.02<=t<26.61:
  centered(out,gar1,1040,t-25.02,26.61-t);centered(out,gar2,1240,t-25.02,26.61-t);check(out,t,25.02)
 if 26.70<=t<27.68:check(out,t,26.70)
 return out
for t in [.3,1.3,4.2,7.5,11.7,14.8,18.5,24.2,25.6,27.1,28.5]:frame(t).save(R/f'overlay-{t}.png')
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(round((D-CUT)*30)):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0;print('GRAPHICS DONE',flush=True)
vf='fps=30,scale=1080:1920:in_range=pc:out_range=tv:flags=lanczos,setsar=1,eq=contrast=1.04:brightness=0.003:saturation=1.035:gamma=1.045'
f=f'[0:v]{vf}[base];[base][1:v]overlay=shortest=1,format=yuv420p[v]'
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(CUT),'-i',str(source),'-i',str(R/'graphics.mov'),'-i',str(R/'master.wav'),'-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','2:a','-t',str(D-CUT),'-c:v','libx264','-preset','fast','-crf','15','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/'videos/anuncio-iphone-04-v2.mp4')],check=True)
(R/'montaje.json').write_text(json.dumps({'duracion':D-CUT,'velocidad':1,'recorte_inicial':CUT,'resto_conservado':True,'precios':prices,'captions':caps,'garantia':[25.02,26.61,'60 DÍAS DE GARANTÍA'],'voz':'Fuente original; EQ y compresión moderadas, sin WPE ni cambios de tono/velocidad','musica':'Arreglo132BPM aprobado extendido musicalmente a29.3s, nivel -31dBRMS antes de ducking','efectos':events,'fuente':'86F3673D-C971-40E3-ACC4-CF51DB8EE3E4.MP4','timings':'Estimación de alineación de texto a frases, basada en ASR segmentado y frames; precios re-transcritos por fragmento completo.','nota':'Gancho TU PRIMER IPHONE / CON SOLO USD370 desde el inicio; se retira Sabés que. Títulos aprobados conservados, modelo y precio animados por separado, brillo de glifos y acentos celestes puntuales. Sin fotos ni condiciones nuevas.'},ensure_ascii=False,indent=2));print('V2 DONE',flush=True)
