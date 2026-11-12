from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.io import wavfile
import numpy as np,json,subprocess
r=Path('/workspace/rayban-01-v2');repo=Path('/workspace/edicion-videos');fonts=r/'fonts';fonts.mkdir(exist_ok=True)
for source,name in [('Montserrat.ttf','GomoryMontserrat'),('Montserrat-Italic.ttf','GomoryMontserratItalic')]:
 f=instantiateVariableFont(TTFont(repo/'materiales/fuentes/montserrat'/source),{'wght':850},inplace=False)
 for rec in f['name'].names:
  if rec.nameID in [1,4,6,16]:
   try:rec.string=name.encode(rec.getEncoding())
   except Exception:pass
 f.save(fonts/(name+'.ttf'))
def text(tx,size,col=(255,255,250,255),italic=False,maxw=900):
 f=ImageFont.truetype(str(fonts/('GomoryMontserratItalic.ttf' if italic else 'GomoryMontserrat.ttf')),size)
 if f.getlength(tx)>maxw:f=ImageFont.truetype(f.path,round(size*maxw/f.getlength(tx)))
 im=Image.new('RGBA',(round(f.getlength(tx))+50,f.size+65));sh=Image.new('RGBA',im.size);d=ImageDraw.Draw(sh);d.text((27,25),tx,font=f,fill=(0,0,0,245),stroke_width=3);sh=sh.filter(ImageFilter.GaussianBlur(4));ImageDraw.Draw(im).text((24,21),tx,font=f,fill=col);sh.alpha_composite(im);return sh
for name,tx,size,y,col,it in [('titulo','CASI PIERDO UNA VENTA',90,150,(255,255,250,255),False),('error','POR ESTE ERROR EN LA CÁMARA',83,245,(245,24,35,255),True),('modelo','ENTREGA · IPHONE 15 PRO MAX',51,140,(255,255,250,255),False),('marca','GOMORY IMPORTADOS',66,125,(255,255,250,255),True)]:
 out=Image.new('RGBA',(1080,1920));im=text(tx,size,col,it);out.alpha_composite(im,((1080-im.width)//2,y));out.save(r/f'{name}.png')
# Preserve the levelled stereo conversation and redesign only the soundtrack accents.
sr,v=wavfile.read('/workspace/rayban-01/voice.wav');N=round(84.472993*sr);v=v[:N].astype(float);v=np.pad(v,((0,max(0,N-len(v))),(0,0)));fx=np.zeros_like(v);events=[]
def add(x,at,g):
 if x.ndim==1:x=np.column_stack([x,x])
 i=round(at*sr);n=min(len(x),N-i);fx[i:i+n]+=x[:n]*g
for at,g in [(.10,.62),(.86,.22),(1.66,.20),(2.46,.19),(3.26,.17),(4.06,.15),(5.50,.30)]:
 u=np.arange(round(.18*sr))/sr;p=2*np.pi*(78*u+48*.012*(1-np.exp(-u/.012)));x=(np.sin(p)+.42*np.sin(2*p)+.23*np.sin(4*p))*np.exp(-u*28)*np.minimum(1,u/.001);add(x,at,g);events.append([at,'impacto/tensión',g])
u=np.arange(round(5.5*sr))/sr;drone=(np.sin(2*np.pi*82.4*u)+.75*np.sin(2*np.pi*87.31*u)+.30*np.sin(2*np.pi*164.8*u));drone*=np.minimum(u/.3,1)*np.minimum((5.5-u)/.5,1);add(drone,0,.014)
_,bank=wavfile.read(repo/'materiales/audio/efectos-aislados-anuncio-v11.wav')
for at,index,g in [(.15,8.48/1.12,.34),(.40,15.2/1.12,.22),(5.50,16.7/1.12,.26)]:
 i=round(index*sr);a=bank[i:i+round(.14*sr)].astype(float);a/=np.max(abs(a))+1e-12;add(a,at,g)
t=np.arange(N)/sr;fade=np.minimum(t/.008,1)*np.minimum((N-np.arange(N))/sr/.08,1)
wavfile.write(r/'effects.wav',sr,fx.astype(np.float32));wavfile.write(r/'mix.wav',sr,((v+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
(r/'audio-cambios.json').write_text(json.dumps({'voz':'V1 conservada','intro':'Suspenso tonal y pulsos hasta5.5s, impacto y acentos de cámara claramente presentes, sin rotura de vidrio que implique daño','eventos':events,'resto':'Conversación original sin música añadida'},ensure_ascii=False,indent=2))
