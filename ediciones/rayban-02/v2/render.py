from pathlib import Path
import subprocess,json,sys
r=Path('/workspace/rayban-02-v2');repo=Path('/workspace/edicion-videos');m=json.loads((r/'montaje.json').read_text());clips=m['clips'];D=m['duracion_montage'] if 'duracion_montage' in m else m['duracion_montaje']
a=['ffmpeg','-hide_banner','-y','-i',str(repo/'D8EB53EA-49A5-4D79-A8AD-B5872C04D7D1.mov'),'-i',str(r/'master.wav')]
f=['[0:v]split='+str(len(clips))+''.join('[s'+str(i)+']' for i in range(len(clips)))]
for i,c in enumerate(clips):
 x=20 if c['inicio_original']<62 else (140 if c['inicio_original']<70 else 95)
 f.append(f"[s{i}]trim=start={c['inicio_original']}:end={c['fin_original']},setpts=PTS-STARTPTS,crop=546:970:{x}:0,setsar=1[c{i}]")
f.append(''.join('[c'+str(i)+']' for i in range(len(clips)))+f'concat=n={len(clips)}:v=1:a=0,fps=30,scale=1080:1920:flags=lanczos,setsar=1,eq=contrast=1.025:brightness=0.002:saturation=1.015:gamma=1.015,hue=s=0:enable=lt(t\\,1.3),drawbox=x=0:y=0:w=iw:h=ih:color=white@0.15:t=fill:enable=between(t\\,0.08\\,0.15),drawbox=x=0:y=0:w=iw:h=ih:color=white@0.10:t=fill:enable=between(t\\,0.43\\,0.49),subtitles=filename={r}/subtitulos.ass:fontsdir={r}/fonts,format=yuv420p[v]')
a+=['-filter_complex_threads','2','-filter_complex',';'.join(f),'-map','[v]','-map','1:a','-t',str(D),'-c:v','libx264','-preset','veryfast','-crf','19','-maxrate','6800k','-bufsize','13600k','-threads','4','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/'videos/reel-entrega-iphone-15-pro-revision-v2.mp4')]
if '--preview' in sys.argv:a=a[:-1]+['-ss','0.8','-frames:v','1','-an','-c:v','png','-f','image2',str(r/'preview.png')]
subprocess.run(a,check=True)
