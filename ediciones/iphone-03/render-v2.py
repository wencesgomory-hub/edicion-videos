from pathlib import Path
import subprocess,json,types,math
import numpy as np
from scipy.io import wavfile
from PIL import Image,ImageDraw
R=Path('/workspace/interior-03-v2');old=Path('/workspace/interior-03');repo=Path('/workspace/edicion-videos');sr=48000
cut=32/30;A=2.7;B=A+7.3;D=B+103/30;N=round(D*sr)
# Remove only the dead tail of the hook, leaving its completed phrase and start of movement.
_,v=wavfile.read(old/'voice.wav');v=np.concatenate([v[:round(A*sr)],v[round((113/30)*sr):]])[:N].astype(float);v=np.pad(v,(0,max(0,N-len(v))));v=np.column_stack([v,v])
_,m=wavfile.read(repo/'materiales/audio/musica-base-anuncio-v11.wav');m=m[:N].astype(float)*2.35
_,bank=wavfile.read(repo/'materiales/audio/efectos-aislados-anuncio-v11.wav');fx=np.zeros((N,2));refs={'thud':7.67/1.12,'snap':8.48/1.12,'wood':15.2/1.12,'bubble':16.7/1.12};ev=[]
def add(x,t,g):
 i=round(t*sr)
 if i<0:x=x[-i:];i=0
 e=min(N,i+len(x));x=x[:e-i]*g
 if x.ndim==1:x=x[:,None]
 if e>i:fx[i:e]+=x

def accent(t,kind,g):
 i=round(refs[kind]*sr);x=bank[i:i+round(.18*sr)].astype(float);x/=max(np.max(abs(x)),1e-9);add(x,t,g);ev.append([t,kind,g])
for t,k,g in [(.12,'thud',.50),(1.65,'snap',.36),(A,'thud',.48),(A+1.05,'snap',.39),(A+2.10,'wood',.48),(A+3.38,'snap',.44),(A+4.32,'thud',.48),(A+5.05,'bubble',.44),(A+6.10,'snap',.35),(B,'thud',.43),(B+.82,'snap',.47)]:accent(t,k,g)
# Actual air transition already used in the approved earlier ad.
_,air=wavfile.read('/workspace/ad-v9/fx.wav');air=air.astype(float)
if np.max(abs(air))>2:air/=32768
start=round((1.05/1.12-.12)*sr);whoosh=air[start:start+round(.18*sr)];whoosh/=max(np.max(abs(whoosh)),1e-9)
for t in [A,B]:add(whoosh,t-.12,.19)
fade=np.minimum(np.arange(N)/sr/.025,1)*np.minimum((N-np.arange(N))/sr/.12,1)
wavfile.write(R/'mix.wav',sr,((v+m+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
subs=[(.12,.58,'BASTA','BASTA'),(.58,1.65,'¿hasta\nCUÁNDO?','CUÁNDO?'),(1.65,A,'cambiar tu\nIPHONE','IPHONE'),(A,A+1.05,'con\nNOSOTROS','NOSOTROS'),(A+1.05,A+2.10,'con las\nEXCUSAS','EXCUSAS'),(A+2.10,A+3.38,'los mejores\nPRECIOS','PRECIOS'),(A+3.38,A+4.32,'la mejor\nCALIDAD','CALIDAD'),(A+4.32,A+5.05,'GARANTÍA','GARANTÍA'),(A+5.05,A+6.10,'accesorios de\nREGALO','REGALO'),(A+6.10,B,'¿qué más\nPODÉS PEDIR?','PODÉS PEDIR?'),(B,B+.82,'no esperes\nMÁS','MÁS'),(B+.82,B+1.95,'mandanos un\nMENSAJE','MENSAJE'),(B+1.95,D,'tu próximo\nEQUIPO','EQUIPO')]
a=types.ModuleType('approved');code=(repo/'ediciones/seminuevos-mdp-01/estilo-v11-palabras.py').read_text();code=code.replace("R=Path('/workspace/ad-v4');subs=json.loads((R/'subtitles.json').read_text())",'subs='+repr(subs));code=code.replace('if 14.3<=start<16.6 or 21.76<=start<24.7:normal_y=825-height/2','if False:normal_y=825-height/2');code=code.replace('size=118 if accent else 86','size=(175 if text=="BASTA" else 118) if accent else 86');exec(code,a.__dict__)
def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3
def frame(t):
 out=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(out)
 for y in range(1150,1650):d.line((0,y,1080,y),fill=(0,0,0,int(105*math.sin(math.pi*(y-1150)/500)**1.2)))
 for st,en,placed in a.words:
  if not st<=t<en:continue
  for im,x,y,j,acc in placed:
   q=t-st-min(.14,j*.025)
   if q<0:continue
   p=ease(q/.13);fade=min(clamp(q/.025),clamp((en-t)/.045));sc=1.13-.13*p
   pic=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.BICUBIC);pic.putalpha(pic.getchannel('A').point(lambda z:int(z*fade)))
   angle=(2 if j%2 else -2)*(1-p);pic=pic.rotate(angle,Image.Resampling.BICUBIC,expand=True)
   out.alpha_composite(pic,(int(x+(im.width-pic.width)/2+(22 if j%2 else -22)*(1-p)),int(y+(im.height-pic.height)/2+20*(1-p))))
 if A+4.32<=t<A+5.05:
  q=ease((t-A-4.32)/.12);d.line([(830,1080),(874,1128),(959,1018)],fill=(38,226,128,int(240*q)),width=17,joint='curve')
 return out
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'graphics.mov')],stdin=subprocess.PIPE)
for n in range(round(D*30)):p.stdin.write(frame(n/30).tobytes())
p.stdin.close();assert p.wait()==0;print('GRAPHICS DONE',flush=True)
# Hook crop reframes the distant source, then lands on the existing closer second take.
f="[0:v]trim=end_frame=81,setpts=PTS-STARTPTS,crop=984:1750:48:72,scale=1080:1920:flags=lanczos,setsar=1[a];[1:v]setpts=PTS-STARTPTS,setsar=1[b];[2:v]setpts=PTS-STARTPTS,setsar=1[c];[a][b][c]concat=n=3:v=1:a=0[base];[base][3:v]overlay=shortest=1,format=yuv420p[v]"
cmd=['ffmpeg','-v','error','-y']
for j in range(3):cmd+=['-i',str(old/f'clip-{j}.mp4')]
cmd+=['-i',str(R/'graphics.mov'),'-i',str(R/'master.wav'),'-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','4:a','-t',str(D),'-c:v','libx264','-preset','fast','-crf','14','-threads','4','-c:a','aac','-b:a','256k','-movflags','+faststart',str(repo/'videos/anuncio-iphone-03-v2.mp4')]
(R/'montaje.json').write_text(json.dumps({'duration':D,'hook_end':A,'cut_removed':[A,113/30],'speed':1,'captions':subs,'effects':ev,'style':'Tipografía animada blanca/amarilla original V11, por palabra. Sin fotos, sin accesorios ilustrados, sin carteles cian/rojo de V1.','source_clips':['IMG_0391','IMG_0378 editor 2','IMG_0381 3 espera']},ensure_ascii=False,indent=2));subprocess.run(cmd,check=True);print('V2 DONE',flush=True)
