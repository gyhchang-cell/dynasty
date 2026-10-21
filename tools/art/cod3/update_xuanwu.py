#!/usr/bin/env python3
"""Export revised cuboids and tracks from turtle(), preserving the accepted pixel atlas and face islands."""
import copy,hashlib,json,shutil
from pathlib import Path
from scenic_resources import ROOT,A,D,turtle,dump
OUT=ROOT/'docs/art/cod3-xuanwu-v2'
r=turtle();texture=A/'textures/entity/scenic/mountain_xuanwu.png';before=hashlib.sha256(texture.read_bytes()).hexdigest()
p=A/'geo/scenic/mountain_xuanwu.geo.json';geo=json.loads(p.read_text());g=geo['minecraft:geometry'][0]
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
  b['cubes']=([c for c in cubes if min(c['size'])>=3 or b['name'] in ('head','snake_head')] if lod=='medium' else cubes[:4]+cubes[10:] if b['name']=='shell' else cubes[:2])
 reduced['minecraft:geometry'][0]['description']['identifier']+='_'+lod
 dump(A/f'geo/scenic/mountain_xuanwu_{lod}.geo.json',reduced)
 lod_counts[lod]=sum(len(b['cubes']) for b in reduced['minecraft:geometry'][0]['bones'])
anim={'format_version':'1.8.0','animations':{'animation.scenic.idle':{'loop':True,'animation_length':4,'bones':r.tracks}}}
dump(A/'animations/scenic/mountain_xuanwu.animation.json',anim)
source=json.loads((D/'blockbench/mountain_xuanwu.bbmodel').read_text()); by={b['name']:b for b in r.bones}
def groups(nodes):
 for n in nodes:
  if isinstance(n,dict):
   b=by[n['name']];n['origin']=[-b['pivot'][0],*b['pivot'][1:]];groups(n['children'])
groups(source['outliner'])
for element,(b,c) in zip(source['elements'],[(b,c) for b in r.bones for c in b['cubes']]):
 x,y,z=c['origin'];w,h,d=c['size'];element['from']=[-x-w,y,z];element['to']=[-x,y+h,z+d];element['origin']=[-b['pivot'][0],*b['pivot'][1:]]
for folder in (D,OUT):
 dump(folder/'blockbench/mountain_xuanwu.bbmodel',source);dump(folder/'blockbench/mountain_xuanwu.animation.json',anim)
authoring=json.loads((D/'authoring.json').read_text())
for record in authoring['records']:
 if record['name']=='mountain_xuanwu':record['lod_cubes']=lod_counts
dump(D/'authoring.json',authoring)
assert before==hashlib.sha256(texture.read_bytes()).hexdigest()
print('Exported mountain_xuanwu only; texture SHA256 unchanged:',before)
