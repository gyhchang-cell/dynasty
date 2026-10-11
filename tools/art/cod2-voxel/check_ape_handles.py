"""Exported dao palm and exact geometric contact offsets used by wall IK."""
import json,numpy as np
from build_models import OUT
from armies_tree import matrices
import review
review.select('zuwu_daoshou');g=json.loads(review.GEO.read_text())['minecraft:geometry'][0]
class Exported:pass
rig=Exported();rig.bones=g['bones'];maximum=0
for clip in json.loads(review.ANIM.read_text())['animations'].values():
 for tick in np.arange(0,clip['animation_length']*20+.01,.25):
  w=matrices(rig,clip['bones'],tick)
  maximum=max(maximum,float(np.max(np.abs(w['right_grip']-w['dao']))))
assert maximum<.001
review.select('shanjing_shanxiao');g=json.loads(review.GEO.read_text())['minecraft:geometry'][0];a=json.loads(review.ANIM.read_text())['animations'];by={b['name']:b for b in g['bones']}
contacts=[]
for side in ['right','left']:
 for point,joint,offset,mesh in [('claw_contact','wrist',1.95,'hand'),('foot_contact','ankle',1.72,'foot')]:
  p=by[side+'_'+point]['pivot'];q=by[side+'_'+joint]['pivot'];assert abs(q[1]-p[1]-offset)<1e-9
  assert any(all(c['origin'][i]-.05<=p[i]<=c['origin'][i]+c['size'][i]+.05 for i in range(3)) for c in by[side+'_'+mesh]['cubes']), 'Contact does not touch actual paw'
  contacts.append(dict(locator=side+'_'+point,pivot=p,production_wrist_vertical_offset=offset,inside_authored_paw=True))
 for part in ['shoulder','elbow','wrist','thigh','knee','ankle']:
  n=side+'_climb_'+part
  assert by[n].get('rotation',[0,0,0])==[0,0,0] and all(n not in clip['bones'] for clip in a.values()),'Climb wrapper keyed'
(OUT/'grip-validation-ape-dao.json').write_text(json.dumps(dict(passed=True,dao_all_quarter_tick_matrix_error=maximum,climb_contacts=contacts,identity_climb_wrappers=12),indent=2)+'\n');print('PASS dao matrix and four real-paw contact offsets / 12 unkeyed climb wrappers')
