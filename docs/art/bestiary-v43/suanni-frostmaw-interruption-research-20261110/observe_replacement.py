"""Conditional same-landmark comparisons; not server/network/game replay."""
from pathlib import Path
import contextlib
import io
import json
import math
import re
import runpy
B=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    m=runpy.run_path(str(B/'observe_wake_geometry.py'))
bones=m['bones']; fields=set(re.findall(r'public AdvancedModelRenderer (\w+);',m['text']))
assert set(bones)==fields
paths={}
for name in ('head','jaw','leftFoot','rightFoot','leftHand','rightHand'):
    chain=[];node=name
    while node:
        assert node not in chain
        chain.append(node);node=bones[node]['parent']
    paths[name]=chain
observations=[]
for label,old,new in [
    ('fatal damage replacing wake36',('ACTIVATE_ANIMATION',36,36,1.1),('DEATH_AT_0',0,36,1.1)),
    ('nonfatal damage replacing deactivation10',('DEACTIVATE_ANIMATION',10,10,1.1),('ACTIVATE_ANIMATION',0,10,1.05+.05*math.cos(.5)))]:
    p=m['pose_at'](*old);q=m['pose_at'](*new);changes={}
    for n in ('headJoint','jawJoint','leftFoot','rightFoot','leftHand','rightHand'):
        a=m['world']([0.,0.,0.],n,p);z=m['world']([0.,0.,0.],n,q)
        changes[n]={'before_origin_model':a,'after_origin_model':z,'distance_model_units':math.dist(a,z)}
    observations.append(dict(case=label,before=old,after=new,joint_origin_changes=changes))
(B/'conditional-interruption-observation.json').write_text(json.dumps(dict(
    kind='conditional source pose replacement; no scheduler/network replay',
    assumptions='Selected server replacement reaches model at new tick0; look/gait0, cached leg heights0. Scale history explicitly supplied. Actual packet timing/order not proved.',
    observations=observations,bone_parent_chains=paths,constructor_fields_equal=True,new_accepted_credit=0),indent=2)+'\n')
print(json.dumps([{ 'case':r['case'],'joint_origin_distances':{k:round(v['distance_model_units'],5) for k,v in r['joint_origin_changes'].items()}} for r in observations],indent=2))
