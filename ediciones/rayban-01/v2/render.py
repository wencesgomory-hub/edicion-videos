from pathlib import Path
import subprocess,json
r=Path('/workspace/rayban-01-v2');repo=Path('/workspace/edicion-videos');source=repo/'9869B4DA-35D1-4B40-B519-43BDC03C8FC3.mov';D=84.472993
args=['ffmpeg','-v','error','-y','-i',str(source)]
assets=[('titulo.png',.10,5.5),('error.png',.30,5.5),('modelo.png',6.,9.),('marca.png',80.5,D)]
for name,a,b in assets:args+=['-loop','1','-framerate','30','-i',str(r/name)]
args+=['-i',str(r/'master.wav')]
f=["[0:v]fps=30,eq=contrast=1.025:brightness=0.002:saturation=1.02:gamma=1.02,hue=s=0:enable='lt(t,5.5)',eq=contrast=1.08:enable='lt(t,5.5)',split=2[bgin][fgin]",'[bgin]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.13:saturation=0.65[bg]','[fgin]scale=1080:1440:flags=lanczos,setsar=1[fg]','[bg][fg]overlay=0:240,setsar=1[v0]']
for i,(name,a,b) in enumerate(assets,1):f.append(f"[v{i-1}][{i}:v]overlay=0:0:enable='between(t,{a},{b})'[v{i}]")
f.append(f"[v{len(assets)}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.16:t=fill:enable='between(t,0.10,0.17)+between(t,5.50,5.57)',subtitles=filename='{r/'subtitulos.ass'}':fontsdir='{r/'fonts'}',format=yuv420p[v]")
args+=['-filter_complex_threads','2','-filter_complex',';'.join(f),'-map','[v]','-map',f'{len(assets)+1}:a','-t',str(D),'-c:v','libx264','-preset','veryfast','-crf','18','-maxrate','7500k','-bufsize','15000k','-threads','4','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(repo/'videos/entrega-iphone-15-pro-max-rayban-v2.mp4')]
print('RENDER START',flush=True);subprocess.run(args,check=True);print('DONE',flush=True)
(r/'montaje.json').write_text(json.dumps({'duracion':D,'velocidad':1,'gancho':'CASI PIERDO UNA VENTA / POR ESTE ERROR EN LA CÁMARA (texto indicado por usuario)','blanco_y_negro':[0,5.5],'subtitulos':'Conversación con Whisperlarge-v3, revisión textual; tiempos de fragmentos basados en timestamps ASR y distribución estimada dentro de cada segmento, no alineación exacta de palabras.','audio':'Misma conversación V1; nuevo diseño de suspenso/impactos de entrada hasta5.5s, sin rotura de vidrio ni afirmación de daño físico','encuadre':'3:4 completo, extensiones de fondo9:16','nota':'No acelerar voces, no congelados iniciales, no precios/condiciones añadidos'},ensure_ascii=False,indent=2))
