from pathlib import Path
import json
R=Path('/workspace/seminuevos-01-v7');B=Path('/workspace/seminuevos-01-v6');s=json.loads((B/'edit.json').read_text());extra=34/30;start=24.82
for c in s['captions']:
 if c[0]>=start-.001:c[0]+=extra;c[1]+=extra
s['clips'][3]['start']=53/30;s['clips'][3]['output_end']+=extra;s['duration']+=extra;s['revision']='V7: conservar lanzamiento y recepción de cajas, restaurar pops audibles por accesorio y dos acentos diferentes de equipos; música +1.5 dB.';s['cajas']={'source':'IMG_6242.MOV','start':53/30,'end':2.9,'video_insertion':745/30,'duration':extra,'preparation_speech':'No incluida: se mantiene música durante el lanzamiento para evitar volver a insertar la indicación decinos.'};(R/'edit.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
a=(B/'audio.py').read_text().replace("R=Path('/workspace/seminuevos-01-v6')","R=Path('/workspace/seminuevos-01-v7')")
a=a.replace("if v.ndim==1:v=np.column_stack([v,v])","v=np.concatenate([v[:round((745/30)*sr)],np.zeros(round((34/30)*sr)),v[round((745/30)*sr):]])[:N]\nif v.ndim==1:v=np.column_stack([v,v])")
a=a.replace('(-30.3/20)','(-28.8/20)')
a=a.replace("if kind=='pop':x=np.sin(2*np.pi*(180*t+650*.012*(1-np.exp(-t/.012))))", "if kind.startswith('pop'):\n  pitch={'pop':1.,'pop-high':1.18,'pop-low':.83}.get(kind,1.);x=np.sin(2*np.pi*(180*pitch*t+650*pitch*.012*(1-np.exp(-t/.012))))")
a=a.replace("effect(.07,'pop',.18)","effect(.07,'pop',.25)").replace("add(fx,cash,price,.16)","add(fx,cash,price,.21)").replace("kind='cash',gain=.16","kind='cash',gain=.21")
a=a.replace("first=7.30;effect(first,'impact',.42)","first=7.30;effect(first,'pop',.46)\nsecond=next(c[0] for c in s['captions'] if c[3]=='SEMINUEVOS');effect(second,'pop-low',.42)")
a=a.replace("['pop','click','impact'],[.30,.23,.24]","['pop','pop-high','pop-low'],[.52,.50,.52]")
a=a.replace("effect(red,'impact',.25)","effect(red,'impact',.35)").replace(".27)",".37)").replace("effect(cta,'click',.24)","effect(cta,'click',.35)")
a=a.replace("assert sum(6.4<=e['at']<9.1 for e in events)==1,'La presentación de equipos debe tener un solo acento.'","assert sum(6.4<=e['at']<9.1 for e in events)==2,'Solo dos acentos diferentes al mostrar los equipos.'\neffect(745/30+(2.45-53/30),'impact',.28)")
a=a.replace('AUDIO DONE: fondo nuevo limpio, sin sonido de referencia; un acento en equipos.','AUDIO DONE: pops restaurados, dos acentos en equipos, música +1.5 dB, cajas completas.')
(R/'audio.py').write_text(a)
