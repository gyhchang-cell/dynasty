"""Derive an original elite silhouette from the existing segmented heavy infantry rig.

Only JSON geometry and animation sources are authored; the native atlas is read-only.
"""
import copy
import json
from pathlib import Path

BASE = Path('src/main/resources/assets/dynasty')
ID = 'xianzhen_duantoujiang'
source = json.loads((BASE / 'geo/blueprint/pijia_panjiang_huwei.geo.json').read_text())
geometry = source['minecraft:geometry'][0]
bones = geometry['bones']
by_name = {b['name']: b for b in bones}
remove = {'head', 'right_axe', 'left_axe'}
for _ in range(len(bones)):
    remove.update(b['name'] for b in bones if b.get('parent') in remove)
bones[:] = [b for b in bones if b['name'] not in remove]
for b in bones:
    b['pivot'] = [v * 1.38 for v in b['pivot']]
    for c in b.get('cubes', []):
        c['origin'] = [v * 1.38 for v in c['origin']]
        c['size'] = [v * 1.38 for v in c['size']]
        if 'pivot' in c:
            c['pivot'] = [v * 1.38 for v in c['pivot']]

iron = by_name['chest_front']['cubes'][0]['uv']
gold = by_name['chest_mirror']['cubes'][0]['uv']
skin = by_name['left_grip']['cubes'][0]['uv']
def cube(origin, size, uv):
    return {'origin': origin, 'size': size, 'uv': copy.deepcopy(uv)}

def bone(name, parent, pivot, cubes=(), rotation=None):
    b = {'name': name, 'parent': parent, 'pivot': pivot, 'cubes': list(cubes)}
    if rotation:
        b['rotation'] = rotation
    bones.append(b)

# The neck ends at the seal: no invisible or ordinary head remains above the shoulders.
by_name['neck']['cubes'] = [cube([-2, 37.2, -2], [4, 2, 4], iron)]
bone('neck_seal', 'neck', [0, 40, 0], [cube([-3.7, 39.2, -3.7], [7.4, .5, 7.4], gold)])
bone('seal_flame', 'neck_seal', [0, 40, 0], [cube([-1.7, 39.6, -.3], [3.4, 2.1, .6], gold)])
bone('held_head', 'left_hand', [9.66, 21.25, 0], [cube([6.3, 15.3, -3], [6.8, 5.8, 6], skin)])
bone('held_helmet', 'held_head', [9.66, 20.5, 0], [cube([5.6, 20, -3.7], [8.1, 2.7, 7.4], iron), cube([9.15, 22.5, -2], [1, 3.6, 4], gold)])
bone('held_eyes', 'held_head', [9.66, 18.9, -3.1], [cube([7.3, 18.5, -3.3], [1.1, .7, .3], gold), cube([10.9, 18.5, -3.3], [1.1, .7, .3], gold)])
bone('greatblade', 'right_hand', [-9.66, 21.25, 0], [cube([-10.2, 16.3, -.5], [1.1, 11, 1], iron), cube([-14, 26.5, -.7], [8.7, 1.1, 1.4], gold)], [-115, 0, 0])
for n in range(3):
    bone(f'blade_fragment_{n}', 'greatblade', [-9.66, 27.6+n*10.7, 0], [cube([-12.5, 27.6+n*10.7, -.55], [6.4, 10.7, 1.1], iron), cube([-13.1, 27.6+n*10.7, -.57], [.65, 10.7, 1.15], gold)])

geometry['description'].update(identifier=f'geometry.{ID}', visible_bounds_width=9, visible_bounds_height=7, visible_bounds_offset=[0, 2, 0])
target = BASE / f'geo/blueprint/elite/{ID}.geo.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(source, indent=2)+'\n')

animations = {}
def animation(clip, seconds, transforms, loop=False):
    animations[f'animation.{ID}.{clip}'] = {'loop': loop, 'animation_length': seconds, 'bones': transforms}
def rotation(points):
    return {'rotation': {str(t): value for t, value in points}}

