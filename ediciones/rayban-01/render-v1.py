from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.io import wavfile
import numpy as np,subprocess,json
r=Path('/workspace/rayban-01');repo=Path('/workspace/edicion-videos');source=repo/'9869B4DA-35D1-4B40-B519-43BDC03C8FC3.mov';sr=48000;D=84.472993;N=round(D*sr)
# Preserve the continuous conversation, original speed and stereo perspective.
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-vn','-ar',str(sr),'-ac','2','-af','highpass=f=85,equalizer=f=320:t=q:w=0.9:g=-1.5,equalizer=f=2900:t=q:w=0.8:g=1.5,acompressor=threshold=0.075:ratio=2.0:attack=10:release=130:makeup=1.0,loudnorm=I=-16:TP=-2:LRA=9','-c:a','pcm_f32le',str(r/'voice.wav')],check=True)
_,v=wavfile.read(r/'voice.wav');v=v[:N].astype(float);v=np.pad(v,((0,max(0,N-len(v))),(0,0)));fx=np.zeros_like(v)
def add(x,at,g):
 i=round(at*sr);n=min(len(x),N-i)
 if x.ndim==1:x=np.column_stack([x,x])
 fx[i:i+n]+=x[:n]*g
for at,f,g in [(.10,84,.25),(.35,98,.13),(.65,110,.12)]:
 u=np.arange(round(.14*sr))/sr;p=2*np.pi*(f*u+28*.012*(1-np.exp(-u/.012)));x=(np.sin(p)+.3*np.sin(2*p))*np.exp(-u*32)*np.minimum(1,u/.0015);add(x,at,g)
u=np.arange(round(.14*sr))/sr;x=np.sin(2*np.pi*(400*u+300*u*u/.14))*np.sin(np.pi*u/.14)**2;add(x,3.,.075)
u=np.arange(round(.12*sr))/sr;x=(np.sin(2*np.pi*1174*u)+.16*np.sin(2*np.pi*1761*u))*np.exp(-u*42)*np.minimum(1,u/.002);add(x,80.8,.09)
fade=np.minimum(np.arange(N)/sr/.008,1)*np.minimum((N-np.arange(N))/sr/.08,1)
wavfile.write(r/'effects.wav',sr,fx.astype(np.float32));wavfile.write(r/'mix.wav',sr,((v+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.89:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
F=repo/'materiales/fuentes/montserrat/Montserrat.ttf';I=repo/'materiales/fuentes/montserrat/Montserrat-Italic.ttf'
def text(tx,size,color=(255,255,250,255),italic=False,weight=850,maxw=890):
 def font(n):
  f=ImageFont.truetype(str(I if italic else F),n);f.set_variation_by_axes([weight]);return f
 f=font(size)
 if f.getlength(tx)>maxw:f=font(round(size*maxw/f.getlength(tx)))
 im=Image.new('RGBA',(round(f.getlength(tx))+50,f.size+65));shadow=Image.new('RGBA',im.size);d=ImageDraw.Draw(shadow);d.text((27,26),tx,font=f,fill=(0,0,0,230),stroke_width=3);shadow=shadow.filter(ImageFilter.GaussianBlur(5));d=ImageDraw.Draw(im);d.text((24,21),tx,font=f,fill=color);shadow.alpha_composite(im);return shadow

def canvas(lines,gradient=False):
 out=Image.new('RGBA',(1080,1920))
 if gradient:
  d=ImageDraw.Draw(out)
  for y in range(1000,1610):d.line((0,y,1080,y),fill=(0,0,0,round(95*np.sin(np.pi*(y-1000)/610))))
 for tx,size,y,col,italic in lines:
  im=text(tx,size,col,italic);out.alpha_composite(im,((1080-im.width)//2,y))
 return out
white=(255,255,250,255);gold=(255,224,90,255);red=(239,32,44,255)
# Headlines reflect the user's requested teaser; no unsupported claim that the device was damaged.
canvas([('CASI PIERDO',109,1110,white,False)],True).save(r/'hook-a.png')
canvas([('ESTA VENTA',133,1245,white,True)]).save(r/'hook-b.png')
x=canvas([('POR ESTE DETALLE…',71,1415,white,False)]);ImageDraw.Draw(x).line((455,1540,625,1540),fill=red,width=4);x.save(r/'hook-c.png')
canvas([('ENTREGA · IPHONE 15 PRO MAX',51,150,white,False)]).save(r/'modelo.png')
canvas([('EQUIPO + GARANTÍA',69,1420,white,True)]).save(r/'garantia.png')
canvas([('GOMORY IMPORTADOS',77,1370,white,True),('ENTREGA REAL',53,1485,white,False)]).save(r/'cierre.png')
inputs=['ffmpeg','-v','error','-y','-i',str(source)]
assets=[('hook-a.png',.10,3.),('hook-b.png',.35,3.),('hook-c.png',.65,3.),('modelo.png',3.20,7.),('garantia.png',67.,70.),('cierre.png',80.8,D)]
for name,st,en in assets:inputs+=['-loop','1','-framerate','30','-i',str(r/name)]
inputs+=['-i',str(r/'master.wav')]
f=["[0:v]fps=30,eq=contrast=1.025:brightness=0.002:saturation=1.02:gamma=1.02,hue=s=0:enable='lt(t,3.0)',split=2[bgin][fgin]",'[bgin]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.13:saturation=0.65[bg]','[fgin]scale=1080:1440:flags=lanczos,setsar=1[fg]','[bg][fg]overlay=0:240,setsar=1[v0]']
for i,(name,st,en) in enumerate(assets,1):f.append(f"[v{i-1}][{i}:v]overlay=0:0:enable='between(t,{st},{en})':eof_action=repeat[v{i}]")
f.append(f'[v{len(assets)}]format=yuv420p[v]')
cmd=inputs+['-filter_complex_threads','2','-filter_complex',';'.join(f),'-map','[v]','-map',f'{len(assets)+1}:a','-t',str(D),'-c:v','libx264','-preset','veryfast','-crf','18','-maxrate','7500k','-bufsize','15000k','-threads','4','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/'videos/entrega-iphone-15-pro-max-rayban-v1.mp4')]
print('RENDER START',flush=True);subprocess.run(cmd,check=True)
(r/'montaje.json').write_text(json.dumps({'fuente':source.name,'duracion_fuente':D,'fuente_resolucion':[720,960],'fuente_fps':50,'salida':[1080,1920,30],'velocidad':1,'recortes_temporales':False,'composicion':'Captura3:4 completa centrada con extensiones desenfocadas9:16; sin recortar manos ni rostros','gancho':'CASI PIERDO ESTA VENTA POR ESTE DETALLE… (propuesta del usuario)','blanco_negro':[0,3],'rotulos':assets,'audio':'Conversación estéreo original con EQ/compresión y nivelación moderada; efectos discretos de entrada y cierre; sin música añadida','precaucion':'No se confirma daño en cámara ni se inventa una explicación al detalle. No se subtitula literalmente ASR incierto.','nota':'Conservar conversación/entrega a1x, sin congelado inicial ni imágenes ajenas.'},ensure_ascii=False,indent=2));print('DONE',flush=True)
