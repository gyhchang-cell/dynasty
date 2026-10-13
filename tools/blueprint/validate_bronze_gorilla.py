#!/usr/bin/env python3
"""Actual resource/source and software-envelope checks; never a Java/native acceptance claim."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import math
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[2]
A = R / 'src/main/resources/assets/dynasty'
D = R / 'docs/blueprint-cod1/evidence/bronze-gorilla-v1'
ID = 'hanshan_tongjia_juyuan'


def pairs(rows):
    d = {}
    for k, v in rows:
        assert k not in d, ('duplicate JSON key', k)
        d[k] = v
    return d


def read(p):
    return json.loads(p.read_text(), object_pairs_hook=pairs)


paths = []
counts = {}
for identifier in (ID,'gorilla_cast_boulder','gorilla_stone_fragment'):
    gp = A / f'geo/blueprint/elite/{identifier}.geo.json'
    ap = A / f'animations/blueprint/elite/{identifier}.animation.json'
    paths += [gp, ap]
    g = read(gp)['minecraft:geometry'][0]
    a = read(ap)['animations']
    bones = {b['name']: b for b in g['bones']}
    assert len(bones) == len(g['bones'])
    counts[identifier] = {'bones': len(bones), 'cuboids': sum(len(b.get('cubes', [])) for b in bones.values()), 'clips': len(a)}
    for b in bones.values():
        parent, chain = b, set()
        while parent.get('parent'):
            assert parent['name'] not in chain
            chain.add(parent['name'])
            parent = bones[parent['parent']]
        for c in b.get('cubes', []):
            assert all(v > 0 and math.isfinite(v) for v in c['size'])
            for f in c['uv'].values():
                u, v = f['uv']
                w, h = f['uv_size']
                assert all(isinstance(n, int) for n in (u, v, w, h))
                assert min(u, v) >= 0 and u + w <= 16 and v + h <= 16
    for clip, definition in a.items():
        assert clip.startswith('animation.' + identifier + '.')
        assert set(definition['bones']) <= set(bones)
        for ch in definition['bones'].values():
            for channel, track in ch.items():
                if isinstance(track, dict):
                    assert all(0 <= float(t) <= definition['animation_length'] for t in track)
                    if definition.get('loop'):
                        ordered = sorted(track, key=float)
                        delta = np.array(track[ordered[-1]]) - track[ordered[0]]
                        if channel == 'rotation':
                            delta = (delta + 180) % 360 - 180
                        assert np.allclose(delta, 0), ('loop seam', clip, channel)
    assert set(a) == ({'animation.' + ID + '.' + n for n in ('idle', 'walk', 'smash', 'leap', 'throw', 'hurt', 'death')} if identifier == ID else {'animation.'+identifier+'.spin'})

for p in [A / f'textures/entity/blueprint/elite/{ID}.png'] + [A / f'textures/item/{n}.png' for n in ('gorilla_cast_plate','gorilla_stone_chip')]:
    paths.append(p)
    im = Image.open(p).convert('RGB')
    assert im.size == (16, 16) and len(set(im.get_flattened_data())) == 4
    for y in range(16):
        for x in range(16):
            color = im.getpixel((x, y))
            if x < 2 or x > 13 or y < 2 or y > 13:
                assert color == (255, 255, 255)
            assert any(all(im.getpixel((xx, yy)) == color for xx in (sx, sx + 1) for yy in (sy, sy + 1))
                       for sx in (x - 1, x) for sy in (y - 1, y) if 0 <= sx < 15 and 0 <= sy < 15), ('smaller than 2x2 color region', p, x, y)

spec = importlib.util.spec_from_file_location('gorilla_geometry_review', R / 'tools/art/secondary-cuboid/review_models.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
r.CATEGORY = 'blueprint/elite'


def geometry(clip=None, tick=0):
    q = r.geometry(ID, clip='animation.' + ID + '.' + clip if clip else None, tick=tick)
    return [p for p in q if p[2] != 'held_rock' or clip == 'throw']


report = read(D / 'software-sampling.json')
assert report['samplesPerClip'] == 81 and len(report['clips']) == 7
assert all(c['minimumY'] >= -1e-4 for c in report['clips'].values())
assert report['clips']['walk']['minGroundedFeet'] >= 3
assert all(c['maximumY'] / 16 < 5 and c['maximumXZ'] / 16 < 4 for c in report['clips'].values())
assert 3.3<report['standVisibleHeightMetres']<3.45
for identifier,data in report['projectileSampling'].items():
    assert data['samples']==81 and data['minimumY']>=-1e-4
    assert data['maximumXZ']/16<(1.2 if identifier=='gorilla_cast_boulder' else .45)
points = np.concatenate([v for v, u, b in geometry() if b not in ('broken_bronze_pile','held_rock')])
lo, hi = points.min(0) / 16, points.max(0) / 16
report['bodyAndSupportsDimensionsMetres'] = {'min': lo.round(4).tolist(), 'max': hi.round(4).tolist(), 'size': (hi-lo).round(4).tolist()}
points = np.concatenate([v for v, u, b in geometry()])
lo, hi = points.min(0) / 16, points.max(0) / 16
report['restVisibleDimensionsMetres'] = {'min': lo.round(4).tolist(), 'max': hi.round(4).tolist(), 'size': (hi-lo).round(4).tolist()}
radius = 0
for clip, c in report['clips'].items():
    # The compact final report can be checked again without recreating hundreds of saved rows.
    length = read(A / f'animations/blueprint/elite/{ID}.animation.json')['animations']['animation.'+ID+'.'+clip]['animation_length']
    for tick in np.linspace(0, length * 20, 81):
        points = np.concatenate([v for v, u, b in geometry(clip, float(tick))])
        radius = max(radius, float(np.linalg.norm(points[:, [0, 2]], axis=1).max()) / 16)
    c.pop('samples', None)
    c['sampleCount'] = 81
report['maximumHorizontalRadiusMetres'] = round(radius, 4)
report['nativePhysicsDimensionsMetres'] = {'width':3.8,'height':3.4}
report['nativeAttackDimensionsMetres']={'smashTotalAdvance':8,'smashWidth':2,'smashImpacts':8,'fistPortForward':1.2,'perImpactFloorCells':1,'throwWidth':1.5,'fragmentWidth':.5,'fragments':3,'projectileLifeTicks':[60,30],'leapMaxDistance':12,'leapFlightTicks':24,'leapPeakAboveFloor':3,'landingRadius':4,'redWarningLastTicks':6}
report['nativeClientCullDimensionsMetres']={'width':8,'height':6,'minRelativeY':-1,'maxRelativeY':5}
report['counts'] = counts
report['physicalFlight'] = 'Server clipped movement advances actual entity position; source pose preview omits world trajectory. Native collision/gravity acceptance NOT RUN.'

data = R / 'src/main/resources/data/dynasty'
for p in [data / f'loot_tables/entities/{ID}.json', data / f'advancements/blueprint/kill_{ID}.json', data / 'tags/worldgen/structure/blueprint/battlefields.json', data / 'tags/worldgen/structure/blueprint/gorilla_sites.json', data / 'recipes/blueprint/gorilla_plate_recycle.json', data / 'recipes/blueprint/gorilla_chip_stonecutter.json']:
    read(p)
    paths.append(p)
assert read(data / f'advancements/blueprint/kill_{ID}.json')['criteria']['kill']['conditions']['entity']['type'] == 'dynasty:' + ID
for name in ('zh_cn', 'en_us'):
    language = read(A / f'lang/{name}.json')
    assert 'entity.dynasty.'+ID in language
    for item in ('gorilla_cast_plate','gorilla_stone_chip'):
        assert 'item.dynasty.' + item in language
        assert read(A / f'models/item/{item}.json')['textures']['layer0'] == 'dynasty:item/' + item
for p in [R / 'tools/blueprint/generate_bronze_gorilla.py', R / 'tools/blueprint/review_bronze_gorilla.py', Path(__file__)]:
    ast.parse(p.read_text())
    paths.append(p)
report['staticChecks'] = 'PASS_SOURCE_SOFTWARE_ONLY'
report['nativeAcceptance'] = 'NOT_RUN_USER_EXAM_JAVA_PAUSE'
report['resourceSha256'] = {p.relative_to(R).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(D / 'software-sampling.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Ape/projectile resource counts:', counts)
print('Body/support dimensions:', report['bodyAndSupportsDimensionsMetres'])
print('Full rest dimensions:', report['restVisibleDimensionsMetres'])
print('Sampled horizontal radius:', report['maximumHorizontalRadiusMetres'])
print('Seven clips x81: floor, loop seams, three grounded walking contacts and finite culling pass.')
print('16px four pure colors, 2px white margins, every color region >=2x2, integer UV and use paths pass. Java/native NOT RUN.')
