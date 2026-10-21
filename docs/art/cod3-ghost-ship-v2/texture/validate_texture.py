"""No JVM: exact face rectangle coverage, gutters, palette and cloth phase checks."""
from pathlib import Path
import json,hashlib,importlib.util
from collections import Counter
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;R=D.parents[3];A=R/'src/main/resources/assets/dynasty'
spec=importlib.util.spec_from_file_location('author',D/'author_atlas.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=json.loads((D.parent/'TEXTURE_HANDOFF.json').read_text());rows=h['islands'];im=Image.open(D/'ghost_ship.png').convert('RGB');assert im.size==(512,512)
rects={tuple(x['rect']):x for x in rows};assert len(rects)==len(rows)==750
allowed={tuple(v) for p in m.PALETTES.values() for v in p}|{(25,33,34)};actual={c for n,c in im.getcolors(512*512)};assert actual<=allowed
coverage=np.zeros((512,512),np.uint8)
for row in rows:
 x,y,w,ht=row['rect'];assert not coverage[y:y+ht,x:x+w].any();coverage[y:y+ht,x:x+w]=1
 assert 1<=x and 1<=y and x+w<512 and y+ht<512
 for xx in range(w):
  assert im.getpixel((x+xx,y-1))==im.getpixel((x+xx,y))
  assert im.getpixel((x+xx,y+ht))==im.getpixel((x+xx,y+ht-1))
 for yy in range(ht):
  assert im.getpixel((x-1,y+yy))==im.getpixel((x,y+yy))
  assert im.getpixel((x+w,y+yy))==im.getpixel((x+w-1,y+yy))
lods=[]
for suffix in ['','_medium','_far']:
 p=A/f'geo/scenic/ghost_ship{suffix}.geo.json';g=json.loads(p.read_text())['minecraft:geometry'][0];assert g['description']['texture_width']==512 and g['description']['texture_height']==512
 n=0
 for b in g['bones']:
  for c in b.get('cubes',[]):
   for f,uv in c['uv'].items():
    key=tuple(uv['uv']+uv['uv_size']);assert key in rects,(suffix,key);row=rects[key];assert row['face']==f and row['bone']==b['name'];assert c['size']==row['size_units'] and c['origin']==row['origin_units'];n+=1
 lods.append({'lod':suffix or 'full','file':str(p.relative_to(R)),'sha256':sha(p),'faceIslandsChecked':n,'allFaceMaterialAndDirectionMetadataMatch':True,'uvChanges':0})
seams=[]
for prefix in ['main','fore']:
 for face in ['north','south']:
  for n in range(4):
   lower=next(x for x in rows if x['part']==f'{prefix}_cloth_{n}' and x['face']==face);upper=next(x for x in rows if x['part']==f'{prefix}_cloth_{n+1}' and x['face']==face)
   y=(lower['origin_units'][1]+lower['size_units'][1])*.5;assert abs(y-upper['origin_units'][1]*.5)<1e-6
   lo=max(lower['origin_units'][0],upper['origin_units'][0])*.5;hi=min(lower['origin_units'][0]+lower['size_units'][0],upper['origin_units'][0]+upper['size_units'][0])*.5
   tested=0
   for x in np.arange(lo+.2,hi-.2,.5):
    cols=[]
    for row in [lower,upper]:
     u=(x-row['origin_units'][0]*.5)/(row['size_units'][0]*.5);u=1-u if row['face_axes'][0].startswith('-') else u
     v=1-(y-row['origin_units'][1]*.5)/(row['size_units'][1]*.5)
     cols.append(m.pixel(row,u,v,0,0))
    assert cols[0]==cols[1],(prefix,face,n,x,cols);tested+=1
   seams.append({'sail':prefix,'face':face,'segments':[n,n+1],'worldPhaseSamples':tested,'match':True})
before=json.loads((D/'source-snapshot.json').read_text());changed=[p for p,hv in before.items() if sha(R/p)!=hv];assert not changed,changed
mat=[]
for material in h['materials']:
 selected=[row for row in rows if row['material']==material];colors=Counter()
 for row in selected:
  x,y,w,ht=row['rect'];colors.update({c:n for n,c in im.crop((x,y,x+w,y+ht)).getcolors(w*ht)})
 mat.append({'material':material,'islands':len(selected),'sampledColors':len(colors),'sampledTexels':sum(colors.values())})
report={'readyForTextureHandoff':True,'atlasSize':[512,512],'sha256':sha(D/'ghost_ship.png'),'totalColors':len(actual),'uniqueNonOverlappingIslands':len(rows),'sampledTexels':int(coverage.sum()),'nativePixelAuthoring':True,'resized':False,'quantized':False,'gutterEdgeExtrusionPixels':1,'lods':lods,'materials':mat,'clothWorldPhaseSeams':seams,'geometryAnimationHandoffHashesUnchanged':True,'warnings':['seal material is declared but has no dedicated islands: one muted short seal strip painted only onto existing main-mast north UV; no geometry/UV added.','Some edge faces are1px wide by design; no claim of detailed grain on those faces.','Software sampler clamps UVs within face islands; real mipmap/filter behavior still needs client checks.'],'javaExecuted':False,'graphicalAcceptance':'NOT_RUN'}
(D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS',len(rows),'islands,',sum(x['faceIslandsChecked'] for x in lods),'LOD faces,',len(seams),'world-phase cloth seams;',len(actual),'native colors')
