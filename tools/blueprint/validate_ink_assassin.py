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
D = R / 'docs/blueprint-cod1/evidence/ink-assassin-v1'
ID = 'mojia_jueying_cike'


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
for identifier in (ID, 'assassin_ink_bamboo_anchor', 'assassin_finite_ink_cloud'):
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
    assert set(a) == ({'animation.' + ID + '.' + n for n in ('idle', 'walk', 'stealth', 'field', 'mist', 'hurt', 'death')} if identifier == ID else {'animation.' + identifier + '.idle'})

for p in [A / f'textures/entity/blueprint/elite/{ID}.png'] + [A / f'textures/item/{n}.png' for n in ('ink_crystal_shard', 'waterproof_ink_silk', 'hollow_ink_bamboo')]:
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

spec = importlib.util.spec_from_file_location('ink_geometry_review', R / 'tools/art/secondary-cuboid/review_models.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
r.CATEGORY = 'blueprint/elite'


def geometry(clip=None, tick=0):
    q = r.geometry(ID, clip='animation.' + ID + '.' + clip if clip else None, tick=tick)
    return [p for p in q if p[2] != 'death_wash' or clip == 'death']


report = read(D / 'software-sampling.json')
assert report['samplesPerClip'] == 81 and len(report['clips']) == 7
assert all(c['minimumY'] >= -1e-4 for c in report['clips'].values())
assert report['clips']['walk']['minGroundedSkids'] >= 2
assert all(c['maximumY'] / 16 < 1.4 and c['maximumXZ'] / 16 < 2.4 for c in report['clips'].values())
points = np.concatenate([v for v, u, b in geometry() if not b.endswith(('reverse_dagger', 'dagger_carriage', 'silk_tail0', 'silk_tail1'))])
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
report['nativePhysicsDimensionsMetres'] = {'width': 1.4, 'height': .8}
report['nativeAttackDimensionsMetres'] = {'backEmergenceBehindTarget': 1, 'maximumBlink': 8, 'fieldHalfWidth': 2, 'fourDiagonalPasses': 4, 'fieldActualContactRadius': 1.1, 'fieldMaximumLivingVictimsPerContact': 12, 'cloudRadius': 1.5, 'cloudFuseTicks': 20, 'cloudMaximumLifeTicks': 100, 'blindnessTicks': 100, 'breathReach': 6, 'breathAngleDegrees': 60}
report['nativeClientCullDimensionsMetres'] = {'width': 4.8, 'height': 2, 'minRelativeY': -.6, 'maxRelativeY': 1.4}
report['counts'] = counts
report['concealment'] = {'hiddenTicks': [1,79], 'ordinaryDamageColliderRetained': True, 'sourceNote': 'Native visibility, trails, blink, path and shield acceptance NOT RUN. Software previews inspect source fold/blade poses only.'}
spike_bounds=[]
for tick in np.linspace(0,20,81):
    p=np.concatenate([v for v,u,b in r.geometry('assassin_ink_bamboo_anchor',clip='animation.assassin_ink_bamboo_anchor.idle',tick=float(tick))]);assert p[:,1].min()>=0 and p[:,1].max()<27 and np.abs(p[:,[0,2]]).max()<=2
    spike_bounds.append(p.max(0))
report['anchorSourceMaximumMetres']=(np.max(spike_bounds,axis=0)/16).round(4).tolist()
pellet_bounds=[]
for tick in np.linspace(0,20,81):
    p=np.concatenate([v for v,u,b in r.geometry('assassin_finite_ink_cloud',clip='animation.assassin_finite_ink_cloud.idle',tick=float(tick))]);assert p[:,1].min()>=0 and p[:,1].max()<=6 and np.abs(p[:,[0,2]]).max()<5
    pellet_bounds.append(p.max(0))
report['pelletSourceMaximumMetres']=(np.max(pellet_bounds,axis=0)/16).round(4).tolist()

data = R / 'src/main/resources/data/dynasty'
for p in [data / f'loot_tables/entities/{ID}.json', data / f'advancements/blueprint/kill_{ID}.json', data / 'tags/worldgen/structure/blueprint/mechanist_sites.json', data / 'recipes/blueprint/ink_crystal_dye.json', data / 'recipes/blueprint/ink_silk_string.json', data / 'loot_tables/entities/assassin_ink_bamboo_anchor.json']:
    read(p)
    paths.append(p)
assert read(data / f'advancements/blueprint/kill_{ID}.json')['criteria']['kill']['conditions']['entity']['type'] == 'dynasty:' + ID
for name in ('zh_cn', 'en_us'):
    language = read(A / f'lang/{name}.json')
    assert 'entity.dynasty.' + ID in language
    for item in ('ink_crystal_shard', 'waterproof_ink_silk', 'hollow_ink_bamboo'):
        assert 'item.dynasty.' + item in language
        assert read(A / f'models/item/{item}.json')['textures']['layer0'] == 'dynasty:item/' + item
for p in [R / 'tools/blueprint/generate_ink_assassin.py', R / 'tools/blueprint/review_ink_assassin.py', Path(__file__)]:
    ast.parse(p.read_text())
    paths.append(p)
report['staticChecks'] = 'PASS_SOURCE_SOFTWARE_ONLY'
report['nativeAcceptance'] = 'NOT_RUN_USER_EXAM_JAVA_PAUSE'
report['resourceSha256'] = {p.relative_to(R).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(D / 'software-sampling.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Resource counts:', counts)
print('Body/support dimensions:', report['bodyAndSupportsDimensionsMetres'])
print('Full rest dimensions:', report['restVisibleDimensionsMetres'])
print('Sampled horizontal radius:', report['maximumHorizontalRadiusMetres'])
print('Seven clips x81: floor, loop seams, two planted sliding runners and finite culling pass.')
print('16px four pure colors, 2px white margins, every color region >=2x2, integer UV and use paths pass. Java/native NOT RUN.')
