"""One held terminal source pose. Standard library only; no production writes."""
import copy, hashlib, itertools, json, math, re
from pathlib import Path
B=Path(__file__).resolve().parent
ROOT=B.parents[3]
def nums(s): return [float(x.strip().removesuffix('F')) for x in s.split(',')]
source=(B/'sources/BroodMotherModel.java').read_text()
method=source[source.index('public static LayerDefinition createBodyLayer()'):source.index('return LayerDefinition.create')]
parts={'root':dict(pos=[0,0,0],rot=[0,0,0],parent=None,boxes=[])}
alias={'partdefinition':'root'}
for statement in method.split(';'):
    match=re.search(r'PartDefinition (\w+) = (\w+)\.addOrReplaceChild\("([^"]+)"',statement)
    if not match: continue
    variable,parent,name=match.groups(); assert parent in alias
    p=dict(pos=[0,0,0],rot=[0,0,0],parent=alias[parent],boxes=[])
    for box in re.finditer(r'\.addBox\(([-\d.Ff,\s]+), new CubeDeformation\(([-\d.Ff]+)\)\)',statement):
        v=nums(box[1]); inflate=nums(box[2])[0]; assert len(v)==6
        p['boxes'].append(dict(origin=[x-inflate for x in v[:3]],size=[x+2*inflate for x in v[3:]]))
    assert len(p['boxes']) == statement.count('.addBox(')
    pose=re.search(r'PartPose\.(offsetAndRotation|offset)\(([-\d.Ff,\s]+)\)',statement)
    assert pose; v=nums(pose[2]); p['pos']=v[:3]
    if pose[1]=='offsetAndRotation':p['rot']=v[3:]
    parts[name]=p;alias[variable]=name
card=ROOT/'build/creature-reference-1000/cards/Goety-2-BroodMotherModel.json'
assert parts==json.loads(card.read_text()), 'Source/card mismatch'
channels=json.loads((B/'death-channels.json').read_text());assert len(channels)==21
posed=copy.deepcopy(parts)
for c in channels:
    assert c['frames'][-1][0]<=1.35
    v=c['frames'][-1][1:];p=posed[c['bone']]
    if c['kind']=='ROTATION':p['rot']=[x+math.radians(y) for x,y in zip(p['rot'],v)]
    elif c['kind']=='POSITION':p['pos']=[x+y*s for x,y,s in zip(p['pos'],v,[1,-1,1])]
    else:raise ValueError(c['kind'])
posed['head']['rot'][:2]=[0,0]
posed['right_mouth']['rot']=[0,0,math.radians(2.5)]
posed['left_mouth']['rot']=[0,0,-math.radians(2.5)]
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def mv(a,v):return [sum(x*y for x,y in zip(row,v)) for row in a]
def rotation(v):
    x,y,z=v;cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return mm(mm([[cz,-sz,0],[sz,cz,0],[0,0,1]],[[cy,0,sy],[0,1,0],[-sy,0,cy]]),[[1,0,0],[0,cx,-sx],[0,sx,cx]])
cache={}
def transform(name):
    if name in cache:return cache[name]
    p=posed[name];r=rotation(p['rot']);t=p['pos']
    if p['parent'] is not None:
        pr,pt=transform(p['parent']);r=mm(pr,r);t=[x+y for x,y in zip(mv(pr,t),pt)]
    cache[name]=(r,t);return r,t
points={}
for name,p in posed.items():
    r,t=transform(name);vs=[]
    for box in p['boxes']:
        for corner in itertools.product([0,1],repeat=3):
            v=[a*b+c for a,b,c in zip(corner,box['size'],box['origin'])]
            vs.append([a+b for a,b in zip(mv(r,v),t)])
    if vs:points[name]=vs
groups={}
for name in ['mid','abdomen','head','left_mouth','right_mouth','knee8','knee4','knee7','knee3','knee6','knee2','knee5','knee9']:
    ys=[v[1] for v in points[name]]
    groups[name]={'model_y_range':[min(ys),max(ys)],'signed_lowest_clearance_y24':24-max(ys)}
result={'scope':'ONE_OFFLINE_SOURCE_CUBOID_POSE_NOT_NATIVE_ACCEPTANCE','time_seconds':1.35,'ticks':27,'channels_not_references':21,'source_card_equality_assertion':True,
'assumptions':['Only DEATH active; neutral look; limbSwingAmount=0 assumed, not proven final native input.','Entity id divisible by10 gives mouth Z +/-2.5deg; no death freeze guard in setupAnim.','Source cuboids include constant CubeDeformation (thigh0.5), verified against card. Alpha masks, hair transparency, float rounding and world offsets omitted.','Y down, nominal floor24; no generic renderer flip applied. Fresh entity base deathTime stays0 under selected source chain; NBT/Mixins not covered.','Nonloop last values held after25ticks; snapshot27ticks precedes removal30.'], 'groups':groups,'new_accepted_credit':0}
(B/'terminal-source-probe.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
