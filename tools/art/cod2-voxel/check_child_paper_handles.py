"""Independently sample actual exported grip transforms and dirty-file preservation."""
import json,numpy as np
from build_models import OUT
from armies_tree import matrices
from resource_paths import resource_paths
from child_paper import preserve_legacy
results=[]
for name in ['fuhun_baibu_tongzi','zhiren_jianke']:
 g,a,_=resource_paths(name)
 class Exported:pass
 r=Exported();r.bones=json.loads(g.read_text())['minecraft:geometry'][0]['bones']
 rest=matrices(r,{},0);pairs=[('right_grip','paper_sword')] if name=='zhiren_jianke' else [('right_grip','lamp_handle'),('left_grip','lamp_handle')]
 expected={hand:np.linalg.inv(rest[obj])@rest[hand] for hand,obj in pairs};error=0
 for animation in json.loads(a.read_text())['animations'].values():
  if name=='fuhun_baibu_tongzi':assert not {'lamp_inertia','ribbon_spring_0','ribbon_spring_1','ribbon_spring_2'}&set(animation['bones'])
  for tick in np.arange(0,animation['animation_length']*20+.01,.25):
   w=matrices(r,animation['bones'],tick)
   for hand,obj in pairs:error=max(error,float(np.max(np.abs(np.linalg.inv(w[obj])@w[hand]-expected[hand]))))
 assert error<.001,(name,error)
 results.append(dict(id=name,grip_to_handle_matrix_error=error,quarter_tick_sampling=True,grips=[h for h,_ in pairs]))
(OUT/'grip-validation-child-paper.json').write_text(json.dumps(dict(passed=True,models=results,unchanged_legacy=preserve_legacy()),indent=2)+'\n')
print('PASS: two child grips / paper sword grip / four unkeyed secondary wrappers / dirty legacy preserved')
