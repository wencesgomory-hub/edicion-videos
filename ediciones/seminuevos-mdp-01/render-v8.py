from pathlib import Path
import json,subprocess,types
R=Path('/workspace/seminuevos-01-v8'); repo=Path('/workspace/edicion-videos');old=Path('/workspace/seminuevos-01-v7')
s=json.loads((old/'edit.json').read_text());delta=7/30;s['duration']-=delta
for c in s['captions']:
 if c[0]>25:c[0]-=delta;c[1]-=delta
s['cards']['sellados'][3]=24.80
s['clips'][-1]['start']=2.0;s['clips'][-1]['output_end']-=delta
s['cajas'].update(start=2.0,duration=.9,preparation_speech='Audio original de caída y recepción recuperado; sin impacto sintético.')
s.update(version='v8',estado='exportado',revision='V8: entrada directa de cajas cayendo, sonido original, garantía fuera del último clip y tres pops secos sin bip.',salida='videos/anuncio-seminuevos-mdp-01-v8.mp4')
(R/'edit.json').write_text(json.dumps(s,ensure_ascii=False,indent=2))
for n in ['cable.png','funda.png','cargador.png','dolar.png']:
 if not (R/n).exists():(R/n).symlink_to(Path('/workspace/seminuevos-01-v6')/n)
a=(old/'audio.py').read_text().replace('seminuevos-01-v7','seminuevos-01-v8').replace('(34/30)*sr','(.9)*sr')
a=a.replace("for (name,label,at),kind,gain in zip(s['accessories'],['pop','pop-high','pop-low'],[.52,.50,.52]):effect(at,kind,gain)",'''# Dry broadband plops: no pitched oscillator or beep.
pop_rng=np.random.default_rng(8020)
for j,(name,label,at) in enumerate(s['accessories']):
 t=np.arange(round(.105*sr))/sr
 noise=pop_rng.normal(size=len(t))
 body=filt(noise,120+j*55,1650+j*500)
 air=filt(noise,1800,7000)*.20
 x=(body+air)*np.minimum(1,t/.0007)*np.exp(-t*(55+j*8))
 x/=max(abs(x))+1e-12
 add(fx,x,at,.55);events.append(dict(at=at,kind='pop-seco-'+name,gain=.55))''')
a=a.replace("effect(745/30+(2.45-53/30),'impact',.28)",'''# Original recording of boxes falling/caught, not a replacement hit.
subprocess.run(['ffmpeg','-v','error','-y','-ss','2.0','-t','0.9','-i','/workspace/edicion-videos/IMG_6242.MOV','-vn','-ac','1','-ar','48000','-af','highpass=f=110,afade=t=in:d=0.008,afade=t=out:st=0.82:d=0.08','-c:a','pcm_f32le',str(R/'cajas-original.wav')],check=True)
_,original=wavfile.read(R/'cajas-original.wav')
add(fx,original,745/30,1.0);events.append(dict(at=745/30,kind='cajas-audio-original',gain=1.0))''')
(R/'audio.py').write_text(a)
subprocess.run(['python',str(R/'audio.py')],check=True)
g=Path('/workspace/seminuevos-01-v6/graphics.py').read_text().split("if '--export-graphics' not in sys.argv:")[0].replace('seminuevos-01-v6','seminuevos-01-v8');m=types.ModuleType('graphics');exec(g,m.__dict__)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-an','-c:v','qtrle','-threads','2',str(R/'final-graphics.mov')],stdin=subprocess.PIPE)
for n in range(179):p.stdin.write(m.frame(745/30+n/30).tobytes())
p.stdin.close();assert p.wait()==0
vf='fps=30,scale=1080:1920:flags=lanczos,setsar=1,crop=1000:1778:40:65,scale=1080:1920:flags=lanczos,eq=contrast=1.10:brightness=-0.009:saturation=1.045:gamma=1.02,colorbalance=rs=-0.018:gs=0.002:bs=0.020:rh=0.006:bh=-0.006,vignette=angle=PI/6,setsar=1'
subprocess.run(['ffmpeg','-v','error','-y','-ss','2.0','-t','5.95','-i',str(repo/'IMG_6242.MOV'),'-i',str(R/'final-graphics.mov'),'-filter_complex_threads','4','-filter_complex',f'[0:v]{vf}[b];[b][1:v]overlay=shortest=1,format=yuv420p[v]','-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','13','-threads','4',str(R/'final-take.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(repo/'videos/anuncio-seminuevos-mdp-01-v6.mp4'),'-i',str(R/'final-take.mp4'),'-i',str(R/'master.wav'),'-filter_complex_threads','4','-filter_complex','[0:v]trim=end_frame=745,setpts=PTS-STARTPTS,setsar=1[p];[1:v]setpts=PTS-STARTPTS,setsar=1[q];[p][q]concat=n=2:v=1:a=0,format=yuv420p[v]','-map','[v]','-map','2:a','-t',str(s['duration']),'-c:v','libx264','-preset','faster','-crf','14','-threads','4','-c:a','aac','-b:a','256k','-movflags','+faststart',str(repo/s['salida'])],check=True)
print('V8 DONE',flush=True)
