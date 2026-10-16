#!/usr/bin/env python3
"""Editable original horseshoe-shell yasha, six ground supports and one connected fork-claw.

The carapace is the main body; there is no human chest, waist, neck or pair of human arms.
The Cataclysm author's Amethyst_Crab_Model constructor was studied for low body/support
organization only. No geometry, texture or animation data from that mod is copied.
"""
from pathlib import Path
import copy
import json
import math
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / 'src/main/resources/assets/dynasty'
DATA = ROOT / 'src/main/resources/data/dynasty'
ID = 'fubo_xunhai_yecha'
COLORS = {'shell': '#20344B', 'bronze': '#9D8052', 'water': '#67BFCB', 'white': '#FFFFFF'}
UV = {'shell': [3, 3], 'bronze': [9, 3], 'water': [3, 9], 'white': [9, 9]}
bones = []


def bone(name, parent=None, pivot=(0, 0, 0), rotation=None):
    b = {'name': name, 'pivot': list(pivot)}
    if parent:
        b['parent'] = parent
    if rotation:
        b['rotation'] = list(rotation)
    bones.append(b)
    return b


def cube(b, at, size, color='shell', rotation=None):
    c = {'origin': list(at), 'size': list(size), 'uv': {
        face: {'uv': UV[color], 'uv_size': [4, 4]}
        for face in ('north', 'south', 'east', 'west', 'up', 'down')}}
    if rotation:
        c.update(pivot=b['pivot'], rotation=list(rotation))
    b.setdefault('cubes', []).append(c)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def geo(identifier, model, width, height, offset):
    write(A / 'geo/blueprint/elite' / f'{identifier}.geo.json', {
        'format_version': '1.12.0', 'minecraft:geometry': [{
            'description': {'identifier': 'geometry.' + identifier, 'texture_width': 16,
                            'texture_height': 16, 'visible_bounds_width': width,
                            'visible_bounds_height': height, 'visible_bounds_offset': offset},
            'bones': model}]})


def keys(data):
    return {str(t): v for t, v in data}


bone('root')
body = bone('carapace', 'root', (0, 12, 0))
cube(body, (-14, 10, -13), (28, 8, 26))
cube(body, (-11, 18, -10), (22, 3, 20), 'bronze')
cube(body, (-8, 21, -6), (16, 2, 12))
belly = bone('belly', 'carapace', (0, 10, 0))
cube(belly, (-11, 7, -10), (22, 4, 20))
# Broad shell shoulders and rear fins establish a low aquatic mass.
for side, sign in [('left', 1), ('right', -1)]:
    shoulder = bone(side + '_shell_rim', 'carapace', (sign * 12, 13, 0))
    cube(shoulder, (12 if sign > 0 else -18, 11, -11), (6, 5, 22), 'bronze')
    cube(shoulder, (18 if sign > 0 else -20, 12, -8), (2, 4, 5))
    fin = bone(side + '_rear_fin', 'carapace', (sign * 12, 13, 10), (0, sign * -12, 0))
    cube(fin, (10 if sign > 0 else -15, 10, 8), (5, 4, 11))
    vent = bone(side + '_tide_vent', 'carapace', (sign * 13, 13, -12))
    cube(vent, (sign * 13 - 2, 11, -15), (4, 4, 3), 'water')
    eye = bone(side + '_eye', 'carapace', (sign * 7, 17, -12))
    cube(eye, (sign * 7 - 3, 16, -16), (6, 4, 4), 'bronze')
    cube(eye, (sign * 7 - 2, 17, -17), (4, 2, 2), 'water')
mouth = bone('mandible', 'carapace', (0, 10, -12))
cube(mouth, (-7, 8, -16), (14, 4, 4))
cube(mouth, (-5, 9, -17), (10, 2, 2), 'white')
for x in (-5, 3):
    cube(mouth, (x, 7, -18), (2, 5, 2), 'white')