animation('idle', 2, {'waist': rotation([(0,[0,-2,0]),(1,[0,2,0]),(2,[0,-2,0])]), 'seal_flame': {'scale': {'0':[1,.8,1],'1':[1,1.15,1],'2':[1,.8,1]}}}, True)
animation('walk', 1.2, {**{f'{side}_thigh': rotation([(0,[s*18,0,0]),(.6,[-s*18,0,0]),(1.2,[s*18,0,0])]) for side,s in [('left',1),('right',-1)]}, 'chest': rotation([(0,[3,0,-2]),(.6,[3,0,2]),(1.2,[3,0,-2])]), 'greatblade': rotation([(0,[-3,0,0]),(.6,[3,0,0]),(1.2,[-3,0,0])])}, True)
animation('hurt', .35, {'chest': rotation([(0,[0,0,0]),(.1,[-12,0,5]),(.35,[0,0,0])])})
animation('roar', 2.5, {'left_shoulder': rotation([(0,[0,0,0]),(.45,[70,0,-18]),(1.2,[80,0,-15]),(1.35,[105,0,0]),(1.6,[90,0,0]),(2.5,[0,0,0])]), 'left_elbow': rotation([(0,[0,0,0]),(.8,[70,0,0]),(1.2,[75,0,0]),(1.35,[20,0,0]),(2.5,[0,0,0])]), 'held_eyes': {'scale': {'0':[1,1,1],'.9':[1.6,1.6,1.6],'1.5':[1,1,1]}}, 'chest': rotation([(0,[0,0,0]),(1.2,[-10,0,0]),(1.3,[13,0,0]),(2.5,[0,0,0])])})
animation('spin', 3.8, {'waist': rotation([(0,[0,0,0]),(.8,[0,-65,0]),(1.3,[0,360,0]),(1.8,[0,720,0]),(2.3,[0,1080,0]),(3.8,[0,1080,0])]), 'right_shoulder': rotation([(0,[0,0,0]),(.8,[0,15,65]),(2.3,[0,0,65]),(3.8,[0,0,0])]), 'chest': rotation([(0,[0,0,0]),(.8,[20,0,0]),(2.3,[20,0,0]),(3.8,[0,0,0])])})
animation('throw', 2.5, {'left_shoulder': rotation([(0,[0,0,0]),(.6,[140,0,-10]),(1,[35,0,-10]),(1.3,[25,0,-10]),(2.5,[0,0,0])]), 'held_head': {'position': {'0':[0,0,0],'.8':[0,0,0],'1':[0,3,-18],'1.25':[0,-2,-32],'1.8':[0,0,0],'2.5':[0,0,0]}}, 'right_shoulder': rotation([(0,[0,0,0]),(.7,[-20,0,0]),(2.5,[0,0,0])])})
death = {'chest': rotation([(0,[0,0,0]),(1.2,[0,0,0]),(2.1,[28,0,0]),(3.5,[38,0,0])]), 'root': {'position': {'0':[0,0,0],'1.2':[0,0,0],'2.4':[0,-8,0],'3.5':[0,-8,0]}}, 'left_knee': rotation([(0,[0,0,0]),(2.4,[88,0,0]),(3.5,[88,0,0])]), 'right_knee': rotation([(0,[0,0,0]),(2.4,[88,0,0]),(3.5,[88,0,0])]), 'held_head': {'scale': {'0':[1,1,1],'1':[1,1,1],'1.4':[0,0,0]}}, 'seal_flame': {'scale': {'0':[1,1,1],'1.4':[0,0,0]}}}
for n in range(3):
    death[f'blade_fragment_{n}'] = {'rotation': {'0':[0,0,0],'1.6':[0,0,0],'2.1':[25+n*15,0,(-1 if n%2 else 1)*30]}, 'position': {'0':[0,0,0],'1.6':[0,0,0],'2.1':[(-1 if n%2 else 1)*(n+1)*2,-(n+1)*4,0]}}
animation('death', 3.5, death)
target=BASE/f'animations/blueprint/elite/{ID}.animation.json';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({'format_version':'1.8.0','animations':animations},indent=2)+'\n')
print(f'Generated {ID}: {len(bones)} bones, {len(animations)} clips')
