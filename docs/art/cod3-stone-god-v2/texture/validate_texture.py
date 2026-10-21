"""Read-only exact-UV validation, without JVM or game client."""
from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;R=D.parents[3];A=R/'src/main/resources/assets/dynasty'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=json.loads((D.parent/'TEXTURE_HANDOFF.json').read_text());rows=h['islands'];im=Image.open(D/'stone_god.png').convert('RGB');assert im.size==(1024,1024)
assert h==json.loads((D.parent/'UV_LOCK.json').read_text()) and h['status']=='UV_FROZEN'
author=json.loads((D/'authoring.json').read_text());allowed={tuple(c) for p in author['palettes'].values() for c in p}|{(30,39,40)}
actual={c for n,c in im.getcolors(1024**2)};assert actual<=allowed
rects={tuple(r['rect']):r for r in rows};assert len(rects)==len(rows)==420
coverage=np.zeros((1024,1024),np.uint8)
for row in rows:
 x,y,w,ht=row['rect'];assert 1<=x and 1<=y and x+w<1024 and y+ht<1024
 assert not coverage[y:y+ht,x:x+w].any();coverage[y:y+ht,x:x+w]=1
 for xx in range(w):
  assert im.getpixel((x+xx,y-1))==im.getpixel((x+xx,y))
  assert im.getpixel((x+xx,y+ht))==im.getpixel((x+xx,y+ht-1))
 for yy in range(ht):
  assert im.getpixel((x-1,y+yy))==im.getpixel((x,y+yy))
  assert im.getpixel((x+w,y+yy))==im.getpixel((x+w-1,y+yy))
 colors={c for n,c in im.crop((x,y,x+w,y+ht)).getcolors(w*ht)}
 assert colors<={tuple(c) for c in author['palettes'][row['material']]}
lods=[]
for suffix in ['','_medium','_far']:
 p=A/f'geo/scenic/stone_god{suffix}.geo.json';g=json.loads(p.read_text())['minecraft:geometry'][0];assert g['description']['texture_width']==1024 and g['description']['texture_height']==1024
 n=0
 for b in g['bones']:
  for c in b.get('cubes',[]):
   for f,uv in c['uv'].items():
    key=tuple(uv['uv']+uv['uv_size']);assert key in rects,(suffix,key);row=rects[key]
    assert row['face']==f and row['bone']==b['name']
    assert c['size']==row['cube_size'] and c['origin']==row['cube_origin']
    assert c.get('rotation',[0,0,0])==row['cube_rotation']
    assert c.get('pivot')==row['cube_pivot'];n+=1
 lods.append({'lod':suffix or 'full','sha256':sha(p),'faceIslandsChecked':n,'uvChanges':0})
before=json.loads((D/'source-snapshot.json').read_text());changed=[p for p,hv in before.items() if sha(R/p)!=hv];assert not changed,changed
report={'readyForTextureHandoff':True,'atlasSize':[1024,1024],'sha256':sha(D/'stone_god.png'),'totalColors':len(actual),'uniqueNonOverlappingIslands':len(rows),'sampledTexels':int(coverage.sum()),'nativePixelAuthoring':True,'resized':False,'quantized':False,'gutterEdgeExtrusionPixels':1,'lods':lods,'allFaceMaterialDirectionOriginSizeRotationPivotMatch':True,'geometryAnimationHandoffHashesUnchanged':True,'ghostShipHashUnchanged':True,'javaExecuted':False,'graphicalAcceptance':'NOT_RUN','limitations':['Software nearest sampling clamps inside each UV island; real mipmap, fog, night lighting and animation must be checked by integrating chat in client.','No claim of fine grain on narrow 1px face islands.']}
(D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS:',len(rows),'islands;',sum(x['faceIslandsChecked'] for x in lods),'LOD faces;',len(actual),'native palette colors; protected source hashes unchanged')
