"""Bounded rigid-source observation; model-space plane, not world collision or runtime."""
from pathlib import Path
import copy
import itertools
import json
import math
import re
import runpy

B = Path(__file__).resolve().parent
R = runpy.run_path(str(B.parent/'suanni-frostmaw-wake-research-20261110/read_wake_phases.py'))
text = R['SOURCE'].read_text()
c = text.split('public ModelFrostmaw() {',1)[1].split('updateDefaultPose();',1)[0]
c = re.sub(r'//[^\n]*', '', c)
def nums(s): return [float(v.strip().rstrip('fF')) for v in s.split(',')]
names = re.findall(r'(?:this\.)?(\w+)\s*= new AdvancedModelRenderer\(this(?:,|\))', c)
assert len(names) == len(set(names))
bones = {n:dict(pos=[0.,0.,0.],rot=[0.,0.,0.],scale=[1.,1.,1.],parent=None,boxes=[]) for n in names}
for name,b in bones.items():
    for raw in re.findall(rf'(?:this\.)?\b{name}\.setRotationPoint\(([^)]+)\)',c): b['pos']=nums(raw)
    for raw in re.findall(rf'setRotateAngle\({name}, ([^)]+)\)',c): b['rot']=nums(raw)
    for raw in re.findall(rf'(?:this\.)?\b{name}\.setScale\(([^)]+)\)',c): b['scale']=nums(raw)
    for raw in re.findall(rf'(?:this\.)?\b{name}(?:\.setTextureOffset\([^)]*\))?\.addBox\(([^)]+)\)',c):
        args=raw.split(',');v=nums(','.join(args[:6]));delta=0. if len(args)==6 or args[6].strip() in ('true','false') else float(args[6].strip().rstrip('Ff'))
        b['boxes'].append(dict(origin=[v[i]-delta for i in range(3)],size=[v[i+3]+2*delta for i in range(3)]))
for parent,child in re.findall(r'(?:this\.)?(\w+)\.addChild\((?:this\.)?(\w+)\)',c):
    assert bones[child]['parent'] is None
    bones[child]['parent']=parent
for name in ('leftThumb','rightThumb'):
    assert f'{name}.rotateAngleY = (float) (Math.PI);' in c
    assert f'{name}.rotationPointZ = 4;' in c
    bones[name]['rot'][1]=math.pi; bones[name]['pos'][2]=4.
assert sum(len(b['boxes']) for b in bones.values())==len(re.findall(r'\.addBox\(',c))
assert all(len(b['scale'])==3 for b in bones.values())
(B/'parsed-constructor.json').write_text(json.dumps(bones,indent=2)+'\n')

def rotate(v,rot):
    x,y,z=v;a,b,c=rot
    y,z=y*math.cos(a)-z*math.sin(a),y*math.sin(a)+z*math.cos(a)
    x,z=x*math.cos(b)+z*math.sin(b),-x*math.sin(b)+z*math.cos(b)
    x,y=x*math.cos(c)-y*math.sin(c),x*math.sin(c)+y*math.cos(c)
    return [x,y,z]

def world(v,name,pose,scale=True):
    b=pose[name]
    if scale:v=[a*s for a,s in zip(v,b['scale'])]
    v=[a+p for a,p in zip(rotate(v,b['rot']),b['pos'])]
    # AdvancedModelRenderer cancels parent's scale before child's local transform.
    return world(v,b['parent'],pose,False) if b['parent'] else v