# The six connected supports attach directly to the shell, never to a human pelvis.
for i, z in enumerate((-8, 0, 8)):
    for side, sign in [('left', 1), ('right', -1)]:
        name = f'{side}_leg{i}'
        upper = bone(name, 'root', (sign * 12, 10, z))
        cube(upper, (11 if sign > 0 else -20, 7, z - 2), (9, 4, 4))
        knee = bone(name + '_knee', name, (sign * 19, 7, z))
        cube(knee, (18 if sign > 0 else -21, 2, z - 2), (3, 6, 4), 'bronze')
        foot = bone(name + '_foot', knee['name'], (sign * 20, 2, z))
        cube(foot, (18 if sign > 0 else -24, 0, z - 3), (6, 2, 6))
        cube(foot, (19 if sign > 0 else -23, 2, z - 2), (4, 2, 4), 'bronze')
# Three tapering tail segments provide a rear counterweight; the tail is not a torso.
tail = bone('telson_base', 'carapace', (0, 13, 11))
cube(tail, (-4, 11, 10), (8, 4, 12), 'bronze')
tail2 = bone('telson_middle', 'telson_base', (0, 13, 21))
cube(tail2, (-2, 12, 20), (4, 3, 10))
tail3 = bone('telson_tip', 'telson_middle', (0, 13, 29))
cube(tail3, (-1, 12, 28), (2, 2, 10), 'bronze')
# One crab appendage: shell hinge -> foresegment -> two gripping jaws -> rigid fork.
hinge = bone('fork_hinge', 'carapace', (-12, 13, -9))
cube(hinge, (-21, 11, -13), (10, 4, 6))
fore = bone('fork_foresegment', 'fork_hinge', (-20, 13, -12))
cube(fore, (-22, 11, -26), (4, 4, 15), 'bronze')
clamp = bone('fork_clamp', 'fork_foresegment', (-20, 13, -24))
cube(clamp, (-24, 10, -28), (3, 6, 7))
cube(clamp, (-19, 10, -28), (3, 6, 7))
fork = bone('trident', 'fork_clamp', (-20, 13, -24))
cube(fork, (-21, 12, -34), (2, 2, 23), 'bronze')
cube(fork, (-26, 12, -37), (12, 2, 3), 'white')
for x in (-26, -21, -16):
    cube(fork, (x, 12, -44), (2, 2, 9), 'white')
    cube(fork, (x, 14, -43), (2, 2, 3), 'water')
death_fork = bone('planted_trident', 'root', (-20, 13, -24))
death_fork['cubes'] = copy.deepcopy(fork['cubes'])
# A distinct pale mineral shell appears during petrification, then fractures with the supports.
reef = bone('reef_shell', 'root', (0, 12, 0))
cube(reef, (-14, 9, -13), (28, 9, 26), 'white')
cube(reef, (-11, 18, -10), (22, 3, 20))
cube(reef, (-8, 21, -6), (16, 2, 12), 'white')
for i, x in enumerate((-10, 0, 10)):
    fragment = bone(f'reef_fragment{i}', 'reef_shell', (x, 14, 0))
    cube(fragment, (x - 3, 10, -14), (6, 7, 3), 'white')

anims = {}


def anim(name, length, loop=False):
    d = {'animation_length': length, 'bones': {}}
    if loop:
        d['loop'] = True
    anims['animation.' + ID + '.' + name] = d
    return d['bones']


def living(a):
    a['reef_shell'] = {'scale': [0, 0, 0]}
    a['planted_trident'] = {'scale': [0, 0, 0]}


a = anim('idle', 2, True)
living(a)
a['carapace'] = {'position': keys([(0, [0, 0, 0]), (1, [0, .4, 0]), (2, [0, 0, 0])])}
a['mandible'] = {'rotation': keys([(0, [0, 0, 0]), (1, [8, 0, 0]), (2, [0, 0, 0])])}
for i, name in enumerate(('telson_base', 'telson_middle', 'telson_tip')):
    a[name] = {'rotation': keys([(0, [0, -3 - i, 0]), (1, [0, 3 + i, 0]), (2, [0, -3 - i, 0])])}
