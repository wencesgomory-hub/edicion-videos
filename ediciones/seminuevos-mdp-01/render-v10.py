from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
from PIL import Image
R=Path('/workspace/seminuevos-01-v10');repo=Path('/workspace/edicion-videos');sr=48000
s=json.loads(Path('/workspace/seminuevos-01-v9/montaje.json').read_text());D=s['duration'];N=round(D*sr)
def load(name):
 r,x=wavfile.read('/workspace/seminuevos-01-v9/'+name);assert r==sr;return x.astype(float)
v=load('voz.wav');music=load('musica.wav')*10**(3/20);fx=load('efectos.wav')
# Short telephone texture on the hook-to-explanation phrase; no speed/pitch change.
l=round(5.6*sr);h=round(6.4*sr);part=v[l:h].copy();bp=sosfilt(butter(2,[330,3100],btype='bandpass',fs=sr,output='sos'),part,axis=0)
bp*=np.sqrt(np.mean(part*part))/(np.sqrt(np.mean(bp*bp))+1e-12)
f=np.minimum(np.arange(h-l)/sr/.025,1)*np.minimum((h-l-np.arange(h-l))/sr/.025,1)
v[l:h]=part*(1-.58*f[:,None])+bp*.58*f[:,None]
source_sr,source=wavfile.read('/workspace/ad-v10/effects.wav');assert source_sr==sr
old=json.loads(Path('/workspace/seminuevos-01-v9/eventos.json').read_text());rng=np.random.default_rng(1010)
def add(x,at,g=1):
 i=round(at*sr);e=min(N,i+len(x));x=x[:e-i]*g
 if x.ndim==1:x=x[:,None]
 fx[i:e]+=x
refs={'bubble':16.7/1.12,'wood':15.2/1.12,'low-pop':24.86/1.12}
# Remove the three V9 accessory accents before putting three contrasting textures in their place.
for (_,_,at),kind in zip(s['accessories'],['bubble','wood','low-pop']):
 i=round(refs[kind]*sr);x=source[i:i+round(.18*sr)].astype(float);x*=.47/(np.max(abs(x))+1e-12);add(x,at,-1)
# Rounded bubble, crisp snap, then an airy rising flick: no repeated sequence of dings.
i=round(16.7/1.12*sr);x=source[i:i+round(.18*sr)].astype(float);add(x,s['accessories'][0][2],.49/(np.max(abs(x))+1e-12))
i=round(8.48/1.12*sr);x=source[i:i+round(.18*sr)].astype(float);add(x,s['accessories'][1][2],.45/(np.max(abs(x))+1e-12))
t=np.arange(round(.16*sr))/sr;air=sosfilt(butter(2,[900,7500],btype='bandpass',fs=sr,output='sos'),rng.normal(size=len(t)));air*=np.sin(np.pi*t/.16)**2;air/=max(abs(air));add(air,s['accessories'][2][2]-.06,.32)
# One concise metallic 'bim' at the moving opening, never repeated under equipment.
t=np.arange(round(.28*sr))/sr;bim=sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*d) for a,f,d in [(1,523,19),(.32,1049,26),(.18,1481,33)])*np.minimum(1,t/.0015);bim/=max(abs(bim));add(bim,.015,.30)
# Subtle reverse air pickups for major chapter changes, not each word.
for at in [6.4,16.92,21.2]:
 t=np.arange(round(.13*sr))/sr;x=sosfilt(butter(2,[700,6000],btype='bandpass',fs=sr,output='sos'),rng.normal(size=len(t)));x*=np.sin(np.pi*t/.13)**2;x/=max(abs(x));add(x,at-.10,.16)
fade=np.minimum(np.arange(N)/sr/.02,1)*np.minimum((N-np.arange(N))/sr/.14,1)
wavfile.write(R/'mezcla.wav',sr,((v+music+fx)*fade[:,None]).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mezcla.wav'),'-af','alimiter=limit=0.84:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
# Gentle colored edge light, keeping face, products and white/gold text legible.
y,x=np.mgrid[0:1920,0:1080]
for name,c,xx in [('amber',(255,152,37),0),('cyan',(26,177,246),1080),('green',(28,220,130),1080)]:
 a=np.exp(-(((x-xx)/250)**2+((y-720)/750)**2))*37
 rgba=np.zeros((1920,1080,4),dtype=np.uint8);rgba[:,:,:3]=c;rgba[:,:,3]=a.astype(np.uint8);Image.fromarray(rgba).save(R/(name+'.png'))
f="[0:v][2:v]overlay=enable='between(t,0,6.4)+between(t,25.73,30.77)':eof_action=repeat[a];[a][3:v]overlay=enable='between(t,6.4,14.85)+between(t,17.08,21.2)':eof_action=repeat[b];[b][4:v]overlay=enable='between(t,21.2,24.80)':eof_action=repeat,format=yuv420p[v]"
cmd=['ffmpeg','-v','error','-y','-i',str(repo/'videos/anuncio-seminuevos-mdp-01-v9.mp4'),'-i',str(R/'master.wav')]
for name in ['amber','cyan','green']:cmd+=['-loop','1','-framerate','30','-i',str(R/(name+'.png'))]
cmd+=['-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','1:a:0','-t',str(D),'-c:v','libx264','-preset','fast','-crf','14','-threads','4','-c:a','aac','-b:a','256k','-movflags','+faststart',str(repo/'videos/anuncio-seminuevos-mdp-01-v10.mp4')]
s.update(version='v10',revision='Música V11 +3 dB, bim inicial, accesorios variados, transiciones de aire, textura telefónica breve a 1x y luces de borde ámbar/cian/verde.',salida='videos/anuncio-seminuevos-mdp-01-v10.mp4');(R/'montaje.json').write_text(json.dumps(s,ensure_ascii=False,indent=2));(R/'cambios-audio.json').write_text(json.dumps({'musica_db_sobre_v9':3,'voz_textura_intervalo':[5.6,6.4],'velocidad':1,'accesorios':['bubble V11','snap V11','aire ascendente'],'intro':'bim único 0.015 s','cajas':'Original de V8 conservado'},ensure_ascii=False,indent=2))
subprocess.run(cmd,check=True);print('V10 DONE',flush=True)
