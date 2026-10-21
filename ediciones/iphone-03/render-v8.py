from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import subprocess,json,math
R=Path('/workspace/interior-03-v8');repo=Path('/workspace/edicion-videos');old=Path('/workspace/interior-03');A=2.7;B=10.;D=13+13/30
F=str(R/'Montserrat.ttf');I=str(R/'Montserrat-Italic.ttf')
C=F
M=F
def getfont(path,size):
 f=ImageFont.truetype(path,size)
 f.set_variation_by_axes([850 if path==I else 800])
 return f
# Direct-on-footage kinetic typography, matching the newly supplied visual reference.
# Exact font identity in reference cannot be confirmed; these are selected substitutes.
subs=[(.10,.65,['¡BASTA!'],'¡BASTA!',205),(.65,1.5,['¿hasta cuándo','vas a seguir'],'¿hasta cuándo',106),(1.5,2.13,['POSTERGANDO','cambiar tu'],'POSTERGANDO',126),(2.13,A,['IPHONE?'],'IPHONE?',149),(A,A+1.05,['con','NOSOTROS'],'NOSOTROS',113),(A+1.05,A+2.10,['terminá con las','EXCUSAS'],'EXCUSAS',119),(A+2.10,A+3.38,['los mejores','PRECIOS'],'PRECIOS',128),(A+3.38,A+4.32,['la mejor','CALIDAD'],'CALIDAD',126),(A+4.32,A+5.05,['GARANTÍA'],'GARANTÍA',138),(A+5.05,A+6.10,['accesorios','de REGALO'],'REGALO',120),(A+6.10,B,['¿qué más','podés pedir?'],'podés pedir?',111),(B,B+.82,['NO ESPERES','MÁS'],'MÁS',158),(B+.82,B+1.65,['mandanos','un MENSAJE'],'MENSAJE',119),(B+1.65,B+2.60,['que te','ASESORAMOS'],'ASESORAMOS',145),(B+2.60,D,['en tu próximo','EQUIPO'],'EQUIPO',124)]
def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3
cache=[]
for st,en,lines,key,sz in subs:
 rows=[]
 stylefont=M if key=='¡BASTA!' else (F if key in ['POSTERGANDO','GARANTÍA','CALIDAD'] else I)
 palette={'¡BASTA!':(255,61,64,255),'¿hasta cuándo':(255,91,88,255),'POSTERGANDO':(255,224,110,255),'PRECIOS':(255,224,90,255),'REGALO':(255,78,75,255),'GARANTÍA':(68,240,139,255),'MÁS':(255,72,69,255)}
 color=palette.get(key,(255,255,252,255))
 for line in lines:
  iskey=key is not None and key in line;font=getfont(stylefont if iskey else F,sz if iskey else 82)
  if font.getlength(line)>900:font=getfont(stylefont if iskey else F,round(font.size*900/font.getlength(line)))
  entries=[]
  for word in line.split():
   w=round(font.getlength(word))+46;h=font.size+74;im=Image.new('RGBA',(w,h));shadow=Image.new('RGBA',(w,h));sd=ImageDraw.Draw(shadow)
   sd.text((23,27),word,font=font,fill=(0,0,0,215),stroke_width=1);shadow=shadow.filter(ImageFilter.GaussianBlur(3))
   d=ImageDraw.Draw(im);d.text((22,23),word,font=font,fill=color if iskey and (key!='REGALO' or word=='REGALO') else (255,255,252,255),stroke_width=0);shadow.alpha_composite(im)
   entries.append((shadow,font.getlength(word)))
  rows.append((entries,font.getlength(' '),font.size,iskey))
 total_h=sum(x[2]+5 for x in rows);yy=1150-total_h/2;placed=[];j=0
 for k,(entries,space,size,iskey) in enumerate(rows):
  width=sum(w for _,w in entries)+space*(len(entries)-1);xx=(1080-width)/2+(16 if k%2 else -16)
  for im,w in entries:placed.append((im,xx-22,yy-20,j,iskey));xx+=w+space;j+=1
  yy+=size+5
 cache.append((st,en,placed))
# Warm diagonal light sweep for the opening; no plate or rectangle behind the title.
beam=Image.new('RGBA',(720,2100));bd=ImageDraw.Draw(beam)
for x in range(720):
 alpha=round(102*math.exp(-((x-360)/105)**2))
 bd.line((x,0,x,2100),fill=(255,231,183,alpha))
