#!/usr/bin/env python3
"""Original possessed alchemy ding. The furnace is the body, never an accessory to a humanoid.

Authority: this source and its exported GeckoLib files. Three ground contacts drive locomotion;
a hinged vessel, embedded ritual mask, cloak straps and a connected tool arm drive the seven
existing animation names. No third-party geometry, UVs or animation data is copied.
"""
from pathlib import Path
import json
import math
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / 'src/main/resources/assets/dynasty'
ID = 'yinyang_liandan_fangshi'
COLORS = {'dark': '#28242B', 'copper': '#B66D35', 'cold': '#63BAC7', 'white': '#FFFFFF'}
UV = {'dark': [3, 3], 'copper': [9, 3], 'cold': [3, 9], 'white': [9, 9]}
bones = []


def bone(name, parent=None, pivot=(0, 0, 0), rotation=None):
    b = {'name': name, 'pivot': list(pivot)}
    if parent:
        b['parent'] = parent
    if rotation:
        b['rotation'] = list(rotation)
    bones.append(b)
    return b


def cube(b, at, size, color='dark', rotation=None):
    c = {'origin': list(at), 'size': list(size), 'uv': {
        face: {'uv': UV[color], 'uv_size': [4, 4]}
        for face in ('north', 'south', 'east', 'west', 'up', 'down')}}
    if rotation:
        c.update(pivot=b['pivot'], rotation=list(rotation))
    b.setdefault('cubes', []).append(c)


def keys(data):
    return {str(t): v for t, v in data}


def geo(identifier, model, width, height):
    p = A / 'geo/blueprint/elite' / f'{identifier}.geo.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'format_version': '1.12.0', 'minecraft:geometry': [{
        'description': {'identifier': 'geometry.' + identifier,
                        'texture_width': 16, 'texture_height': 16,
                        'visible_bounds_width': width, 'visible_bounds_height': height,
                        'visible_bounds_offset': [0, 1, 0]}, 'bones': model}]}, indent=2) + '\n')


def animation(identifier, data):
    p = A / 'animations/blueprint/elite' / f'{identifier}.animation.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'format_version': '1.8.0', 'animations': data}, indent=2) + '\n')


bone('root', pivot=(0, 10, 0))
cradle = bone('cradle', 'root', (0, 8, 0))
cube(cradle, (-7, 7, -6), (14, 3, 12), 'copper')
cube(cradle, (-8, 9, -7), (16, 2, 14))
# Thick vessel walls leave a real six-by-eight opening. No hidden chest/waist/legs.
furnace = bone('furnace', 'cradle', (0, 14, 0))
cube(furnace, (-10, 11, -8), (3, 12, 16), 'copper')
cube(furnace, (7, 11, -8), (3, 12, 16), 'copper')
cube(furnace, (-7, 11, 5), (14, 12, 3), 'copper')
cube(furnace, (-7, 11, -8), (14, 3, 3), 'copper')
cube(furnace, (-7, 21, -8), (14, 3, 3), 'copper')
cube(furnace, (-7, 14, -8), (4, 7, 3))
cube(furnace, (3, 14, -8), (4, 7, 3))
cube(furnace, (-7, 11, -5), (14, 2, 10))
core = bone('alchemical_core', 'furnace', (0, 17, 0))
cube(core, (-3, 14, -2), (6, 7, 5), 'cold')
cube(core, (-2, 15, -4), (4, 5, 2), 'copper')
# A ritual mask is embedded in the vessel's front rim, not perched on a humanoid neck.
mask = bone('mask', 'furnace', (0, 19, -8))
cube(mask, (-5, 17, -9), (2, 6, 2), 'white')
cube(mask, (3, 17, -9), (2, 6, 2), 'white')
cube(mask, (-3, 21, -9), (6, 2, 2), 'white')
cube(mask, (-3, 17, -9), (6, 2, 2), 'white')
cube(mask, (-1, 19, -9), (2, 2, 2), 'copper')
for side, x, color in [('warm', -11, 'copper'), ('cold', 9, 'cold')]:
    port = bone(side + '_port', 'furnace', (x + 1, 23, -6))
    cube(port, (x, 22, -9), (2, 3, 3), color)
    cube(port, (x, 24, -8), (2, 2, 2), 'white')
