"""Freeze existing workshop texture declarations, without editing production or Java."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw
import hashlib, json, zipfile, io, math

D = Path(__file__).resolve().parent
R = D.parents[3]
A = R / 'src/main/resources/assets/dynasty'
OUT = R / 'build/art-reference-20261101/existing-workshops'
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda data: hashlib.sha256(data).hexdigest()

def freeze(path):
    data = path.read_bytes()
    dst = OUT / path.relative_to(R)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return dict(path=str(path.relative_to(R)), frozen_copy=str(dst.relative_to(R)), sha256=sha(data))

names = ['marrow_vat', 'essence_condenser', 'jade_mending_forge', 'vitality_shrine',
         'hide_stretcher', 'herbal_basin', 'lapidary_bench', 'ember_brazier']
rows = []
prior = [r for p in D.glob('review-batch-*.json') for r in json.loads(p.read_text())['rows']]
client = next(Path(r['jar']) for r in prior if Path(r.get('jar', '')).name == 'client.jar')
client_sha = sha(client.read_bytes())
images = {}
for i, name in enumerate(names):
    block_path = A / 'models/block' / (name + '.json')
    item_path = A / 'models/item' / (name + '.json')
    state_path = A / 'blockstates' / (name + '.json')
    block = json.loads(block_path.read_text())
    item = json.loads(item_path.read_text())
    state = json.loads(state_path.read_text())
    texture_rows = []
    for texture in sorted({v for v in block.get('textures', {}).values() if not v.startswith('#')}):
        namespace, resource = texture.split(':', 1)
        p = A.parent / namespace / 'textures' / (resource + '.png')
        if p.is_file():
            source = freeze(p)
            data = p.read_bytes()
        else:
            assert namespace == 'minecraft', 'Unresolved non-vanilla resource'
            entry = 'assets/minecraft/textures/' + resource + '.png'
            with zipfile.ZipFile(client) as z:
                data = z.read(entry)
            dst = OUT / 'vanilla-primary' / entry
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            source = dict(jar=str(client), jar_sha256=client_sha, entry=entry,
                frozen_copy=str(dst.relative_to(R)), sha256=sha(data))
        im = Image.open(io.BytesIO(data)).convert('RGBA')
        pixels = list(im.get_flattened_data())
        texture_rows.append(dict(resource=texture, source=source, dimensions=list(im.size),
            visible_rgba_colors=len({p for p in pixels if p[3]}),
            partial_alpha_pixels=sum(0 < p[3] < 255 for p in pixels),
            alpha_bbox=im.getchannel('A').getbbox()))
        images[texture] = im
    faces = [f for element in block.get('elements', []) for f in element.get('faces', {}).values()]
    gui_candidates = sorted(str(p.relative_to(R)) for p in (A / 'textures/gui').rglob('*') if p.is_file() and name in p.name)
    rows.append(dict(id=name, sources=[freeze(block_path), freeze(item_path), freeze(state_path)],
        item_parent=item.get('parent'), item_has_own_textures='textures' in item,
        block_texture_aliases=block.get('textures', {}),
        state_model_declarations=sorted({v['model'] for v in state.get('variants', {}).values()}),
        block_elements=len(block.get('elements', [])), declared_faces=len(faces),
        faces_without_explicit_uv=sum('uv' not in f for f in faces),
        explicit_face_uv=[f['uv'] for f in faces if 'uv' in f], textures=texture_rows,
        dedicated_gui_filename_matches=gui_candidates,
        limits='Source JSON declarations only. Omitted UV uses loader defaults; not independently unfolded here. No Java/runtime GUI route or state overlay inference.'))

sheet = OUT / 'source-textures.png'
canvas = Image.new('RGB', (1000, 42 + 260 * math.ceil(len(images) / 3)), (65, 70, 74))
draw = ImageDraw.Draw(canvas)
draw.text((12, 8), 'EXISTING PRIMARY PNGs / integer enlargement / NOT GAME / NO NEW ART', fill='white')
for i, (texture, im) in enumerate(images.items()):
    x, y = 12 + (i % 3) * 330, 42 + (i // 3) * 260
    draw.text((x, y), texture + ' / ' + str(im.size), fill='white')
    scale = min(224 // im.width, 224 // im.height)
    assert scale >= 1, 'Never shrink a source to fit this proof sheet'
    enlarged = im.resize((im.width * scale, im.height * scale), Image.Resampling.NEAREST)
    canvas.paste(enlarged, (x, y + 22), enlarged)
canvas.save(sheet)
result = dict(recorded_at=datetime.now(timezone.utc).isoformat(), rows=rows,
    sheet=str(sheet.relative_to(R)), sheet_actually_opened=False,
    distinct_pngs=len(images), production_changes=0, new_reference_credit=0, game_starts=0,
    limitation='Eight existing machines, not eight new art examples. No named GUI PNG does not prove GUI absent. Same state model does not prove absence of dynamic effects.')
(D / 'existing-workshop-material-source.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(rows=len(rows), faces=sum(r['declared_faces'] for r in rows), sheet=result['sheet']), ensure_ascii=False))
