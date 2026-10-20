from pathlib import Path
import subprocess,json
R=Path('/workspace/seminuevos-01-v4');repo=Path('/workspace/edicion-videos');s=json.loads((R/'edit.json').read_text())
for i,c in enumerate(s['clips']):
 print('Preparando original 1x',c['file'],flush=True)
 source=repo/c['file'];vf=f"trim=start={c['start']}:end={c['end']},setpts=PTS-STARTPTS,fps=30,scale=1080:1920:flags=lanczos,setsar=1"
 if i in [0,3]:vf+=',crop=1000:1778:40:65,scale=1080:1920:flags=lanczos'
 vf+=',eq=contrast=1.10:brightness=-0.009:saturation=1.045:gamma=1.02,colorbalance=rs=-0.018:gs=0.002:bs=0.020:rh=0.006:bh=-0.006,vignette=angle=PI/6,format=yuv420p'
 subprocess.run(['ffmpeg','-v','error','-y','-threads','3','-i',str(source),'-an','-vf',vf,'-c:v','libx264','-preset','faster','-crf','13','-threads','3','-map_metadata','-1',str(R/f'clip-{i}.mp4')],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-vn','-af',f"atrim=start={c['start']}:end={c['end']},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={c['end']-c['start']-.006}:d=0.006",'-ar','48000','-ac','1',str(R/f'voice-{i}.wav')],check=True)
print('Preparación lista, no se exportó el anuncio.',flush=True)
