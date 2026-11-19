from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,sys
r=Path('/workspace/work/14pro-vs-15');repo=Path('/workspace/edicion-videos')
im=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(im)
for y in range(1920):
 a=0 if y<980 else round(min(155,155*(y-980)/280))
 if y>1670:a=round(155*(1920-y)/250)
 d.line((0,y,1080,y),fill=(0,0,0,max(0,a)))
im.save(r/'scrim.png')
f=f'[0:v]fps=30,scale=1080:1920:in_range=pc:out_range=tv,eq=contrast=1.018:brightness=0.003:saturation=1.02[bg];[bg][1:v]overlay=0:0,subtitles=filename={r}/base.ass:fontsdir={r}/fonts,format=yuv420p[v]'
cmd=['ffmpeg','-v','error','-y','-i',str(r/'original.mp4'),'-i',str(r/'scrim.png'),'-i',str(r/'master.wav'),'-filter_complex_threads','2','-filter_complex',f,'-map','[v]','-map','2:a','-t','68.1','-c:v','libx264','-preset','veryfast','-crf','20','-maxrate','7500k','-bufsize','15000k','-threads','3','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/'videos/comparativa-14pro-vs-15-base-v1.mp4')]
if '--frames' in sys.argv:
 cmd=cmd[:cmd.index('-t')]+['-vf','scale=360:640','-an'] if False else cmd
 # Keep the same graphic timeline while rendering a few representative frames.
 f=f.replace(',format=yuv420p[v]',",select='eq(n,25)+eq(n,420)+eq(n,825)+eq(n,1095)+eq(n,1500)+eq(n,1665)+eq(n,1935)',scale=360:640,format=yuv420p[v]")
 cmd=['ffmpeg','-v','error','-y','-i',str(r/'original.mp4'),'-i',str(r/'scrim.png'),'-filter_complex_threads','2','-filter_complex',f,'-map','[v]','-fps_mode','vfr','-frames:v','7',str(r/'qa-%02d.jpg')]
subprocess.run(cmd,check=True)
