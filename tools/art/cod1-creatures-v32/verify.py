"""Narrow production-resource checks, not a gameplay audit framework."""
from paint import *
from PIL import Image
D=R/'docs/art/cod1-creatures-v32'
results={}
for id,spec in SPECS.items():
 data=json.loads(path(id,'geo').read_text());before=json.loads((D/id/'before.geo.json').read_text());assert topology(data)==topology(before),id
 png=Image.open(path(id,'texture')).convert('RGBA');legacy=Image.open(D/id/'before-texture.png').convert('RGBA');assert png.crop((0,0,16,16)).tobytes()==legacy.tobytes()
 desc=data['minecraft:geometry'][0]['description'];assert png.size==(desc['texture_width'],desc['texture_height'])
 islands=json.loads((D/id/'islands.json').read_text());occupied=set()
 for v in islands:
  x,y,w,h=v['rect'];assert x>=0 and y>=18 and x+w<=png.width and y+h<=png.height
  for Y in range(y,y+h):
   for X in range(x,x+w):
    assert (X,Y)not in occupied,(id,v);occupied.add((X,Y));assert png.getpixel((X,Y))[3]==255
 for b in data['minecraft:geometry'][0]['bones']:
  for j,c in enumerate(b.get('cubes',[])):
   mat,role=category(id,b['name'],j,c)
   if mat is None:
    original=next(v for v in before['minecraft:geometry'][0]['bones'] if v['name']==b['name'])['cubes'][j];assert original==c,(id,b['name'])
 oldanim=R/'build/cod1-creatures-v32/baseline'/path(id,'anim').relative_to(R)
 if oldanim.exists():assert oldanim.read_bytes()==path(id,'anim').read_bytes()
 results[id]={'geometryAndSkeletonUnchanged':True,'animationBytesUnchanged':oldanim.exists(),'oldWeaponUVAndPixelsUnchanged':True,'allPaintedIslandsOpaqueAndDisjoint':True,'textureSize':png.size,'paintedFaces':len(islands),'pngSha256':hashlib.sha256(path(id,'texture').read_bytes()).hexdigest(),'geoSha256':hashlib.sha256(path(id,'geo').read_bytes()).hexdigest()}
report={'result':'PASS','scope':'9 production creatures: geometry/bones, all original animation bytes, unchanged weapon UV/pixels, non-overlapping opaque body UV islands, matching dimensions. Not natural combat/MP certification.','creatures':results}
(D/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report['result'],len(results))