# Two lateral vessel handles, clearly joined to the body.
for side, sign in [('left', 1), ('right', -1)]:
    handle = bone(side + '_vessel_handle', 'furnace', (sign * 9, 20, 0))
    x = 10 if sign > 0 else -13
    cube(handle, (x, 18, -3), (3, 2, 6), 'copper')
    cube(handle, (x, 22, -3), (3, 2, 6), 'copper')
    cube(handle, (12 if sign > 0 else -14, 20, -3), (2, 2, 6), 'copper')
# Three load-bearing feet: paired front contacts and one rear counterbalance.
for i, (x, z) in enumerate([(-7, -5), (7, -5), (0, 5)]):
    upper = bone(f'furnace_leg{i}', 'root', (x, 9, z))
    cube(upper, (x - 2, 5, z - 2), (4, 5, 4), 'copper')
    knee = bone(f'furnace_knee{i}', upper['name'], (x, 5, z))
    cube(knee, (x - 2, 2, z - 3), (4, 4, 5))
    foot = bone(f'furnace_foot{i}', knee['name'], (x, 2, z - 1))
    cube(foot, (x - 3, 0, z - 4), (6, 2, 7), 'copper')
    cube(foot, (x - 2, 1, z - 3), (4, 2, 4))
# A hinged lotus-shaped lid carries the old crown motif without recreating a head.
lid = bone('lid', 'furnace', (0, 24, 6))
cube(lid, (-9, 24, -7), (18, 2, 14))
cube(lid, (-7, 26, -5), (14, 2, 10), 'copper')
crown = bone('lotus_crown', 'lid', (0, 28, 0))
cube(crown, (-4, 28, -3), (8, 2, 6), 'copper')
cube(crown, (-4, 30, -2), (2, 3, 4), 'copper')
cube(crown, (2, 30, -2), (2, 2, 4), 'copper')
cube(crown, (-1, 30, -1), (2, 3, 2), 'cold')
# One side-mounted tool arm, with a continuous hinge -> link -> clamp -> whisk path.
arm = bone('whisk_hinge', 'furnace', (-10, 20, 0))
cube(arm, (-13, 18, -2), (4, 4, 4), 'copper')
cube(arm, (-18, 19, -1), (6, 2, 2))
link = bone('whisk_link', 'whisk_hinge', (-17, 20, 0))
cube(link, (-19, 13, -1), (3, 7, 2), 'copper')
clamp = bone('whisk_clamp', 'whisk_link', (-18, 14, 0))
cube(clamp, (-20, 12, -2), (4, 2, 4))
cube(clamp, (-20, 15, -2), (4, 2, 4))
whisk = bone('whisk', 'whisk_clamp', (-18, 14, 0))
cube(whisk, (-19, 9, -1), (2, 10, 2), 'copper')
cube(whisk, (-20, 7, -2), (4, 3, 4), 'white')
for i, x in enumerate((-21, -19, -17)):
    strand = bone(f'whisk_tassel{i}', 'whisk', (x + 1, 7, 0), (0, 0, (i - 1) * 12))
    cube(strand, (x, 4 - i, -1), (2, 3 + i, 2), 'white')
# Cloak hangs from actual straps on the rear rim; neither robe legs nor a hidden body.
strap = bone('cloak_strap', 'furnace', (0, 23, 7))
cube(strap, (-9, 21, 7), (18, 3, 2))
for i, x in enumerate((-6, 0, 6)):
    cloth = bone(f'cloak_panel{i}', 'cloak_strap', (x, 22, 8))
    cube(cloth, (x - 2.5, 12, 8), (5, 10, 2))
    tail = bone(f'cloak_tail{i}', cloth['name'], (x, 12, 9))
    cube(tail, (x - 2, 5 + (i % 2), 9), (4, 7 - (i % 2), 2))
    cube(tail, (x - 2, 5 + (i % 2), 11), (4, 2, 2), 'white')
for i in range(3):
    pill = bone(f'gold{i}', 'furnace', (-5 + i * 5, 27, -11))
    cube(pill, (-6 + i * 5, 26, -12), (2, 2, 2), 'copper')

anims = {}

def anim(name, length, loop=False):
    d = {'animation_length': length, 'bones': {}}
    if loop:
        d['loop'] = True
    anims['animation.' + ID + '.' + name] = d
    return d['bones']