a = anim('walk', 1.2, True)
living(a)
for i in range(3):
    for side, sign in [('left', 1), ('right', -1)]:
        pos, yaw = [], []
        for tick in range(25):
            t = tick / 20
            phase = (t / 1.2 + (i % 2) * .5 + (0 if sign > 0 else .5)) % 1
            lift = 2.3 * math.sin(phase / .42 * math.pi) if phase < .42 else 0
            pos.append((t, [0, round(lift, 4), 0]))
            yaw.append((t, [0, round(math.sin(phase * 2 * math.pi) * 9, 4), 0]))
        a[f'{side}_leg{i}'] = {'position': keys(pos), 'rotation': keys(yaw)}
a['carapace'] = {'rotation': keys([(0, [0, 0, 1]), (.6, [0, 0, -1]), (1.2, [0, 0, 1])])}
a['telson_tip'] = {'rotation': keys([(0, [0, -8, 0]), (.6, [0, 8, 0]), (1.2, [0, -8, 0])])}
a = anim('wave', 4.1)
living(a)
a['fork_hinge'] = {'rotation': keys([(0, [0, 0, 0]), (.6, [0, -12, 0]), (.9, [0, 10, 0]), (1.2, [0, 10, 0]), (2.9, [0, 0, 0]), (4.1, [0, 0, 0])])}
a['trident'] = {'rotation': keys([(0, [0, 0, 0]), (.3, [0, 240, 0]), (.6, [0, 480, 0]), (.85, [0, 720, 0]), (.9, [0, 720, 0]), (4.1, [0, 720, 0])])}
for side in ('left', 'right'):
    a[side + '_tide_vent'] = {'scale': keys([(0, [1, 1, 1]), (.85, [1.25, 1.25, 1.25]), (.9, [1, 1, 1]), (4.1, [1, 1, 1])])}
a = anim('dive', 3.55)
living(a)
# Compress above the real floor. The renderer hides this magical phase from tick 9 to 29;
# the server retains the normal damage collider and permits exactly one legal emergence.
a['root'] = {'scale': keys([(0, [1, 1, 1]), (.4, [1, .08, 1]), (1.45, [1, .08, 1]), (1.5, [1, .08, 1]), (1.7, [1, 1, 1]), (3.55, [1, 1, 1])])}
a['fork_foresegment'] = {'rotation': keys([(0, [0, 0, 0]), (.35, [0, 0, -10]), (1.45, [0, 0, -10]), (1.5, [0, 0, 25]), (1.8, [0, 0, 0]), (3.55, [0, 0, 0])])}
a = anim('combo', 4.2)
living(a)
a['fork_hinge'] = {'rotation': keys([(0, [0, 0, 0]), (.5, [0, -35, 0]), (.95, [0, 18, 0]), (1.1, [0, -30, 0]), (1.55, [0, 18, 0]), (1.7, [0, -35, 0]), (2.15, [0, 15, 0]), (2.5, [0, 0, 0]), (4.2, [0, 0, 0])])}
a['fork_foresegment'] = {'rotation': keys([(0, [0, 0, 0]), (.5, [0, 0, -10]), (.95, [0, 0, 15]), (1.1, [0, 0, -10]), (1.55, [0, 0, 15]), (1.7, [0, 0, -20]), (1.95, [0, 0, 30]), (2.15, [0, 0, 5]), (2.7, [0, 0, 0]), (4.2, [0, 0, 0])])}
a['carapace'] = {'rotation': keys([(0, [0, 0, 0]), (.5, [0, 0, -2]), (.95, [0, 0, 2]), (1.55, [0, 0, 2]), (1.7, [-5, 0, 0]), (2.15, [3, 0, 0]), (2.7, [0, 0, 0]), (4.2, [0, 0, 0])])}
a['telson_tip'] = {'rotation': keys([(0, [0, 0, 0]), (1.7, [0, -15, 0]), (2.15, [0, 15, 0]), (2.7, [0, 0, 0]), (4.2, [0, 0, 0])])}
a = anim('hurt', .4)
living(a)
a['carapace'] = {'rotation': keys([(0, [0, 0, 0]), (.1, [0, 0, -4]), (.4, [0, 0, 0])])}
a['mandible'] = {'rotation': keys([(0, [0, 0, 0]), (.1, [14, 0, 0]), (.4, [0, 0, 0])])}
a = anim('death', 4)
a['trident'] = {'scale': [0, 0, 0]}
plant_rotation, plant_lift = [], []
for tick in range(9):
    t = tick / 20
    degrees = min(90, tick * 11.25)
    radians = math.radians(degrees)
    low = 13 - math.cos(radians) - 20 * math.sin(radians)
    plant_rotation.append((t, [degrees, 0, 0]))
    plant_lift.append((t, [0, max(0, -low), 0]))
