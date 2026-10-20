from pathlib import Path
from PIL import Image
import shutil,json
R=Path('/workspace/seminuevos-01-v4');repo=Path('/workspace/edicion-videos');s=json.loads((R/'edit.json').read_text())
im=Image.open('/workspace/generated_images/exec-26150607-619f-405e-828a-49d9d6d439bb.png').convert('RGBA');w,h=im.size
for name,box in [('cargador',(0,0,int(w*.44),h)),('dolar',(int(w*.46),0,w,h))]:
 p=im.crop(box);p=p.crop(p.getbbox());p.save(R/(name+'.png'))
for name in ['cable','funda']:shutil.copyfile(repo/f'materiales/graficos/accesorios-ilustrativos/{name}.png',R/(name+'.png'))
old=Path('/workspace/seminuevos-01-v2/graphics.py').read_text();old=old.replace("R=Path('/workspace/seminuevos-01-v2')","R=Path('/workspace/seminuevos-01-v4')");old=old.replace("Path('/workspace/ad-v4/animate.py')","Path('/workspace/edicion-videos/ediciones/seminuevos-mdp-01/estilo-v11-palabras.py')")
old=old.replace("if not st<=t<en:continue\n  # Item labels", "if not st<=t<en:continue\n  if spec['accessories'][0][2] <= t < spec['accessories_end']:continue\n  # Item labels")
old=old.replace('365/im.height','310/im.height').replace('(365-ph.height)/2','(330-ph.height)/2')
old=old.replace("panel=Image.new('RGBA',(320,450))","panel=Image.new('RGBA',(320,490))").replace('(1,1,319,449)','(1,1,319,489)').replace('lab.width)/2,365','lab.width)/2,350').replace('im.height)/2,365','im.height)/2,350').replace(')/2,1213,fade',')/2,1230,fade')
old=old.replace("# Item labels are carried", "# Item labels are carried")
old=old.replace("def frame(t):", "bill=Image.open(R/'dolar.png').convert('RGBA');bill.thumbnail((450,280),Image.Resampling.LANCZOS)\nlabel=Image.new('RGBA',(320,142));ld=ImageDraw.Draw(label)\nfor y,text,size in [(0,'DESCUENTO EN',27),(42,'CARGADOR',36),(87,'ORIGINAL',36)]:ld.text((160,y),text,font=ImageFont.truetype(a.F,size),fill=G,anchor='mt')\nlabels['cargador']=label\n\ndef frame(t):")
old=old.replace("d=ImageDraw.Draw(out)\n for st,en,kind", "d=ImageDraw.Draw(out)\n st=spec['precio_dolar']['inicio'];en=spec['precio_dolar']['fin']\n if st<=t<en:\n  q=t-st;fade=min(clamp(q/.07),clamp((en-t)/.09));p=back(q/.18);paste(out,bill,560+60*(1-ease(q/.18)),860+35*(1-p),fade,scale=.8+.2*p,angle=-5*(1-ease(q/.18)))\n  d=ImageDraw.Draw(out);d.line([(860,1130),(910,1180),(1010,1060)],fill=(25,240,105,int(245*fade)),width=24,joint='curve')\n for st,en,kind")
old=old.replace("[.8,10.6,11.4,12.8,20.25,21.7]","[.5,3.2,12.0,14.0,22.0,23.7]")
old=old.replace("if '--preview' in sys.argv:","if '--export-graphics' not in sys.argv:")
(R/'graphics.py').write_text(old)
