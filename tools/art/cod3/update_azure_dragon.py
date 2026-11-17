#!/usr/bin/env python3
"""Export revised cuboids and tracks from dragon(), preserving the accepted pixel atlas and face islands."""
import copy,hashlib,json,shutil
from pathlib import Path
from scenic_resources import ROOT,A,D,dragon,dump
OUT=ROOT/'docs/art/cod3-azure-dragon-v2'
r=dragon();texture=A/'textures/entity/scenic/azure_dragon.png';before=hashlib.sha256(texture.read_bytes()).hexdigest()
p=A/'geo/scenic/azure_dragon.geo.json';geo=json.loads(p.read_text());g=geo['minecraft:geometry'][0]
assert [b['name'] for b in g['bones']]==[b['name'] for b in r.bones]
for old,new in zip(g['bones'],r.bones):
 assert len(old['cubes'])==len(new['cubes'])
 old['pivot']=new['pivot'];old['rotation']=new.get('rotation',[0,0,0])
 for cube,source in zip(old['cubes'],new['cubes']):
  cube['origin']=source['origin'];cube['size']=source['size']
dump(p,geo)
lod_counts={}
for lod in ('medium','far'):
 reduced=copy.deepcopy(geo)
 for b in reduced['minecraft:geometry'][0]['bones']:
  cubes=b['cubes']
  name=b['name']
  if lod=='medium':
   b['cubes']=cubes[:2] if name.startswith('trunk_') and int(name.split('_')[1])%2 else cubes[:2] if 'limb' in name else cubes
  else:
   limit=1 if name.startswith('trunk_') else 3 if 'antler' in name or name=='head' else 2 if 'limb' in name else 0 if 'whisker' in name else 1
   b['cubes']=cubes[:limit]

 reduced['minecraft:geometry'][0]['description']['identifier']+='_'+lod
 dump(A/f'geo/scenic/azure_dragon_{lod}.geo.json',reduced)
 lod_counts[lod]=sum(len(b['cubes']) for b in reduced['minecraft:geometry'][0]['bones'])
anim={'format_version':'1.8.0','animations':{'animation.scenic.idle':{'loop':True,'animation_length':4,'bones':r.tracks}}}
dump(A/'animations/scenic/azure_dragon.animation.json',anim)
source=json.loads((D/'blockbench/azure_dragon.bbmodel').read_text()); by={b['name']:b for b in r.bones}
def groups(nodes):
 for n in nodes:
  if isinstance(n,dict):
   b=by[n['name']];rot=b.get('rotation',[0,0,0]);n['rotation']=[-rot[0],-rot[1],rot[2]];n['origin']=[-b['pivot'][0],*b['pivot'][1:]];groups(n['children'])
groups(source['outliner'])
for element,(b,c) in zip(source['elements'],[(b,c) for b in r.bones for c in b['cubes']]):
 x,y,z=c['origin'];w,h,d=c['size'];element['from']=[-x-w,y,z];element['to']=[-x,y+h,z+d];element['origin']=[-b['pivot'][0],*b['pivot'][1:]]
for folder in (D,OUT):
 dump(folder/'blockbench/azure_dragon.bbmodel',source);dump(folder/'blockbench/azure_dragon.animation.json',anim)
assert before==hashlib.sha256(texture.read_bytes()).hexdigest()
print('Exported azure_dragon only; texture SHA256 unchanged:',before)
