from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import json,math,subprocess,sys
R=Path('/workspace/seminuevos-01');spec=json.loads((R/'edit.json').read_text());W,H=1080,1920
F='/usr/share/fonts/openai-sans/OpenAISans-Bold.woff2';I='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf';GREEN=(183,255,82,255);WHITE=(255,255,251,255)
def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3
def paste(out,im,x,y,alpha=1,scale=1):
 if alpha<=0:return
 if abs(scale-1)>.001:
  w,h=im.size;im=im.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.Resampling.BICUBIC);x+=(w-im.width)/2;y+=(h-im.height)/2
 if alpha<.999:im=im.copy();im.putalpha(im.getchannel('A').point(lambda a:int(a*alpha)))
 out.alpha_composite(im,(int(x),int(y)))
words=[]
for st,en,text,key in spec['captions']:
 lines=text.split('\n');sizes=[min(116 if key in l else 78,int((116 if key in l else 78)*940/max(1,ImageFont.truetype(I if key in l else F,116 if key in l else 78).getlength(l)))) for l in lines];y=1450-sum(s+14 for s in sizes)/2;placed=[];index=0
 for l,size in zip(lines,sizes):
  acc=key in l;font=ImageFont.truetype(I if acc else F,size);x=(1080-font.getlength(l))/2
  for word in l.split():
   width=int(font.getlength(word));im=Image.new('RGBA',(width+50,size+80));d=ImageDraw.Draw(im);d.text((25,25),word,font=font,fill=GREEN if acc else WHITE,stroke_width=2,stroke_fill=(0,0,0,230))
   sh=Image.new('RGBA',im.size);sd=ImageDraw.Draw(sh);sd.text((25,31),word,font=font,fill=(0,0,0,225),stroke_width=4);sh=sh.filter(ImageFilter.GaussianBlur(4));sh.alpha_composite(im);placed.append((sh,x-25,y-25,index));index+=1;x+=font.getlength(word+' ')
  y+=size+14
 words.append((st,en,placed))
def card(title,sub,color=GREEN):
 im=Image.new('RGBA',(940,250));d=ImageDraw.Draw(im);d.rounded_rectangle((3,3,937,247),radius=24,fill=(12,21,22,239),outline=color,width=4)
 font=ImageFont.truetype(I,110);d.text((470,20),title,font=font,fill=color,anchor='mt');d.text((470,154),sub,font=ImageFont.truetype(F,40),fill=WHITE,anchor='mt');return im
cards={k:card(v[0],v[1]) for k,v in spec['cards'].items()}
grad=Image.new('RGBA',(1080,600));d=ImageDraw.Draw(grad)
for y in range(600):d.line((0,y,1080,y),fill=(0,8,10,int(140*math.sin(math.pi*y/600)**1.2)))
# Thin animated framing accents preserve the real room and skin tones.
def frame(t):
 out=Image.new('RGBA',(W,H));paste(out,grad,0,1130)
 d=ImageDraw.Draw(out)
 for st,en,kind in spec['accents']:
  if not st<=t<en:continue
  q=t-st;a=min(clamp(q/.06),clamp((en-t)/.1));c=(28,246,113) if kind=='green' else (255,35,57)
  d.rectangle((0,0,W,H),fill=(*c,int(25*a)))
  if kind=='red':
   ox=int(8*math.sin(q*55)*math.exp(-q*6));d.line((800+ox,290,970+ox,460),fill=(*c,int(245*a)),width=25);d.line((970+ox,290,800+ox,460),fill=(*c,int(245*a)),width=25)
  else:d.line([(838,350),(886,398),(985,280)],fill=(*c,int(245*a)),width=20,joint='curve')
 for k,(title,sub,st,en) in spec['cards'].items():
  if st<=t<en:
   q=t-st;a=min(clamp(q/.08),clamp((en-t)/.1));paste(out,cards[k],70+70*(1-ease(q/.17)),1320+32*(1-ease(q/.17)),a,scale=.9+.1*ease(q/.17))
 for st,en,placed in words:
  if not st<=t<en:continue
  for im,x,y,j in placed:
   q=t-st-min(j*.027,.1)
   if q<0:continue
   a=min(clamp(q/.04),clamp((en-t)/.055));p=ease(q/.13);paste(out,im,x+(1-p)*(32 if j%2 else -32),y+24*(1-p),a,1.12-.12*p)
 # Local offer badge: appears in intro only, with a restrained slide.
 if .06<=t<1.28:
  a=min(clamp((t-.06)/.10),clamp((1.28-t)/.1));im=Image.new('RGBA',(610,82));dd=ImageDraw.Draw(im);dd.rounded_rectangle((0,0,609,81),radius=18,fill=(13,23,24,235),outline=GREEN,width=2);dd.text((305,17),'MAR DEL PLATA',anchor='mt',font=ImageFont.truetype(F,43),fill=GREEN);paste(out,im,235,230-25*(1-ease((t-.06)/.16)),a)
 return out
if '--preview' in sys.argv:
 for t in [.8,7.5,19,21,25.2]:frame(t).save(R/f'overlay-{t}.png')
 sys.exit()
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(math.ceil(spec['duration']*30)):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0
