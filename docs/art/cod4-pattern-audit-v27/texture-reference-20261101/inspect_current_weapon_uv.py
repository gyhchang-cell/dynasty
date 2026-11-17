"""Read-only current model/PNG binding measurements; no model edits or runtime claims."""
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[3]
A = R / 'src/main/resources/assets'
mapping_path = D.parent / 'identity-chapter-mapping-20261030.json'
mapping = json.loads(mapping_path.read_text())

def resource(rid, category, suffix):
    ns, rel = rid.split(':', 1)
    return A / ns / category / (rel + suffix)

rows = []
for weapon in [r for r in mapping['rows'] if r['kind'] == 'weapon']:
    base = R / next(a['path'] for a in weapon['assets'] if '/models/item/' in a['path'])
    base_doc = json.loads(base.read_text())
    models = [(base, None)] + [(resource(o['model'], 'models', '.json'), o['predicate']) for o in base_doc.get('overrides', [])]
    for model, predicate in models:
        m = json.loads(model.read_text())
        layers = dict(m.get('textures', {}))
        resolved = {}
        for key, value in layers.items():
            seen = set()
            while value.startswith('#') and value[1:] in layers and value not in seen:
                seen.add(value); value = layers[value[1:]]
            if not value.startswith('#'):
                resolved[key] = value
        tex_id = resolved.get('layer0')
        if not tex_id:
            rows.append(dict(weapon=weapon['id'], model=str(model.relative_to(R)), status='PENDING_INHERITED_TEXTURE_RESOLUTION'))
            continue
        texture = resource(tex_id, 'textures', '.png')
        im = Image.open(texture).convert('RGBA')
        faces = []; outside = []; transparent_edge_samples = 0; edge_samples = 0
        for i, element in enumerate(m.get('elements', [])):
            for face, value in element.get('faces', {}).items():
                uv = value.get('uv')
                if uv is None:
                    continue
                if any(not math.isfinite(c) or c < 0 or c > 16 for c in uv):
                    outside.append(dict(element=i, face=face, uv=uv))
                faces.append(uv)
                if face in ['east', 'west', 'up', 'down'] and value['texture'] == '#layer0':
                    edge_samples += 1
                    x = max(0, min(im.width-1, int((uv[0]+uv[2]) / 32 * im.width)))
                    y = max(0, min(im.height-1, int((uv[1]+uv[3]) / 32 * im.height)))
                    transparent_edge_samples += im.getpixel((x,y))[3] == 0
        first = m.get('elements', [{}])[0]
        alphas = im.getchannel('A')
        rows.append(dict(weapon=weapon['id'], name=weapon['name'], predicate=predicate,
            model=str(model.relative_to(R)), model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
            png=str(texture.relative_to(R)), png_sha256=hashlib.sha256(texture.read_bytes()).hexdigest(),
            original_png_size=list(im.size), alpha_bbox=alphas.getbbox(),
            elements=len(m.get('elements', [])), explicit_face_uvs=len(faces),
            primary_front_back_faces=first.get('faces', {}),
            uv_unit='Minecraft item model 0..16; actual PNG pixel coordinate = UV * image dimension /16',
            reversed_axes_are_recorded_not_classified_as_bugs=True,
            outside_0_16=outside, edge_midpoint_samples=edge_samples,
            completely_transparent_edge_midpoint_samples=transparent_edge_samples,
            status='STATIC_BINDING_MEASURED_NOT_RUNTIME_ACCEPTED',
            limit='Midpoint alpha only does not prove full-face winding, mip/filter seams, grip, pose, animation, inventory scale or correct lettering from both sides.'))
out = dict(recorded_at=datetime.now(timezone.utc).isoformat(),
    mapping_sha256=hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
    weapon_ids=10, model_states_measured=len(rows), production_edits=0, visual_reference_credit=0,
    finding_zh='现有平面正背面之外还有许多按轮廓构建的侧边面；后续贴图若改透明轮廓，不能只覆盖 PNG 就默认旧侧边仍匹配。双弓各有三个独立拉弦模型/贴图状态。此轮只记录约束，不改精致原稿或模型。',
    rows=rows)
(D/'current-weapon-uv-bindings.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(dict(model_states=len(rows), outside_uv_rows=sum(bool(r.get('outside_0_16')) for r in rows),
    transparent_edge_midpoints=sum(r.get('completely_transparent_edge_midpoint_samples',0) for r in rows), production_changes=0, reference_credit=0)))