plant_rotation += [(4, [90, 0, 0])]
plant_lift += [(4, [0, 7, 0])]
a['planted_trident'] = {'rotation': keys(plant_rotation), 'position': keys(plant_lift),
    'scale': keys([(0, [1, 1, 1]), (2.7, [1, 1, 1]), (3.8, [0, 0, 0]), (4, [0, 0, 0])])}
a['reef_shell'] = {'scale': keys([(0, [0, 0, 0]), (1.2, [0, 0, 0]), (1.6, [1, 1, 1]), (2.7, [1, 1, 1]), (3.8, [0, 0, 0]), (4, [0, 0, 0])])}
a['carapace'] = {'scale': keys([(0, [1, 1, 1]), (1.2, [1, 1, 1]), (1.6, [0, 0, 0]), (4, [0, 0, 0])])}
for i in range(3):
    for side in ('left', 'right'):
        a[f'{side}_leg{i}'] = {'scale': keys([(0, [1, 1, 1]), (2.7, [1, 1, 1]), (3.8, [0, 0, 0]), (4, [0, 0, 0])])}
for i in range(3):
    a[f'reef_fragment{i}'] = {'position': keys([(0, [0, 0, 0]), (2.7, [0, 0, 0]), (3.5, [(i - 1) * 8, 2, -5]), (4, [(i - 1) * 8, 2, -5])])}

geo(ID, bones, 6.4, 3.2, [0, 1, 0])
write(A / 'animations/blueprint/elite' / f'{ID}.animation.json', {'format_version': '1.8.0', 'animations': anims})
tex = Image.new('RGB', (16, 16), COLORS['white'])
d = ImageDraw.Draw(tex)
for key in ('shell', 'bronze', 'water'):
    x, y = UV[key]
    d.rectangle((x - 1, y - 1, x + 4, y + 4), fill=COLORS[key])
p = A / 'textures/entity/blueprint/elite' / f'{ID}.png'
p.parent.mkdir(parents=True, exist_ok=True)
tex.save(p)

# A three-metre column of two continuous twisting ribbons, rather than stacked floating blocks.
bones = []
bone('root')
axis = bone('water_axis', 'root', (0, 24, 0))
cube(axis, (-1, 0, -1), (2, 48, 2), 'water')
for branch in range(2):
    for i in range(8):
        ring = bone(f'water_ring{branch * 8 + i}', 'root', (0, 3 + i * 6, 0), (0, i * 45 + branch * 180, 0))
        cube(ring, (2.5, i * 6, -1.5), (3, 6 if i == 7 else 8, 3), 'water')
        if branch == 0:
            cube(ring, (4, 3 + i * 6, -1), (2, 2, 2), 'white')
