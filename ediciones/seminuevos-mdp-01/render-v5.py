from pathlib import Path
import subprocess,json
R=Path('/workspace/seminuevos-01-v5');repo=Path('/workspace/edicion-videos');s=json.loads((R/'edit.json').read_text());cmd=['ffmpeg','-v','error','-y']
for i in range(4):cmd+=['-i',str(R/f'clip-{i}.mp4')]
cmd+=['-i',str(R/'graphics.mov'),'-i',str(R/'master.wav')]
f=''.join(f"[{i}:v]trim=duration={c['output_end']-c['output_start']},setpts=PTS-STARTPTS,setsar=1[v{i}];" for i,c in enumerate(s['clips']))+'[v0][v1][v2][v3]concat=n=4:v=1:a=0[base];[base][4:v]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[v]'
cmd+=['-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','5:a:0','-t',str(s['duration']),'-c:v','libx264','-preset','fast','-crf','16','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-map_metadata','-1','-movflags','+faststart',str(repo/'videos/anuncio-seminuevos-mdp-01-v5.mp4')]
subprocess.run(cmd,check=True);print('DONE',flush=True)
