"""Omit only faces completely occluded by another cuboid on the SAME bone.

Never changes a cuboid, joint, transform, UV on a surviving face or animation.
Rotated/inflated cubes are excluded. This proof remains valid during animation
because the occluder and the covered face share the exact bone transform.
"""
import copy
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ASSET = REPO / 'src/main/resources/assets/dynasty'
IDS = ('river_imp', 'tree_spirit', 'locust_swarm')
# BakedModelFactory mirrors geometry X. With per-face UV (mirror=false),
# Direction.EAST is the RAW minimum-X plane, WEST the raw maximum-X plane.
FACES = {'east': (0, 0, -1), 'west': (0, 1, 1),
         'down': (1, 0, -1), 'up': (1, 1, 1),
         'north': (2, 0, -1), 'south': (2, 1, 1)}

def eligible(cube):
    return not cube.get('inflate', 0) and not cube.get('mirror', False) and not any(cube.get('rotation', [0, 0, 0])) and all(s > 0 for s in cube['size'])

def cull(geo):
    changes = []
    for bone in geo['minecraft:geometry'][0]['bones']:
        if bone.get('inflate', 0):
            continue
        cubes = bone.get('cubes', [])
        for i, cube in enumerate(cubes):
            if not eligible(cube) or not isinstance(cube['uv'], dict):
                continue
            lo = cube['origin']; hi = [a + s for a, s in zip(lo, cube['size'])]
            for face, (axis, edge, sign) in FACES.items():
                if face not in cube['uv'] or len(cube['uv']) <= 1:
                    continue
                plane = (hi if edge else lo)[axis]
                for j, other in enumerate(cubes):
                    if i == j or not eligible(other):
                        continue
                    ol = other['origin']; oh = [a + s for a, s in zip(ol, other['size'])]
                    # A positive thickness must cover the outward side. No gaps,
                    # coplanar outer faces, partial coverage or cross-bone tests.
                    inside = ol[axis] <= plane < oh[axis] if sign > 0 else ol[axis] < plane <= oh[axis]
                    if inside and all(ol[k] <= lo[k] and oh[k] >= hi[k] for k in range(3) if k != axis):
                        changes.append({'bone': bone['name'], 'cube': i, 'face': face, 'occluderCube': j})
                        del cube['uv'][face]
                        break
    return changes

def geometry_without_uv(geo):
    g = copy.deepcopy(geo)
    for b in g['minecraft:geometry'][0]['bones']:
        for c in b.get('cubes', []):
            c.pop('uv')
    return g

def apply_export(id, geo):
    return cull(geo) if id in IDS else []

def main():
    out = REPO / 'docs/art/secondary-cuboid-v1/face-cull-v1'
    (out / 'before').mkdir(parents=True, exist_ok=True)
    records = {}
    previous = json.loads((out / 'occlusion-proof.json').read_text()) if (out / 'occlusion-proof.json').exists() else {}
    for id in IDS:
        path = ASSET / f'geo/secondary/{id}.geo.json'
        before = path.read_bytes(); original = json.loads(before)
        backup = out / f'before/{id}.geo.json'
        if backup.exists():
            original = json.loads(backup.read_bytes())
        else:
            backup.write_bytes(before)
        geo = copy.deepcopy(original); removed = cull(geo)
        assert geometry_without_uv(original) == geometry_without_uv(geo)
        for b, ob in zip(geo['minecraft:geometry'][0]['bones'], original['minecraft:geometry'][0]['bones']):
            for c, oc in zip(b.get('cubes', []), ob.get('cubes', [])):
                assert c['uv'] and all(v == oc['uv'][f] for f, v in c['uv'].items())
        data = (json.dumps(geo, indent=2) + '\n').encode()
        assert before == backup.read_bytes() or before == data or sha_before(before) == previous.get(id, {}).get('afterSha256'), 'Concurrent/unexpected art edit: ' + id
        path.write_bytes(data)
        count = lambda g: sum(len(c['uv']) for b in g['minecraft:geometry'][0]['bones'] for c in b.get('cubes', []))
        records[id] = {'beforeSha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
                       'afterSha256': hashlib.sha256(data).hexdigest(), 'facesBefore': count(original),
                       'facesAfter': count(geo), 'removed': removed,
                       'cuboids': sum(len(b.get('cubes', [])) for b in geo['minecraft:geometry'][0]['bones']),
                       'geometryAndBonesIdentical': True,
                       'unchangedResources': {kind: hashlib.sha256((ASSET / rel).read_bytes()).hexdigest() for kind, rel in
                         [('animation', f'animations/secondary/{id}.animation.json'), ('texture', f'textures/entity/secondary/{id}.png')]}}
    (out / 'occlusion-proof.json').write_text(json.dumps(records, indent=2) + '\n')
    print({id: (r['facesBefore'], r['facesAfter']) for id, r in records.items()})

def sha_before(data):
    return hashlib.sha256(data).hexdigest()

if __name__ == '__main__':
    main()
