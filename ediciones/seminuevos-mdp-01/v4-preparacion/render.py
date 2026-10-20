from pathlib import Path
import subprocess,json,sys
R=Path('/workspace/seminuevos-01-v4');repo=Path('/workspace/edicion-videos');s=json.loads((R/'edit.json').read_text())
if '--export' not in sys.argv:
 print('Preparación solamente. Exportación del anuncio desactivada por indicación del usuario.');sys.exit()
subprocess.run([sys.executable,str(R/'graphics.py'),'--export-graphics'],check=True)
cmd=['ffmpeg','-v','error','-y']
for i in range(4):cmd+=['-i',str(R/f'clip-{i}.mp4')]
for p in [R/'graphics.mov',R/'master.wav',repo/'materiales/productos/caja-violeta-mano-01-sin-marca.mp4',repo/'materiales/productos/iphonecontenido.mp4']:cmd+=['-i',str(p)]
parts=[]
for i,c in enumerate(s['clips']):parts.append(f"[{i}:v]trim=duration={c['output_end']-c['output_start']},setpts=PTS-STARTPTS[v{i}];")
f=''.join(parts)+'[v0][v1][v2][v3]concat=n=4:v=1:a=0[base];'
semi=s['insertos'][1];sellend=semi['inicio']-.02;sellstart=sellend-1.1
f+=f"[6:v]trim=duration=1.1,setpts=PTS-STARTPTS+{sellstart}/TB,setsar=1[sell];[7:v]trim=start=0.35:duration={semi['fin']-semi['inicio']},setpts=PTS-STARTPTS+{semi['inicio']}/TB,fps=30,scale=1080:1920:flags=lanczos,setsar=1,eq=contrast=1.025:saturation=1.015[semi];"
f+=f"[base][sell]overlay=0:0:format=auto:eof_action=pass:enable='between(t,{sellstart},{sellend})'[b];[b][semi]overlay=0:0:format=auto:eof_action=pass:enable='between(t,{semi['inicio']},{semi['fin']})'[c];[c][4:v]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[v]"
cmd+=['-filter_complex_threads','4','-filter_complex',f,'-map','[v]','-map','5:a:0','-t',str(s['duration']),'-c:v','libx264','-preset','fast','-crf','16','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-map_metadata','-1','-movflags','+faststart',str(repo/'videos/anuncio-seminuevos-mdp-01-v4.mp4')]
subprocess.run(cmd,check=True)
