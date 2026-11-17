"""Inspect original Geo-model PNGs on their literal UVs, offline only.

This renders source body surfaces, not equipment layers, particles, animation,
or an in-game scene. External artwork stays in the private build cache.
"""
from pathlib import Path
import hashlib, importlib.util, json, math, sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/art/bestiary-v41'))
spec = importlib.util.spec_from_file_location('bestiary_reference_raster', ROOT / 'tools/art/bestiary-v41/review.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)
from build_models import face_rects

CACHE = ROOT / 'build/bestiary-v43/humanoid-candidates'
SOURCE = ROOT / 'build/bestiary-v43/references/iron431__Irons-Spells-n-Spellbooks__1.20.1-legacy'


def quads(path, atlas):
    geo = json.loads(path.read_text())['minecraft:geometry'][0]
    bones = {b['name']: b for b in geo['bones']}
    world, stats = {}, dict(bones=len(bones), textured_cubes=0, empty_uv_cubes_skipped=0,
                           zero_volume_cubes_skipped=0, textured_faces=0)
    def transform(name):
        if name in world:
            return world[name]
        bone = bones[name]
        pivot = np.array(bone.get('pivot', [0, 0, 0]), dtype=float)
        parent = bone.get('parent')
        delta = pivot - np.array(bones.get(parent, {}).get('pivot', [0, 0, 0]))
        delta[1] *= -1
        rot = np.radians(bone.get('rotation', [0, 0, 0]))
        world[name] = (transform(parent) if parent else np.eye(4)) @ preview.matrix(delta, rot)
        return world[name]
    output = []
    desc = geo['description']
    uv_scale = np.array([atlas.width / desc['texture_width'], atlas.height / desc['texture_height']])
    for name, bone in bones.items():
        for cube in bone.get('cubes', []):
            uv = cube.get('uv')
            if not uv:
                stats['empty_uv_cubes_skipped'] += 1
                continue
            if any(s <= 0 for s in cube['size']):
                stats['zero_volume_cubes_skipped'] += 1
                continue
            pivot = np.array(bone.get('pivot', [0, 0, 0]), dtype=float)
            cp = np.array(cube.get('pivot', pivot), dtype=float)
            delta = cp - pivot
            delta[1] *= -1
            matrix = transform(name) @ preview.matrix(delta, np.radians(cube.get('rotation', [0, 0, 0])))
            size = np.array(cube['size'], dtype=float)
            origin = np.array(cube['origin'], dtype=float) - cp
            origin[1] = -origin[1] - size[1]
            inflate = cube.get('inflate', 0)
            points = preview.V * (size + 2 * inflate) + origin - inflate
            points = points @ matrix[:3, :3].T + matrix[:3, 3]
            points[:, 1] *= -1
            rects = face_rects(dict(uv=uv, size=size)) if isinstance(uv, list) else None
            stats['textured_cubes'] += 1
            for face, indices in preview.POLYS.items():
                if rects:
                    u, v, w, h = rects[face]
                    if face == 'down':
                        v += h
                        h = -h
                elif face in uv:
                    data = uv[face]
                    u, v = data['uv']
                    w, h = data['uv_size']
                else:
                    continue
                tc = np.array([[u+w, v], [u, v], [u, v+h], [u+w, v+h]]) * uv_scale
                if cube.get('mirror'):
                    tc[:, 0] = tc[:, 0].min() + tc[:, 0].max() - tc[:, 0]
                output.append((points[indices], tc, name))
                stats['textured_faces'] += 1
    return output, stats


def main():
    candidates = json.loads((CACHE / 'candidates.json').read_text())['items']
    report = []
    out = CACHE / 'textured-geo'
    out.mkdir(exist_ok=True)
    for row in candidates:
        if row['repo'] != 'iron431/Irons-Spells-n-Spellbooks':
            continue
        geo_url = next((u for u in row['construction_sources'] if u.endswith('.geo.json')), None)
        if not geo_url:
            continue
        path = SOURCE / geo_url.split('/'+row['commit']+'/')[1]
        texture = SOURCE / row['texture_source'].split('/'+row['commit']+'/')[1]
        atlas = Image.open(texture).convert('RGBA')
        q, stats = quads(path, atlas)
        slug = row['identity'].split(':')[-1]
        # Fit the camera to the model, with one fixed scale across its four
        # views. This is source-study framing, not a game-size comparison.
        points = np.concatenate([v for v, _, _ in q])
        midpoint = (points.min(axis=0) + points.max(axis=0)) / 2
        offset = np.array([0, 12, 5]) - midpoint
        q = [(vertices + offset, tc, bone) for vertices, tc, bone in q]
        points += offset
        scale = 12.0
        for angle in (0, 45, 90, 180):
            a, e = math.radians(angle), math.radians(9)
            right = np.array([math.cos(a), 0, math.sin(a)])
            toward = np.array([math.sin(a)*math.cos(e), math.sin(e), -math.cos(a)*math.cos(e)])
            up = -np.cross(toward, right)
            span = np.ptp(points @ np.vstack((right, up)).T, axis=0)
            scale = min(scale, 410 / max(span[0], 1), 450 / max(span[1], 1))
        views = []
        for label, angle, mode in [('front', 0, 'unlit'), ('45', 45, 'lit'), ('side', 90, 'lit'), ('back', 180, 'unlit')]:
            file = out / (slug + '-' + label + '.png')
            preview.raster(q, atlas, yaw=angle, size=(480, 540), scale=scale, mode=mode).save(file)
            views.append(dict(view=label, mode=mode, path=str(file.relative_to(ROOT)), sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
        report.append(dict(identity=row['identity'], geo_source=geo_url, texture_source=row['texture_source'],
                           geometry=stats, views=views, source_bounds=[list(x) for x in (points.min(axis=0)-offset, points.max(axis=0)-offset)],
                           camera_pixels_per_model_unit=scale,
                           limits='Body-texture UV study only. Equipment items/armour layers, runtime hiding, animation and effects are not reconstructed. Not a game capture.'))
    (out / 'report.json').write_text(json.dumps(dict(items=report, count=len(report),
        external_assets_exported_to_runtime=False), ensure_ascii=False, indent=2)+'\n')
    print(f'{len(report)} source geometry/PNG studies, {sum(len(r["views"]) for r in report)} offline views; no Java/game launched')


if __name__ == '__main__':
    main()
