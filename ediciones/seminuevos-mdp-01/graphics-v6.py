from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import json,math,subprocess,sys,types
R=Path('/workspace/seminuevos-01-v6');spec=json.loads((R/'edit.json').read_text());a=types.ModuleType('approved_style')
s=Path('/workspace/edicion-videos/ediciones/seminuevos-mdp-01/estilo-v11-palabras.py').read_text().split('\nscreens=')[0]
s=s.replace("R=Path('/workspace/ad-v4');subs=json.loads((R/'subtitles.json').read_text())","R=Path('/workspace/seminuevos-01-v6');subs="+repr(spec['captions']))
s=s.replace('if 14.3<=start<16.6 or 21.76<=start<24.7:normal_y=825-height/2','if False:normal_y=825-height/2');exec(s,a.__dict__)
G=a.GOLD;WHITE=a.WHITE
# Approved V11 motion: each word pops, glows, slides and settles from a slight angle.
def clamp(x):return max(0,min(x,1))
def ease(x):return 1-(1-clamp(x))**3
def back(x):x=clamp(x)-1;return 1+2.1*x*x*x+1.1*x*x

def paste(out,im,x,y,alpha=1,scale=1,angle=0):
 if alpha<=0:return
 if abs(scale-1)>.002:
  w,h=im.size;im=im.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.Resampling.BICUBIC);x+=(w-im.width)/2;y+=(h-im.height)/2
 if abs(angle)>.1:
  w,h=im.size;im=im.rotate(angle,Image.Resampling.BICUBIC,expand=True);x+=(w-im.width)/2;y+=(h-im.height)/2
 if alpha<.999:im=im.copy();im.putalpha(im.getchannel('A').point(lambda p:int(p*alpha)))
 out.alpha_composite(im,(int(x),int(y)))

def outlined(text,size,color=G,italic=True):
 f=ImageFont.truetype(a.I if italic else a.F,size)
 if f.getlength(text)>945:f=ImageFont.truetype(a.I if italic else a.F,int(size*945/f.getlength(text)))
 w=int(f.getlength(text))+64;im=Image.new('RGBA',(w,size+94));d=ImageDraw.Draw(im);d.text((32,20),text,font=f,fill=color,stroke_width=2,stroke_fill=(0,0,0,220));sh=Image.new('RGBA',im.size);sd=ImageDraw.Draw(sh);sd.text((35,28),text,font=f,fill=(0,0,0,230),stroke_width=4);sh=sh.filter(ImageFilter.GaussianBlur(5));sh.alpha_composite(im);return sh

photos={}
for name in ['cable','funda','cargador']:
 im=Image.open(R/(name+'.png')).convert('RGBA');f=min(292/im.width,310/im.height);im=im.resize((round(im.width*f),round(im.height*f)),Image.Resampling.LANCZOS);photos[name]=im
labels={name:outlined(text,36,G,False) for name,text,st in spec['accessories']}
for name,im in list(labels.items()):
 if im.width>300:labels[name]=im.resize((300,round(im.height*300/im.width)),Image.Resampling.LANCZOS)
grad=Image.new('RGBA',(1080,650));d=ImageDraw.Draw(grad)
for y in range(650):d.line((0,y,1080,y),fill=(0,0,0,int(140*math.sin(math.pi*y/650)**1.2)))

def guarantee(t,st,en,kind):
 q=t-st;im=Image.new('RGBA',(1000,470));d=ImageDraw.Draw(im)
 d.rounded_rectangle((12,8,988,458),radius=22,fill=(7,9,13,236),outline=(*G[:3],230),width=3)
 d.polygon([(12,8),(80,8),(12,76)],fill=G)
 if kind=='60-dias':
  title='GARANTÍA';typed=title[:min(len(title),int(max(0,q)/.037)+1)];f=ImageFont.truetype(a.F,97);d.text((500,30),typed,font=f,fill=WHITE,anchor='mt')
  if q<.35:
   x=500+f.getlength(typed)/2+12;d.line((x,45,x,128),fill=G,width=5)
  x=100+800*ease((q-.13)/.25);d.line((100,146,x,146),fill=G,width=7)
  num=outlined('60 DÍAS',190,G);paste(im,num,(1000-num.width)/2,155,scale=.78+.22*back((q-.15)/.18),alpha=clamp((q-.12)/.08))
  d.text((500,386),'EN IPHONE SEMINUEVOS',font=ImageFont.truetype(a.F,43),fill=WHITE,anchor='mt')
 else:
  title=outlined('1 AÑO',180,G);paste(im,title,(1000-title.width)/2,28)
  d.text((500,260),'GARANTÍA OFICIAL',font=ImageFont.truetype(a.F,64),fill=WHITE,anchor='mt');d.text((500,367),'EN EQUIPOS SELLADOS',font=ImageFont.truetype(a.F,43),fill=G,anchor='mt')
 return im

bill=Image.open(R/'dolar.png').convert('RGBA');bill.thumbnail((450,280),Image.Resampling.LANCZOS)
label=Image.new('RGBA',(320,142));ld=ImageDraw.Draw(label)
for y,text,size in [(0,'DESCUENTO EN',27),(42,'CARGADOR',36),(87,'ORIGINAL',36)]:ld.text((160,y),text,font=ImageFont.truetype(a.F,size),fill=G,anchor='mt')
labels['cargador']=label

