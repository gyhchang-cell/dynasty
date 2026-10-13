#!/usr/bin/env python3
"""Validate the actual sword/field exports and current temple resource provenance, without Java."""
from pathlib import Path
import ast,json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'docs/blueprint-cod1/evidence/zhanlu-sword-v1';D.mkdir(parents=True,exist_ok=True)
p=R/'tools/blueprint/review_taoyan_cauldrons.py';ns={'__file__':str(p)};exec(p.read_text().split('\nreport={}\n',1)[0],ns)
r=ns['r'];r.CATEGORY='blueprint/artifact';references=ns['references'];raster=ns['raster'];sheet=ns['sheet'];sheet.__globals__['D']=D
for n in ast.parse(p.read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name=='render':exec(ast.get_source_segment(p.read_text(),n).replace('blueprint/boss','blueprint/artifact'),ns)
report={}
for ident in ('zhanlu_rendao_bamian_jian','zhanlu_ceasefire_field'):
 g=json.loads((A/f'geo/blueprint/artifact/{ident}.geo.json').read_text())['minecraft:geometry'][0];a=json.loads((A/f'animations/blueprint/artifact/{ident}.animation.json').read_text())['animations'];names={b['name'] for b in g['bones']};assert len(names)==len(g['bones'])
 for b in g['bones']:
  assert not b.get('parent') or b['parent'] in names
  for c in b.get('cubes',[]):
   assert all(x>0 and math.isfinite(x) for x in c['size'])
   for face,u in c['uv'].items():
    assert all(type(v)==int for v in u['uv']+u['uv_size'])
    x,y=u['uv'];w,h=u['uv_size'];assert 2<=x<=14-w and 2<=y<=14-h and w>=2 and h>=2
 samples=[]
 for name,clip in a.items():
  assert set(clip['bones'])<=names
  q0=np.concatenate([v for v,u,b in r.geometry(ident,clip=name,tick=0)])
  qe=np.concatenate([v for v,u,b in r.geometry(ident,clip=name,tick=clip['animation_length']*20)])
  if clip.get('loop'):assert np.max(np.abs(q0-qe))<1e-7,(ident,'loop')
  for tick in np.linspace(0,clip['animation_length']*20,81):
   points=np.concatenate([v for v,u,b in r.geometry(ident,clip=name,tick=float(tick))]);assert np.isfinite(points).all();assert points[:,1].min()>=-1e-6
   desc=g['description'];minimum=(desc['visible_bounds_offset'][1]-desc['visible_bounds_height']/2)*16;maximum=(desc['visible_bounds_offset'][1]+desc['visible_bounds_height']/2)*16
   assert points[:,1].min()>=minimum and points[:,1].max()<=maximum;assert np.abs(points[:,[0,2]]).max()<=desc['visible_bounds_width']*8
   samples.append(points)
 points=np.concatenate(samples);report[ident]={'bones':len(g['bones']),'cuboids':sum(len(b.get('cubes',[])) for b in g['bones']),'clips':len(a),'samplesPerClip':81,'minimumYMetres':float(points[:,1].min()/16),'maximumYMetres':float(points[:,1].max()/16),'maximumRadiusMetres':float(np.linalg.norm(points[:,[0,2]],axis=1).max()/16),'fullRestDimensionsMetres':((q0.max(0)-q0.min(0))/16).tolist()}
 assert ident!='zhanlu_ceasefire_field' or report[ident]['maximumRadiusMetres']<=5
geo=json.loads((A/'geo/blueprint/artifact/zhanlu_rendao_bamian_jian.geo.json').read_text())['minecraft:geometry'][0];cubes=[c for b in geo['bones'] for c in b.get('cubes',[])];mesh=json.loads((A/'models/item/zhanlu_rendao_bamian_jian_mesh.json').read_text())['elements'];assert len(cubes)==len(mesh)==15
for c,e in zip(cubes,mesh):
 assert np.max(np.abs(np.array(e['from'])-np.array(c['origin'])-[8,5,8]))<1e-8
 assert np.max(np.abs(np.array(e['to'])-np.array(e['from'])-np.array(c['size'])))<1e-8
 if c.get('rotation'):assert e['rotation']['angle']==-45 and e['rotation']['axis']=='y' and np.max(np.abs(np.array(e['rotation']['origin'])-np.array(c['pivot'])-[8,5,8]))<1e-8
assert abs(report['zhanlu_rendao_bamian_jian']['maximumYMetres']-1.4)<1e-8
# Intersect actual cuboid cross-sections with a blade plane. Their union has the prescribed eight corners.
parts=[]
for b in geo['bones']:
 for c in b.get('cubes',[]):
  if not c['origin'][1]<=10<=c['origin'][1]+c['size'][1]:continue
  x,y,z=c['origin'];w,h,d=c['size'];verts=np.array([[x,z],[x+w,z],[x+w,z+d],[x,z+d]])
  if c.get('rotation'):
   pivot=np.array(c['pivot'])[[0,2]];angle=math.radians(45);rot=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]);verts=(verts-pivot)@rot.T+pivot
  parts.append(verts)
points=sorted({tuple(round(float(v),10) for v in point) for part in parts for point in part})
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def half(rows):
 out=[]
 for point in rows:
  while len(out)>1 and cross(out[-2],out[-1],point)<=1e-9:out.pop()
  out.append(point)
 return out
