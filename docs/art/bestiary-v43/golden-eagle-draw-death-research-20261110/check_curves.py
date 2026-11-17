"""Read-only selected curve study; writes only this evidence directory."""
from pathlib import Path
import ast, json, math, hashlib, importlib.util
import numpy as np
R=Path(__file__).resolve().parents[4]; O=Path(__file__).resolve().parent
ID='liefeng_jindiao_yushi'; A=R/'src/main/resources/assets/dynasty'
gp=A/f'geo/blueprint/elite/{ID}.geo.json'; ap=A/f'animations/blueprint/elite/{ID}.animation.json'
source=R/'tools/blueprint/generate_golden_eagle.py'; txt=source.read_text(); tree=ast.parse(txt)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
before={str(p):sha(p) for p in [source,gp,ap]}
# Extract only pure keys/legs functions and their literal constants. Never run exporter.
ns={'math':math}
for n in tree.body:
 if isinstance(n,ast.Assign):
  for target in n.targets:
   if isinstance(target,ast.Name) and target.id in ['HIP','REST','L']:ns[target.id]=ast.literal_eval(n.value)
 if isinstance(n,ast.FunctionDef) and n.name in ['keys','legs']:
  exec(compile(ast.Module(body=[n],type_ignores=[]),str(source),'exec'),ns)
rain=False; controls=None
for n in tree.body:
 if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='anim':
  rain=isinstance(n.value.args[0],ast.Constant) and n.value.args[0].value=='rain'
 if rain and isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='legs':
  controls=ast.literal_eval(n.value.args[1]);break
assert controls is not None
expected={}; ns['legs'](expected,controls)
anims=json.loads(ap.read_text())['animations']; rain_channels=anims['animation.'+ID+'.rain']['bones']
comparison={b:{c:rain_channels.get(b,{}).get(c)==v for c,v in ch.items()} for b,ch in expected.items()}
spec=importlib.util.spec_from_file_location('eagle_readonly_transforms',R/'tools/art/secondary-cuboid/review_models.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review);review.CATEGORY='blueprint/elite'
g=json.loads(gp.read_text())['minecraft:geometry'][0]; bones=g['bones']; piv={b['name']:np.array(b['pivot']) for b in bones}
def matrices(clip,t):
 world={}; channels=anims['animation.'+ID+'.'+clip]['bones']
 for b in bones:
  ch=channels.get(b['name'],{});pos=piv[b['name']]-(piv[b['parent']] if b.get('parent') else np.zeros(3))
  rot=np.array(b.get('rotation',[0,0,0]),dtype=float)
  if 'position' in ch:pos=pos+review.sample(ch['position'],t)
  if 'rotation' in ch:rot=rot+review.sample(ch['rotation'],t)
  scale=review.sample(ch['scale'],t) if 'scale' in ch else [1,1,1]
  world[b['name']]=(world[b['parent']] if b.get('parent') else np.eye(4))@review.transform(pos,rot,scale)
 return world
# Check every exported rain key and every interval midpoint: complements old 81 poses.
times=sorted({float(t) for ch in expected.values() for track in ch.values() for t in track})
times=sorted(set(times+[(a+b)/2 for a,b in zip(times,times[1:])]))
joint=[]
for t in times:
 w=matrices('rain',t); row={'tick':t*20}
 for name in ['grip','draw']:
  row[name+'_hock_talon_error_units']=float(np.linalg.norm((w[name+'_hock']@np.array([0,-12,0,1])-w[name+'_talon']@np.array([0,0,0,1]))[:3]))
 nock=w['drawn_arrow']@np.array([0,0,0,1]);draw=w['draw_talon']@np.array([0,0,0,1])
 row['nock_draw_error_units']=float(np.linalg.norm((nock-draw)[:3]))
 for side,sign in [('upper',1),('lower',-1)]:
  row[side+'_string_nock_error_units']=float(np.linalg.norm((w[side+'_string']@np.array([0,-sign*20,0,1])-nock)[:3]))
 joint.append(row)
errors={k:max(r[k] for r in joint) for k in joint[0] if k!='tick'}
worst={k:max(joint,key=lambda r:r[k]) for k in errors}
death=anims['animation.'+ID+'.death']['bones']['raptor_body']
dt=sorted({float(t) for ch in death.values() for t in ch})
dt=sorted(set(dt+[(a+b)/2 for a,b in zip(dt,dt[1:])]))
object_bones={'rib_bow','upper_bow_limb','lower_bow_limb','upper_string','lower_string','drawn_arrow'}
floor=[]
for t in dt:
 q=review.geometry(ID,clip='animation.'+ID+'.death',tick=t*20)
 body=[(p,b) for p,uv,b in q if b not in object_bones]
 minimum=min((float(p[:,1].min()),b) for p,b in body)
 all_min=min((float(p[:,1].min()),b) for p,uv,b in q)
 visible_min=min((float(p[:,1].min()),b) for p,uv,b in q if b!='drawn_arrow')
 floor.append(dict(tick=t*20,body_min_y_units=minimum[0],lowest_body_bone=minimum[1],whole_min_y_units=all_min[0],
  lowest_including_attachment=all_min[1],visible_min_y_units=visible_min[0],lowest_visible_bone=visible_min[1],
  compensation_units=review.sample(death['position'],t).tolist(),scale=review.sample(death['scale'],t).tolist()))
write('rain-key-and-midpoint-contacts.json',joint)
write('death-key-and-midpoint-clearance.json',floor)
write('curve-source-comparison.json',dict(pure_function_names=['keys','legs'],exporter_executed=False,controls_seconds_pull_units_tilt_degrees=controls,
 exported_tracks_equal_pure_solver=comparison,all_tracks_equal=all(v for ch in comparison.values() for v in ch.values()),
 sample_count=len(times),max_errors_units=errors,max_errors_metres={k:v/16 for k,v in errors.items()},worst_samples=worst,
 units_per_metre=16,interpolation='existing software helper linear interpolation, not Gecko native acceptance'))
write('death-compensation-summary.json',dict(sample_count=len(floor),position_key_count=len(death['position']),
 position_range_units={axis:[min(v[i] for v in death['position'].values()),max(v[i] for v in death['position'].values())] for i,axis in enumerate('xyz')},
 body_lowest=min(floor,key=lambda r:r['body_min_y_units']),
 visible_lowest=min(floor,key=lambda r:r['visible_min_y_units']),
 body_highest_floor_before_shrink=max([r for r in floor if r['tick']<=56],key=lambda r:r['body_min_y_units']),
 source_sequence='generator computes compensation before v33/v34/v35 geometry refiners; no full exporter rerun',
 native_gravity_not_modelled=True,attachment_geometry_read_only=True))
assert before=={str(p):sha(p) for p in [source,gp,ap]},'production changed during read'
print(json.dumps(dict(rain_samples=len(times),max_errors_units=errors,all_solver_tracks_equal=all(v for ch in comparison.values() for v in ch.values()),
 death_samples=len(floor),body_lowest=min(floor,key=lambda r:r['body_min_y_units']),
 body_highest_floor_before_shrink=max([r for r in floor if r['tick']<=56],key=lambda r:r['body_min_y_units']),production_unchanged=True),ensure_ascii=False,indent=2))
