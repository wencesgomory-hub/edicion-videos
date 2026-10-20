from pathlib import Path
import json,subprocess
R=Path('/workspace/seminuevos-01');repo=Path('/workspace/edicion-videos');speed=1.07;clips=[];off=0
for idx,(name,start,end) in enumerate([('IMG_6229',3.97,10.40),('IMG_6234',1.09,11.52),('IMG_6236',.59,8.32),('IMG_6242',2.32,7.91)]):
 d=(end-start)/speed;clips.append(dict(file=name+'.MOV',start=start,end=end,speed=speed,output_start=off,output_end=off+d));off+=d
 # Keep the guarantee document and product handling in frame. Small alternating punch-ins elsewhere.
 zoom='1.055' if idx==2 else ('if(lt(t,1.2),1.13,if(lt(t,3.4),1.075,1.15))' if idx in [0,3] else 'if(lt(t,2.3),1.07,if(lt(t,4.9),1.14,1.07))')
 # zoompan is evaluated on the final timeline after speed change.
 z=zoom.replace('t','on/30')
 vf=f"trim=start={start}:end={end},setpts=(PTS-STARTPTS)/{speed},fps=30,scale=1080:1920:flags=lanczos,setsar=1,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih*.38-ih/zoom*.38':d=1:s=1080x1920:fps=30,eq=contrast=1.105:brightness=-0.013:saturation=1.06:gamma=1.015,colorbalance=rs=-0.022:gs=0.003:bs=0.025:rh=0.008:bh=-0.008,vignette=angle=PI/6,format=yuv420p"
 # Replace only standalone t in expression above, not the 'lt' function.
 vf=vf.replace('lon/30','lt')
 print('RENDER',name,flush=True)
 subprocess.run(['ffmpeg','-v','error','-y','-threads','3','-i',str(repo/(name+'.MOV')),'-an','-vf',vf,'-c:v','libx264','-preset','fast','-crf','12','-threads','3','-map_metadata','-1','-movflags','+faststart',str(R/f'clip-{idx}.mp4')],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/(name+'.MOV')),'-vn','-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS,atempo={speed}','-ar','48000','-ac','1',str(R/f'voice-{idx}.wav')],check=True)
(R/'timeline.json').write_text(json.dumps(dict(clips=clips,duration=off),indent=2));print('DONE',off,flush=True)
