from pathlib import Path
import subprocess,json
R=Path('/workspace/seminuevos-01-v7');repo=Path('/workspace/edicion-videos');s=json.loads((R/'edit.json').read_text())
f='[0:v]split=2[a][b];[a]trim=end_frame=745,setpts=PTS-STARTPTS,setsar=1[p];[b]trim=start_frame=745,setpts=PTS-STARTPTS,setsar=1[q];[1:v]setpts=PTS-STARTPTS,setsar=1[c];[p][c][q]concat=n=3:v=1:a=0,format=yuv420p[v]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/'videos/anuncio-seminuevos-mdp-01-v6.mp4'),'-i',str(R/'cajas.mp4'),'-i',str(R/'master.wav'),'-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','2:a:0','-t',str(s['duration']),'-c:v','libx264','-preset','faster','-crf','14','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-map_metadata','-1','-movflags','+faststart',str(repo/'videos/anuncio-seminuevos-mdp-01-v7.mp4')],check=True)
print('DONE',flush=True)
