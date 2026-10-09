#!/usr/bin/env python3
"""Deterministic pixel GUI and distinct elemental crest icons; no new item assets."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
out=root/'src/main/resources/assets/dynasty/textures/gui';out.mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(176,202),'#372d25');d=ImageDraw.Draw(im)
d.rectangle((0,0,175,201),outline='#1a201b',width=2);d.rectangle((2,2,173,199),outline='#b49a62');d.rectangle((4,4,171,197),outline='#65533d')
for y in range(15,198,11):d.line((5,y,170,y),fill='#3d3228');d.line((5,y+1,170,y+1),fill='#30291f')
for x,y in [(5,5),(167,5),(5,193),(167,193)]:d.rectangle((x,y,x+3,y+3),fill='#709982');d.point((x,y),fill='#b4d1ad')
d.rectangle((19,26,46,51),fill='#262c25',outline='#7d7953');d.rectangle((73,26,100,51),fill='#262c25',outline='#7d7953');d.rectangle((128,26,155,51),fill='#263f34',outline='#b69d63');d.line((8,105,167,105),fill='#866e46');im.save(out/'infusion.png')
atlas=Image.new('RGBA',(160,64))
rows=json.loads((root/'src/main/resources/data/dynasty/infusion/materials.json').read_text())
for index,effect in enumerate(sorted({r['enhancementId'].split(':')[1] for r in rows})):
 h=hashlib.sha256(effect.encode()).digest();im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im);color=tuple(115+v//2 for v in h[:3])+(255,)
 d.polygon([(7,0),(14,5),(14,10),(7,15),(1,10),(1,5)],fill='#263b32',outline='#b89f66')
 # Symmetric rune, unique deterministic 21-bit signature inside each framed crest.
 for y in range(4,11):
  for x in range(3):
   if h[3+y]&(1<<x):d.point((5+x,y),fill=color);d.point((10-x,y),fill=color)
 atlas.paste(im,((index%10)*16,(index//10)*16))
atlas.save(out/'infusion_crests.png')
print('Generated 176x202 background and 40 distinct 16px crests')
