"""Exact JSON-only archery texture chains and enlarged unchanged source atlases."""
from pathlib import Path
import hashlib,json,zipfile
from PIL import Image,ImageDraw
from collect import ROOT,OUT,RAW

rows=json.loads((OUT/'batch-18-candidates.json').read_text())['rows']
by_id={r['reference_id']:r for r in rows}
folder=RAW/'batch18-binding';folder.mkdir(parents=True,exist_ok=True)
jobs=[('VIS-651','twilightforest:item/ice_bow'),('VIS-667','deep_aether:item/storm_bow'),
 ('VIS-678','cataclysm:item/cursed_bow'),('VIS-685','goety_revelation:item/bow_of_revelation')]
models=[];roots=[]
for ref,root in jobs:
 source=by_id[ref];seen=set();outside=[];missing=[]
 with zipfile.ZipFile(source['jar']) as z:
  def walk(model):
   if model in seen:return
   seen.add(model)
   namespace,path=model.split(':',1) if ':' in model else ('minecraft',model)
   entry=f'assets/{namespace}/models/{path}.json'
   if namespace=='minecraft':outside.append(model);return
   if entry not in z.namelist():missing.append(model);return
   data=z.read(entry);doc=json.loads(data)
   dst=folder/namespace/(path+'.json');dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
   layers=[]
   for layer,texture in doc.get('textures',{}).items():
    if texture.startswith('#'):continue
    ns,tp=texture.split(':',1) if ':' in texture else ('minecraft',texture)
    png_entry=f'assets/{ns}/textures/{tp}.png'
    match=[r for r in rows if r['jar']==source['jar'] and r['path']==png_entry]
    layers.append(dict(layer=layer,texture=texture,entry=png_entry,source_references=[r['reference_id'] for r in match],
     png_present_in_same_archive=png_entry in z.namelist()))
   models.append(dict(root=root,jar=source['jar'],jar_sha256=source['jar_sha256'],model=model,entry=entry,
    local_path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),parent=doc.get('parent'),
    direct_texture_layers=layers,overrides=doc.get('overrides',[]),display=doc.get('display',{})))
   if doc.get('parent'):walk(doc['parent'])
   for override in doc.get('overrides',[]):walk(override['model'])
  walk(root)
 roots.append(dict(root=root,archive=source['jar'],unexpanded_external_parents=sorted(set(outside)),missing_local_model_refs=missing))

page=Image.new('RGB',(1160,640),'#444a50');draw=ImageDraw.Draw(page)
draw.text((12,10),'CURSED BOW: UNCHANGED FULL 128px ATLASES x4 / NOT INVENTORY ICONS OR GAME',fill='white')
for col,ref in enumerate(['VIS-678','VIS-679']):
 r=by_id[ref];im=Image.open(ROOT/r['local_path']).convert('RGBA');assert im.size==(128,128)
 preview=im.resize((512,512),Image.Resampling.NEAREST);x=20+col*570
 draw.rectangle((x,70,x+511,581),fill='#666c71');page.paste(preview,(x,70),preview)
 draw.text((x,40),ref+' '+Path(r['path']).name,fill='white')
atlas_sheet=folder/'cursed-full-atlases.png';page.save(atlas_sheet)

r=by_id['VIS-673'];im=Image.open(ROOT/r['local_path']).convert('RGBA');assert im.size==(16,32)
with zipfile.ZipFile(r['jar']) as z:
 entry=r['path']+'.mcmeta';data=z.read(entry)
meta=json.loads(data);meta_path=folder/'storm-special.png.mcmeta';meta_path.write_bytes(data)
page=Image.new('RGB',(720,360),'#444a50');draw=ImageDraw.Draw(page)
draw.text((12,10),'VIS-673 / UNCHANGED SOURCE TILES x16 / NOT GAME / interpolate=true',fill='white')
tiles=[]
for i in range(2):
 patch=im.crop((0,i*16,16,(i+1)*16));preview=patch.resize((256,256),Image.Resampling.NEAREST)
 x=20+i*350;draw.rectangle((x,65,x+255,320),fill='#666c71');page.paste(preview,(x,65),preview)
 draw.text((x,40),f'source tile {i}',fill='white');tiles.append(dict(index=i,rgba_sha256=hashlib.sha256(patch.tobytes()).hexdigest()))
frame_sheet=folder/'storm-source-frames.png';page.save(frame_sheet)
out=dict(roots=roots,models=models,model_jsons=len(models),full_atlas_sheet=str(atlas_sheet.relative_to(ROOT)),
 animation=dict(reference='VIS-673',jar=r['jar'],metadata_entry=entry,metadata_local_path=str(meta_path.relative_to(ROOT)),
  metadata_sha256=hashlib.sha256(data).hexdigest(),metadata=meta,png=r['local_path'],png_sha256=r['sha256'],tiles=tiles,inspection_sheet=str(frame_sheet.relative_to(ROOT))),
 manual_review_complete=False,new_design_credit=0,production_changes=0,
 limit='Only declared model parents/overrides/layers. No registered predicates, resource-pack priority, custom renderer, GPU transparency or runtime acceptance inferred.')
(OUT/'batch18-resource-bindings.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(roots=roots,model_jsons=len(models),models=[dict(model=m['model'],parent=m['parent'],layers=m['direct_texture_layers']) for m in models]),ensure_ascii=False))