old=json.loads((B.parent/'suanni-frostmaw-wake-research-20261110/phase-observation.json').read_text())
clips={p['name']:p for p in old['clips']}
sleep=old['inactive_direct_base']
def pose_at(name,t,age,carry):
    p=copy.deepcopy(bones)
    # resetToDefaultPose restores only rotation/position; scales carry from earlier renders.
    p['chest']['scale']=[carry]*3;p['backHair']['scale']=[carry]*3
    targets={}
    if name in clips:
        keys={key for phase in clips[name]['phases'] for key in phase['target']}
        targets={key:R['channel_at'](clips[name],t,key) for key in keys}
    # Death0 is a fresh 4tick transition from default, not an activation pose snapshot.
    if name=='DEATH_AT_0':assert t==0
    if name in ('SLEEP','DEACTIVATE_ANIMATION'):
        for key,vector in sleep.items():targets[key]=[a+b for a,b in zip(targets.get(key,[0.,0.,0.]),vector)]
    for key,v in targets.items():
        n,channel=key.split(':');field='rot' if channel=='rotate' else 'pos'
        p[n][field]=[a+b for a,b in zip(p[n][field],v)]
    p['waist']['pos'][2]+=10
    if name in ('SLEEP','DEACTIVATE_ANIMATION'):
        sc=1.05+.05*math.cos(age*.05)
        p['chest']['scale']=[sc]*3;p['backHair']['scale']=[sc]*3
        p['backHair']['pos'][2]-=(sc-1.05)*20
        p['headJoint']['rot'][0]+=.04*math.cos(age*.05-1)
    p['jawJoint']['rot'][0]+=.08*p['roarController']['pos'][0]*math.cos(2*age)
    p['headBack']['scale']=[1,max(.000001,1-p['roarController']['pos'][1]),1]
    for side,axis in [('right',1),('left',0)]:
        control=p['handController']['pos'][axis]
        p[side+'FingersJoint']['rot'][0]-=control*math.pi/2
        p[side+'Fingers']['rot'][0]-=control*math.pi/2
        p[side+'Thumb']['rot'][1]+=control*math.pi*(1 if side=='right' else -1)
        p[side+'Thumb']['rot'][2]+=control*.7*(1 if side=='right' else -1)
        p[side+'Thumb']['pos'][2]-=control*6
    return p

landmarks=['head','jaw','leftFoot','rightFoot','leftHand','rightHand','leftFingers','rightFingers','waist','chest']
results=[]; scenes={}
cases=[('SLEEP',0,0,1.),('ACTIVATE_ANIMATION',0,0,1.1),('ACTIVATE_ANIMATION',36,36,1.1),('ACTIVATE_ANIMATION',51,51,1.1),('ACTIVATE_ANIMATION',117.999,117.999,1.1),('DEACTIVATE_ANIMATION',0,0,1.1),('DEACTIVATE_ANIMATION',10,10,1.1),('DEACTIVATE_ANIMATION',24.999,24.999,1.1),('DEATH_AT_0',0,36,1.1)]
for name,t,age,carry in cases:
    p=pose_at(name,t,age,carry);geometry={}
    for n,b in p.items():
        if n.startswith('iceCrystal'):continue
        geometry[n]=[[world([box['origin'][i]+s[i]*box['size'][i] for i in range(3)],n,p) for s in itertools.product((0,1),repeat=3)] for box in b['boxes'] if any(box['size'])]
    key=f'{name}@{t}'
    results.append(dict(case=key,age=age,carried_chest_scale=carry,nominal_gaps_model_units={n:24-max(v[1] for box in geometry[n] for v in box) for n in landmarks},root_pose=p['root'],head_joint=p['headJoint']))
    scenes[key]=geometry
out=dict(kind='New bounded Frostmaw rigid-constructor observation, NOT native/world contact certification',
         parts=len(bones),declared_boxes=sum(len(b['boxes']) for b in bones.values()),nominal_plane_model_y=24,
         coordinate_convention='Y down; gap=24-max(transformed model Y). No parent MobRenderer/world transform assumed.',
         inputs='zero cached leg heights; active clip uses zero look/gait; inactive breathing and unconditional hand/jaw consumers included; selected scale history1.1',
         exclusions=['no server/world terrain or collision','no textures/alpha, planes rendered opaque in source diagram','no other active attack clips','no guarantee of paused renderer scale history','no native Forge1.20.1 compatibility','no frame-continuity promise across network packets'],results=results)
(B/'geometry-observation.json').write_text(json.dumps(out,indent=2)+'\n')
(B/'diagram-geometry.json').write_text(json.dumps(scenes)+'\n')
print(json.dumps({k:out[k] for k in ('parts','declared_boxes','kind')}))
print(json.dumps([{k:r[k] for k in ('case','nominal_gaps_model_units')} for r in results],indent=2))