a = anim('idle', 2, True)
a['lid'] = {'rotation': keys([(0, [0, 0, 0]), (1, [-5, 0, 0]), (2, [0, 0, 0])])}
a['alchemical_core'] = {'scale': keys([(0, [1, 1, 1]), (1, [1.04, 1.05, 1.04]), (2, [1, 1, 1])])}
a['whisk_link'] = {'rotation': keys([(0, [0, 0, -3]), (1, [0, 0, 3]), (2, [0, 0, -3])])}
for i in range(3):
    a[f'cloak_tail{i}'] = {'rotation': keys([(0, [2 + i, 0, 0]), (1, [-2 - i, 0, 0]), (2, [2 + i, 0, 0])])}
a = anim('walk', 1.2, True)
# Tripod contacts lift in successive thirds; no simultaneous three-foot hopping.
for i in range(3):
    track = []
    knee = []
    for tick in range(25):
        t = tick / 20
        phase = (t / 1.2 - i / 3) % 1
        lift = math.sin(phase / .28 * math.pi) * 2.4 if phase < .28 else 0
        travel = 3 * math.sin(phase * math.pi * 2)
        track.append((round(t, 3), [0, round(lift, 3), round(travel, 3)]))
        knee.append((round(t, 3), [round(lift * 4, 3), 0, 0]))
    a[f'furnace_leg{i}'] = {'position': keys(track)}
    a[f'furnace_knee{i}'] = {'rotation': keys(knee)}
a['furnace'] = {'rotation': keys([(0, [0, 0, 2]), (.4, [0, 0, -2]), (.8, [2, 0, 0]), (1.2, [0, 0, 2])])}
for i in range(3):
    a[f'cloak_panel{i}'] = {'rotation': keys([(0, [7, 0, 0]), (.6, [10, 0, 0]), (1.2, [7, 0, 0])])}
a = anim('helix', 4)
a['lid'] = {'rotation': keys([(0, [0, 0, 0]), (.65, [-24, 0, 0]), (.8, [-32, 0, 0]), (2.8, [-18, 0, 0]), (4, [0, 0, 0])])}
a['whisk_hinge'] = {'rotation': keys([(0, [0, 0, 0]), (.6, [0, 55, -25]), (.8, [0, -35, 12]), (1.1, [0, -35, 12]), (3.4, [0, 0, 0]), (4, [0, 0, 0])])}
a['whisk_link'] = {'rotation': keys([(0, [0, 0, 0]), (.65, [0, 0, -30]), (.8, [0, 0, 30]), (1.3, [0, 0, 20]), (4, [0, 0, 0])])}
for name in ('warm_port', 'cold_port'):
    a[name] = {'scale': keys([(0, [1, 1, 1]), (.75, [1.2, 1.2, 1.2]), (.8, [1, 1, 1]), (4, [1, 1, 1])])}
a = anim('sea', 3.05)
# The cradle rocks the whole vessel forward while all three feet retain support.
a['cradle'] = {'rotation': keys([(0, [0, 0, 0]), (1.1, [-12, 0, 0]), (1.2, [28, 0, 0]), (1.6, [28, 0, 0]), (2.5, [0, 0, 0]), (3.05, [0, 0, 0])])}
a['lid'] = {'rotation': keys([(0, [0, 0, 0]), (1.15, [-45, 0, 0]), (1.2, [-62, 0, 0]), (1.6, [-62, 0, 0]), (2.5, [0, 0, 0]), (3.05, [0, 0, 0])])}
a['whisk_hinge'] = {'rotation': keys([(0, [0, 0, 0]), (1, [0, 0, -15]), (1.2, [0, 0, -45]), (2.4, [0, 0, 0]), (3.05, [0, 0, 0])])}
a = anim('pells', 2.75)
a['lid'] = {'rotation': keys([(0, [0, 0, 0]), (.8, [-20, 0, 0]), (1.1, [-25, 0, 0]), (1.3, [-4, 0, 0]), (2.75, [0, 0, 0])])}
a['mask'] = {'position': keys([(0, [0, 0, 0]), (.9, [0, 0, -.5]), (1.1, [0, 0, -.5]), (1.35, [0, 0, 0]), (2.75, [0, 0, 0])])}
for i in range(3):
    # Raise three readable pills outside the lid, then draw one into the real mouth.
    # The other two converge on the forward launch point at the existing 22-tick frame.
    release = [[5, -7, 3], [-2, -3, 2], [-3, -3, 2]][i]
    a[f'gold{i}'] = {'position': keys([(0, [0, -4, 3]), (.3, [0, 0, 0]), (.9, release), (1.1, release)]), 'scale': keys([(0, [0, 0, 0]), (.15, [1, 1, 1]), (1.05, [1, 1, 1]), (1.1, [0, 0, 0]), (2.75, [0, 0, 0])])}
