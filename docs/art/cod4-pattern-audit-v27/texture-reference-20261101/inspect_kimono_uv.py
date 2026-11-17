"""Exact signed UV sampling of a known source PNG; never new production/model work."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image,ImageDraw,ImageOps
from collect import ROOT,OUT,RAW
jar=Path('/Users/a15356015027/Public/.minecraft/versions/测试/mods/samurai_dynasty-0.0.48-1.20.1-neo.jar')
sha=hashlib.sha256(jar.read_bytes()).hexdigest();folder=RAW/'kimono-uv';folder.mkdir(parents=True,exist_ok=True)
refs=json.loads((OUT/'review-batch-20.json').read_text())['rows'];ref=next(r for r in refs if r['reference_id']=='VIS-766')
models=[]
with zipfile.ZipFile(jar) as z:
 for name in ['samurai_armor','steel_armor','kimono']:
  e=f'assets/samurai_dynasty/geo/{name}.geo.json';data=z.read(e);p=folder/(name+'.geo.json');p.write_bytes(data)
  g=json.loads(data)['minecraft:geometry'][0];cc=[(b,i,c) for b in g['bones'] for i,c in enumerate(b.get('cubes',[]))]
  models.append(dict(name=name,entry=e,local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),description=g['description'],
    total_cubes=len(cc),face_uv_cubes=sum(isinstance(c['uv'],dict) for _,_,c in cc),box_uv_cubes=sum(isinstance(c['uv'],list) for _,_,c in cc),
    limit='Source geometry read only for documented UV; no runtime texture/slot assignment established. Box UV unfolding deliberately held.'))
 data=z.read(ref['path']);im=Image.open(io.BytesIO(data)).convert('RGBA')
 g=json.loads((folder/'kimono.geo.json').read_text())['minecraft:geometry'][0]
 assert im.size==(g['description']['texture_width'],g['description']['texture_height'])
 assert hashlib.sha256(data).hexdigest()==ref['sha256']
 cubes=[(b,i,c) for b in g['bones'] for i,c in enumerate(b.get('cubes',[])) if isinstance(c['uv'],dict)]
 rows=[];pages=[]
 for start in range(0,len(cubes),3):
  page=Image.new('RGB',(1320,800),'#454b50');dr=ImageDraw.Draw(page);dr.text((8,8),'KIMONO / EXACT SIGNED SOURCE UV CROPS / NOT 3D, NEW ART OR GAME',fill='white')
  p=folder/f'faces-{start//3+1:02}.png'
  for ri,(bone,ci,cube) in enumerate(cubes[start:start+3]):
   y=35+ri*250;dr.text((8,y),f"{bone['name']}[{ci}] size={cube['size']} inflate={cube.get('inflate',0)}",fill='white')
   row=dict(bone=bone['name'],cube_index=ci,inspection_sheet=str(p.relative_to(ROOT)),faces=[])
   for j,name in enumerate(['north','south','east','west','up','down']):
    u,v=cube['uv'][name]['uv'];du,dv=cube['uv'][name]['uv_size'];bounds=[min(u,u+du),min(v,v+dv),max(u,u+du),max(v,v+dv)]
    assert du and dv and all(float(n).is_integer() for n in bounds)
    bounds=list(map(int,bounds));assert 0<=bounds[0]<bounds[2]<=im.width and 0<=bounds[1]<bounds[3]<=im.height
    patch=im.crop(bounds)
    if du<0:patch=ImageOps.mirror(patch)
    if dv<0:patch=ImageOps.flip(patch)
    x=j*220;dr.text((x+8,y+22),name,fill='white')
    for yy in range(16):
     for xx in range(18):dr.rectangle((x+15+xx*10,y+45+yy*10,x+24+xx*10,y+54+yy*10),fill='#60666b' if (xx+yy)%2 else '#555b60')
    f=min(180//patch.width,150//patch.height);preview=patch.resize((patch.width*f,patch.height*f),Image.Resampling.NEAREST);page.paste(preview,(x+15,y+45),preview)
    dr.text((x+8,y+210),f'UV {u},{v}+{du},{dv}',fill='white')
    row['faces'].append(dict(face=name,uv=[u,v],uv_size=[du,dv],bounds=bounds,flip_u=du<0,flip_v=dv<0,crop_rgba_sha256=hashlib.sha256(patch.tobytes()).hexdigest(),alpha_nonzero_pixels=sum(a>0 for a in patch.getchannel('A').tobytes())))
   rows.append(row)
  page.save(p);pages.append(str(p.relative_to(ROOT)))
out=dict(jar=str(jar),jar_sha256=sha,models=models,png_reference='VIS-766',png_entry=ref['path'],png_local_path=ref['local_path'],png_sha256=ref['sha256'],rows=rows,sheets=pages,
 box_uv_held=2,face_uv_cubes=6,signed_face_crops=36,new_reference_designs=0,production_changes=0,
 limits='Matched same-archive names and texture dimensions are source study only, not code renderer binding. 37+37 box UV cubes in two armor sources and2kimono box UV cubes NOT unfolded. Signed crops are 2D only.')
(OUT/'kimono-uv-source.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(cubes=len(rows),faces=36,sheets=pages),ensure_ascii=False))
