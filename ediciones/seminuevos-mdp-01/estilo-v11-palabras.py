from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import json,math,subprocess,sys
R=Path('/workspace/ad-v4');subs=json.loads((R/'subtitles.json').read_text())
F='/usr/share/fonts/openai-sans/OpenAISans-Bold.woff2';I='/usr/share/fonts/opentype/urw-base35/NimbusSans-BoldItalic.otf'
WHITE=(255,255,251,255);GOLD=(255,223,72,255)
# Each word is a separate animated layer, with actual type-size hierarchy and light bloom.
words=[]
for start,end,text,key in subs:
 lines=text.split('\n');lineinfos=[]
 for line in lines:
  accent=key in line;size=118 if accent else 86;font=ImageFont.truetype(I if accent else F,size)
  if font.getlength(line)>930:size=int(size*930/font.getlength(line));font=ImageFont.truetype(I if accent else F,size)
  entries=[]
  for w in line.split(' '):
   width=int(font.getlength(w))+44;im=Image.new('RGBA',(width,size+72));d=ImageDraw.Draw(im)
   d.text((22,22),w,font=font,fill=GOLD if accent else WHITE,stroke_width=1,stroke_fill=(0,0,0,200))
   alpha=im.getchannel('A');shadow=Image.new('RGBA',im.size,(0,0,0,0));sd=ImageDraw.Draw(shadow);sd.text((24,28),w,font=font,fill=(0,0,0,220),stroke_width=2,stroke_fill=(0,0,0,160));shadow=shadow.filter(ImageFilter.GaussianBlur(4));shadow.alpha_composite(im)
   glow=Image.new('RGBA',im.size,GOLD if accent else WHITE);glow.putalpha(alpha.filter(ImageFilter.GaussianBlur(9)).point(lambda a:int(a*.52)))
   glow.alpha_composite(shadow)
   entries.append((glow,font.getlength(w),accent))
  lineinfos.append((entries,font.getlength(' '),size))
 height=sum(size+18 for _,_,size in lineinfos)
 normal_y=1420-height/2
 # On these two source screenshots the old captions are baked in; place new type over that same band.
 if 14.3<=start<16.6 or 21.76<=start<24.7:normal_y=825-height/2
 index=0;placed=[];y=normal_y
 for entries,space,size in lineinfos:
  total=sum(w for _,w,_ in entries)+space*(len(entries)-1);x=(1080-total)/2
  for im,width,accent in entries:
   placed.append((im,x-22,y-22,index,accent));index+=1;x+=width+space
  y+=size+18
 words.append((start,end,placed))