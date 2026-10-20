from pathlib import Path
import json,subprocess
import numpy as np
from scipy.io import wavfile
R=Path('/workspace/seminuevos-01-v9');repo=Path('/workspace/edicion-videos');sr=48000
s=json.loads(Path('/workspace/seminuevos-01-v8/edit.json').read_text());D=s['duration'];N=round(D*sr)
def load(p):
 r,x=wavfile.read(p);assert r==sr
 return x.astype(float)/(32768 if x.dtype==np.int16 else 1)
def stereo(x):return np.column_stack([x,x]) if x.ndim==1 else x
v=load('/workspace/seminuevos-01-v4/voice.wav');v=np.concatenate([v[:round(6.4*sr)],v[round(6.6*sr):]])
i=round(745/30*sr);v=np.concatenate([v[:i],np.zeros(round(.9*sr)),v[i:]])[:N];v=stereo(v)*1.03*.65
music=stereo(load('/workspace/ad-v9/music.wav'))[:N].copy()
# Original approved music stem: same tempo and timbre, no regeneration.
# Match its music/voice relationship to the approved V11 at the current voice level.
oldvoice=stereo(load('/workspace/ad-v11/voz-clara.wav'))*1.08
ratio=np.sqrt(np.mean(v*v))/np.sqrt(np.mean(oldvoice*oldvoice))
music*=ratio
fx=np.zeros((N,2));events=[]
source=stereo(load('/workspace/ad-v10/effects.wav'))
def add(x,at,g=1):
 x=stereo(x);i=round(at*sr);e=min(N,i+len(x))
 if e>i:fx[i:e]+=x[:e-i]*g
# Reuse actual isolated effects rendered for approved V10/V11.
refs={'thud':7.67/1.12,'snap':8.48/1.12,'wood':15.2/1.12,'bubble':16.7/1.12,'low-pop':24.86/1.12}
def effect(at,kind,peak):
 i=round(refs[kind]*sr);x=source[i:i+round(.18*sr)].copy();x*=peak/(np.max(abs(x))+1e-12);add(x,at);events.append(dict(at=at,kind=kind,source='V10/V11 isolated effect',peak=peak))
# Accent the message, rather than every subtitle word.
effect(.07,'snap',.34)
effect(2.8,'wood',.37)
effect(6.4,'thud',.40)
effect(7.30,'bubble',.43)
effect(7.70,'snap',.39)
for (name,label,at),kind in zip(s['accessories'],['bubble','wood','low-pop']):effect(at,kind,.47)
effect(16.20,'thud',.48)
effect(18.27,'snap',.32)
effect(21.2,'thud',.43)
effect(22.97,'bubble',.41)
cta=next(c[0] for c in s['captions'] if c[3]=='MENSAJE');effect(cta,'snap',.38)
# Retain the original box recording requested in V8.
add(load('/workspace/seminuevos-01-v8/cajas-original.wav'),745/30)
# Brief lead-in from the already approved moving intro, no freeze or extra time.
intro=source[:round(.34*sr)];add(intro,0,.55)
fade=np.minimum(np.arange(N)/sr/.025,1)*np.minimum((N-np.arange(N))/sr/.14,1)
mix=(v+music+fx)*fade[:,None]
for name,x in [('voz.wav',v),('musica.wav',music),('efectos.wav',fx),('mezcla.wav',mix)]:wavfile.write(R/name,sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mezcla.wav'),'-af','alimiter=limit=0.84:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
s.update(version='v9',revision='Audio reconstruido con música y efectos aislados reales de V10/V11; imagen V8 intacta.',salida='videos/anuncio-seminuevos-mdp-01-v9.mp4');s['audio_fuentes']={'musica':'/workspace/ad-v9/music.wav','efectos':'/workspace/ad-v10/effects.wav','voz':'V8 misma voz a 1x','cajas':'Audio original conservado'}
(R/'montaje.json').write_text(json.dumps(s,ensure_ascii=False,indent=2));(R/'eventos.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/'videos/anuncio-seminuevos-mdp-01-v8.mp4'),'-i',str(R/'master.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-t',str(D),'-movflags','+faststart',str(repo/s['salida'])],check=True)
print('V9 DONE; music ratio',ratio,'voice RMS',np.sqrt(np.mean(v*v)),'music RMS',np.sqrt(np.mean(music*music)))
