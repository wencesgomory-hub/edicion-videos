from pathlib import Path
import subprocess,json
r=Path('/workspace/rayban-01-v3');repo=Path('/workspace/edicion-videos');source=repo/'9869B4DA-35D1-4B40-B519-43BDC03C8FC3.mov';D=84.472993
args=['ffmpeg','-v','error','-y','-i',str(source)]
assets=[('titulo.png',.10,3.0),('venta.png',.18,3.0),('error.png',.34,3.0)]
for name,a,b in assets:args+=['-loop','1','-framerate','30','-i',str(r/name)]
args+=['-i',str(r/'master.wav')]
f=["[0:v]fps=30,crop=540:960:x='if(lt(t,12),165,if(lt(t,16),165-(t-12)*18.75,if(lt(t,44),90,if(lt(t,48),90+(t-44)*17.5,if(lt(t,54),160,if(lt(t,58),160-(t-54)*22.5,if(lt(t,76),70,min(160,70+(t-76)*22.5))))))))':y=0,scale=1080:1920:flags=lanczos,setsar=1,eq=contrast=1.025:brightness=0.002:saturation=1.02:gamma=1.02,hue=s=0:enable='lt(t,5.5)',eq=contrast=1.08:enable='lt(t,5.5)'[v0]"]
for i,(name,a,b) in enumerate(assets,1):f.append(f"[v{i-1}][{i}:v]overlay=0:0:enable='between(t,{a},{b})'[v{i}]")
f.append(f"[v{len(assets)}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.16:t=fill:enable='between(t,0.10,0.17)+between(t,5.50,5.57)',subtitles=filename='{r/'subtitulos.ass'}':fontsdir='{r/'fonts'}',format=yuv420p[v]")
args+=['-filter_complex_threads','2','-filter_complex',';'.join(f),'-map','[v]','-map',f'{len(assets)+1}:a','-t',str(D),'-c:v','libx264','-preset','veryfast','-crf','18','-maxrate','7500k','-bufsize','15000k','-threads','4','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/'videos/entrega-iphone-15-pro-max-rayban-v3.mp4')]
print('RENDER START',flush=True);subprocess.run(args,check=True);print('DONE',flush=True)