namecaps={c[3]:c for c in spec['captions'] if c[3] in ['SELLADOS','SEMINUEVOS']}
nameplates={}
for name in ['SELLADOS','SEMINUEVOS']:
 im=Image.new('RGBA',(475,163));dd=ImageDraw.Draw(im);dd.rounded_rectangle((2,2,472,160),radius=15,fill=(8,10,14,237),outline=G,width=3)
 dd.text((237,16),'IPHONES',anchor='mt',font=ImageFont.truetype(a.F,29),fill=WHITE)
 f=ImageFont.truetype(a.I,80)
 if f.getlength(name)>435:f=ImageFont.truetype(a.I,int(80*435/f.getlength(name)))
 dd.text((237,57),name,anchor='mt',font=f,fill=G,stroke_width=1,stroke_fill=(0,0,0,255));nameplates[name]=im

def frame(t):
 out=Image.new('RGBA',(1080,1920));paste(out,grad,0,1120)
 d=ImageDraw.Draw(out)
 st=spec['precio_dolar']['inicio'];en=spec['precio_dolar']['fin']
 if st<=t<en:
  q=t-st;fade=min(clamp(q/.07),clamp((en-t)/.09));p=back(q/.18);paste(out,bill,560+60*(1-ease(q/.18)),860+35*(1-p),fade,scale=.84*(.8+.2*p),angle=-5*(1-ease(q/.18)))
  d=ImageDraw.Draw(out);d.line([(828,1130),(878,1180),(978,1060)],fill=(25,240,105,int(245*fade)),width=24,joint='curve')
 for st,en,kind in spec['accents']:
  if not st<=t<en:continue
  q=t-st;fade=min(clamp(q/.06),clamp((en-t)/.1));c=(25,244,108) if kind=='green' else (255,25,48);d.rectangle((0,0,1080,1920),fill=(*c,int(30*fade)))
  if kind=='red':
   ox=int(10*math.sin(q*50)*math.exp(-q*5));d.line((795+ox,270,970+ox,445),fill=(*c,int(245*fade)),width=27);d.line((970+ox,270,795+ox,445),fill=(*c,int(245*fade)),width=27)
  else:d.line([(832,340),(880,392),(982,274)],fill=(*c,int(245*fade)),width=21,joint='curve')
 # The item photographs are illustrative. Cable/case are included; charger is explicitly discounted.
 for j,(name,label,st) in enumerate(spec['accessories']):
  en=spec['accessories_end']
  if not st<=t<en:continue
  q=t-st;p=back(q/.19);fade=min(clamp(q/.05),clamp((en-t)/.08));x=70+j*310;y=820
  panel=Image.new('RGBA',(320,490));pd=ImageDraw.Draw(panel);pd.rounded_rectangle((1,1,319,489),radius=18,fill=(11,14,19,226),outline=(*G[:3],205),width=2);ph=photos[name];paste(panel,ph,(320-ph.width)/2,18+(330-ph.height)/2);lab=labels[name];paste(panel,lab,(320-lab.width)/2,350)
  paste(out,panel,x+55*(1-ease(q/.16)),y+45*(1-p),fade,scale=.86*(.75+.25*p),angle=(-5 if j%2 else 5)*(1-ease(q/.2)))
  if j<2:
   tag=outlined('INCLUIDO' if j==0 else 'INCLUIDA',24,WHITE,False);paste(out,tag,x+(320-tag.width)/2,1230,fade)
 for name,xx,side in [('SELLADOS',52,1),('SEMINUEVOS',552,-1)]:
  st=namecaps[name][0];en=namecaps['SEMINUEVOS'][1]
  if st<=t<en:
   q=t-st;p=back(q/.19);fade=min(clamp(q/.055),clamp((en-t)/.08));paste(out,nameplates[name],xx-side*95*(1-ease(q/.18)),1135+35*(1-p),fade,scale=.84*(.84+.16*p),angle=side*3*(1-ease(q/.18)))
   dd=ImageDraw.Draw(out);col=(*G[:3],int(235*fade))
   if name=='SELLADOS':dd.line([(255,1135),(255,1085),(345,1030)],fill=col,width=5)
   else:dd.line([(812,1298),(812,1350),(750,1410)],fill=col,width=5)
 for st,en,placed in a.words:
  if st in [namecaps['SELLADOS'][0],namecaps['SEMINUEVOS'][0]]:continue
  if not st<=t<en:continue
  if spec['accessories'][0][2] <= t < spec['accessories_end']:continue
  # Item labels are carried by the photo stickers to avoid duplicated words.
  if spec['accessories'][0][2]<=st<spec['accessories'][2][2] and '\n' not in next(c[2] for c in spec['captions'] if c[0]==st):continue
  for im,x,y,j,acc in placed:
   q=t-st-min(.19,j*.035)
   if q<0:continue
   p=back(q/.18);fade=min(clamp(q/.045),clamp((en-t)/.06));paste(out,im,x+(1-ease(q/.17))*(40 if j%2 else -40),y+32*(1-p),fade,scale=1.2-.2*p,angle=(3 if j%2 else -3)*(1-ease(q/.16)))
 for kind,(title,sub,st,en) in spec['cards'].items():
  if st<=t<en:
   q=t-st;im=guarantee(t,st,en,kind);fade=min(clamp(q/.06),clamp((en-t)/.08));paste(out,im,40+80*(1-ease(q/.16)),1100+40*(1-back(q/.18)),fade,scale=.90*(.85+.15*back(q/.18)),angle=-2*(1-ease(q/.18)))
 return out
if '--export-graphics' not in sys.argv:
 for t in [.5,3.2,12.0,14.0,22.0,23.7]:frame(t).save(R/f'overlay-{t}.png')
 sys.exit()
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(math.ceil(spec['duration']*30)):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0;print('GRAPHICS DONE',flush=True)
