from refine import *
import numpy as np
s=importlib.util.spec_from_file_location('geom',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);r.CATEGORY='blueprint/elite'
report={}
for id in SPECS:
 g=json.loads(old.path(id,'geo').read_text());before=json.loads((D/id/'before.geo.json').read_text());B={b['name']:b for b in g['minecraft:geometry'][0]['bones']};P={b['name']:b for b in before['minecraft:geometry'][0]['bones']};assert set(B)==set(P)
 for n,b in B.items():
  assert {k:v for k,v in b.items()if k!='cubes'}=={k:v for k,v in P[n].items()if k!='cubes'},(id,n)
  if any(old.category(id,n,j,c)[0]is None for j,c in enumerate(P[n].get('cubes',[]))):assert b==P[n],(id,n,'weapon modified')
 a=json.loads(old.path(id,'anim').read_text());assert old.path(id,'anim').read_bytes()==(D/id/'before.animation.json').read_bytes()
 im=Image.open(old.path(id,'texture')).convert('RGBA');assert im.crop((0,0,16,16)).tobytes()==Image.open(D/id/'before.png').convert('RGBA').crop((0,0,16,16)).tobytes()
 size=g['minecraft:geometry'][0]['description'];assert im.size==(size['texture_width'],size['texture_height']);occupied=set()
 for v in json.loads((D/id/'islands.json').read_text()):
  x,y,w,h=v['rect'];assert x>=0 and y>=18 and x+w<=im.width and y+h<=im.height
  for Y in range(y,y+h):
   for X in range(x,x+w):assert(X,Y)not in occupied;occupied.add((X,Y));assert im.getpixel((X,Y))[3]==255
 bounds={}
 for clip,an in a['animations'].items():
  points=np.concatenate([v for t in np.linspace(0,an.get('animation_length',1)*20,41)for v,u,b in r.geometry(id,clip=clip,tick=float(t))]);assert np.isfinite(points).all();bounds[clip]={'low':points.min(0).tolist(),'high':points.max(0).tolist()}
 report[id]={'sameBonesPivotsHierarchy':True,'sameAnimationBytes':True,'sameWeaponGeometryUVPixels':True,'facesDoNotShareUV':True,'shapeChanged':old.topology(g)!=old.topology(before),'size':im.size,'animatedBounds':bounds}
(D/'verification.json').write_text(json.dumps(report,indent=2));print('PASS',len(report),'rigs/weapon preservation, changed forms, UV, 41 samples per existing clip')
