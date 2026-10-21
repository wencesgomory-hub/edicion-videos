from pathlib import Path
import numpy as np,subprocess,json
from scipy.io import wavfile
R=Path('/workspace/iphone-04-v2');repo=Path('/workspace/edicion-videos');sr=48000;cut=7/30;D=29.3-cut
# Start at con solo, preserving the word; early boundary checked on .18/.24 excerpts.
_,full=wavfile.read(R/'mix.wav');_,fx=wavfile.read(R/'effects.wav');x=full[round(cut*sr):].copy();x[:round(.3*sr)]+=fx[:round(.3*sr)];x[:round(.003*sr)]*=np.linspace(0,1,round(.003*sr))[:,None];wavfile.write(R/'mix-start-final.wav',sr,x.astype(np.float32))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'mix-start-final.wav'),'-af','alimiter=limit=0.82:level=false:latency=true','-c:a','pcm_f32le',str(R/'master-final.wav')],check=True)
# Five extra source frames restore the full word before the originally rendered start.
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(cut),'-i',str(repo/'86F3673D-C971-40E3-ACC4-CF51DB8EE3E4.MP4'),'-i',str(R/'graphics.mov'),'-filter_complex_threads','4','-filter_complex','[0:v]fps=30,scale=1080:1920:in_range=pc:out_range=tv:flags=lanczos,setsar=1,eq=contrast=1.04:brightness=0.003:saturation=1.035:gamma=1.045[b];[b][1:v]overlay,format=yuv420p[v]','-map','[v]','-frames:v','5','-an','-c:v','libx264','-preset','fast','-crf','15','-threads','4',str(R/'prefix.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/'videos/anuncio-iphone-04-v2.mp4'),'-map','0:v','-c','copy',str(R/'rendered-video-only.mp4')],check=True)
(R/'concat.txt').write_text("file 'prefix.mp4'\nfile 'rendered-video-only.mp4'\n")
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(R/'concat.txt'),'-i',str(R/'master-final.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-t',str(D),'-movflags','+faststart',str(R/'delivery.mp4')],check=True)
import shutil;shutil.copy2(R/'delivery.mp4',repo/'videos/anuncio-iphone-04-v2.mp4')
p=R/'montaje.json';s=json.loads(p.read_text());s['duracion']=D;s['recorte_inicial']=cut;s['nota_corte']='Fuente empieza en con solo; se conserva palabra completa, se elimina Sabés que.';p.write_text(json.dumps(s,ensure_ascii=False,indent=2))
print('BOUNDARY DONE',D)
