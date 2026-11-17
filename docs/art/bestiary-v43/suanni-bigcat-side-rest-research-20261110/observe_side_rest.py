"""Complete rigid cuboid hierarchy, selected sleep progress ONLY; not runtime playback."""
import copy
import itertools
import json
import math
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
source=(HERE/'sources/ModelBigCat.java').read_text()
constructor=source.split('animator = ModelAnimator.create();')[0]
def numbers(raw): return [float(x.strip().rstrip('F')) for x in raw.split(',')]
bones={}
for name in re.findall(r'this\.(\w+) = new AdvancedModelBox\(this,',constructor):
    pos=re.search(rf'this\.{name}\.setRotationPoint\(([^)]+)\)',constructor)
    rot=re.search(rf'this\.setRotateAngle\({name}, ([^)]+)\)',constructor)
    parent=re.search(rf'this\.(\w+)\.addChild\(this\.{name}\)',constructor)
    boxes=[]
    for raw in re.findall(rf'this\.{name}\.addBox\(([^)]+)\)',constructor):
        v=numbers(raw);assert len(v)==7
        boxes.append({'origin':[a-v[6] for a in v[:3]],'size':[a+2*v[6] for a in v[3:6]]})
    bones[name]={'pos':numbers(pos[1]),'rot':numbers(rot[1]) if rot else [0,0,0], 'parent':parent[1] if parent else None,'boxes':boxes}
assert len(bones)==35 and sum(len(b['boxes']) for b in bones.values())==35
assert bones==json.loads((HERE/'constructor-card.json').read_text())
(HERE/'parsed-constructor.json').write_text(json.dumps(bones,indent=2)+'\n')

def rotate(v,rot):
    x,y,z=v;a,b,c=rot
    y,z=y*math.cos(a)-z*math.sin(a),y*math.sin(a)+z*math.cos(a)
    x,z=x*math.cos(b)+z*math.sin(b),-x*math.sin(b)+z*math.cos(b)
    x,y=x*math.cos(c)-y*math.sin(c),x*math.sin(c)+y*math.cos(c)
    return [x,y,z]
def world(v,name,pose):
    b=pose[name];v=[a+c for a,c in zip(rotate(v,b['rot']),b['pos'])]
    return world(v,b['parent'],pose) if b['parent'] else v

sleep=source.split('// Sleeping Animation')[1]
operations=[]
for method,name,raw in re.findall(r'this\.progress(Rotation|Position)\((\w+), big_cat.sleepProgress, (.*), 40\);',sleep):
    expr=re.sub(r'\(float\)\s*Math.toRadians\(', 'rad(',raw)
    expr=re.sub(r'(?<=\d)F\b','',expr)
    v=eval('['+expr+']',{'__builtins__':{},'rad':math.radians})
    operations.append({'method':method,'bone':name,'target':v,'divisor':40})
assert len(operations)==9

geometries={};results={}
for label,progress in [('constructor',0),('sleep_progress_only',40)]:
    pose=copy.deepcopy(bones)
    for op in operations:
        key='rot' if op['method']=='Rotation' else 'pos'
        name=op['bone']
        # Exact released Citadel3681528 bytecode confirms non-Prev subtraction.
        pose[name][key]=[now+(goal-default)*progress/40 for now,goal,default in zip(pose[name][key],op['target'],bones[name][key])]
    parts={}
    for name,b in pose.items():
        parts[name]=[]
        for box in b['boxes']:
            points=[world([(box['origin'][i]+s[i]*box['size'][i])*(0.95 if name=='head_jaw' and i==0 else 1) for i in range(3)],name,pose) for s in itertools.product((0,1),repeat=3)]
            parts[name].append(points)
    geometries[label]=parts
    results[label]={'part_gap_to_nominal_floor_model_units':{name:24-max(p[1] for box in boxes for p in box) for name,boxes in parts.items() if not name.startswith('eye_')},'poses':{name:{k:b[k] for k in ('pos','rot')} for name,b in pose.items()}}
out={'kind':'complete source constructor geometry + selected sleep target progress; NOT full setupAnim or native render', 'constructor_card_equality':True,'rigging':'rigid parented cuboids; no weighted skin data;35parts/35boxes,2zero-depth eyeplanes', 'progress_operations':operations,'parameters':{'sleep':40,'sit':0,'nominal_floor_y':24},'excluded':['all attack/stretch/talk keyframes','breathing scales, bobs and head walk','eye relocation/atlas transparency; all constructor boxes shown','head tracking (disabled by source while sleeping)','renderer getMobSize, baby model switch and world transforms; nonfluffy tail assumed','terrain and collision'], 'results':results}
(HERE/'prone-observation.json').write_text(json.dumps(out,indent=2)+'\n')

faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620"><rect width="1200" height="620" fill="#ecebe7"/>']
for offset,(label,parts) in zip((0,600),geometries.items()):
    svg.append(f'<text x="{offset+24}" y="32">{label}: rigid source side view / NOT game</text>')
    svg.append(f'<line x1="{offset+20}" y1="410" x2="{offset+580}" y2="410" stroke="#ad4134"/>')
    polygons=[]
    for name,boxes in parts.items():
        if name.startswith('eye_'):continue
        for box in boxes:
            for face in faces:
                v=[box[i] for i in face];polygons.append((sum(p[0] for p in v),name,v))
    for _,name,v in sorted(polygons):
        fill='#b7bec1' if name in ('head_main','head_neck','head_jaw','head_snout') else '#929da1' if name.startswith('body_') else '#737f84'
        points=' '.join(f'{offset+220+p[2]*8:.2f},{218+p[1]*8:.2f}' for p in v)
        svg.append(f'<polygon points="{points}" fill="{fill}" stroke="#424b50"/>')
    svg.append(f'<text x="{offset+24}" y="548">Same projection/scale; nominal source floor y24.</text>')
    svg.append(f'<text x="{offset+24}" y="570">Sleep progress only: procedural breathing/head idle excluded.</text>')
svg.append('</svg>')
(HERE/'bigcat-side-rest.svg').write_text('\n'.join(svg))
print(json.dumps({k:v['part_gap_to_nominal_floor_model_units'] for k,v in results.items()},indent=2))
