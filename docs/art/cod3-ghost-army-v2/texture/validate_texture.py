"""Non-graphical file/UV integrity checks; never native/game acceptance."""
from pathlib import Path
import json,hashlib,base64,io
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;R=D.parents[3];M=D.parent;A=R/'src/main/resources/assets/dynasty';N='ghost_army_soldier'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 before=json.loads((D/'source-before.json').read_text());stable={p:sha(R/p)==h for p,h in before.items() if not p.endswith('.bbmodel')};assert all(stable.values()),stable
 lock=json.loads((M/'UV_LOCK.json').read_text());rows=lock['islands'];assert len(rows)==336;mask=np.zeros((256,256),int)
 keys={}
 for r in rows:
  x,y,w,h=r['rect'];assert w>0 and h>0 and x>=0 and y>=0 and x+w<=256 and y+h<=256;mask[y:y+h,x:x+w]+=1
  keys[(r['bone'],tuple(r['cube_origin']),tuple(r['cube_size']),tuple(r['cube_rotation']),tuple(r['cube_pivot'] or []),r['face'])]=r['rect']
 assert mask.max()==1
 counts=[]
 for lod in ('','_medium','_far'):
  g=json.loads((A/f'geo/scenic/{N}{lod}.geo.json').read_text())['minecraft:geometry'][0];assert g['description']['texture_width']==256 and g['description']['texture_height']==256;count=0
  for b in g['bones']:
   for c in b.get('cubes',[]):
    for face,uv in c['uv'].items():
     key=(b['name'],tuple(c['origin']),tuple(c['size']),tuple(c.get('rotation',[0,0,0])),tuple(c.get('pivot',[])),face)
     assert keys[key]==uv['uv']+uv['uv_size'],(lod,key);count+=1
  counts.append(count)
 im=Image.open(D/'texture.png');assert im.size==(256,256) and im.mode=='RGB';colors=len(im.getcolors(65536));assert colors<=36
 prod=A/f'textures/entity/scenic/{N}.png'
 embedded=False
 if prod.exists():
  assert prod.read_bytes()==(D/'texture.png').read_bytes()
  old=json.loads((D/'before'/f'{N}.bbmodel').read_text());new=json.loads((M/'blockbench'/f'{N}.bbmodel').read_text());assert len(new['textures'])==1
  assert base64.b64decode(new['textures'][0]['source'].split(',',1)[1])==prod.read_bytes()
  for b in (old,new):
   for t in b['textures']:t.pop('source');t.pop('name')
  assert old==new,'BB mutation outside embedded source/name';embedded=True
 report={'status':'PASS','atlas':[256,256],'colors':colors,'islands':336,'islandOverlap':False,'lodFaces':counts,'frozenSourceHashesUnchanged':stable,'bbEmbeddedMatchesProduction':embedded,'evidenceScope':'Python file/UV/palette checks and software previews only; native bake/client pending main','javaStarted':False}
 (D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':run()
