#!/usr/bin/env python3
"""Validate actual hollow bronze lion resources and sampled poses; never invoke Java/native tests."""
from pathlib import Path
import ast, hashlib, importlib.util, json, math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'docs/blueprint-cod1/evidence/bronze-suanni-v1'
ID='zhenmu_suanni_tonghou';paths=[];counts={}
def pairs(rows):
 d={}
 for k,v in rows:
  assert k not in d,('duplicate JSON key',k)
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
for identifier in (ID,'suanni_fixed_flame_jet','suanni_ground_fire_crack'):
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
 assert set(a)==({'animation.'+ID+'.'+n for n in ('idle','walk','fire','stomp','roar','hurt','death')} if identifier==ID else {'animation.'+identifier+'.idle'})
for p in [A/f'textures/entity/blueprint/elite/{ID}{suffix}.png' for suffix in ('','_dead')]+[A/f'textures/item/{n}.png' for n in ('suanni_copper_gear','stone_fire_cinder')]:
 paths.append(p);im=Image.open(p).convert('RGB');assert im.size==(16,16) and 2<=len(set(im.get_flattened_data()))<=4
 for y in range(16):
  for x in range(16):
   color=im.getpixel((x,y))
   if x<2 or x>13 or y<2 or y>13:assert color==(255,255,255)
   assert any(all(im.getpixel((xx,yy))==color for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15),(p,'color region smaller than2x2',x,y)
spec=importlib.util.spec_from_file_location('suanni_review',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/elite'
def points(clip='idle',tick=0,body=False):
 q=r.geometry(ID,clip='animation.'+ID+'.'+clip,tick=tick)
 if body:q=[p for p in q if p[2] not in ('exhaust_tail','curled_tail_tip')]
 return np.concatenate([p[0] for p in q])
report=read(D/'software-sampling.json');assert report['samplesPerClip']==81 and len(report['clips'])==7
assert all(c['minimumY']>=-1e-4 for c in report['clips'].values())
assert all(c['maximumY']/16<4.5 and c['maximumXZ']/16<3 for c in report['clips'].values())
assert all(c['minGroundedFeet']>=3 for c in report['clips'].values())
radius=0
for clip,c in report['clips'].items():
 definition=read(A/f'animations/blueprint/elite/{ID}.animation.json')['animations']['animation.'+ID+'.'+clip]
 for tick in np.linspace(0,definition['animation_length']*20,81):
  p=points(clip,float(tick));assert np.isfinite(p).all();radius=max(radius,float(np.linalg.norm(p[:,[0,2]],axis=1).max())/16)
 c.pop('samples',None);c['sampleCount']=81
report['bodyAndSupportsDimensionsMetres']=((points(body=True).max(0)-points(body=True).min(0))/16).round(4).tolist()
report['restVisibleDimensionsMetres']=((points().max(0)-points().min(0))/16).round(4).tolist()
report['maximumHorizontalRadiusMetres']=round(radius,4)
# Measure serial shin endpoints against the independent real paw pivots.
g=read(A/f'geo/blueprint/elite/{ID}.geo.json')['minecraft:geometry'][0]
piv={b['name']:np.array(b['pivot']) for b in g['bones']}
def matrices(clip,tick):
 definition=read(A/f'animations/blueprint/elite/{ID}.animation.json')['animations']['animation.'+ID+'.'+clip];world={}
 for b in g['bones']:
  ch=definition['bones'].get(b['name'],{});pos=piv[b['name']]-(piv[b['parent']] if b.get('parent') else np.zeros(3));rot=np.array(b.get('rotation',[0,0,0]),float)
  if 'position' in ch:pos=pos+r.sample(ch['position'],tick/20)
  if 'rotation' in ch:rot=rot+r.sample(ch['rotation'],tick/20)
  scale=r.sample(ch['scale'],tick/20) if 'scale' in ch else [1,1,1]
  world[b['name']]=(world[b['parent']] if b.get('parent') else np.eye(4))@r.transform(pos,rot,scale)
 return world
errors=[]
for clip in ('idle','walk','fire','stomp','roar','hurt'):
 definition=read(A/f'animations/blueprint/elite/{ID}.animation.json')['animations']['animation.'+ID+'.'+clip]
 for tick in np.linspace(0,definition['animation_length']*20,81):
  w=matrices(clip,float(tick))
  for name in ('front_left','front_right','rear_left','rear_right'):errors.append(float(np.linalg.norm((w[name+'_shin']@np.array([0,-10.5,0,1])-w[name+'_paw']@np.array([0,0,0,1]))[:3])))
assert max(errors)<.03,max(errors)
report['actualShinPawMaxErrorMetres']=round(max(errors)/16,6)
# Exact authored impact pose meets the native10tick stomp, not one tick later.
stomp=r.geometry(ID,clip='animation.'+ID+'.stomp',tick=10)
assert abs(min(v[:,1].min() for v,u,b in stomp if b=='front_left_bronze_ball'))<.001
report['auxiliaryGeometry']={}
for identifier in ('suanni_fixed_flame_jet','suanni_ground_fire_crack'):
 q=r.geometry(identifier,clip='animation.'+identifier+'.idle',tick=0);pts=np.concatenate([v for v,u,b in q]);assert np.isfinite(pts).all()
 report['auxiliaryGeometry'][identifier]={'dimensionsMetres':((pts.max(0)-pts.min(0))/16).round(4).tolist(),'counts':counts[identifier]}
report['nativePhysicsDimensionsMetres']={'width':4,'height':2.4,'flameWidth':.1,'flameHeight':.1,'crackWidth':.6,'crackHeight':1.2}
report['nativeAttackDimensionsMetres']={'fireTellTicks':24,'fireActiveTicks':60,'fireRangeFromMuzzle':8,'firePerFrameWidth':4,'sweepDegrees':90,'fireImpactTicks':[24,34,44,54,64,74],'stompTellTicks':10,'crackCount':5,'crackLineLength':5,'crackLifeTicks':60,'roarTellTicks':14,'roarRadius':4,'roarShieldCooldownTicks':60,'roarNativeKnockbackStrength':1.4,'heavyWindupStunTicks':35,'ownedEffectCap':6,'muzzleY':1.4375,'headPivotForward':.75,'muzzleDistanceFromPivot':1.25,'stompPivotSide':-.75,'stompPivotForward':.8125}
report['nativeClientCullDimensionsMetres']={'width':6,'height':5,'minRelativeY':-.5,'maxRelativeY':4.5,'flame':'actual directional segment+2m horizontal and1m vertical margin','crack':'native .6x1.2 bbox+.5m'}
data=R/'src/main/resources/data/dynasty'
for p in [data/f'loot_tables/entities/{ID}.json',data/f'advancements/blueprint/kill_{ID}.json',data/'tags/worldgen/structure/blueprint/suanni_sites.json',data/'recipes/blueprint/suanni_gear_recycle.json']:read(p);paths.append(p)
assert read(data/f'advancements/blueprint/kill_{ID}.json')['criteria']['kill']['conditions']['entity']['type']=='dynasty:'+ID
for name in ('zh_cn','en_us'):
 language=read(A/f'lang/{name}.json');assert 'entity.dynasty.'+ID in language
 for item in ('suanni_copper_gear','stone_fire_cinder'):
  assert 'item.dynasty.'+item in language;assert read(A/f'models/item/{item}.json')['textures']['layer0']=='dynasty:item/'+item
for p in [R/'tools/blueprint/generate_bronze_suanni.py',R/'tools/blueprint/review_bronze_suanni.py',Path(__file__)]:ast.parse(p.read_text());paths.append(p)
report['counts']=counts;report['staticChecks']='PASS_SOURCE_SOFTWARE_ONLY';report['nativeAcceptance']='NOT_RUN_USER_EXAM_JAVA_PAUSE'
report['resourceSha256']={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(D/'software-sampling.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Actual resources:',counts,'body',report['bodyAndSupportsDimensionsMetres'],'full',report['restVisibleDimensionsMetres'],'radius',report['maximumHorizontalRadiusMetres'])
print('Seven clips x81 finite/floor/loop/grounded real ball-supported limbs and measured serial shin-paw contacts; native NOT RUN. Source PNG/UV/use-path checks PASS.')
