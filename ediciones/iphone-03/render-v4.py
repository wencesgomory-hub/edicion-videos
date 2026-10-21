from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import subprocess,json,math
R=Path('/workspace/interior-03-v4');repo=Path('/workspace/edicion-videos');old=Path('/workspace/interior-03');A=2.7;B=10.;D=13+13/30
F='/usr/share/fonts/openai-sans/OpenAISans-Bold.woff2';I='/usr/share/fonts/opentype/urw-base35/NimbusSans-BoldItalic.otf'
# Direct-on-footage kinetic typography, matching the newly supplied visual reference.
# Exact font identity in reference cannot be confirmed; these are selected substitutes.
subs=[(.10,.58,['BASTA'],'BASTA',191),(.58,1.5,['¿hasta cuándo','vas a seguir'],None,84),(1.5,2.13,['postergando','cambiar tu'],'postergando',116),(2.13,A,['IPHONE?'],'IPHONE?',149),(A,A+1.05,['con','NOSOTROS'],'NOSOTROS',113),(A+1.05,A+2.10,['terminá con las','EXCUSAS'],'EXCUSAS',119),(A+2.10,A+3.38,['los mejores','PRECIOS'],'PRECIOS',128),(A+3.38,A+4.32,['la mejor','CALIDAD'],'CALIDAD',126),(A+4.32,A+5.05,['GARANTÍA'],'GARANTÍA',138),(A+5.05,A+6.10,['accesorios','de REGALO'],'REGALO',120),(A+6.10,B,['¿qué más','podés pedir?'],'podés pedir?',111),(B,B+.82,['no esperes','MÁS'],'MÁS',133),(B+.82,B+1.95,['mandanos','un MENSAJE'],'MENSAJE',119),(B+1.95,D,['tu próximo','EQUIPO'],'EQUIPO',124)]
def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3
cache=[]
for st,en,lines,key,sz in subs:
 rows=[]
 for line in lines:
  iskey=key is not None and key in line;font=ImageFont.truetype(I if iskey else F,sz if iskey else 82)
  if font.getlength(line)>900:font=ImageFont.truetype(I if iskey else F,round(font.size*900/font.getlength(line)))
  entries=[]
  for word in line.split():
   w=round(font.getlength(word))+46;h=font.size+74;im=Image.new('RGBA',(w,h));shadow=Image.new('RGBA',(w,h));sd=ImageDraw.Draw(shadow)
   sd.text((25,31),word,font=font,fill=(0,0,0,225),stroke_width=3);shadow=shadow.filter(ImageFilter.GaussianBlur(4))
   d=ImageDraw.Draw(im);d.text((22,23),word,font=font,fill=(255,255,252,255),stroke_width=1,stroke_fill=(10,12,16,160));shadow.alpha_composite(im)
   entries.append((shadow,font.getlength(word)))
  rows.append((entries,font.getlength(' '),font.size,iskey))
 total_h=sum(x[2]+5 for x in rows);yy=1150-total_h/2;placed=[];j=0
 for k,(entries,space,size,iskey) in enumerate(rows):
  width=sum(w for _,w in entries)+space*(len(entries)-1);xx=(1080-width)/2+(16 if k%2 else -16)
  for im,w in entries:placed.append((im,xx-22,yy-20,j,iskey));xx+=w+space;j+=1
  yy+=size+5
 cache.append((st,en,placed))
def frame(t):
 out=Image.new('RGBA',(1080,1920))
 for st,en,placed in cache:
  if not st<=t<en:continue
  for im,x,y,j,key in placed:
   q=t-st-min(.15,j*.026)
   if q<0:continue
   p=ease(q/.125);fade=min(clamp(q/.022),clamp((en-t)/.035));scale=1.16-.16*p
   pic=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.BICUBIC)
   if key:pic=pic.rotate(-2*(1-p),Image.Resampling.BICUBIC,expand=True)
   pic.putalpha(pic.getchannel('A').point(lambda a:int(a*fade)))
   out.alpha_composite(pic,(round(x+(im.width-pic.width)/2+(28 if j%2 else -28)*(1-p)),round(y+(im.height-pic.height)/2+22*(1-p))))
 # A restrained cyan underline appears only at the guarantee, echoing the reference's cooler accent.
 if A+4.32<=t<A+5.05:
  d=ImageDraw.Draw(out);p=ease((t-A-4.32)/.2);d.line((330,1225,330+round(420*p),1225),fill=(180,219,226,230),width=5)
 return out
for t in [.30,1.1,2.35,5.3,8.1,11.2]:frame(t).save(R/f'overlay-{t}.png')
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(403):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0;print('GRAPHICS DONE',flush=True)
f="[0:v]trim=end_frame=81,setpts=PTS-STARTPTS,crop=900:1600:90:160,scale=1080:1920:flags=lanczos,setsar=1[a];[1:v]setpts=PTS-STARTPTS,setsar=1[b];[2:v]setpts=PTS-STARTPTS,setsar=1[c];[a][b][c]concat=n=3:v=1:a=0,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.12:t=fill:enable='between(t,2.666,2.733)',drawbox=x=0:y=0:w=iw:h=ih:color=0xCDEAF2@0.10:t=fill:enable='between(t,9.966,10.033)'[base];[base][3:v]overlay=shortest=1,format=yuv420p[v]"
cmd=['ffmpeg','-v','error','-y']
for j in range(3):cmd+=['-i',str(old/f'clip-{j}.mp4')]
cmd+=['-i',str(R/'graphics.mov'),'-i','/workspace/interior-03-v3/master.wav','-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','4:a','-t',str(D),'-c:v','libx264','-preset','fast','-crf','14','-threads','4','-c:a','aac','-b:a','256k','-movflags','+faststart',str(repo/'videos/anuncio-iphone-03-v4.mp4')]
(R/'montaje.json').write_text(json.dumps({'duracion':D,'source_cuts':[2.7,7.3,103/30],'voice':'V3 rehecha desde audios originales con WPE; sin nueva alteración','music_and_sfx':'Mezcla V3 conservada','referencia':'WhatsApp Video 2026-10-21 at 10.35.37 AM.mp4','captions':subs,'estilo':'Texto blanco con sombra, jerarquías de peso y tamaño, énfasis inclinados, palabras animadas sobre video sin placas ni recuadros. Cortes con destello de 2 fotogramas y encuadre inicial más cercano. Sin fotos ni clips ajenos insertados.','identidad_fuente_referencia':'No puedo confirmar esto con certeza.'},ensure_ascii=False,indent=2));subprocess.run(cmd,check=True);print('V4 DONE',flush=True)
