"""Exact per-face reference crops. No source image edits; no runtime rendering claims."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageOps

D = Path(__file__).resolve().parent
R = D.parents[3]
B = R/'build/art-reference-20261101'

models = json.loads((D/'uv-model-supplement.json').read_text())['rows']
candidates = json.loads((D/'candidates.json').read_text())['rows']
textures = {Path(r['path']).stem:r for r in candidates}
report = []
for row in models:
    name = Path(row['path']).stem.replace('.geo','').replace('_armor','')
    tex = textures[name]
    im = Image.open(R/tex['local_path']).convert('RGBA')
    desc = row['description']
    assert list(im.size) == [desc['texture_width'], desc['texture_height']]
    page = Image.new('RGB',(1200,600),'#41474c')
    dr = ImageDraw.Draw(page)
    dr.text((8,8), f'REFERENCE UV CROPS / {name} / signed source UVs / NOT 3D or in-game',fill='white')
    cube = next(b for b in row['bones'] if b['name']=='armorBody')['cubes'][0]
    entry = {'model':row['path'], 'texture':tex['local_path'], 'source_model_url':row['source_url'],
             'source_texture_url':tex['source_url'], 'bone':'armorBody','cube_index':0,
             'mesh_size':cube['size'], 'raw_uv':cube['uv'], 'face_samples':[],
             'reference_credit_added':0,
             'not_proven':'Full model, rotations, front-facing world orientation, game animation and shader are not verified by flat UV samples.'}
    if not isinstance(cube['uv'],dict):
        entry['status']='BOX_UV_RECORDED_NOT_EXPANDED'
        entry['reason']='Keep raw box-UV origin/size; do not pretend this script has verified format-specific winding.'
        report.append(entry)
        continue
    for i,face in enumerate(['north','south','east','west','up','down']):
        uv = cube['uv'].get(face)
        x=(i%3)*400;y=35+(i//3)*280
        dr.text((x+8,y),face,fill='white')
        if not uv:
            dr.text((x+8,y+25),'not present on this cube / no bug inferred',fill='white')
            continue
        u,v=uv['uv'];du,dv=uv['uv_size']
        bounds=[min(u,u+du),min(v,v+dv),max(u,u+du),max(v,v+dv)]
        assert all(float(z).is_integer() for z in bounds)
        bounds=list(map(int,bounds))
        assert 0<=bounds[0]<bounds[2]<=im.width and 0<=bounds[1]<bounds[3]<=im.height
        patch=im.crop(bounds)
        if du<0:patch=ImageOps.mirror(patch)
        if dv<0:patch=ImageOps.flip(patch)
        factor=max(1,min(300//patch.width,190//patch.height))
        preview=patch.resize((patch.width*factor,patch.height*factor),Image.Resampling.NEAREST)
        page.paste(preview,(x+40,y+23),preview)
        dr.text((x+8,y+225),f'uv {u},{v}   size {du},{dv}',fill='white')
        entry['face_samples'].append({'face':face,'uv':[u,v],'uv_size':[du,dv],
             'pixel_bounds':bounds,'flip_u_for_sample':du<0,'flip_v_for_sample':dv<0})
    path=B/f'uv-face-{name}.png';page.save(path)
    entry.update(status='EXACT_SIGNED_FACE_CROPS', inspection_sheet=str(path.relative_to(R)))
    report.append(entry)
(D/'uv-face-correspondence.json').write_text(json.dumps({'policy':'Supplementary analysis only; zero new design-reference credit and zero production changes','rows':report},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'models':len(report),'per_face_pages':sum(r['status']=='EXACT_SIGNED_FACE_CROPS' for r in report),'new_design_credit':0}))