corners=half(points)[:-1]+half(list(reversed(points)))[:-1]
assert len(corners)==8,corners
assert set(corners)=={(-2.,-.5),(-1.5,-1.),(1.5,-1.),(2.,-.5),(2.,.5),(1.5,1.),(-1.5,1.),(-2.,.5)},corners
# Check the actual cuboid union, not merely its convex hull, on a dense blade section.
for x in np.linspace(-2,2,81):
 for z in np.linspace(-1,1,41):
  expected=abs(x)<=2+1e-8 and abs(z)<=1+1e-8 and abs(x)+abs(z)<=2.5+1e-8
  actual=False
  for part in parts:
   signs=[cross(tuple(part[i]),tuple(part[(i+1)%4]),(x,z)) for i in range(4)]
   if all(v>=-1e-8 for v in signs) or all(v<=1e-8 for v in signs):actual=True;break
  assert actual==expected,(x,z,actual,expected)
paths=set(R.glob('src/main/java/com/dynasty/blueprint/artifact/**/*.java'))|set(R.glob('src/main/resources/assets/dynasty/*/blueprint/artifact/*zhanlu*'))|set(R.glob('src/main/resources/assets/dynasty/models/item/zhanlu*'))|set(R.glob('src/main/resources/assets/dynasty/textures/entity/blueprint/artifact/zhanlu*'))|set(R.glob('src/main/resources/assets/dynasty/textures/item/zhanlu*'))|set(R.glob('src/main/resources/data/dynasty/advancements/blueprint/acquire_zhanlu*'))|{R/'tools/blueprint/generate_zhanlu.py',R/'src/main/resources/data/dynasty/damage_type/zhanlu_void_submission.json',R/'src/main/resources/assets/dynasty/lang/zh_cn.json',R/'src/main/resources/assets/dynasty/lang/en_us.json'}
paths.update(R.glob('src/main/resources/assets/dynasty/models/block/taiqing*.json'));paths.update(R.glob('src/main/resources/assets/dynasty/blockstates/taiqing*.json'));paths.update(R.glob('src/main/resources/assets/dynasty/textures/block/taiqing*.png'));paths.update(R.glob('src/main/resources/data/dynasty/**/*taiqing*.json'));paths.update(R/p for p in ('tools/blueprint/generate_taiqing_resources.py','tools/blueprint/review_taiqing_case.py','tools/blueprint/validate_zhanlu.py','docs/blueprint-cod1/evidence/zhanlu-sword-v1/taiqing-case-states.png','docs/blueprint-cod1/evidence/zhanlu-sword-v1/taiqing-case-software.json'))
for tag in ('bypasses_armor','bypasses_resistance','bypasses_enchantments','bypasses_shield'):paths.add(R/f'src/main/resources/data/minecraft/tags/damage_type/{tag}.json')
result={'staticChecks':'PASS_SOURCE_SOFTWARE_ONLY','nativeChecks':'NOT_RUN_USER_EXAM_JAVA_PAUSE','models':report,'wholeWeaponLengthMetres':1.4,'actualJadeBladeSectionCorners':corners,'heldMeshParity':True,'sourceMechanics':{'fourDistinctProfiles':True,'windupTicks':20,'fieldDurationTicks':80,'radiusMetres':5,'targetCap':16,'movementMultiplier':.3,'restoreLeaseGraceTicks':3,'healMaximumHealthFraction':.3,'normalGuardTicks':3,'maximumMissingHealthGuardTicks':12,'voidDamageMultiplier':3,'voidBypassesInvulnerability':False},'nativeAcceptance':'EIGHT_ARTIFACT_PLUS_TWO_TEMPLE_SOURCE_TESTS_WRITTEN_NOT_RUN','pending':['NATIVE_BUILD_AND_API_VALIDATION','NATIVE_TEMPLE_GENERATION_FLOOR_TRAVERSAL_ALL_THREE_GOALS_CASE_SHAPE_CULLING_AND_SAVED_CLAIM','SINGLE_AND_TWO_PLAYER_ACTUAL_HELD_CHAIN_STANCE_COMBAT_WORLD_RELOAD','DENSE_HOSTILE_COUNTS_ABOVE16_AND_PVP_DISARM_POLICY','FULL_MANUAL_ATTACK_CLOCK_INTERRUPT_FOR_OTHER_ELITES','GEAR_DURABILITY_DAMAGE_STUN_COOLDOWN_BALANCE_AND_PERFORMANCE'],'resourceSha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}}
result['acquisitionSource']={'status':'ACTUAL_STRUCTURE_THREE_SERVER_GOALS_AND_CASE_SOURCE_WIRED_NATIVE_PENDING','structure':'dynasty:taiqing_hidden_temple','meditationStationaryTicks':40,'pathWaypoints':5,'unhurtRingTicks':120,'ringPulses':4,'trialMaximumTicks':1800,'claimScope':'PER_WORLD_PLAYER_UUID','caseSoftware':json.loads((D/'taiqing-case-software.json').read_text())}
(D/'validated-source.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report));print('Actual fifteen-cuboid held/world parity, eight-sided blade, two81-sample clips/floor/cull/loops PASS_SOFTWARE_ONLY')
