from pathlib import Path
import json
R=Path('/workspace/seminuevos-01-v6');B=Path('/workspace/seminuevos-01-v5');s=json.loads((B/'edit.json').read_text());s['revision']='V6 final: fondo limpio nuevo sin separación de referencia, una sola entrada de sonido en equipos, márgenes Instagram ampliados.';(R/'edit.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
for name in ['clip-0.mp4','clip-1.mp4','clip-2.mp4','clip-3.mp4','cable.png','funda.png','cargador.png','dolar.png']:(R/name).symlink_to(B/name)
g=(B/'graphics.py').read_text().replace("R=Path('/workspace/seminuevos-01-v5')","R=Path('/workspace/seminuevos-01-v6')")
g=g.replace("[('SELLADOS',30,1),('SEMINUEVOS',575,-1)]","[('SELLADOS',52,1),('SEMINUEVOS',552,-1)]").replace('scale=.84+.16*p,angle=side*3','scale=.84*(.84+.16*p),angle=side*3')
g=g.replace('x=30+j*350;y=820','x=70+j*310;y=820').replace('scale=.75+.25*p,angle=','scale=.86*(.75+.25*p),angle=')
g=g.replace('scale=.85+.15*back(q/.18),angle=-2','scale=.90*(.85+.15*back(q/.18)),angle=-2')
g=g.replace('scale=.8+.2*p,angle=-5','scale=.84*(.8+.2*p),angle=-5').replace('[(860,1130),(910,1180),(1010,1060)]','[(828,1130),(878,1180),(978,1060)]')
(R/'graphics.py').write_text(g)
v=(B/'render.py').read_text().replace("R=Path('/workspace/seminuevos-01-v5')","R=Path('/workspace/seminuevos-01-v6')").replace('anuncio-seminuevos-mdp-01-v5.mp4','anuncio-seminuevos-mdp-01-v6.mp4');(R/'render.py').write_text(v)
