"""Read-only face-island study. Crops are reference evidence, never game renders."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageOps

D = Path(__file__).resolve().parent
R = D.parents[3]
B = R / 'build/art-reference-20261101/uv-layers'
B.mkdir(parents=True, exist_ok=True)
models = json.loads((D/'uv-model-supplement.json').read_text())['rows']
textures = {Path(r['path']).stem:r for r in json.loads((D/'candidates.json').read_text())['rows']}
rows = []
pages = []
faces = ['north', 'south', 'east', 'west', 'up', 'down']
for model in models:
    name = Path(model['path']).stem.replace('.geo', '').replace('_armor', '')
    texture = textures[name]
    model_path = R/model['path']
    texture_path = R/texture['local_path']
    assert hashlib.sha256(model_path.read_bytes()).hexdigest() == model['sha256']
    im = Image.open(texture_path).convert('RGBA')
    cubes = [(bone, i, cube) for bone in model['bones'] for i, cube in enumerate(bone['cubes'])]
    if any(not isinstance(c['uv'], dict) for _, _, c in cubes):
        continue  # Box-UV winding not established by this study.
    for start in range(0, len(cubes), 4):
        page = Image.new('RGB', (1320, 1020), '#454b50')
        dr = ImageDraw.Draw(page)
        dr.text((8, 8), f'{name} / EXACT SIGNED PNG CROPS / NOT 3D OR GAME / page {start//4+1}', fill='white')
        sheet = B/f'{name}-{start//4+1:02}.png'
        for row_index, (bone, cube_index, cube) in enumerate(cubes[start:start+4]):
            y = 36 + row_index*242
            dr.text((8, y), f"{bone['name']} [{cube_index}] mesh {cube['size']} inflate={cube.get('inflate', 0)}", fill='white')
            entry = {'model':model['path'], 'model_sha256':model['sha256'],
                'texture':texture['local_path'], 'texture_sha256':hashlib.sha256(texture_path.read_bytes()).hexdigest(),
                'model_source_url':model['source_url'], 'texture_source_url':texture['source_url'],
                'bone':bone['name'], 'cube_index':cube_index, 'mesh_size':cube['size'],
                'inspection_sheet':str(sheet.relative_to(R)), 'faces':[]}
            for j, face in enumerate(faces):
                x = j*220
                dr.text((x+8, y+20), face, fill='white')
                uv = cube['uv'].get(face)
                if not uv:
                    dr.text((x+8, y+55), 'not defined on cube', fill='#c5c5c5')
                    continue
                u, v = uv['uv']; du, dv = uv['uv_size']
                bounds = [min(u,u+du),min(v,v+dv),max(u,u+du),max(v,v+dv)]
                sample = {'face':face,'uv':[u,v],'uv_size':[du,dv], 'bounds':bounds,
                    'flip_u_for_sample':du<0,'flip_v_for_sample':dv<0}
                if du == 0 or dv == 0 or not all(float(a).is_integer() for a in bounds):
                    sample['status'] = 'DEGENERATE_OR_FRACTIONAL_NOT_RESAMPLED'
                    dr.text((x+8,y+55),sample['status'][:25],fill='white')
                else:
                    bounds = list(map(int,bounds))
                    assert 0 <= bounds[0] < bounds[2] <= im.width and 0 <= bounds[1] < bounds[3] <= im.height
                    patch = im.crop(bounds)
                    if du < 0: patch = ImageOps.mirror(patch)
                    if dv < 0: patch = ImageOps.flip(patch)
                    factor = max(1, min(180//patch.width, 150//patch.height))
                    preview = patch.resize((patch.width*factor,patch.height*factor),Image.Resampling.NEAREST)
                    # Checker remains visible wherever the unchanged source is transparent.
                    for cy in range(150//10):
                        for cx in range(18):
                            shade = '#60666b' if (cx+cy)%2 else '#555b60'
                            dr.rectangle((x+15+cx*10,y+42+cy*10,x+24+cx*10,y+51+cy*10),fill=shade)
                    page.paste(preview,(x+15,y+42),preview)
                    sample.update(status='SIGNED_INTEGER_CROP', crop_rgba_sha256=hashlib.sha256(patch.tobytes()).hexdigest(),
                        sampled_pixels=patch.width*patch.height, opaque_pixels=sum(a>0 for a in patch.getchannel('A').getdata()))
                dr.text((x+8,y+199),f'UV {u},{v} + {du},{dv}',fill='white')
                entry['faces'].append(sample)
            rows.append(entry)
        page.save(sheet)
        pages.append(str(sheet.relative_to(R)))
(D/'uv-layer-crops.json').write_text(json.dumps({'purpose':'Actual per-face reference island study; not model pose or runtime proof',
    'new_design_credit':0,'production_changes':0,'manual_review_complete':False,
    'box_uv_excluded':'paladin_chestplate: winding not independently established',
    'models':len(set(r['model'] for r in rows)), 'cubes':len(rows), 'sheets':pages,'rows':rows},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'models':len(set(r['model'] for r in rows)),'cubes':len(rows),'pages':pages,'faces':sum(len(r['faces']) for r in rows)}))
