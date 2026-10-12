"""Small candidate checks: hierarchy, finite geometry, grey UV, editor parity and grounding."""
from create import *
import sys, numpy as np
sys.path.insert(0,str(R/'tools/art/secondary-cuboid'))
from rig_bounds import vertices,transform
def run():
 results=[]
 for id in IDS:
  p=D/'candidates'/id;g=json.loads((p/(id+'.geo.json')).read_text())['minecraft:geometry'][0]
  an=json.loads((p/(id+'.animation.json')).read_text())['animations'];bb=json.loads((D/'blockbench'/(id+'.bbmodel')).read_text())
  names=set();cubes=[]
  for b in g['bones']:
   assert b['name'] not in names
   assert not b.get('parent') or b['parent'] in names
   names.add(b['name']);assert np.isfinite(b['pivot']).all()
   for c in b['cubes']:
    assert np.isfinite(c['origin']+c['size']+c.get('rotation',[])).all()
    assert min(c['size'])>0;assert not any(k.startswith('_') for k in c)
    for f,uv in c['uv'].items():assert all(0<=uv['uv'][j]<uv['uv'][j]+uv['uv_size'][j]<=16 for j in range(2))
    cubes.append(c)
  assert {'root','chest','head','left_grip','right_grip'}<=names
  assert len(cubes)==len(bb['elements'])
  for c,e in zip(cubes,bb['elements']):
   start=[-c['origin'][0]-c['size'][0],c['origin'][1],c['origin'][2]]
   assert np.allclose(e['from'],start) and np.allclose(np.subtract(e['to'],e['from']),c['size'])
  for clip,a in an.items():
   assert set(a['bones'])<=names
   for t in np.linspace(0,a['animation_length'],31):
    v=np.array(vertices(g['bones'],a['bones'],float(t)));assert np.isfinite(v).all()
    assert abs(float(v[:,1].min()))<1e-6,(id,clip,t,v[:,1].min())
   if a.get('loop'):assert np.allclose(vertices(g['bones'],a['bones'],0),vertices(g['bones'],a['bones'],a['animation_length']))
  distance=None
  if id!=IDS[2]:
   by={b['name']:b for b in g['bones']};c=by['weapon']['cubes'][0]
   center=np.array([c['origin'][i]+c['size'][i]/2 for i in range(3)])*[-1,1,1]
   grip=np.array(by['right_grip']['pivot'])*[-1,1,1]
   direction=np.array(transform(r=c['rotation']))[:3,1]
   along=float((grip-center)@direction);nearest=center+direction*np.clip(along,-c['size'][1]/2,c['size'][1]/2)
   distance=float(np.linalg.norm(nearest-grip));assert distance<3,(id,'shaft misses grip',distance)
  results.append({'id':id,'hierarchy':'PASS','geometry_and_UV':'PASS','bbmodel_geometry_parity':'PASS','idle_loop':'PASS','grounding_62_samples':'PASS','shaft_to_grip_model_units':distance,'production_binding':'not installed; grey approval pending','Java_build':'not run for candidate-only resources','game':'not validated'})
 (D/'validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
