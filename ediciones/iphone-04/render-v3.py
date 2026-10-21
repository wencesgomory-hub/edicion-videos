from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.io import wavfile
import numpy as np,json,math,subprocess,hashlib
from PIL import ImageChops
CUT=7/30
R=Path('/workspace/iphone-04-v3');repo=Path('/workspace/edicion-videos');source=repo/'86F3673D-C971-40E3-ACC4-CF51DB8EE3E4.MP4';D=29.3;sr=48000;N=round(D*sr)
# Preserve the approved V2 mix exactly.

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
 p=ease(q/.15);fade=min(clamp(q/.03),clamp(en/.06));sc=scale*(1.035-.035*p);pic=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.BICUBIC)
 pic.putalpha(pic.getchannel('A').point(lambda a:int(a*fade)));out.alpha_composite(pic,(round(x+(im.width-pic.width)/2+side*16*(1-p)),round(y+(im.height-pic.height)/2+10*(1-p))))

def centered(out,im,y,q,en,**kw):place(out,im,(1080-im.width)/2,y,q,en,**kw)
prices=[(3.24,5.52,'13',370),(5.72,9.63,'14 PRO',550),(10.02,13.28,'15 PRO',650),(13.35,16.78,'15 PRO MAX',760),(16.96,20.12,'16 PRO',800)]
price_assets={}
for st,en,model,amount in prices:
 im=Image.new('RGBA',(1000,470));title=text('IPHONE '+model,89,(191,232,243,255) if model in ['14 PRO','16 PRO'] else WHITE,False,900,maxw=880);im.alpha_composite(title,((1000-title.width)//2,0));money=text('$'+str(amount),202,GOLD,False,900,maxw=730);unit=text('USD',49,WHITE,False,800);group=money.width+unit.width-15;xx=(1000-group)//2;im.alpha_composite(money,(xx,130));im.alpha_composite(unit,(xx+money.width-12,267));price_assets[model]=im
hook1=text('¿SABÉS QUE...?',128,WHITE,True,900);con=text('CON SOLO',73,WHITE,False,750);money=text('USD 370',184,GOLD,False,900);first_a=text('tu primer',82,WHITE,False,700);first_b=text('IPHONE',148,WHITE,True,900)
offer_title=text('TU PRIMER IPHONE',96,WHITE,True,900,maxw=920)
offer_small=text('CON SOLO',66,WHITE,False,750)
offer_price=text('USD 370',183,GOLD,False,900)
promo_a=text('POR VER ESTE VIDEO',72,WHITE,False,800)
promo_b=text('USD 30 MENOS',151,GOLD,True,900)
promo_c=text('EN TU IPHONE',76,WHITE,False,850)
promo_condition=text('Sobre los precios que te muestro',43,WHITE,False,650)
price_disclaimer=text('PRECIO ANTES DEL DESCUENTO',42,WHITE,False,700)
# Caption blocks after the actual product/price demonstration.
caps=[(20.25,21.55,['MAR DEL PLATA','Y ALREDEDORES'],'MAR DEL PLATA',WHITE),(21.55,22.45,['aprovechá','CALIDAD'],'CALIDAD',GOLD),(22.45,23.55,['y','PRECIO'],'PRECIO',GOLD),(23.68,24.82,['mandanos','un MENSAJE'],'MENSAJE',GOLD),(26.70,27.68,['accesorios de','REGALO'],'REGALO',RED),(27.78,29.3,['DECÍ «VIDEO»','USD 30 MENOS'],'USD 30 MENOS',GOLD)]
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
  centered(out,promo_a,985,q,3.18-t)
  centered(out,promo_b,1100,q,3.18-t)
  centered(out,promo_c,1300,q,3.18-t)
  centered(out,promo_condition,1410,q,3.18-t)
 for st,en,model,amount in prices:
  if st<=t<en:
   q=t-st;im=price_assets[model]
   top=im.crop((0,0,1000,130));bottom=im.crop((0,130,1000,470))
   # A short gloss passes through the glyphs only.
   if False:
    gloss=Image.new('RGBA',bottom.size);gd=ImageDraw.Draw(gloss);x=round(-180+1400*((q-.18)/.5));alpha=round(170*math.sin(math.pi*(q-.18)/.5))
    gd.polygon([(x,0),(x+100,0),(x-40,340),(x-140,340)],fill=(255,255,255,alpha))
    gloss.putalpha(ImageChops.multiply(gloss.getchannel('A'),bottom.getchannel('A')));bottom.alpha_composite(gloss)
   place(out,top,40,1000,q,en-t,side=-1)
   place(out,bottom,40,1130,max(0,q-.045),en-t,side=1)
   if False:out.alpha_composite(Image.new('RGBA',(1080,1920),(245,250,255,16)))
   # Thin expanding rule gives each amount a clean graphic landing, without a panel.
   p=ease(q/.23);d=ImageDraw.Draw(out);d.line((355,1417,355+round(370*p),1417),fill=GOLD,width=5)
   centered(out,price_disclaimer,1440,q,en-t)
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
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(CUT),'-i',str(source),'-i',str(R/'graphics.mov'),'-i',str(R/'master.wav'),'-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','2:a','-t',str(D-CUT),'-c:v','libx264','-preset','fast','-crf','15','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/'videos/anuncio-iphone-04-v3.mp4')],check=True)
(R/'montaje.json').write_text(json.dumps({'duracion':D-CUT,'velocidad':1,'recorte_inicial':CUT,'resto_conservado':True,'precios_antes_descuento':prices,'descuento_usd':30,'precios_con_descuento':{model:amount-30 for st,en,model,amount in prices},'captions':caps,'garantia':[25.02,26.61,'60 DÍAS DE GARANTÍA'],'voz':'Fuente original; EQ y compresión moderadas, sin WPE ni cambios de tono/velocidad','musica':'Arreglo132BPM aprobado extendido musicalmente a29.3s, nivel -31dBRMS antes de ducking','efectos':'Mezcla aprobada V2 preservada sin cambios','fuente':'86F3673D-C971-40E3-ACC4-CF51DB8EE3E4.MP4','timings':'Estimación de alineación de texto a frases, basada en ASR segmentado y frames; precios re-transcritos por fragmento completo.','nota':'Promo autorizada de USD30 menos por ver el video; importes mostrados son antes del descuento. Keyword VIDEO en CTA. Animaciones suavizadas, sin gloss ni flash por precio; sonidos y voz V2 conservados. Sin vencimientos, stock ni otras condiciones inventadas.'},ensure_ascii=False,indent=2));print('V3 DONE',flush=True)