beam=beam.rotate(-18,Image.Resampling.BICUBIC,expand=True)
redbeam=Image.new('RGBA',beam.size,(255,67,63,0));redbeam.putalpha(beam.getchannel('A'))
def frame(t):
 out=Image.new('RGBA',(1080,1920))
 if 0<=t<.50:
  xx=round(-beam.width+(1080+beam.width)*(t/.50));out.alpha_composite(redbeam,(xx,-100))
 for cue,length,strength in [(A,.20,.55),(A+4.32,.18,.40),(B,.22,.50)]:
  if cue-.08<=t<cue-.08+length:
   phase=(t-cue+.08)/length;xx=round(-beam.width+(1080+beam.width)*phase)
   extra=(redbeam if cue==B else beam).copy();extra.putalpha(extra.getchannel('A').point(lambda a:int(a*strength)));out.alpha_composite(extra,(xx,-100))
 for st,en,placed in cache:
  if not st<=t<en:continue
  for im,x,y,j,key in placed:
   q=t-st-min(.15,j*.026)
   if q<0:continue
   p=ease(q/.125);fade=min(clamp(q/.022),clamp((en-t)/.035));scale=1.16-.16*p
   if st<.2:scale=1.25-.25*p
   pic=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.BICUBIC)
   if key:pic=pic.rotate(-2*(1-p),Image.Resampling.BICUBIC,expand=True)
   pic.putalpha(pic.getchannel('A').point(lambda a:int(a*fade)))
   out.alpha_composite(pic,(round(x+(im.width-pic.width)/2+((190 if st<.2 else 28) if j%2 else (-190 if st<.2 else -28))*(1-p)),round(y+(im.height-pic.height)/2+22*(1-p))))
 # Draw-on green check and pressure ring at the accessories cue, not an emoji.
 if A+4.32<=t<A+5.05 or A+5.05<=t<A+6.10:
  cue=A+4.32 if t<A+5.05 else A+5.05
  q=t-cue;progress=ease(q/.20);d=ImageDraw.Draw(out)
  center=(865,1015);rr=round(55+60*clamp(q/.38));alpha=round(95*(1-clamp(q/.38)))
  d.ellipse((center[0]-rr,center[1]-rr,center[0]+rr,center[1]+rr),outline=(48,238,132,alpha),width=5)
  points=[(810,1015),(852,1059),(935,947)]
  if progress<.4:
   z=progress/.4;end=(round(810+42*z),round(1015+44*z));d.line([points[0],end],fill=(63,244,140,255),width=16)
  else:
   z=(progress-.4)/.6;end=(round(852+83*z),round(1059-112*z));d.line([points[0],points[1],end],fill=(63,244,140,255),width=16,joint='curve')
 # A restrained cyan underline appears only at the guarantee, echoing the reference's cooler accent.
 if A+4.32<=t<A+5.05:
  d=ImageDraw.Draw(out);p=ease((t-A-4.32)/.2);d.line((330,1225,330+round(420*p),1225),fill=(68,240,139,235),width=5)
 return out
for t in [.30,1.1,2.35,5.3,8.1,11.2]:frame(t).save(R/f'overlay-{t}.png')
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(403):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0;print('GRAPHICS DONE',flush=True)
f="[0:v]trim=end_frame=81,setpts=PTS-STARTPTS,crop=900:1600:90:160,scale=1080:1920:flags=lanczos,setsar=1[a];[1:v]setpts=PTS-STARTPTS,setsar=1[b];[2:v]setpts=PTS-STARTPTS,setsar=1[c];[a][b][c]concat=n=3:v=1:a=0,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.12:t=fill:enable='between(t,2.666,2.733)',drawbox=x=0:y=0:w=iw:h=ih:color=0xCDEAF2@0.10:t=fill:enable='between(t,9.966,10.033)'[base];[base][3:v]overlay=shortest=1,format=yuv420p[v]"
cmd=['ffmpeg','-v','error','-y']
for j in range(3):cmd+=['-i',str(old/f'clip-{j}.mp4')]
cmd+=['-i',str(R/'graphics.mov'),'-i',str(R/'master.wav'),'-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','4:a','-t',str(D),'-c:v','libx264','-preset','fast','-crf','14','-threads','4','-c:a','aac','-b:a','256k','-movflags','+faststart',str(repo/'videos/anuncio-iphone-03-v8.mp4')]
(R/'montaje.json').write_text(json.dumps({'duracion':D,'source_cuts':[2.7,7.3,103/30],'voice':'V3 rehecha desde audios originales con WPE; sin nueva alteración','music_and_sfx':'Voz y música preservadas; pops de accesorios +1.5 dB aproximadamente, aire breve en cambios principales.','referencia':'WhatsApp Video 2026-10-21 at 10.35.37 AM.mp4','captions':subs,'estilo':'NO ESPERES MÁS grande con acento rojo y barrido rojo en cambio al cierre. Montserrat conservada; BASTA rojo y luz roja inicial, énfasis rojo en hasta cuándo, solo REGALO rojo dejando de blanco, GARANTÍA y tilde verdes; ASESORAMOS grande conservado. Paleta blanca/dorada; verde solo en tilde. Barridos cortos de luz en cambios principales. Palabras sobre video sin placas. Tilde verde dibujado en accesorios. Sin fotos.','identidad_fuente_referencia':'No puedo confirmar esto con certeza.'},ensure_ascii=False,indent=2));subprocess.run(cmd,check=True);print('V8 DONE',flush=True)
