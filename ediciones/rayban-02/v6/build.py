from pathlib import Path
import subprocess
import numpy as np
from scipy.io import wavfile
r=Path('/workspace/rayban-02-v6');repo=Path('/workspace/edicion-videos')
sr,v=wavfile.read('/workspace/rayban-02/voz-editada.wav');sf,fx=wavfile.read('/workspace/rayban-02-v3/efectos.wav');assert sr==sf and v.shape==fx.shape
wavfile.write(r/'mix.wav',sr,(v.astype(float)+fx.astype(float)).astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'mix.wav'),'-af','alimiter=limit=0.84:level=false:latency=true','-c:a','pcm_f32le',str(r/'master.wav')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/'videos/reel-entrega-iphone-15-pro-revision-v5.mp4'),'-i',str(r/'master.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','87.683333','-movflags','+faststart',str(repo/'videos/reel-entrega-iphone-15-pro-revision-v6.mp4')],check=True)
