"""Only UV and PNG export. Approved geometry and animation files are immutable."""
from pathlib import Path
from types import SimpleNamespace
import json,copy,sys,hashlib
from build import A,R,IDS,BUILDERS
from atlas import atlas
from animate import animate
D=R/'docs/art/boss-textures-v3'

def shape(doc):
 d=copy.deepcopy(doc);g=d['minecraft:geometry'][0]
 for key in ['texture_width','texture_height']:g['description'].pop(key,None)
 for b in g['bones']:
  for c in b['cubes']:c.pop('uv',None);c.pop('_material',None)
 return d

def run(ids):
 D.mkdir(parents=True,exist_ok=True)
 for id in ids:
  i=IDS.index(id);path=A/'geo/boss_forms'/(id+'.geo.json');doc=json.loads(path.read_text());before=shape(doc);geo=doc['minecraft:geometry'][0];template=BUILDERS[i]();animate(template,i);meta=template.by
  for b in geo['bones']:
   assert len(b['cubes'])==len(meta[b['name']]['cubes'])
   for c,m in zip(b['cubes'],meta[b['name']]['cubes']):c['_material']=m['_material']
  rig=SimpleNamespace(bones=geo['bones']);im=atlas(rig,i);geo['description'].update(texture_width=im.width,texture_height=im.height)
  assert shape(doc)==before,(id,'geometry changed')
  path.write_text(json.dumps(doc,indent=2)+'\n');im.save(A/'textures/entity/boss_forms'/(id+'.png'))
  out=D/id;out.mkdir(exist_ok=True);im.save(out/'texture.png');im.resize((im.width*4,im.height*4),resample=0).save(out/'texture-4x.png')
  (out/'islands.json').write_text(json.dumps(rig.texture_islands,indent=2)+'\n');print(id,im.size,len(rig.texture_islands),'unique face islands')
 if IDS[7] in ids:
  # Projectile is the same physical hammer. Update only its four UV dictionaries.
  p=A/'geo/boss_forms/hammer_chain.geo.json';doc=json.loads(p.read_text());before=shape(doc);geo=doc['minecraft:geometry'][0]
  source=json.loads((A/'geo/boss_forms'/(IDS[7]+'.geo.json')).read_text())['minecraft:geometry'][0]
  cubes=next(b['cubes'] for b in source['bones'] if b['name']=='hammer_1')
  assert len(cubes)==len(geo['bones'][0]['cubes'])
  for dest,src in zip(geo['bones'][0]['cubes'],cubes):dest['uv']=copy.deepcopy(src['uv'])
  for k in ['texture_width','texture_height']:geo['description'][k]=source['description'][k]
  assert shape(doc)==before
  p.write_text(json.dumps(doc,indent=2)+'\n')
  (A/'textures/entity/boss_forms/hammer_chain.png').write_bytes((A/'textures/entity/boss_forms'/(IDS[7]+'.png')).read_bytes())
if __name__=='__main__':run(sys.argv[1:] or IDS)
