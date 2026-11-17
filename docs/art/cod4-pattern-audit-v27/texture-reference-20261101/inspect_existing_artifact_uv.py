"""Existing approved artifacts: source texture correspondence only; do not redraw."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageOps,ImageDraw
import hashlib,json
D=Path(__file__).resolve().parent;A=Path('src/main/resources/assets/dynasty');RAW=Path('build/art-reference-20261101/existing-artifacts');RAW.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def freeze(p):
 data=p.read_bytes();dst=RAW/p;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 return dict(path=str(p),frozen_copy=str(dst),sha256=sha(data))
rows=[];pngs=[]
names=['longyin_zhanma_duanyue_dao','zhanlu_rendao_bamian_jian','longyin_ground_crest','zhanlu_ceasefire_field']
for name in names:
 geo_path=A/'geo/blueprint/artifact'/f'{name}.geo.json';png_path=A/'textures/entity/blueprint/artifact'/f'{name}.png';geo=json.loads(geo_path.read_text())['minecraft:geometry'][0];im=Image.open(png_path).convert('RGBA')
 row=dict(name=name,geo=freeze(geo_path),png=freeze(png_path),atlas_dimensions=list(im.size),declared_dimensions=[geo['description']['texture_width'],geo['description']['texture_height']],bones=len(geo['bones']),cubes=0,faces=[])
 for bone in geo['bones']:
  for i,cube in enumerate(bone.get('cubes',[])):
   row['cubes']+=1
   assert isinstance(cube['uv'],dict)
   for face,uv in cube['uv'].items():
    u,v=uv['uv'];du,dv=uv['uv_size'];sx=im.width/row['declared_dimensions'][0];sy=im.height/row['declared_dimensions'][1];bounds=[min(u,u+du)*sx,min(v,v+dv)*sy,max(u,u+du)*sx,max(v,v+dv)*sy];assert all(x==int(x) for x in bounds);bounds=list(map(int,bounds))
    patch=im.crop(bounds)
    if du<0:patch=ImageOps.mirror(patch)
    if dv<0:patch=ImageOps.flip(patch)
    pix=list(patch.get_flattened_data());row['faces'].append(dict(bone=bone['name'],cube_index=i,face=face,uv=uv['uv'],uv_size=uv['uv_size'],pixel_bounds=bounds,within_atlas=(0<=bounds[0]<bounds[2]<=im.width and 0<=bounds[1]<bounds[3]<=im.height),signed_crop_rgba_sha256=sha(patch.tobytes()),visible_rgba_colors=len({p for p in pix if p[3]}),nonzero_alpha_pixels=sum(p[3]>0 for p in pix)))
 row['unique_source_pixel_rectangles']=sorted({tuple(f['pixel_bounds']) for f in row['faces']});row['face_count']=len(row['faces']);pngs.append((name+' / WORLD ATLAS',png_path));rows.append(row)
 if name in names[:2]:
  model_paths=[A/'models/item'/f'{name}{suffix}.json' for suffix in ['', '_icon','_mesh']];row['item_models']=[freeze(p) for p in model_paths];mesh=json.loads(model_paths[2].read_text());cubes=[c for b in geo['bones'] for c in b.get('cubes',[])];comparisons=[]
  assert len(cubes)==len(mesh['elements'])
  for ci,(cube,element) in enumerate(zip(cubes,mesh['elements'])):
   for face,uv in cube['uv'].items():
    m=element['faces'][face];u,v=uv['uv'];du,dv=uv['uv_size'];expected=[u*16/row['declared_dimensions'][0],v*16/row['declared_dimensions'][1],(u+du)*16/row['declared_dimensions'][0],(v+dv)*16/row['declared_dimensions'][1]]
    comparisons.append(dict(cube_flat_index=ci,face=face,item_mesh_uv=m['uv'],geo_normalized_uv=expected,same_rectangle=m['uv']==expected,mesh_texture_alias=m['texture']))
  row['item_mesh_geo_face_correspondence']=comparisons
  icon_png=A/'textures/item'/f'{name}.png';row['item_icon_png']=freeze(icon_png);pngs.append((name+' / ITEM ICON',icon_png));row['item_root_parent']=json.loads(model_paths[0].read_text()).get('parent');row['mesh_declared_textures']=mesh['textures']
canvas=Image.new('RGB',(1050,720),(59,65,69));dr=ImageDraw.Draw(canvas);dr.text((10,6),'EXISTING DYNASTY SOURCE PNGS / unchanged integer enlargement / NOT GAME / NOT NEW ART',(255,255,255))
for i,(label,p) in enumerate(pngs):
 im=Image.open(p).convert('RGBA');x=(i%3)*350;y=32+(i//3)*342;dr.text((x+8,y),label,(255,255,255));canvas.paste(im.resize((256,256),Image.Resampling.NEAREST),(x+8,y+24),im.resize((256,256),Image.Resampling.NEAREST))
sheet=RAW/'source-palettes-icons.png';canvas.save(sheet)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),purpose='Existing source UV/material region checks only; mesh cube order compared as declared, no geometry transform/game binding claim.',rows=rows,source_sheet=str(sheet),source_sheet_actually_opened=False,face_crops=sum(r['face_count'] for r in rows),item_geo_uv_comparisons=sum(len(r.get('item_mesh_geo_face_correspondence',[])) for r in rows),production_changes=0,new_reference_cases=0,
 limits='builtin/entity roots do not themselves declare runtime texture/GUI route. Exact source UV rectangles do not prove renderer lookup, 3D winding, seams, grip, scaling or gameplay. Palette-only PNG does not prove absent glyph: glyph may be geometry. Fine existing originals protected.')
(D/'existing-artifact-uv-source.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(source_faces=out['face_crops'],item_geo_face_comparisons=out['item_geo_uv_comparisons'],rectangle_mismatches=sum(not c['same_rectangle'] for r in rows for c in r.get('item_mesh_geo_face_correspondence',[])),outside_atlas=sum(not f['within_atlas'] for r in rows for f in r['faces']),new_art=0),ensure_ascii=False))
