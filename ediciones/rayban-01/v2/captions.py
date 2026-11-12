from pathlib import Path
import json,re,math
r=Path('/workspace/rayban-01-v2');data=json.loads((r/'transcript-reviewed.json').read_text());events=[]
for part in data:
 off=part['offset'];res=part['result'];starts=res.get('segment_timestamps',[]);durations=res.get('segment_durations',[]);texts=res.get('segment_texts',[])
 for a,d,tx in zip(starts,durations,texts):
  tx=re.sub(r'^\s*[-–]\s*','',tx).strip()
  if not tx or d<=0:continue
  words=tx.split();groups=[];group=[]
  for word in words:
   if group and (len(group)>=5 or len(' '.join(group+[word]))>37):groups.append(group);group=[]
   group.append(word)
  if group:groups.append(group)
  weights=[sum(len(w.strip('¿?¡!.,'))+2 for w in g) for g in groups];total=sum(weights);start=off+a
  for g,w in zip(groups,weights):
   end=min(84.472993,start+d*w/total);events.append({'inicio':round(start,3),'fin':round(end,3),'texto':' '.join(g)});start=end
(r/'captions.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
def stamp(t,ass=False):
 h=int(t//3600);m=int(t%3600//60);s=int(t%60);ms=round((t-int(t))*1000)
 return f'{h}:{m:02}:{s:02}.{ms//10:02}' if ass else f'{h:02}:{m:02}:{s:02},{min(ms,999):03}'
def styled(tx):
 words=tx.split()
 if len(tx)>28 and len(words)>2:
  mid=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))));words.insert(mid,r'\N')
 out=[]
 for w in words:
  clean=w.lower().strip('¿?¡!.,;:')
  col='5AE0FF' if clean in ['cámara','cámaras','batería','max','iphone'] else '8FEB47' if clean in ['garantía','gracias'] else '2920EF' if clean in ['rayita','rayón'] else None
  if col:out.append(r'{\c&H'+col+r'&}'+w+r'{\c&HFAFFFF&}')
  else:out.append(w)
 return ' '.join(out)
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Base,GomoryMontserrat,78,&H00FAFFFF,&H005AE0FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.8,2.3,2,95,95,395,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
ass=[];srt=[]
for i,x in enumerate(events,1):
 a,b,tx=x['inicio'],x['fin'],x['texto'];ass.append(f'Dialogue: 0,{stamp(a,True)},{stamp(b,True)},Base,,0,0,0,,'+r'{\fad(25,35)\blur0.35\fscx103\fscy103\t(0,90,\fscx100\fscy100)}'+styled(tx));srt.append(f'{i}\n{stamp(a)} --> {stamp(b)}\n{tx}\n')
(r/'subtitulos.ass').write_text(head+'\n'.join(ass));(r/'subtitulos.srt').write_text('\n'.join(srt));print('CAPTIONS',len(events),flush=True)
