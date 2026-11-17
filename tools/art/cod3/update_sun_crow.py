#!/usr/bin/env python3
"""Export revised cuboids and tracks from crow(), preserving the accepted pixel atlas and face islands."""
import copy,hashlib,json,shutil
from pathlib import Path
from scenic_resources import ROOT,A,D,crow,dump
OUT=ROOT/'docs/art/cod3-sun-crow-v2'
r=crow();texture=A/'textures/entity/scenic/sun_crow.png';before=hashlib.sha256(texture.read_bytes()).hexdigest()
p=A/'geo/scenic/sun_crow.geo.json';geo=json.loads(p.read_text());g=geo['minecraft:geometry'][0]
assert [b['name'] for b in g['bones']]==[b['name'] for b in r.bones]
for old,new in zip(g['bones'],r.bones):
 assert len(old['cubes'])==len(new['cubes'])
 old['pivot']=new['pivot']
 for cube,source in zip(old['cubes'],new['cubes']):
  cube['origin']=source['origin'];cube['size']=source['size']
dump(p,geo)
lod_counts={}
for lod in ('medium','far'):
 reduced=copy.deepcopy(geo)
 for b in reduced['minecraft:geometry'][0]['bones']:
  cubes=b['cubes']
  b['cubes']=([c for c in cubes if min(c['size'])>=2 or b['name']=='head'] if lod=='medium' else cubes[:1]+cubes[1::2] if b['name'].endswith('_outer') else cubes[:2])
 reduced['minecraft:geometry'][0]['description']['identifier']+='_'+lod
 dump(A/f'geo/scenic/sun_crow_{lod}.geo.json',reduced)
 lod_counts[lod]=sum(len(b['cubes']) for b in reduced['minecraft:geometry'][0]['bones'])
anim={'format_version':'1.8.0','animations':{'animation.scenic.idle':{'loop':True,'animation_length':4,'bones':r.tracks}}}
dump(A/'animations/scenic/sun_crow.animation.json',anim)
source=json.loads((D/'blockbench/sun_crow.bbmodel').read_text()); by={b['name']:b for b in r.bones}
def groups(nodes):
 for n in nodes:
  if isinstance(n,dict):
   b=by[n['name']];n['origin']=[-b['pivot'][0],*b['pivot'][1:]];groups(n['children'])
groups(source['outliner'])
for element,(b,c) in zip(source['elements'],[(b,c) for b in r.bones for c in b['cubes']]):
 x,y,z=c['origin'];w,h,d=c['size'];element['from']=[-x-w,y,z];element['to']=[-x,y+h,z+d];element['origin']=[-b['pivot'][0],*b['pivot'][1:]]
for folder in (D,OUT):
 dump(folder/'blockbench/sun_crow.bbmodel',source);dump(folder/'blockbench/sun_crow.animation.json',anim)
authoring=json.loads((D/'authoring.json').read_text())
for record in authoring['records']:
 if record['name']=='sun_crow':record['lod_cubes']=lod_counts
dump(D/'authoring.json',authoring)
assert before==hashlib.sha256(texture.read_bytes()).hexdigest()
print('Exported sun_crow only; texture SHA256 unchanged:',before)
