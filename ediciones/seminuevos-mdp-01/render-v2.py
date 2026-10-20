from pathlib import Path
import subprocess,json
R=Path('/workspace/seminuevos-01-v2');repo=Path('/workspace/edicion-videos');s=json.loads((R/'edit.json').read_text());cmd=['ffmpeg','-v','error','-y']
for j in range(4):cmd+=['-i',str(R/f'clip-{j}.mp4')]
cmd+=['-i',str(R/'graphics.mov'),'-i',str(R/'master.wav')]
flash='+'.join(f'between(t,{c["output_start"]},{c["output_start"]+.033})' for c in s['clips'][1:])
f=''.join(f"[{j}:v]trim=start={s['clips'][j]['cache_trim']}:duration={s['clips'][j]['output_end']-s['clips'][j]['output_start']},setpts=PTS-STARTPTS[v{j}];" for j in range(4))+'[v0][v1][v2][v3]concat=n=4:v=1:a=0[base];'+f"[base]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.09:t=fill:enable='{flash}'[flash];[flash][4:v]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[v]"
cmd+=['-filter_complex_threads','3','-filter_complex',f,'-map','[v]','-map','5:a:0','-t',str(s['duration']),'-c:v','libx264','-preset','fast','-crf','16','-maxrate','14000k','-bufsize','28000k','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-map_metadata','-1','-metadata:s:v:0','rotate=0','-movflags','+faststart',str(repo/'videos/anuncio-seminuevos-mdp-01-v2.mp4')]
subprocess.run(cmd,check=True);print('DONE',flush=True)