geo('yasha_tidal_vortex', bones, 2, 3.2, [0, 1.5, 0])
spin = {'animation_length': 1, 'loop': True, 'bones': {}}
for i in range(16):
    spin['bones'][f'water_ring{i}'] = {'rotation': keys([(0, [0, 0, 0]), (1, [0, 360, 0])])}
write(A / 'animations/blueprint/elite/yasha_tidal_vortex.animation.json', {'format_version': '1.8.0', 'animations': {'animation.yasha_tidal_vortex.spin': spin}})

items = ('yasha_tidal_plate', 'yasha_tide_essence', 'corroded_trident_tine')
for identifier in items:
    im = Image.new('RGB', (16, 16), COLORS['white'])
    draw = ImageDraw.Draw(im)
    if identifier.endswith('plate'):
        draw.rectangle((4, 2, 11, 13), fill=COLORS['shell'])
        draw.rectangle((2, 4, 13, 11), fill=COLORS['shell'])
        draw.rectangle((4, 4, 11, 5), fill=COLORS['bronze'])
        draw.rectangle((6, 6, 9, 11), fill=COLORS['water'])
    elif identifier.endswith('essence'):
        draw.rectangle((6, 2, 9, 13), fill=COLORS['water'])
        draw.rectangle((4, 6, 11, 13), fill=COLORS['water'])
        draw.rectangle((2, 8, 13, 11), fill=COLORS['shell'])
        draw.rectangle((4, 8, 11, 11), fill=COLORS['water'])
        draw.rectangle((6, 6, 7, 9), fill=COLORS['bronze'])
    else:
        draw.rectangle((6, 2, 9, 13), fill=COLORS['bronze'])
        draw.rectangle((4, 2, 5, 5), fill=COLORS['shell'])
        draw.rectangle((10, 2, 11, 5), fill=COLORS['water'])
        draw.rectangle((6, 10, 9, 13), fill=COLORS['shell'])
    im.save(A / 'textures/item' / f'{identifier}.png')
    write(A / 'models/item' / f'{identifier}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'dynasty:item/' + identifier}})
write(A / 'models/item' / f'{ID}_spawn_egg.json', {'parent': 'minecraft:item/template_spawn_egg'})
write(DATA / 'loot_tables/entities' / f'{ID}.json', {'type': 'minecraft:entity', 'pools': [
    {'rolls': 1, 'entries': [{'type': 'minecraft:item', 'name': 'dynasty:' + identifier}]} for identifier in items]})
write(DATA / 'advancements/blueprint' / f'kill_{ID}.json', {'criteria': {'kill': {
    'trigger': 'minecraft:player_killed_entity', 'conditions': {'entity': {'type': 'dynasty:' + ID}}}}})
write(DATA / 'tags/worldgen/structure/blueprint/tide_yasha_sites.json', {'replace': False, 'values': ['minecraft:ocean_ruin_warm', 'minecraft:ocean_ruin_cold']})
write(DATA / 'recipes/blueprint/yasha_tidal_shield.json', {'type': 'minecraft:crafting_shapeless', 'ingredients': [
    {'item': 'dynasty:yasha_tidal_plate'}, {'item': 'minecraft:iron_ingot'}, {'item': 'minecraft:iron_ingot'}, {'item': 'minecraft:leather'}], 'result': {'item': 'minecraft:shield'}})
write(DATA / 'recipes/blueprint/yasha_recovered_trident.json', {'type': 'minecraft:crafting_shaped', 'pattern': ['TTT', ' S ', ' S '],
    'key': {'T': {'item': 'dynasty:corroded_trident_tine'}, 'S': {'item': 'minecraft:stick'}}, 'result': {'item': 'minecraft:trident'}})
print('Exported original yasha, seven clips, finite vortex and three usable salvage items.')

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('fubo_xunhai_yecha')

# Original MC creature shape correction, after the material export.
import runpy as _creature33_runpy
_creature33_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v33/refine.py"))["finish"]('fubo_xunhai_yecha')
