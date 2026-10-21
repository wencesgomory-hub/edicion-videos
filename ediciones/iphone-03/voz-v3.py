from pathlib import Path
import numpy as np,json,subprocess
from scipy.io import wavfile
from scipy.signal import stft,istft
from nara_wpe.wpe import wpe
R=Path('/workspace/interior-03-v3');old=Path('/workspace/interior-03');sr=48000;N=round((2.7+7.3+103/30)*sr)
pieces=[]
for j in range(3):
 r,x=wavfile.read(old/f'voice-{j}.wav');assert r==sr
 pieces.append(x[:round(2.7*sr)] if j==0 else x)
x=np.concatenate(pieces)[:N].astype(float)
_,_,Y=stft(x,fs=sr,nperseg=1024,noverlap=768,boundary='zeros',padded=True)
Z=wpe(Y[:,None,:],taps=12,delay=3,iterations=3)[:,0,:]
_,dry=istft(Z,fs=sr,nperseg=1024,noverlap=768,boundary=True);dry=dry[:N]
# Moderate original blend preserves consonants and avoids an overprocessed/boxed voice.
y=.65*dry+.35*x
wavfile.write(R/'voice-dereverb.wav',sr,y.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'voice-dereverb.wav'),'-af','highpass=f=75,equalizer=f=350:t=q:w=0.9:g=-2.5,equalizer=f=950:t=q:w=1:g=-1.3,equalizer=f=3400:t=q:w=0.8:g=1.4,acompressor=threshold=0.15:ratio=2:attack=14:release=110:makeup=1.1,loudnorm=I=-16:TP=-3:LRA=8','-ar','48000','-c:a','pcm_f32le',str(R/'voice-new.wav')],check=True)
(R/'tratamiento-voz.json').write_text(json.dumps({'fuente':'Audios originales sin el tratamiento espectral de V1/V2','dereverberacion':'WPE mono, 12 taps, delay 3, 3 iterations, mezcla 65% WPE +35% original','ecualizacion':'HP75, -2.5 dB350Hz, -1.3 dB950Hz, +1.4dB3400Hz','compresion':'2:1 ataque14ms release110ms','sin_cambios_de_tono_o_velocidad':True,'nota':'Reducción de reverberación estimada por modelo; no equivale a una grabación real con micrófono DJI.'},ensure_ascii=False,indent=2))
print('VOICE DONE',flush=True)
