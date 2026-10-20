from pathlib import Path
import subprocess,json
R=Path('/workspace/seminuevos-01-v3');repo=Path('/workspace/edicion-videos');s=json.loads((R/'edit.json').read_text());cmd=['ffmpeg','-v','error','-y']
for j in range(4):cmd+=['-i',str(R/f'clip-{j}.mp4')]
for p in ['graphics.mov','master.wav','sellados.mp4','seminuevos.mp4']:cmd+=['-i',str(R/p)]
parts=[]
for j in range(4):
 c=s['clips'][j];f=f"[{j}:v]trim=start={c['cache_trim']}:duration={c['output_end']-c['output_start']},setpts=PTS-STARTPTS"
 if j in [0,3]:
  z="if(lt(on,36),1.18,if(lt(on,96),1.12,1.20))" if j==0 else "if(lt(on,54),1.10,1.16)"
  f+=f",zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih*.28-ih/zoom*.28':d=1:s=1080x1920:fps=30,eq=gamma=1.015"
 parts.append(f+f'[v{j}];')
f=''.join(parts)+'[v0][v1][v2][v3]concat=n=4:v=1:a=0[base];'
f+='[6:v]trim=duration=1.09,setpts=PTS-STARTPTS+6.07/TB[sell];[7:v]trim=duration=1.11,setpts=PTS-STARTPTS+7.17/TB[semi];'
f+="[base][sell]overlay=0:0:format=auto:eof_action=pass:enable='between(t,6.07,7.16)'[b1];[b1][semi]overlay=0:0:format=auto:eof_action=pass:enable='between(t,7.17,8.28)'[b2];"
flash='+'.join(f'between(t,{c["output_start"]},{c["output_start"]+.033})' for c in s['clips'][1:])
f+=f"[b2]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.09:t=fill:enable='{flash}'[fl];[fl][4:v]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[v]"
cmd+=['-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','5:a:0','-t',str(s['duration']),'-c:v','libx264','-preset','fast','-crf','16','-maxrate','14000k','-bufsize','28000k','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-map_metadata','-1','-metadata:s:v:0','rotate=0','-movflags','+faststart',str(repo/'videos/anuncio-seminuevos-mdp-01-v3.mp4')]
subprocess.run(cmd,check=True);print('DONE',flush=True)
