from pathlib import Path
import subprocess
r=Path('/workspace/rayban-02');repo=Path('/workspace/edicion-videos')
model=repo/'ediciones/rayban-02/v1/modelo-ruido.rnnn'
if not model.exists():model=Path('/workspace/rayban-01-v3/speech.rnnn')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/'D8EB53EA-49A5-4D79-A8AD-B5872C04D7D1.mov'),'-vn','-ar','48000','-ac','2','-af',f'highpass=f=85,arnndn=m={model}:mix=0.35,equalizer=f=300:t=q:w=0.9:g=-1,equalizer=f=2800:t=q:w=0.8:g=1.3,acompressor=threshold=0.075:ratio=2:attack=10:release=130,loudnorm=I=-16:TP=-2:LRA=8','-c:a','pcm_f32le',str(r/'voice.wav')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'voice.wav'),'-ar','16000','-ac','1',str(r/'asr.wav')],check=True)
