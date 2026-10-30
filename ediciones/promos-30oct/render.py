from pathlib import Path
import subprocess,json
repo=Path(__file__).resolve().parents[2]
source=repo/'materiales/productos/iphonecontenido.mp4';fg=repo/'materiales/promos/30oct/capa-transparente.png'
f="[0:v]setpts=1.0818602197*(PTS-STARTPTS),fps=30,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,eq=contrast=1.025:brightness=-0.01:saturation=0.98,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.28:t=fill[bg];[1:v]scale=1080:1920:flags=lanczos,format=rgba[fg];[bg][fg]overlay=0:0:shortest=1,format=yuv420p[v]"
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-loop','1','-i',str(fg),'-filter_complex',f,'-map','[v]','-an','-t','5','-c:v','libx264','-preset','fast','-crf','16','-threads','4','-movflags','+faststart',str(repo/'videos/historia-promos-30oct-fondo-real.mp4')],check=True)
