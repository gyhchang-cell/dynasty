#!/usr/bin/env python3
"""Read-only asset, export and integration checks. Native evidence is checked by the collector."""
import base64,json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];A=ROOT/'src/main/resources/assets/dynasty';D=ROOT/'docs/art/cod3-white-deer-v1'
geo=json.loads((A/'geo/cod3/white_deer.geo.json').read_text())['minecraft:geometry'][0]
anims=json.loads((A/'animations/cod3/white_deer.animation.json').read_text())['animations'];bb=json.loads((D/'blockbench/white_deer.bbmodel').read_text())
bones={b['name']:b for b in geo['bones']};assert len(bones)==len(geo['bones'])==23
assert 'left_hand' not in bones and 'pelvis' not in bones
for name,b in bones.items():
 seen={name};parent=b.get('parent')
 while parent:
  assert parent in bones and parent not in seen;seen.add(parent);parent=bones[parent].get('parent')
assert bones['herb']['parent']=='head' and 'mouth_herb' in bones['herb']['locators']
# Contrasting overlapping cubes with same-facing coplanar surfaces visibly flicker.
# Identical solid color islands and adjacent opposite faces are valid here.
for name,b in bones.items():
 boxes=b.get('cubes',[])
 for i,a in enumerate(boxes):
  for c in boxes[i+1:]:
   if a['uv']==c['uv']:continue
   for axis in range(3):
    other=[j for j in range(3) if j!=axis]
    overlaps=all(min(a['origin'][j]+a['size'][j],c['origin'][j]+c['size'][j])>max(a['origin'][j],c['origin'][j])+1e-6 for j in other)
    if not overlaps:continue
    for sign in [0,1]:
     assert abs(a['origin'][axis]+sign*a['size'][axis]-c['origin'][axis]-sign*c['size'][axis])>1e-6,('coplanar face',name,axis,a,c)
for front in ['front','hind']:
 for side in ['left','right']:
  n=front+'_'+side;assert bones[n+'_shin']['parent']==n+'_upper' and bones[n+'_hoof']['parent']==n+'_shin'
for rel in ['textures/entity/cod3/white_deer.png','textures/item/white_deer_token.png']:
 im=Image.open(A/rel).convert('RGB');assert im.size==(16,16) and len(set(im.getdata()))<=4
 for x in range(16):assert im.getpixel((x,0))==im.getpixel((x,15))==(255,255,255)
 for y in range(16):assert im.getpixel((0,y))==im.getpixel((15,y))==(255,255,255)
 for y in range(0,16,2):
  for x in range(0,16,2):assert len(set(im.crop((x,y,x+2,y+2)).getdata()))==1
tex=Image.open(A/'textures/entity/cod3/white_deer.png').convert('RGB');cubes=[]
for b in bones.values():
 for c in b.get('cubes',[]):
  assert all(v>0 for v in c['size']) and len(c['uv'])==6
  for f,m in c['uv'].items():
   u,v=m['uv'];assert m['uv_size']==[2,2] and 1<=u<=12 and 1<=v<=12
   samples=set(tex.crop((u,v,u+2,v+2)).getdata());assert len(samples)==1
   if (255,255,255) in samples:assert [u,v]==[6,6] # Authored white fur, not free background.
  cubes.append((b,c))
elements=[e for e in bb['elements'] if e['type']=='cube'];assert len(cubes)==len(elements)==37
for (b,c),e in zip(cubes,elements):
 x,y,z=c['origin'];w,h,d=c['size'];assert e['from']==[-x-w,y,z] and e['to']==[-x,y+h,z+d]
 for f,m in c['uv'].items():
  u,v=m['uv'];assert e['faces'][f]['uv']==([u+2,v+2,u,v] if f in ['up','down'] else [u,v,u+2,v+2])
assert base64.b64decode(bb['textures'][0]['source'].split(',',1)[1])==(A/'textures/entity/cod3/white_deer.png').read_bytes()
assert set(anims)=={'animation.white_deer.'+s for s in ['idle','walk','graze','look_back','startled']}
for a in anims.values():
 assert a['loop'] and a['animation_length']==1 and set(a['bones'])<=set(bones)
 for channels in a['bones'].values():
  for keys in channels.values():assert keys['0.0']==keys['1.0'] and all(0<=float(k)<=1 for k in keys)
walk=anims['animation.white_deer.walk']['bones'];assert walk['front_left_upper']==walk['hind_right_upper'] and walk['front_left_upper']!=walk['front_right_upper']
assert json.loads((D/'blockbench/white_deer.animation.json').read_text())['animations']==anims
resources=['geo/cod3/white_deer.geo.json','animations/cod3/white_deer.animation.json','textures/entity/cod3/white_deer.png','textures/item/white_deer_token.png','models/item/white_deer_token.json','models/item/white_deer_spawn_egg.json']
for path in [ROOT/'src/main/resources/data/dynasty/dimension/white_deer_grotto.json',ROOT/'src/main/resources/data/dynasty/dimension_type/white_deer_grotto.json',ROOT/'src/main/resources/data/dynasty/forge/biome_modifier/white_deer.json',ROOT/'src/main/resources/data/dynasty/loot_tables/entities/white_deer.json']:json.loads(path.read_text())
print('PASS strict pixels, face UVs, 37 cuboids, 23-bone quadruped hierarchy, five loops, editable source parity and datapack JSON')
