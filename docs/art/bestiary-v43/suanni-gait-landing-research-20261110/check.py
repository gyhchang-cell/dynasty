"""Selected unresolved dense gait/death boundaries; no production writes."""
from pathlib import Path
import json, math, hashlib, importlib.util
import numpy as np
R=Path(__file__).resolve().parents[4]; O=Path(__file__).resolve().parent
ID='zhenmu_suanni_tonghou'; A=R/'src/main/resources/assets/dynasty'
gp=A/f'geo/blueprint/elite/{ID}.geo.json';ap=A/f'animations/blueprint/elite/{ID}.animation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
before={str(p):sha(p)for p in [gp,ap]}
g=json.loads(gp.read_text())['minecraft:geometry'][0];anims=json.loads(ap.read_text())['animations']
spec=importlib.util.spec_from_file_location('suanni_selected_linear_geometry',R/'tools/art/secondary-cuboid/review_models.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/elite'
names=['front_left','front_right','rear_left','rear_right'];piv={b['name']:np.array(b['pivot'])for b in g['bones']}
def matrices(clip,t):
 chs=anims['animation.'+ID+'.'+clip]['bones'];world={}
 for b in g['bones']:
  ch=chs.get(b['name'],{});pos=piv[b['name']]-(piv[b['parent']]if b.get('parent')else np.zeros(3));rot=np.array(b.get('rotation',[0,0,0]),float)
  if 'position'in ch:pos=pos+r.sample(ch['position'],t)
  if 'rotation'in ch:rot=rot+r.sample(ch['rotation'],t)
  sc=r.sample(ch['scale'],t)if 'scale'in ch else [1,1,1]
  world[b['name']]=(world[b['parent']]if b.get('parent')else np.eye(4))@r.transform(pos,rot,sc)
 return world
def times(clip):
 c=anims['animation.'+ID+'.'+clip]; ts=sorted({0.,c['animation_length']}|{float(t)for ch in c['bones'].values()for tr in ch.values()if isinstance(tr,dict)for t in tr})
 return sorted(set(ts+[(a+b)/2 for a,b in zip(ts,ts[1:])]))
def live(clip):
 rows=[];chs=anims['animation.'+ID+'.'+clip]['bones']
 for t in times(clip):
  w=matrices(clip,t);q=r.geometry(ID,clip='animation.'+ID+'.'+clip,tick=t*20);row={'tick':t*20,'feet':{}}
  for name in names:
   error=float(np.linalg.norm((w[name+'_shin']@np.array([0,-10.5,0,1])-w[name+'_paw']@np.array([0,0,0,1]))[:3]))
   lift=float(r.sample(chs[name+'_paw']['position'],t)[1]); minimum=float(min(p[:,1].min()for p,uv,b in q if b==name+'_bronze_ball'))
   row['feet'][name]=dict(shin_paw_error_units=error,lift_units=lift,ball_min_y_units=minimum,ball_extent_residual_units=minimum-lift)
  row['near_ground_ball_count']=sum(abs(v['ball_min_y_units'])<=.03 for v in row['feet'].values())
  row['endpoint_planted_count']=sum(abs(v['lift_units'])<=1e-6 for v in row['feet'].values())
  rows.append(row)
 write(clip+'-key-midpoint.json',rows)
 errors=[(v['shin_paw_error_units'],row['tick'],n)for row in rows for n,v in row['feet'].items()]
 floor=[(abs(v['ball_extent_residual_units']),row['tick'],n,v['ball_extent_residual_units'])for row in rows for n,v in row['feet'].items()]
 return dict(samples=len(rows),maximum_shin_paw_error_units=max(errors),maximum_ball_extent_residual_units=max(floor),
  minimum_near_ground_balls=min(x['near_ground_ball_count']for x in rows),minimum_planted_endpoints=min(x['endpoint_planted_count']for x in rows),
  worst_ground_count_sample=min(rows,key=lambda x:x['near_ground_ball_count']))
walk=live('walk');stomp=live('stomp')
deathrows=[]
for t in times('death'):
 w=matrices('death',t);q=r.geometry(ID,clip='animation.'+ID+'.death',tick=t*20)
 per={b:float(min(p[:,1].min()for p,uv,n in q if n==b))for b in {b for p,uv,b in q}}
 gaps={n:float(np.linalg.norm((w[n+'_shin']@np.array([0,-10.5,0,1])-w[n+'_paw']@np.array([0,0,0,1]))[:3]))for n in names}
 deathrows.append(dict(tick=t*20,lowest_y_units=min(per.values()),lowest_bone=min(per,key=per.get),
  head_and_jaw_min_y_units=min(per['lion_head'],per['hinged_lower_jaw']),
  cast_limb_min_y_units=min(v for n,v in per.items()if n.endswith('_upper')or n.endswith('_shin')),
  support_min_y_units=min(v for n,v in per.items()if n.endswith('_paw')or n.endswith('_bronze_ball')),
  broken_shin_to_paw_distances_units=gaps))
write('death-key-midpoint.json',deathrows)
death=dict(samples=len(deathrows),lowest=min(deathrows,key=lambda v:v['lowest_y_units']),
 lowest_head=min(deathrows,key=lambda v:v['head_and_jaw_min_y_units']),lowest_cast_limb=min(deathrows,key=lambda v:v['cast_limb_min_y_units']),
 endpoint_detachment_is_authored_death_not_live_IK_failure=True)
summary=dict(software_only=True,interpolation='repository helper linear sample/transform, not native Gecko or terrain physics',units_per_metre=16,
 walk=walk,stomp=stomp,death=death,production_unchanged=before=={str(p):sha(p)for p in [gp,ap]},
 source_hashes=before,new_accepted_reference_credit=0)
assert summary['production_unchanged']
write('sampling-summary.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
