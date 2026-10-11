"""Check exported elite grip matrices and protect concurrent legacy resources/code."""
import json
import numpy as np
from armies_tree import matrices
from build_models import OUT
from elites import preserve
from resource_paths import resource_paths

name='xianzhen_duantoujiang'
geo,anim,_=resource_paths(name)
class Exported:pass
rig=Exported();rig.bones=json.loads(geo.read_text())['minecraft:geometry'][0]['bones']
rest=matrices(rig,{},0)
pairs=[('right_grip','greatblade'),('left_grip','held_head')]
expected={hand:np.linalg.inv(rest[obj])@rest[hand] for hand,obj in pairs}
errors={hand:0.0 for hand,_ in pairs};samples={hand:0 for hand,_ in pairs}
for clip in json.loads(anim.read_text())['animations'].values():
    for tick in np.arange(0,clip['animation_length']*20+.01,.25):
        world=matrices(rig,clip['bones'],tick)
        for hand,obj in pairs:
            # The thrown head deliberately scales out; its shrinking release is not a grip.
            if obj=='held_head' and abs(np.linalg.det(world[obj][:3,:3]))<.999:continue
            error=float(np.max(np.abs(np.linalg.inv(world[obj])@world[hand]-expected[hand])))
            errors[hand]=max(errors[hand],error);samples[hand]+=1
assert max(errors.values())<.001,errors
data=dict(passed=True,quarter_tick_sampling=True,grip_to_object_matrix_errors=errors,
          samples=samples,held_head_release_excluded=True,unchanged_original_resources_and_java=preserve())
(OUT/'grip-validation-elites.json').write_text(json.dumps(data,indent=2)+'\n')
print('PASS: greatblade / held-head grips / all original elite resources and Java unchanged')
