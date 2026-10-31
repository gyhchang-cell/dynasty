"""Publish approved originals without resampling; use the direct-texture Forge loader."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from block_atlas_sources import with_model_sprites
import hashlib,json,re,shutil,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
DOC=ROOT/'docs/art/original-runtime-v7'
A=ROOT/'src/main/resources/assets/dynasty'
MAN=ROOT/'docs/art/inventory-refresh-v1/generated-manifest.json'
def read(p):return json.loads(p.read_text())
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def backup(p):
 if p.exists():
  out=DOC/'before'/p.relative_to(ROOT)
  if not out.exists():out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
def publish(ids=None):
 DOC.mkdir(parents=True,exist_ok=True)
 backup(MAN)
 m=read(MAN)
 for batch,filename in [('inventory-mc-v5','selected.json'),('mechanical-mc-v6','selection.json'),('accessories-mc-v8','selection.json'),('accessories-mc-v9','selection.json'),('accessories-mc-v10','selection.json'),('accessories-mc-v11','selection.json'),('supplies-mc-v12','selection.json'),('talismans-mc-v13','selection.json'),('items-mc-v14','selection.json'),('ammunition-mc-v15','selection.json'),('qimen-items-mc-v16','selection.json'),('accessory-finish-mc-v17','selection.json'),('weapons-mc-v19','selection.json'),('weapons-mc-v20','selection.json'),('mixed-items-mc-v21','selection.json'),('armor-curios-mc-v22','selection.json'),('armor-vanilla-v23','selection.json'),('armor-imperial-v24','selection.json'),('armor-sacred-v25','selection.json'),('armor-expansion-v26','selection.json'),('armor-foundations-v28','selection.json'),('armor-foundations-v29','selection.json')]:
  d=ROOT/'docs/art'/batch; rows=read(d/filename)
  if batch=='inventory-mc-v5':rows+= [{'id':x,'group':'materials'} for x in ['raw_silk','silk','roof_tile','brocade']]
  for row in rows:
   ident=row['id'];group=row.get('group','materials')
   for oldgroup in m:m[oldgroup]=[v for v in m[oldgroup] if v['id']!=ident]
   m.setdefault(group,[]).append({**row,'source':str((d/'sources'/f'{ident}.png').relative_to(ROOT))})
 save(MAN,m)
 with zipfile.ZipFile('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar') as z:
  display=json.loads(z.read('assets/minecraft/models/item/generated.json'))['display']
 rows=[r for group in m.values() for r in group]; names={r['id'] for r in rows}
 allpng=A/'textures/item'
 if not (DOC/'untouched-before.json').exists():
  save(DOC/'untouched-before.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in allpng.glob('*.png') if p.stem not in names})
 report=[]
 for row in rows:
  ident=row['id'];target=allpng/f'{ident}.png';model=A/'models/item'/f'{ident}.json'
  if ids is not None and ident not in ids:
   with Image.open(target) as existing: size=list(existing.size)
   report.append({'id':ident,'source':row['source'],'size':size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
   continue
  backup(target);backup(model)
  with Image.open(ROOT/row['source']) as original:
   original=original.convert('RGBA');bounds=row.get('crop_bounds',original.getbbox())
   if not bounds:raise ValueError(ident)
   crop=original.crop(bounds);output=Image.new('RGBA',(crop.width+4,crop.height+4));output.paste(crop,(2,2));output.save(target)
  model_data={'loader':'dynasty:original_item','original_texture':f'dynasty:textures/item/{ident}.png','gui_light':'front','display':row.get('display',display)}
  if ident in {'dynasty_potion','dynasty_splash_potion','dynasty_lingering_potion'}:model_data['tint_index']=0
  save(model,model_data)
  report.append({'id':ident,'source':row['source'],'size':list(output.size),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
 atlas=ROOT/'src/main/resources/assets/minecraft/atlases/blocks.json';backup(atlas)
 # Filter only approved originals; all ordinary game/mod sprites stay in the normal atlas.
 save(atlas,{'sources':with_model_sprites([{'type':'minecraft:filter','pattern':{'namespace':'^dynasty$','path':'^item/('+'|'.join(re.escape(n) for n in sorted(names))+')$'}}])})
 save(DOC/'published.json',report)
 print('Published original pixels and direct-texture models:',len(rows))
if __name__=='__main__':publish()
