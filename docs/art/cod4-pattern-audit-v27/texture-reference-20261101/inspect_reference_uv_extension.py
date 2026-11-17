"""Read unchanged source faces from three pinned local reference models, not new art."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image,ImageDraw,ImageOps
from collect import ROOT,OUT,RAW

jar=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods/[Iron的法术与魔法书] irons_spellbooks-1.20.1-3.15.6.jar')
archive_sha=hashlib.sha256(jar.read_bytes()).hexdigest()
prior=json.loads((OUT/'candidates.json').read_text())['rows']
folder=RAW/'uv-extension';folder.mkdir(parents=True,exist_ok=True)
sources=[];crops=[];sheets=[]
with zipfile.ZipFile(jar) as z:
 for name in ['archevoker','pyromancer','netherite']:
  model_entry=f'assets/irons_spellbooks/geo/{name}_armor.geo.json'
  png_entry=f'assets/irons_spellbooks/textures/models/armor/{name}.png'
  model_data=z.read(model_entry);png_data=z.read(png_entry)
  geometry=json.loads(model_data)['minecraft:geometry'][0]
  im=Image.open(io.BytesIO(png_data)).convert('RGBA')
  model_path=folder/(name+'.geo.json');model_path.write_bytes(model_data)
  png_path=folder/(name+'.png');png_path.write_bytes(png_data)
  old=next(r for r in prior if Path(r['path']).stem==name)
  assert old['sha256']==hashlib.sha256(png_data).hexdigest()
  assert im.size==(geometry['description']['texture_width'],geometry['description']['texture_height'])
  cubes=[(bone,i,cube) for bone in geometry['bones'] for i,cube in enumerate(bone.get('cubes',[]))]
  assert all(isinstance(c['uv'],dict) for _,_,c in cubes)
  src=dict(name=name,jar=str(jar),jar_sha256=archive_sha,
   model_entry=model_entry,model_local=str(model_path.relative_to(ROOT)),model_sha256=hashlib.sha256(model_data).hexdigest(),
   png_entry=png_entry,png_local=str(png_path.relative_to(ROOT)),png_sha256=hashlib.sha256(png_data).hexdigest(),
   prior_reference_id=old['reference_id'],prior_local_png=old['local_path'],prior_exact_png_equal=True,
   description=geometry['description'],cubes=len(cubes),new_design_credit=0,
   binding_limit='Same archive, matching documented resource names and exact atlas size; no Java slot/renderer binding or runtime proof.')
  sources.append(src)
  for start in range(0,len(cubes),4):
   sheet=folder/f'{name}-{start//4+1:02}.png'
   page=Image.new('RGB',(1320,1020),'#454b50');dr=ImageDraw.Draw(page)
   dr.text((8,8),name+' / EXACT SOURCE SIGNED UV CROPS / NOT 3D OR GAME',fill='white')
   for ri,(bone,ci,cube) in enumerate(cubes[start:start+4]):
    y=36+ri*242
    dr.text((8,y),f"{bone['name']}[{ci}] size={cube['size']} inflate={cube.get('inflate',0)} rot={cube.get('rotation',[])}",fill='white')
    row=dict(source_name=name,bone=bone['name'],cube_index=ci,cube_size=cube['size'],
     model_sha256=src['model_sha256'],texture_sha256=src['png_sha256'],inspection_sheet=str(sheet.relative_to(ROOT)),faces=[])
    for j,face_name in enumerate(['north','south','east','west','up','down']):
     x=j*220;dr.text((x+8,y+20),face_name,fill='white')
     uv=cube['uv'].get(face_name)
     if uv is None:
      dr.text((x+8,y+55),'NOT DEFINED ON THIS CUBE',fill='#dddddd');continue
     u,v=uv['uv'];du,dv=uv['uv_size'];bounds=[min(u,u+du),min(v,v+dv),max(u,u+du),max(v,v+dv)]
     face=dict(face=face_name,uv=[u,v],uv_size=[du,dv],bounds=bounds,flip_u=du<0,flip_v=dv<0)
     if du==0 or dv==0:
      face['status']='ZERO_AREA_NOT_RESAMPLED';dr.text((x+8,y+55),'ZERO AREA',fill='white')
     elif not all(float(n).is_integer() for n in bounds):
      face['status']='FRACTIONAL_NOT_RESAMPLED';dr.text((x+8,y+55),'FRACTIONAL UV: NO RESAMPLING',fill='white')
     else:
      bounds=list(map(int,bounds));assert 0<=bounds[0]<bounds[2]<=im.width and 0<=bounds[1]<bounds[3]<=im.height
      patch=im.crop(bounds)
      if du<0:patch=ImageOps.mirror(patch)
      if dv<0:patch=ImageOps.flip(patch)
      factor=max(1,min(180//patch.width,150//patch.height))
      for yy in range(15):
       for xx in range(18):dr.rectangle((x+15+xx*10,y+42+yy*10,x+24+xx*10,y+51+yy*10),fill='#60666b' if (xx+yy)%2 else '#555b60')
      preview=patch.resize((patch.width*factor,patch.height*factor),Image.Resampling.NEAREST);page.paste(preview,(x+15,y+42),preview)
      face.update(status='SIGNED_INTEGER_CROP',crop_rgba_sha256=hashlib.sha256(patch.tobytes()).hexdigest(),
       pixels=patch.width*patch.height,alpha_nonzero_pixels=sum(a>0 for a in patch.getchannel('A').tobytes()))
     dr.text((x+8,y+199),f'UV {u},{v} + {du},{dv}',fill='white');row['faces'].append(face)
    crops.append(row)
   page.save(sheet);sheets.append(str(sheet.relative_to(ROOT)))
out=dict(sources=sources,rows=crops,sheets=sheets,manual_review_complete=False,new_design_credit=0,production_changes=0,
 purpose='Supplement known PNGs with exact signed model-face crops. Same design is never recounted. No copying or model edits.')
(OUT/'reference-uv-extension.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(models=len(sources),cubes=len(crops),faces=sum(len(r['faces']) for r in crops),sheets=sheets),ensure_ascii=False))
