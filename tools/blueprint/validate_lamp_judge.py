#!/usr/bin/env python3
"""Validate actual ledger resources and sampled poses; never invoke Java/native tests."""
from pathlib import Path
import ast, hashlib, importlib.util, json, math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'docs/blueprint-cod1/evidence/lamp-judge-v1'
ID='qingdeng_panguan_guichai';paths=[];counts={}
def pairs(rows):
 d={}
 for k,v in rows:
  assert k not in d,('duplicate JSON key',k)
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
for identifier in (ID,'judge_falling_pen','judge_ink_stroke','judge_chain_cage'):
 gp=A/f'geo/blueprint/elite/{identifier}.geo.json';ap=A/f'animations/blueprint/elite/{identifier}.animation.json';paths.extend((gp,ap))
 g=read(gp)['minecraft:geometry'][0];a=read(ap)['animations'];bones={b['name']:b for b in g['bones']};assert len(bones)==len(g['bones'])
 counts[identifier]={'bones':len(bones),'cuboids':sum(len(b.get('cubes',[])) for b in bones.values()),'clips':len(a)}
 for b in bones.values():
  chain=set();parent=b
  while parent.get('parent'):
   assert parent['name'] not in chain;chain.add(parent['name']);parent=bones[parent['parent']]
  for c in b.get('cubes',[]):
   assert all(v>0 and math.isfinite(v) for v in c['size'])
   for f in c['uv'].values():
    u,v=f['uv'];w,h=f['uv_size'];assert all(isinstance(n,int) for n in (u,v,w,h));assert min(u,v)>=0 and u+w<=16 and v+h<=16
 for clip,definition in a.items():
  assert clip.startswith('animation.'+identifier+'.') and set(definition['bones'])<=set(bones)
  for ch in definition['bones'].values():
   for channel,track in ch.items():
    if isinstance(track,dict):
     assert all(0<=float(t)<=definition['animation_length'] for t in track)
     assert all(math.isfinite(n) for vec in track.values() for n in vec)
     if definition.get('loop'):
      ordered=sorted(track,key=float);delta=np.array(track[ordered[-1]])-track[ordered[0]]
      if channel=='rotation':delta=(delta+180)%360-180
      assert np.allclose(delta,0),('loop seam',clip,channel)
    else:assert all(math.isfinite(n) for n in track)
 assert set(a)==({'animation.'+ID+'.'+n for n in ('idle','walk','name','strokes','cage','hurt','death')} if identifier==ID else {'animation.'+identifier+'.idle'})
for p in [A/f'textures/entity/blueprint/elite/{ID}.png']+[A/f'textures/item/{n}.png' for n in ('judge_iron_page','sealed_judge_ink')]:
 paths.append(p);im=Image.open(p).convert('RGB');assert im.size==(16,16) and len(set(im.get_flattened_data()))==4
 for y in range(16):
  for x in range(16):
   color=im.getpixel((x,y))
   if x<2 or x>13 or y<2 or y>13:assert color==(255,255,255)
   assert any(all(im.getpixel((xx,yy))==color for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15),(p,'color region smaller than2x2',x,y)
spec=importlib.util.spec_from_file_location('ledger_review',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/elite'
def points(clip='idle',tick=0,body=False):
 q=r.geometry(ID,clip='animation.'+ID+'.'+clip,tick=tick)
 if body:q=[p for p in q if not p[2].startswith(('brush_','judgment_','broken_brush','page_butterfly'))]
 return np.concatenate([p[0] for p in q])
report=read(D/'software-sampling.json');assert report['samplesPerClip']==81 and len(report['clips'])==7
assert all(c['minimumY']>=-1e-4 for c in report['clips'].values())
assert all(c['maximumY']/16<4 and c['maximumXZ']/16<3.3 for c in report['clips'].values())
assert report['clips']['walk']['minGroundedFeet']==1
radius=0
for clip,c in report['clips'].items():
 definition=read(A/f'animations/blueprint/elite/{ID}.animation.json')['animations']['animation.'+ID+'.'+clip]
 for tick in np.linspace(0,definition['animation_length']*20,81):
  p=points(clip,float(tick));assert np.isfinite(p).all();radius=max(radius,float(np.linalg.norm(p[:,[0,2]],axis=1).max())/16)
 c.pop('samples',None);c['sampleCount']=81
report['bodyAndSupportsDimensionsMetres']=((points(body=True).max(0)-points(body=True).min(0))/16).round(4).tolist()
report['restVisibleDimensionsMetres']=((points().max(0)-points().min(0))/16).round(4).tolist()
report['maximumHorizontalRadiusMetres']=round(radius,4)
assert set(report['auxiliaryGeometry'])=={'judge_falling_pen','judge_ink_stroke','judge_chain_cage'}
report['nativePhysicsDimensionsMetres']={'width':2.4,'height':2.2,'penWidth':.75,'penHeight':5}
report['nativeAttackDimensionsMetres']={'nameInitialRange':28,'trackedTargetCap':64,'lockTick':36,'fallingPenTipRadius':.3,'penLifeTicks':30,'strokeCount':5,'strokeLength':5.5,'strokeWidth':.5,'strokeLifeTicks':80,'brushPivotSide':-1.25,'brushPivotForward':-.25,'brushNibDistance':2.3125,'brushNibY':1.125,'cageDiameter':6,'cageLifeTicks':160,'capturedPlayerCap':8,'ownedSpellCap':7}
report['nativeClientCullDimensionsMetres']={'width':6.6,'height':4.4,'minRelativeY':-.4,'maxRelativeY':4,'penWidth':1.2,'penHeight':5.2,'cageWidth':7.4,'cageHeight':3.2,'stroke':'actual directional segment +.5m margin; named marker union <=64m'}
data=R/'src/main/resources/data/dynasty'
for p in [data/f'loot_tables/entities/{ID}.json',data/f'advancements/blueprint/kill_{ID}.json',data/'tags/worldgen/structure/blueprint/judge_sites.json']+[data/f'recipes/blueprint/{i}_recycle.json' for i in ('judge_iron_page','sealed_judge_ink')]:read(p);paths.append(p)
assert read(data/f'advancements/blueprint/kill_{ID}.json')['criteria']['kill']['conditions']['entity']['type']=='dynasty:'+ID
for name in ('zh_cn','en_us'):
 language=read(A/f'lang/{name}.json');assert 'entity.dynasty.'+ID in language
 for item in ('judge_iron_page','sealed_judge_ink'):
  assert 'item.dynasty.'+item in language;assert read(A/f'models/item/{item}.json')['textures']['layer0']=='dynasty:item/'+item
for p in [R/'tools/blueprint/generate_lamp_judge.py',R/'tools/blueprint/review_lamp_judge.py',Path(__file__)]:ast.parse(p.read_text());paths.append(p)
report['counts']=counts;report['staticChecks']='PASS_SOURCE_SOFTWARE_ONLY';report['nativeAcceptance']='NOT_RUN_USER_EXAM_JAVA_PAUSE'
report['resourceSha256']={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(D/'software-sampling.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Actual resources:',counts,'body',report['bodyAndSupportsDimensionsMetres'],'full',report['restVisibleDimensionsMetres'],'radius',report['maximumHorizontalRadiusMetres'])
print('Seven clips x81 finite/floor/loop/grounded inkstone; native NOT RUN. Source PNG/UV/use-path checks PASS.')
