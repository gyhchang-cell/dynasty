#!/usr/bin/env python3
"""Inspect this aircraft's actual exported cuboids and animation ports. Never starts Java or a game."""
from pathlib import Path
import hashlib,importlib.util,json,math
from functools import lru_cache
from types import SimpleNamespace
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'docs/blueprint-cod1/evidence/wood-kite-v1';ID='luban_yisha';forms=(ID,ID+'_metal');paths=set()
def read(p):
 paths.add(p)
 def unique(rows):
  out={}
  for k,v in rows:assert k not in out,('duplicate key',k);out[k]=v
  return out
 return json.loads(p.read_text(),object_pairs_hook=unique)
spec=importlib.util.spec_from_file_location('kite_actual_geometry',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/boss';r.json=SimpleNamespace(loads=lru_cache(maxsize=8)(json.loads))
def matrices(g,ch,t):
 piv={b['name']:np.array(b['pivot'],float) for b in g['bones']};world={}
 for b in g['bones']:
  track=ch.get(b['name'],{});position=piv[b['name']]-(piv[b['parent']] if b.get('parent') else np.zeros(3));position+=r.sample(track.get('position',[0,0,0]),t/20)
  rotation=np.array(b.get('rotation',[0,0,0]),float)+r.sample(track.get('rotation',[0,0,0]),t/20);scale=r.sample(track.get('scale',[1,1,1]),t/20)
  world[b['name']]=(world[b['parent']] if b.get('parent') else np.eye(4))@r.transform(position,rotation,scale)
 return world
report={'source':'actual exported geometry/software sampling; not native Minecraft','samplesPerClip':81,'forms':{}}
for ident in forms+('wood_kite_thunder_bomb',):
 g=read(A/f'geo/blueprint/boss/{ident}.geo.json')['minecraft:geometry'][0];anim=read(A/f'animations/blueprint/boss/{ident}.animation.json')['animations'];bones={b['name']:b for b in g['bones']};assert len(bones)==len(g['bones']);assert g['description']['texture_width']==g['description']['texture_height']==16
 tex=Image.open(A/f'textures/entity/blueprint/boss/{ident}.png').convert('RGB');paths.add(A/f'textures/entity/blueprint/boss/{ident}.png')
 for b in bones.values():
  chain=set();node=b
  while node.get('parent'):assert node['name'] not in chain;chain.add(node['name']);node=bones[node['parent']]
  assert all(math.isfinite(x) for x in b['pivot'])
  for c in b.get('cubes',[]):
   assert all(math.isfinite(x) and x>0 for x in c['size'])
   for uv in c['uv'].values():
    u,v=uv['uv'];w,h=uv['uv_size'];assert all(type(x)==int for x in (u,v,w,h));assert 2<=u<=14-w and 2<=v<=14-h and min(w,h)>=2
    assert len({tex.getpixel((x,y)) for x in range(u,u+w) for y in range(v,v+h)})==1
 clips={};jointErrors=[]
 for name,clip in anim.items():
  assert set(clip['bones'])<=set(bones);assert 0<clip['animation_length']<=11
  for channels in clip['bones'].values():
   for channel,track in channels.items():
    if isinstance(track,dict):
     assert all(0<=float(t)<=clip['animation_length'] for t in track)
     assert all(math.isfinite(x) for value in track.values() for x in value)
    else:assert all(math.isfinite(x) for x in track)
  samples=[];short=name.rsplit('.',1)[1];q0=r.geometry(ident,clip=name,tick=0);q1=r.geometry(ident,clip=name,tick=clip['animation_length']*20)
  if clip.get('loop'):assert np.max(np.abs(np.concatenate([p for p,u,b in q0])-np.concatenate([p for p,u,b in q1])))<1e-6,('loop seam',ident,name)
  for tick in np.linspace(0,clip['animation_length']*20,81):
   quads=r.geometry(ident,clip=name,tick=float(tick));points=np.concatenate([p for p,u,b in quads]);assert np.isfinite(points).all()
   live=[(p,u,b) for p,u,b in quads if np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))>1e-8]
   if short!='death':assert points[:,1].min()>=-1e-5,('below aircraft foot plane',ident,short,tick,points[:,1].min())
   desc=g['description'];low=(desc['visible_bounds_offset'][1]-desc['visible_bounds_height']/2)*16;high=(desc['visible_bounds_offset'][1]+desc['visible_bounds_height']/2)*16
   assert points[:,1].min()>=low-1e-6 and points[:,1].max()<=high+1e-6 and np.abs(points[:,[0,2]]).max()<=desc['visible_bounds_width']*8+1e-6,('culling',ident,short,tick)
   if ident in forms:
    world=matrices(g,clip['bones'],float(tick))
    for side,sign in [('left',1),('right',-1)]:
     for i,length in enumerate((14,13,12,11)):
      parent=f'{side}_folding_rail_{i}';child=f'{side}_folding_rail_{i+1}'
      assert bones[child]['parent']==parent;assert abs(bones[child]['pivot'][0]-bones[parent]['pivot'][0])==length
      a=world[parent]@np.array([-sign*length,0,0,1]);b=world[child]@np.array([0,0,0,1]);jointErrors.append(float(np.linalg.norm(a-b)))
     for parent,child,length in [(side+'_landing_upper',side+'_landing_lower',12),(side+'_landing_lower',side+'_four_claw_ankle',10)]:
      assert bones[child]['parent']==parent;assert bones[parent]['cubes'][0]['size'][1]==length
      a=world[parent]@np.array([0,-length,0,1]);b=world[child]@np.array([0,0,0,1]);jointErrors.append(float(np.linalg.norm(a-b)))
     foot=[p for p,u,b in live if b.startswith(side+'_claw') or b==side+'_four_claw_ankle']
     if short in ('idle','wind'):assert abs(np.concatenate(foot)[:,1].min())<.001,('lost planted claw',ident,short,tick)
     if short in ('fly','bombs','wing_cut','lightning'):
      # Folded claws stay outside the open cassette's actual side walls rather than clipping through them.
      assert np.abs(np.concatenate(foot)[:,0]).min()>10+.1
   samples.append({'minimumYMetres':float(points[:,1].min()/16),'maximumYMetres':float(points[:,1].max()/16),'radiusMetres':float(np.linalg.norm(points[:,[0,2]],axis=1).max()/16)})
  clips[short]={'sampleCount':81,'minimumYMetres':min(s['minimumYMetres'] for s in samples),'maximumYMetres':max(s['maximumYMetres'] for s in samples),'maximumRadiusMetres':max(s['radiusMetres'] for s in samples)}
 rest=np.concatenate([p for p,u,b in r.geometry(ident)]);dims=(rest.max(0)-rest.min(0))/16
 if ident in forms:
  assert np.allclose(dims,[9,3,5.5]);assert max(jointErrors)<1e-6
  death=r.geometry(ident,clip='animation.'+ID+'.death',tick=220);assert all(np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))<1e-8 for p,u,b in death)
  for tick in (24,40,55):
   world=matrices(g,anim['animation.'+ID+'.wing_cut']['bones'],tick);pivot=np.array(bones['right_folding_rail_2']['pivot']);local=(np.array([-44.8,28,13])-pivot)*[-1,1,1];port=(world['right_folding_rail_2']@np.append(local,1))[:3]*[-1,1,-1]/16;assert np.allclose(port,[-2.8,1.75,-.8125]),('native wing blade port',ident,tick,port)
  frame=bones['eagle_tool_head']['cubes'];struts=[c for c in frame if c['size']==[2,14,8]];assert len(struts)==2 and all(c['origin'][1]+c['size'][1]>=44 for c in struts)
 report['forms'][ident]={'bones':len(bones),'cuboids':sum(len(b.get('cubes',[])) for b in bones.values()),'clips':clips,'restDimensionsMetres':dims.tolist(),'serialWingAndLandingJointMaximumErrorMetres':max(jointErrors,default=0)/16}
