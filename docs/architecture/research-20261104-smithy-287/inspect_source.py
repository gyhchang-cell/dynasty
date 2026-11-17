"""Offline source projections; no game, production writes, or semantic credit."""
import json, sys
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
R=Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/architecture'))
from whole_building_candidates import iso, AIR, color
from PIL import Image, ImageDraw
d=json.loads((P/'original-all-source.json').read_text())
s=json.loads((P/'source.json').read_text())
pal=d['palette']; blocks={tuple(b['pos']):b for b in d['blocks']}
cells={p:pal[b['state']]['Name'] for p,b in blocks.items() if pal[b['state']]['Name'] not in AIR}
sx,sy,sz=d['size']
counts=[]
for y in range(sy):
 c=Counter('unknown' if (x,y,z) not in blocks else 'air' if pal[blocks[x,y,z]['state']]['Name'] in AIR else 'nonair' for z in range(sz) for x in range(sx))
 counts.append(dict(y=y,**c))
for start in range(0,sy,4):
 im=Image.new('RGB',(1520,880),'#edf0f2');draw=ImageDraw.Draw(im)
 for k in range(4):
  y=start+k;ox=(k%2)*760+70;oy=(k//2)*440+42;step=20
  draw.text((ox,oy-25),f'y={y} / +X right +Z down / WHITE air BLACK omitted',fill='black')
  for z in range(sz):
   for x in range(sx):
    b=blocks.get((x,y,z));n=pal[b['state']]['Name'] if b else None
    col='#171d26' if n is None else '#ffffff' if n in AIR else color(n)
    draw.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=col,outline='#a9afb5')
  for x in range(0,sx,5):draw.text((ox+x*step,oy-12),str(x),fill='black')
  for z in range(0,sz,3):draw.text((ox-24,oy+z*step),str(z),fill='black')
 im.save(P/f'F01-layers-{start:02d}-{start+3:02d}.png')
for cut in [3,7,11]:
 im=Image.new('RGB',(1520,680));im.paste(iso(cells,d['size'],0,f'F01 cut y<={cut}',cut),(0,0));im.paste(iso(cells,d['size'],1,'rotated',cut),(760,0));im.save(P/f'F01-cut-{cut:02d}.png')
special=[dict(position=list(p),state=pal[b['state']]) for p,b in blocks.items() if any(t in pal[b['state']]['Name'] for t in ['_door','bed','furnace','ladder','stairs','crafting_table','bookshelf','lectern'])]
with ZipFile(s['source_archive']) as z:
 names=[n for n in z.namelist() if n.endswith('.json') and ('/worldgen/structure/' in n or '/worldgen/template_pool/' in n) and ('village_fortified' in n or n.endswith('village/fortified/town_centers.json'))]
 ctx={n:z.read(n).decode() for n in names}
 for text in list(ctx.values()):
  try:tag=json.loads(text).get('biomes','')
  except Exception:continue
  if isinstance(tag,str) and tag.startswith('#'):
   ns,p=tag[1:].split(':');n=f'data/{ns}/tags/worldgen/biome/{p}.json'
   if n in z.namelist():ctx[n]=z.read(n).decode()
(P/'layer-counts.json').write_text(json.dumps(counts,indent=2)+'\n')
(P/'special-states.json').write_text(json.dumps(special,ensure_ascii=False,indent=2)+'\n')
(P/'root-context.json').write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+'\n')
print('COUNTS',counts)
print('ROOT',json.dumps(ctx,ensure_ascii=False))
print('DOORS',json.dumps([x for x in special if '_door' in x['state']['Name']],ensure_ascii=False))
