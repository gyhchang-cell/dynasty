"""Source-only pose-blend geometry. Deliberately NOT a full setupAnim emulator."""
import copy
import itertools
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE / 'sources/ModelSnowLeopard.java').read_text()
constructor = source.split('this.updateDefaultPose();')[0]
number = r'(-?\d+(?:\.\d+)?F?)'
def nums(s):
    return [float(v.rstrip('F')) for v in s.split(',')]

bones = {}
for name in re.findall(r'(\w+) = new AdvancedModelBox\(this\)', constructor):
    p = re.search(rf'{name}\.setRotationPoint\(([^)]+)\)', constructor)
    r = re.search(rf'setRotationAngle\({name}, ([^)]+)\)', constructor)
    parent = re.search(rf'(\w+)\.addChild\({name}\)', constructor)
    boxes = []
    for raw in re.findall(rf'{name}\.setTextureOffset\([^)]*\)\.addBox\(([^)]+)\)', constructor):
        v = nums(','.join(raw.split(',')[:7]))
        boxes.append({'origin': [x-v[6] for x in v[:3]], 'size': [x+2*v[6] for x in v[3:6]]})
    bones[name] = {'pos': nums(p[1]), 'rot': nums(r[1]) if r else [0,0,0], 'parent': parent[1] if parent else None, 'boxes': boxes}
assert bones == json.loads((HERE/'constructor-card.json').read_text()), 'independent constructor reconstruction mismatch'

def rotate(v, r):
    x,y,z = v
    a,b,c = r
    y,z = y*math.cos(a)-z*math.sin(a), y*math.sin(a)+z*math.cos(a)
    x,z = x*math.cos(b)+z*math.sin(b), -x*math.sin(b)+z*math.cos(b)
    x,y = x*math.cos(c)-y*math.sin(c), x*math.sin(c)+y*math.cos(c)
    return [x,y,z]

def world(v, name, pose):
    b = pose[name]
    p = [a+c for a,c in zip(rotate(v,b['rot']),b['pos'])]
    return world(p,b['parent'],pose) if b['parent'] else p

def rest_pose(progress):
    pose = copy.deepcopy(bones)
    # Only sitSleep=sleep=progress; all other progress channels zero.
    for method,name,channel,args in re.findall(r'progress(Rotation|Position)Prev\((\w+), (sitSleepProgress|sleepProgress), ([^;]+)\);', source):
        args = args.replace('Maths.rad(', 'rad(').replace('tailAngle', '1')
        args = re.sub(r'(?<=\d)F\b', '', args)
        vals = eval('['+args+']', {'__builtins__':{}, 'rad': math.radians})
        key = 'rot' if method == 'Rotation' else 'pos'
        pose[name][key] = [a+v*progress/vals[3] for a,v in zip(pose[name][key], vals[:3])]
    return pose

faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
observations = {}
geometry = {}
for label,progress in [('bind',0),('sleep_blend_only',5)]:
    pose = rest_pose(progress)
    parts = {}
    for name,b in pose.items():
        if name in ('bubble','whiskersLeft','whiskersRight'): continue
        parts[name] = []
        for box in b['boxes']:
            points = [world([box['origin'][i]+s[i]*box['size'][i] for i in range(3)],name,pose) for s in itertools.product((0,1),repeat=3)]
            parts[name].append(points)
    geometry[label] = parts
    observations[label] = {name: {'lowest_source_y':max(p[1] for box in boxes for p in box), 'gap_to_nominal_floor_model_units':24-max(p[1] for box in boxes for p in box)} for name,boxes in parts.items() if boxes}

out = {'kind':'source progress blend only; NOT complete animation, textured render or game', 'constructor_card_equality':True, 'parameters':{'sleep':5,'sit':0,'stalk':0,'tackle':0,'walk_amount':0,'entity_id_parity':'even'}, 'excluded':['procedural idle head and tail motion','animator state','renderer scale and world transforms','bubble and whisker planes','young scaling'], 'nominal_floor_source_y':24, 'observations':observations}
(HERE/'rest-observation.json').write_text(json.dumps(out,indent=2)+'\n')

# Identical orthographic side view and scale. Gray construction geometry only.
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="540" viewBox="0 0 1200 540"><rect width="1200" height="540" fill="#ecebe7"/>']
for offset,(label,parts) in zip((0,600),geometry.items()):
    svg.append(f'<text x="{offset+24}" y="30" font-size="18">{label}: gray source geometry / not game</text>')
    def point(p): return (offset+265+p[2]*9, 182+p[1]*9)
    svg.append(f'<line x1="{offset+20}" y1="398" x2="{offset+580}" y2="398" stroke="#ad4134"/>')
    polygons = []
    for name,boxes in parts.items():
        for box in boxes:
            for face in faces:
                vertices = [box[i] for i in face]
                polygons.append((sum(p[0] for p in vertices),name,vertices))
    for depth,name,vertices in sorted(polygons):
        color = '#a1a9ad' if name=='head' else '#bdc2c3' if name=='body' else '#858e92'
        points = ' '.join(f'{x:.2f},{y:.2f}' for x,y in map(point,vertices))
        svg.append(f'<polygon points="{points}" fill="{color}" stroke="#4c5559" stroke-width="1"/>')
    svg.append(f'<text x="{offset+24}" y="480" font-size="16">Floor y=24; same camera and scale; no automatic floor correction.</text>')
svg.append('</svg>')
(HERE/'rest-source-side.svg').write_text('\n'.join(svg))
print(json.dumps(out,indent=2))
