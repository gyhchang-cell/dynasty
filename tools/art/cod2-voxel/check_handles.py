"""Independent exported pose matrices check rigid square handles inside palm holes."""
import json,numpy as np
import review
from armies_tree import matrices
from build_models import OUT
pairs={'ludun_jiashi':[('right_grip','mace'),('left_grip','shield_grip')], 'pijia_panjiang_huwei':[('right_grip','right_axe'),('left_grip','left_axe')], 'tiesuo_chihou':[('right_grip','right_claw'),('left_grip','left_claw')]}
results=[]
for name,handles in pairs.items():
 review.select(name);g=json.loads(review.GEO.read_text())['minecraft:geometry'][0];a=json.loads(review.ANIM.read_text())['animations']
 class Exported:pass
 rig=Exported();rig.bones=g['bones'];maxpos=maxrot=0
 for clip in a.values():
  for tick in np.arange(0,clip['animation_length']*20+.01,.25):
   world=matrices(rig,clip['bones'],tick)
   for grip,weapon in handles:
    maxpos=max(maxpos,float(np.linalg.norm(world[grip][:3,3]-world[weapon][:3,3])))
    maxrot=max(maxrot,float(np.max(np.abs(world[grip][:3,:3]-world[weapon][:3,:3]))))
 assert maxpos<.001 and maxrot<.001,(name,maxpos,maxrot)
 results.append(dict(id=name,pairs=handles,maximum_pivot_error=maxpos,maximum_rotation_matrix_error=maxrot))
(OUT/'grip-validation-shield-skull-guard-scout.json').write_text(json.dumps(dict(passed=True,scope='Every quarter tick / all exported clips / square-handle pivot and orientation coincide with authored palm holes; physical native review still required',models=results),indent=2)+'\n');print('PASS: six exported square handles stay inside their palms in all clips')
