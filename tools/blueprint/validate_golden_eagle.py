#!/usr/bin/env python3
"""Validate actual eagle resources and sampled poses; never invoke Java/native tests."""
from pathlib import Path
import ast, hashlib, importlib.util, json, math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'docs/blueprint-cod1/evidence/golden-eagle-v1'
ID='liefeng_jindiao_yushi';paths=[];counts={}
def pairs(rows):
 d={}
 for k,v in rows:
  assert k not in d,('duplicate JSON key',k)
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
for identifier in (ID,'eagle_finite_gold_arrow'):
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
 assert set(a)==({'animation.'+ID+'.'+n for n in ('idle','fly','rain','fan','dive','hurt','death')} if identifier==ID else {'animation.'+identifier+'.idle'})
for p in [A/f'textures/entity/blueprint/elite/{ID}{suffix}.png' for suffix in ('','_dead')]+[A/f'textures/item/{n}.png' for n in ('eagle_hard_feather','eagle_rib_bow_fragment')]:
 paths.append(p);im=Image.open(p).convert('RGB');assert im.size==(16,16) and len(set(im.get_flattened_data()))==4
 for y in range(16):
  for x in range(16):
   color=im.getpixel((x,y))
   if x<2 or x>13 or y<2 or y>13:assert color==(255,255,255)
   assert any(all(im.getpixel((xx,yy))==color for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15),(p,'color region smaller than2x2',x,y)
spec=importlib.util.spec_from_file_location('eagle_review',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/elite'
def points(clip='idle',tick=0,body=False):
 q=r.geometry(ID,clip='animation.'+ID+'.'+clip,tick=tick)
 if body:q=[p for p in q if not p[2] in ('rib_bow','upper_bow_limb','lower_bow_limb','upper_string','lower_string','drawn_arrow')]
 return np.concatenate([p[0] for p in q])
report=read(D/'software-sampling.json');assert report['samplesPerClip']==81 and len(report['clips'])==7
assert all(c['minimumY']+64>=0 for c in report['clips'].values())
assert report['clips']['death']['minimumY']>=-1e-4 and report['clips']['dive']['minimumY']>=-1e-4
assert all(c['maximumY']/16<5.2 and c['minimumY']/16>-1.8 and c['maximumXZ']/16<4 for c in report['clips'].values())
radius=0
for clip,c in report['clips'].items():
 definition=read(A/f'animations/blueprint/elite/{ID}.animation.json')['animations']['animation.'+ID+'.'+clip]
 for tick in np.linspace(0,definition['animation_length']*20,81):
  p=points(clip,float(tick));assert np.isfinite(p).all();radius=max(radius,float(np.linalg.norm(p[:,[0,2]],axis=1).max())/16)
 c.pop('samples',None);c['sampleCount']=81
report['bodyAndSupportsDimensionsMetres']=((points(body=True).max(0)-points(body=True).min(0))/16).round(4).tolist()
report['restVisibleDimensionsMetres']=((points().max(0)-points().min(0))/16).round(4).tolist()
report['maximumHorizontalRadiusMetres']=round(radius,4)
assert set(report['auxiliaryGeometry'])=={'eagle_finite_gold_arrow'}
# Independently verify both actual serial joint endpoints and both string halves at all sampled poses.
def matrices(clip,tick):
 g=read(A/f'geo/blueprint/elite/{ID}.geo.json')['minecraft:geometry'][0];definition=read(A/f'animations/blueprint/elite/{ID}.animation.json')['animations']['animation.'+ID+'.'+clip]
 piv={b['name']:np.array(b['pivot']) for b in g['bones']};world={}
 for b in g['bones']:
  ch=definition['bones'].get(b['name'],{});pos=piv[b['name']]-(piv[b['parent']] if b.get('parent') else np.zeros(3));rot=np.array(b.get('rotation',[0,0,0]),float)
  if 'position' in ch:pos=pos+r.sample(ch['position'],tick/20)
  if 'rotation' in ch:rot=rot+r.sample(ch['rotation'],tick/20)
  scale=r.sample(ch['scale'],tick/20) if 'scale' in ch else [1,1,1]
  world[b['name']]=(world[b['parent']] if b.get('parent') else np.eye(4))@r.transform(pos,rot,scale)
 return world
errors=[];nocks=[];anchors=[]
for clip,c in report['clips'].items():
 definition=read(A/f'animations/blueprint/elite/{ID}.animation.json')['animations']['animation.'+ID+'.'+clip]
 for tick in np.linspace(0,definition['animation_length']*20,81):
  w=matrices(clip,float(tick))
  for name in ('grip','draw'):errors.append(float(np.linalg.norm((w[name+'_hock']@np.array([0,-12,0,1])-w[name+'_talon']@np.array([0,0,0,1]))[:3])))
  if clip=='rain':
   nock=w['drawn_arrow']@np.array([0,0,0,1]);draw=w['draw_talon']@np.array([0,0,0,1]);nocks.append(float(np.linalg.norm((nock-draw)[:3])))
   for side,sign in [('upper',1),('lower',-1)]:
    middle=w[side+'_string']@np.array([0,-sign*20,0,1]);anchors.append(float(np.linalg.norm((middle-nock)[:3])))
assert max(errors)<.025 and max(nocks)<.001 and max(anchors)<.025,(max(errors),max(nocks),max(anchors))
report['actualTalonHockMaxErrorMetres']=round(max(errors)/16,6);report['actualArrowNockAndStringMaxErrorMetres']=round(max(nocks+anchors)/16,6)
assert np.ptp(points('death',84),axis=0).max()<.001
report['nativePhysicsDimensionsMetres']={'width':2.2,'height':2.8,'arrowWidth':.3,'arrowHeight':.3,'groundHover':4}
report['nativeAttackDimensionsMetres']={'rainTellTicks':30,'rainCount':24,'rainRadius':4,'fanTellTicks':12,'fanCount':36,'fanDegrees':180,'diveTellTicks':16,'diveTravelTicks':16,'diveRadius':2,'lateHeavyCounterTicks':100,'ownedArrowCap':80,'markerLifeTicks':30,'arrowLifeTicks':60,'arrowRange':48,'featherRange':16,'bowPivotSide':-.8125,'bowPivotY':.625,'bowTipForward':round((12+5/math.sqrt(2))/16,6),'bowTipY':round((10+5/math.sqrt(2))/16,6)}
report['nativeClientCullDimensionsMetres']={'width':8,'height':7,'minRelativeY':-1.8,'maxRelativeY':5.2,'arrow':'native bbox inflated1m'}
data=R/'src/main/resources/data/dynasty'
for p in [data/f'loot_tables/entities/{ID}.json',data/f'advancements/blueprint/kill_{ID}.json',data/'tags/worldgen/structure/blueprint/eagle_sites.json']+[data/'recipes/blueprint/eagle_feather_arrow.json',data/'recipes/blueprint/eagle_bow_fragment_recycle.json']:read(p);paths.append(p)
assert read(data/f'advancements/blueprint/kill_{ID}.json')['criteria']['kill']['conditions']['entity']['type']=='dynasty:'+ID
for name in ('zh_cn','en_us'):
 language=read(A/f'lang/{name}.json');assert 'entity.dynasty.'+ID in language
 for item in ('eagle_hard_feather','eagle_rib_bow_fragment'):
  assert 'item.dynasty.'+item in language;assert read(A/f'models/item/{item}.json')['textures']['layer0']=='dynasty:item/'+item
for p in [R/'tools/blueprint/generate_golden_eagle.py',R/'tools/blueprint/review_golden_eagle.py',Path(__file__)]:ast.parse(p.read_text());paths.append(p)
report['counts']=counts;report['staticChecks']='PASS_SOURCE_SOFTWARE_ONLY';report['nativeAcceptance']='NOT_RUN_USER_EXAM_JAVA_PAUSE'
report['resourceSha256']={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(D/'software-sampling.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Actual resources:',counts,'body',report['bodyAndSupportsDimensionsMetres'],'full',report['restVisibleDimensionsMetres'],'radius',report['maximumHorizontalRadiusMetres'])
print('Seven clips x81 finite/flight and landing floor/loop; actual hock/talon/nock/string endpoints; native NOT RUN. Source PNG/UV/use-path checks PASS.')
