"""Backup and narrowly install only the thirteen inspected, previously clean items."""
from pathlib import Path
from PIL import Image
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parents[3];O=R/'docs/art/weapons-twenty-v5';A=R/'src/main/resources/assets/dynasty'
rows=json.loads((O/'manifest.json').read_text());baseline=json.loads((O/'before-sha256.json').read_text())
paths=[];textures={};models={}
with zipfile.ZipFile('/Users/a15356015027/Public/.minecraft/versions/1.20.1/1.20.1.jar') as z:bowdisplay=json.loads(z.read('assets/minecraft/models/item/bow.json'))['display']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mesh(im):
 w,h=im.size;sx=16/w;sy=16/h
 def face(uv):return {'texture':'#layer0','uv':uv}
 def solid(x,y):return 0<=x<w and 0<=y<h and im.getpixel((x,y))[3]>0
 e=[{'from':[0,0,7.75],'to':[16,16,8.25],'shade':False,'faces':{'north':face([16,0,0,16]),'south':face([0,0,16,16])}}]
 for y in range(h):
  for x in range(w):
   if not solid(x,y):continue
   uv=[(x+.25)*sx,(y+.25)*sy,(x+.75)*sx,(y+.75)*sy];fs={}
   for name,dx,dy in [('west',-1,0),('east',1,0),('up',0,-1),('down',0,1)]:
    if not solid(x+dx,y+dy):fs[name]=face(uv)
   if fs:e.append({'from':[x*sx,16-(y+1)*sy,7.75],'to':[(x+1)*sx,16-y*sy,8.25],'shade':False,'faces':fs})
 return e
for row in rows:
 if row['candidate']:continue
 for stage in (range(4) if row['type']=='bow' else range(1)):
  name=row['id']+('' if stage==0 else f'_pulling_{stage-1}')
  tp=A/f'textures/item/{name}.png';mp=A/f'models/item/{name}.json';paths.extend([tp,mp]);textures[tp]=O/f'textures/{name}.png'
  old=json.loads(mp.read_text()) if mp.exists() else {};m=dict(old)
  m.update(parent='dynasty:item/solid_bow' if row['type']=='bow' else old.get('parent','dynasty:item/solid_handheld'),textures={'layer0':f'dynasty:item/{name}','particle':'#layer0'},elements=mesh(Image.open(textures[tp]).convert('RGBA')),render_type='minecraft:cutout',dynasty_solid_edges=True)
  if row['type']=='bow':
   m['display']=bowdisplay
   if stage==0:
    m['overrides']=[{'predicate':({'dynasty:pulling':1} if k==0 else {'dynasty:pulling':1,'dynasty:pull':[0,.65,.9][k]}),'model':f'dynasty:item/{row["id"]}_pulling_{k}'} for k in range(3)]
   else:m.pop('overrides',None)
  models[mp]=m
# Refuse any changes since the selection snapshot, and refuse overwriting a prior deployment.
assert not (O/'deployment.json').exists(),'Already deployed; do not overwrite a later edit.'
for p in paths:
 rel=str(p.relative_to(R));expected=baseline.get(rel)
 assert (digest(p) if p.exists() else None)==expected,('external change',rel)
with zipfile.ZipFile(O/'original-thirteen-backup.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:
  if p.exists():z.write(p,str(p.relative_to(R)))
for p,src in textures.items():shutil.copy2(src,p)
for p,m in models.items():p.write_text(json.dumps(m,separators=(',',':'))+'\n')
changed={str(p.relative_to(R)):digest(p) for p in paths};untouched=0
for rel,h in baseline.items():
 if rel in changed:continue
 assert digest(R/rel)==h,('unrelated file changed during task',rel)
 untouched+=1
for p,m in models.items():
 im=Image.open(A/(m['textures']['layer0'].split(':')[1].replace('item/','textures/item/')+'.png')).convert('RGBA')
 assert m['elements']==mesh(im)
 for o in m.get('overrides',[]):assert (A/'models'/(o['model'].split(':')[1]+'.json')).exists()
(O/'deployment.json').write_text(json.dumps({'existing_items':13,'review_candidates':7,'textures_written':len(textures),'models_written':len(models),'unchanged_existing_item_files':untouched,'checks':['no_external_overwrite','28_alpha_matched_meshes','bow_predicate_links','vanilla_bow_transforms','unrelated_asset_hashes'],'game_tested':False,'files':changed},ensure_ascii=False,indent=2))
print('Deployed 13 items: 28 textures + 28 matching models. Unrelated existing files unchanged:',untouched)
