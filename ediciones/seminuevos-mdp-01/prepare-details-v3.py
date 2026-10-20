from pathlib import Path
import subprocess
R=Path('/workspace/seminuevos-01-v3');repo=Path('/workspace/edicion-videos')
# Native 4K details from the user's own take. No competitor images are reused.
shots=[('sellados',2.0,3.25,"crop=1400:2488:100:450,scale=1080:1920:flags=lanczos"),('seminuevos',4.35,5.75,"crop=1020:1812:x='650+200*t/1.4':y=2020,scale=1080:1920:flags=lanczos")]
for name,st,en,crop in shots:
 vf=f"trim=start={st}:end={en},setpts=PTS-STARTPTS,fps=30,{crop},setsar=1,eq=contrast=1.10:brightness=-0.009:saturation=1.055:gamma=1.02,colorbalance=rs=-0.022:gs=0.003:bs=0.025:rh=0.008:bh=-0.008,vignette=angle=PI/6,format=yuv420p"
 subprocess.run(['ffmpeg','-v','error','-y','-threads','3','-i',str(repo/'IMG_6234.MOV'),'-an','-vf',vf,'-c:v','libx264','-preset','fast','-crf','12','-threads','3',str(R/(name+'.mp4'))],check=True)
 print(name,'DONE',flush=True)
