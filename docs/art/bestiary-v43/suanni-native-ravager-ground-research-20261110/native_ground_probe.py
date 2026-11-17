"""Bounded native 1.20.1 Ravager body/render endpoint reconstruction, not a game test."""
import copy
import itertools
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE/'sources/RavagerModel.java').read_text()
constructor = source.split('public static LayerDefinition createBodyLayer()')[1].split('return LayerDefinition.create')[0]
def values(raw):
    raw = raw.replace('(float)Math.PI', 'PI')
    raw = re.sub(r'(?<=\d)F\b','',raw)
    return eval('['+raw+']', {'__builtins__':{},'PI':math.pi})

names = {'partdefinition':'root'}
bones = {'root':{'pos':[0,0,0],'rot':[0,0,0],'parent':None,'boxes':[]}}
for line in constructor.splitlines():
    if '.addOrReplaceChild(' not in line: continue
    match = re.search(r'(?:(?:PartDefinition) (\w+) = )?(\w+)\.addOrReplaceChild\("(\w+)", (.*), PartPose\.(offsetAndRotation|offset)\((.*)\)\);', line.strip())
    assert match, line
    var, parent, name, cubelist, kind, raw = match.groups()
    if var: names[var] = name
    v = values(raw)
    boxes = []
    for rawbox in re.findall(r'\.addBox\(([^)]+)\)',cubelist):
        box = values(rawbox)
        assert len(box)==6
        boxes.append({'origin':box[:3],'size':box[3:]})
    bones[name] = {'pos':v[:3],'rot':v[3:] if kind=='offsetAndRotation' else [0,0,0], 'parent':names[parent], 'boxes':boxes}
assert set(bones)=={'root','neck','head','right_horn','left_horn','mouth','body','right_hind_leg','left_hind_leg','right_front_leg','left_front_leg'}
assert sum(len(b['boxes']) for b in bones.values())==12
(HERE/'parsed-constructor.json').write_text(json.dumps(bones,indent=2)+'\n')

def rotate(p, angles):
    x,y,z=p; a,b,c=angles
    y,z=y*math.cos(a)-z*math.sin(a),y*math.sin(a)+z*math.cos(a)
    x,z=x*math.cos(b)+z*math.sin(b),-x*math.sin(b)+z*math.cos(b)
    x,y=x*math.cos(c)-y*math.sin(c),x*math.sin(c)+y*math.cos(c)
    return [x,y,z]

def model_point(p,name):
    b=pose[name]
    p=[a+c for a,c in zip(rotate(p,b['rot']),b['pos'])]
    return model_point(p,b['parent']) if b['parent'] else p

pose=copy.deepcopy(bones)
# prepareMobModel: attack/stun/roar zero, prior neck pitch zero.
pose['mouth']['rot'][0]=math.pi*.01
# setupAnim: look yaw/pitch zero and dead entity walkAmount=0 supplied by renderer.
# Other source constructor defaults remain unchanged.
observations={}
geometries={}
for label,death in [('neutral_dead_before_flip',0),('death_time_19',19)]:
    roll = min(1,math.sqrt(max(0,(death-1)/20*1.6)))*math.pi/2 if death>0 else 0
    parts={}
    for name,b in pose.items():
        parts[name]=[]
        for box in b['boxes']:
            points=[]
            for signs in itertools.product((0,1),repeat=3):
                p=model_point([box['origin'][i]+box['size'][i]*signs[i] for i in range(3)],name)
                # T(-1.501Y) then scale(-1,-1,1) then death Z roll.
                p=[-p[0]/16,1.501-p[1]/16,p[2]/16]
                points.append(rotate(p,[0,0,roll]))
            parts[name].append(points)
    geometries[label]=parts
    observations[label]={'roll_degrees':math.degrees(roll),'part_min_world_y':{name:min(p[1] for box in boxes for p in box) for name,boxes in parts.items() if boxes}}

out={'kind':'native render-chain endpoint algebra, not runtime or terrain validation', 'parameters':{'entity_ground_y':0,'body_yaw':180,'head_yaw':0,'head_pitch':0,'walk_amount':0,'attack_tick':0,'stunned_tick':0,'roar_tick':0,'previous_neck_pitch':0,'partial_tick':0,'model_y_to_blocks':1/16,'renderer_translation_y':-1.501},'observations':observations,'limits':['No Forge event/mod replacement or arbitrary terrain','No death during a retained attack/stun/roar state','No claim that geometry minimum is collision or damage boundary','No intermediate animation replay or runtime capture']}
(HERE/'native-ground-observation.json').write_text(json.dumps(out,indent=2)+'\n')

faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620"><rect width="1200" height="620" fill="#ecebe7"/>']
for offset,(label,parts) in zip((0,600),geometries.items()):
    svg.append(f'<text x="{offset+24}" y="32">{label}: native front projection / NOT game</text>')
    svg.append(f'<line x1="{offset+25}" y1="410" x2="{offset+575}" y2="410" stroke="#ad4134"/>')
    polygons=[]
    for name,boxes in parts.items():
        for box in boxes:
            for face in faces:
                v=[box[i] for i in face]
                polygons.append((sum(p[2] for p in v),name,v))
    for _,name,v in sorted(polygons,reverse=True):
        color='#b7bec1' if name=='head' else '#909c9f' if name=='body' else '#737f84'
        points=' '.join(f'{offset+300+p[0]*120:.2f},{410-p[1]*120:.2f}' for p in v)
        svg.append(f'<polygon points="{points}" fill="{color}" stroke="#424b50"/>')
    svg.append(f'<text x="{offset+24}" y="548">Same projection/scale. Red = assumed entity ground Y0.</text>')
    svg.append(f'<text x="{offset+24}" y="570">No recentering, floor correction, textures, or effects.</text>')
svg.append('</svg>')
(HERE/'native-ravager-front.svg').write_text('\n'.join(svg))
print(json.dumps(out,indent=2))