# All actual delivered16px assets, icons, material islands and block textures.
textures=list(A.glob('textures/entity/blueprint/boss/luban_yisha*.png'))+[A/'textures/entity/blueprint/boss/wood_kite_thunder_bomb.png']+list(A.glob('textures/item/stargazer_*.png'))+[A/'textures/item/luban_clockwork_diagram_page.png']+list(A.glob('textures/block/stargazer_*.png'))
for p in textures:
 paths.add(p);im=Image.open(p).convert('RGB');assert im.size==(16,16) and len(set(im.get_flattened_data()))<=4
 for y in range(16):
  for x in range(16):
   color=im.getpixel((x,y));assert 2<=x<=13 and 2<=y<=13 or color==(255,255,255)
   assert any(all(im.getpixel((xx,yy))==color for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15)
for p in list(A.glob('models/block/stargazer_*.json'))+list(A.glob('models/item/stargazer_*.json'))+list(A.glob('blockstates/stargazer_*.json'))+[A/'models/item/luban_yisha_spawn_egg.json',A/'models/item/luban_clockwork_diagram_page.json']+list((R/'src/main/resources/data').rglob('*stargazer*.json'))+[R/'src/main/resources/data/dynasty/loot_tables/entities/luban_yisha.json',R/'src/main/resources/data/dynasty/advancements/blueprint/defeat_luban_yisha.json']:
 read(p)
for loc in ('zh_cn','en_us'):read(A/f'lang/{loc}.json')
assert 'dynasty:stargazer_gear_rope' in read(R/'src/main/resources/data/minecraft/tags/blocks/climbable.json')['values']
paths.update(R.glob('src/main/java/com/dynasty/blueprint/boss/**/*.java'));paths.update(R.glob('src/main/java/com/dynasty/blueprint/artifact/**/*.java'))
paths.update(R/p for p in ('src/main/java/com/dynasty/DynastyContent.java','src/main/java/com/dynasty/blueprint/BlueprintVisualEvent.java','src/main/java/com/dynasty/blueprint/client/BlueprintVisuals.java','tools/blueprint/generate_wood_kite.py','tools/blueprint/generate_stargazer_resources.py','tools/blueprint/validate_wood_kite.py','tools/blueprint/review_wood_kite.py','src/main/resources/data/dynasty_army/structures/cauldron_pit_test.nbt'))
report.update(staticChecks='PASS_SOURCE_SOFTWARE_ONLY',nativeChecks='NOT_RUN_USER_EXAM_JAVA_PAUSE',nativeAcceptance='EIGHT_SOURCE_TESTS_WRITTEN_NOT_RUN',nativeDimensions={'bodyColliderMetres':[3.75,3],'visualRestMetres':[9,3,5.5],'bombColliderMetres':[.65,.7],'visualBombMetres':[.625,.6875,.625],'floorY':200,'octagonVoxelWidth':35,'floorCells':1005,'floorLossCapCells':150,'summonUUIDCap':1,'bombCap':8,'targetCap':16,'introTicks':200,'metalThreshold':.6,'morphTicks':48,'deathTicks':220,'meteorAscentTicks':60,'groundWaveJumpHeightMetres':.5},references=[{'url':'https://raw.githubusercontent.com/TeamTwilight/twilightforest/1.20.x/src/main/java/twilightforest/client/model/entity/RavenModel.java','actuallyRead':'Bird head/beak, body-wing-leg parent layout; no geometry copied.'},{'url':'https://raw.githubusercontent.com/lender544/new1.20.1/master/src/main/java/com/github/L_Ender/cataclysm/client/model/entity/The_Harbinger_Model.java','actuallyRead':'Attached jetpack and hinged machine frames; no assets copied.'}],pending=['NATIVE_BUILD_API_VALIDATION','SINGLE_AND_TWO_PLAYER_ACTUAL_FLIGHT_ATTACKS_COLLISION_AND_CULLING','ALL_SKILL_BALANCE_AND_DENSE_TARGETS_ABOVE16','FULL_AIR_CLAW_GRAPPLE_WEIGHT_AND_EDGE_THROW_PLAYTEST','ORDINARY_WORLD_PLATFORM_AND_FIRST_ASCENT_GENERATION','LIVE_DEATH_LOOT_ROPE_CLOUD_HALO_RELOAD_AND_PERFORMANCE'])
report['resourceSha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
D.mkdir(parents=True,exist_ok=True);(D/'validated-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS_SOURCE_SOFTWARE_ONLY',len(paths),'source fingerprints;26clips x81actual geometry samples; native not run')
