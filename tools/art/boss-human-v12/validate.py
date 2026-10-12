"""Focused human-rig/UV/animation/ownership invariants, not a gameplay test suite."""
from create import *
import subprocess
report={}
for id in IDS:
 g=json.loads((A/f'geo/boss_cuboid/{id}.geo.json').read_text())['minecraft:geometry'][0];bones=g['bones'];names=[b['name'] for b in bones];by={b['name']:b for b in bones};tex=Image.open(A/f'textures/entity/boss_cuboid/{id}.png')
 assert len(names)==len(set(names));assert tex.size==(g['description']['texture_width'],g['description']['texture_height'])
 for side in ['left','right']:
  for bn,parent in [(side+'_leg','pelvis'),(side+'_knee',side+'_leg'),(side+'_shin',side+'_knee'),(side+'_foot',side+'_shin'),(side+'_arm','chest'),(side+'_elbow',side+'_arm'),(side+'_forearm',side+'_elbow'),(side+'_hand',side+'_forearm'),(side+'_grip',side+'_hand')]:assert by[bn]['parent']==parent
  foot=by[side+'_foot']['cubes'][0]['size'];assert foot[0]<=8 and foot[1]<=4 and foot[2]<=11
 old_bones=json.loads((D/'before'/f'{id}.geo.json').read_text())['minecraft:geometry'][0]['bones']
 old_parent={b['name']:b.get('parent') for b in old_bones};assert all(n in by and by[n].get('parent')==parent for n,parent in old_parent.items()),'Accepted articulation changed'
 assert all(len(by[b['name']].get('cubes',[]))>=len(b.get('cubes',[])) for b in old_bones),'Accepted Cuboids deleted'
 used=np.zeros(tex.size[::-1],dtype=np.uint8)
 for b in bones:
  if b.get('parent'):assert names.index(b['parent'])<names.index(b['name'])
  for c in b.get('cubes',[]):
   assert min(c['size'])>0 and set(c['uv'])=={'north','south','east','west','up','down'}
   for uv in c['uv'].values():
    x,y=uv['uv'];w,h=uv['uv_size'];assert 0<x and 0<y and x+w<tex.width and y+h<tex.height;assert not used[y:y+h,x:x+w].any();used[y:y+h,x:x+w]=1
 an=json.loads((A/f'animations/boss_cuboid/{id}.animation.json').read_text())['animations'];old=json.loads((D/'before'/f'{id}.animation.json').read_text())['animations'];clips={}
 assert list(an)==list(old)
 for clip,a in an.items():
  assert a['animation_length']==old[clip]['animation_length'] and a.get('loop')==old[clip].get('loop');assert set(a['bones']).issubset(names)
  for ch in a['bones'].values():
   for track in ch.values():
    for v in (track.values() if isinstance(track,dict) else [track]):assert len(v)==3 and np.isfinite(v).all()
  vs=[np.array(vertices(bones,a['bones'],float(t))) for t in np.linspace(0,a['animation_length'],321)]
  min_y=min(p[:,1].min() for p in vs);assert min_y>-.04,(id,clip,min_y)
  if a.get('loop') is True:assert np.allclose(vs[0],vs[-1],atol=.0001),(id,clip,'loop discontinuity')
  clips[clip]={'duration':a['animation_length'],'minY_units':round(float(min_y),5),'maxY_blocks':round(max(p[:,1].max() for p in vs)/16,3)}
 import texture_review as contact_review
 contact_review.r.CATEGORY='boss_cuboid'
 death_quads=contact_review.r.geometry(id,'death',an['death']['animation_length']*20)
 support_names={'left_arm','right_arm','left_pauldron','right_pauldron','left_mantle','right_mantle','left_shoulder','right_shoulder'}
 support_y=min(float(p[:,1].min()) for p,_,n in death_quads if n in support_names)
 assert -.04<support_y<.10,(id,'corpse rests on decoration instead of tangible shoulder/arm',support_y)
 v=np.array(vertices(bones,an['idle']['bones'],0));assert 2.6<v[:,1].max()/16<3.3,(id,'idle height',v[:,1].max()/16);report[id]={'deathSupportGapBlocks':round(support_y/16,5),'atlas':tex.size,'bones':len(bones),'cubes':sum(len(b['cubes']) for b in bones),'bounds_blocks':((v.max(0)-v.min(0))/16).round(3).tolist(),'clips':clips}
# Approved eight resources and actual combat logic are protected, independently of shared dev edits.
protected=[]
for folder in ['geo/boss_forms','animations/boss_forms','textures/entity/boss_forms']:
 for p in (A/folder).glob('*'):
  if p.is_file():assert p.read_bytes()==subprocess.check_output(['git','show','f0f15504:'+str(p.relative_to(R))],cwd=R);protected.append(str(p.relative_to(R)))
combat=R/'src/main/java/com/dynasty/entity/DynastyBosses.java';assert combat.read_bytes()==subprocess.check_output(['git','show','f0f15504:'+str(combat.relative_to(R))],cwd=R)
report['protectedApprovedAssets']=len(protected);report['runtimeHashes']=hashes();(D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
