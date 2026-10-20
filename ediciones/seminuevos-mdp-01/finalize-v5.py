from pathlib import Path
import json,numpy as np,subprocess
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
R=Path('/workspace/seminuevos-01-v5');B=Path('/workspace/seminuevos-01-v4');s=json.loads((R/'edit.json').read_text());cut0=6.4;cut1=6.6;delta=.2
shift=lambda t:t if t<cut0 else cut0 if t<cut1 else t-delta
for i,c in enumerate(s['clips']):
 if i==0:c['end']-=delta;c['output_end']-=delta
 else:c['output_start']-=delta;c['output_end']-=delta
s['duration']-=delta
s['captions']=[[shift(a),shift(b),t,k] for a,b,t,k in s['captions']];s['cards']={k:[v[0],v[1],shift(v[2]),shift(v[3])] for k,v in s['cards'].items()};s['accents']=[[shift(a),shift(b),k] for a,b,k in s['accents']];s['accessories']=[[n,l,shift(t)] for n,l,t in s['accessories']];s['accessories_end']=shift(s['accessories_end']);s['precio_dolar']['inicio']=shift(s['precio_dolar']['inicio']);s['precio_dolar']['fin']=shift(s['precio_dolar']['fin']);s['revision']='V5 final: corte inmediato tras por qué, sin insertos, cruz en réplicas, música +6 dB y acentos reforzados; voz original.';s['cruz_timing']='Estimación de alineación al pronunciar réplicas: 16.20–16.77 s, sin adelantar al inicio de la frase.';(R/'edit.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
sr,x=wavfile.read(R/'mix.wav');_,m=wavfile.read(B/'musica-extraida-0573.wav');x=x.astype(float)+m.astype(float)*.65
x=np.concatenate([x[:round(cut0*sr)],x[round(cut1*sr):]])
rng=np.random.default_rng(107);t=np.arange(round(.21*sr))/sr
# Firm dry impact at the requested 'pum, corte', with low body and short snap.
impact=(np.sin(2*np.pi*(48*t+85*.018*(1-np.exp(-t/.018))))*np.exp(-t*25)+.24*sosfilt(butter(2,[800,6000],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(t)))*np.exp(-t*95));impact/=max(abs(impact));idx=round(cut0*sr);x[idx:idx+len(t)]+=impact[:,None]*.23
# Single soft interface accent on the call to action, not a repeated metallic cue.
at=next(c[0] for c in s['captions'] if 'MENSAJE' in c[2]);t=np.arange(round(.16*sr))/sr;note=(np.sin(2*np.pi*880*t)+.35*np.sin(2*np.pi*1320*t))*np.exp(-t*36)*np.minimum(1,t/.002);note/=max(abs(note));idx=round(at*sr);x[idx:idx+len(t)]+=note[:,None]*.12
wavfile.write(R/'mix-final.wav',sr,x.astype(np.float32));subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix-final.wav'),'-af','alimiter=limit=0.80:level=false:latency=true','-c:a','pcm_f32le',str(R/'master.wav')],check=True)