a = anim('hurt', .4)
a['furnace'] = {'rotation': keys([(0, [0, 0, 0]), (.1, [-8, 0, 5]), (.4, [0, 0, 0])])}
a['lid'] = {'rotation': keys([(0, [0, 0, 0]), (.1, [-12, 0, 0]), (.4, [0, 0, 0])])}
a = anim('death', 4)
a['cradle'] = {'position': keys([(0, [0, 0, 0]), (.4, [0, 1, 0]), (1.3, [0, -4, 0]), (4, [0, -4, 0])]), 'rotation': keys([(0, [0, 0, 0]), (.4, [-8, 0, 0]), (1.2, [18, 0, 5]), (4, [18, 0, 5])])}
a['lid'] = {'position': keys([(0, [0, 0, 0]), (.5, [0, 5, 0]), (1.4, [0, -8, 8]), (4, [0, -8, 8])]), 'rotation': keys([(0, [0, 0, 0]), (.5, [80, 0, 0]), (1.4, [170, 30, 0]), (4, [170, 30, 0])])}
for i, sign in enumerate((-1, 1, 0)):
    # The rear foot remains planted as the front supports spread during collapse.
    a[f'furnace_leg{i}'] = {'rotation': keys([(0, [0, 0, 0]), (1.1, [0, 0, sign * 35]), (4, [0, 0, sign * 35])])}
    if sign:
        # Lift the three-unit outer foot corner as its nine-unit support tips.
        # The small clearance covers interpolation between the sampled angles.
        contact = []
        for t in [n / 20 for n in range(23)]:
            angle = math.radians(35 * t / 1.1)
            lift = max(0, 9 * math.cos(angle) + 3 * math.sin(angle) - 9)
            contact.append((round(t, 3), [0, round(lift + (.02 if t else 0), 4), 0]))
        a[f'furnace_leg{i}']['position'] = keys(contact + [(4, contact[-1][1])])
a['whisk_hinge'] = {'rotation': keys([(0, [0, 0, 0]), (1.1, [0, 0, 50]), (4, [0, 0, 50])])}
a['root'] = {'scale': keys([(0, [1, 1, 1]), (1.4, [1, 1, 1]), (3.8, [0, 0, 0]), (4, [0, 0, 0])])}
geo(ID, bones, 4, 4)
animation(ID, anims)
count = len(bones), sum(len(b.get('cubes', [])) for b in bones)
texture = Image.new('RGB', (16, 16), 'white')
for color, (u, v) in UV.items():
    for x in range(u - 1, u + 5):
        for y in range(v - 1, v + 5):
            texture.putpixel((x, y), tuple(bytes.fromhex(COLORS[color][1:])))
p = A / 'textures/entity/blueprint/elite' / f'{ID}.png'
p.parent.mkdir(parents=True, exist_ok=True)
texture.save(p)
# Projectile resource IDs and branch names remain compatible with the existing renderer.
bones = []
bone('root', pivot=(0, 3, 0))
for name, color in [('warm', 'copper'), ('cold', 'cold'), ('pill', 'copper')]:
    b = bone(name, 'root', (0, 3, 0))
    cube(b, (-2, 1, -2), (4, 4, 4), color)
    if name != 'pill':
        cube(b, (-1, 5, -1), (2, 2, 2), 'white')
geo('alchemist_cast_orb', bones, 1, 1)
animation('alchemist_cast_orb', {'animation.alchemist_cast_orb.spin': {
    'loop': True, 'animation_length': 1, 'bones': {'root': {
        'rotation': keys([(0, [0, 0, 0]), (1, [0, 360, 0])])}}}})
print(f'Possessed ding exported: {count[0]} functional bones, {count[1]} cuboids; seven existing clip IDs; actual16x16/four-colour PNG.')

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('yinyang_liandan_fangshi')
