"""Independent exported-matrix audit for the ghost ge and two-hand standard."""
import json,numpy as np
import review
from armies_tree import matrices
from build_models import OUT
results=[]
for name,weapon in [('yinbing_guizu','ghost_ge'),('zhenwang_zhangqiguan','flagstaff')]:
 review.select(name);g=json.loads(review.GEO.read_text())['minecraft:geometry'][0];a=json.loads(review.ANIM.read_text())['animations']
 class Exported:pass
 rig=Exported();rig.bones=g['bones'];rest=matrices(rig,{},0)
 offset=rest[weapon][:3,:3].T@(rest['left_grip'][:3,3]-rest[weapon][:3,3]) if name=='zhenwang_zhangqiguan' else None
 orientation=rest[weapon][:3,:3].T@rest['left_grip'][:3,:3] if offset is not None else None
 maximum=angular=right=0
 for clip in a.values():
  for tick in np.arange(0,clip['animation_length']*20+.01,.25):
   w=matrices(rig,clip['bones'],tick)
   right=max(right,float(np.linalg.norm(w['right_grip'][:3,3]-w[weapon][:3,3])),float(np.max(np.abs(w['right_grip'][:3,:3]-w[weapon][:3,:3]))))
   if offset is not None:
    maximum=max(maximum,float(np.linalg.norm(w['left_grip'][:3,3]-(w[weapon][:3,3]+w[weapon][:3,:3]@offset))))
    angular=max(angular,float(np.max(np.abs(w['left_grip'][:3,:3]-w[weapon][:3,:3]@orientation))))
 assert right<.001 and maximum<.12 and angular<.01,(name,right,maximum,angular)
 results.append(dict(id=name,weapon=weapon,right_pivot_and_matrix_error=right,left_support_error_pixels=maximum,left_matrix_error=angular,quarter_tick_sampled=True))
(OUT/'grip-validation-corpse-ghost-palanquin-flag.json').write_text(json.dumps(dict(passed=True,models=results),indent=2)+'\n');print('PASS actual exported ge and two-hand flag matrices',results)
