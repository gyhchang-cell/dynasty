"""Follow exact resource-only item bindings; no inferred wearable UV linkage."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,io,json,zipfile
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[3]
B=R/'build/art-reference-20261101/held-item-binding';B.mkdir(parents=True,exist_ok=True)
prior=json.loads((D/'prior-batch11-semantic-review.json').read_text())['rows']
jobs=[('alexscaves-2.0.2.jar','alexscaves',i) for i in ['primordial_helmet','primordial_tunic','primordial_pants']]
jobs.append(('L_Enders_Cataclysm-3.16.jar','cataclysm','monstrous_helm'))
page=Image.new('RGB',(1120,1060),'#454b50');dr=ImageDraw.Draw(page)
dr.text((8,8),'EXACT ITEM SOURCE BINDING / PRIOR ICON COMPARISON / NOT WORN MODEL OR GAME',fill='white')
rows=[]
for i,(base,ns,name) in enumerate(jobs):
 jar=Path('/Users/a15356015027/Public/.minecraft/versions/愚者chishi/mods')/base
 with zipfile.ZipFile(jar) as z:
  entry=f'assets/{ns}/models/item/{name}.json';data=z.read(entry);model=json.loads(data)
  mp=B/(ns+'__'+name+'.json');mp.write_bytes(data)
  row=dict(item=f'{ns}:{name}',source_archive=str(jar),source_archive_sha256=hashlib.sha256(jar.read_bytes()).hexdigest(),
   model_entry=entry,model_local_path=str(mp.relative_to(R)),model_sha256=hashlib.sha256(data).hexdigest(),
   parent=model['parent'],textures=model['textures'],source_pngs=[],wearable_binding_proven=False)
  for layer,texture in model['textures'].items():
   tns,rel=texture.split(':');png=f'assets/{tns}/textures/{rel}.png';payload=z.read(png);im=Image.open(io.BytesIO(payload)).convert('RGBA')
   out=B/(ns+'__'+name+'__'+layer+'.png');out.write_bytes(payload)
   row['source_pngs'].append(dict(layer=layer,entry=png,local_path=str(out.relative_to(R)),sha256=hashlib.sha256(payload).hexdigest(),dimensions=list(im.size)))
   large=im.resize((im.width*12,im.height*12),Image.Resampling.NEAREST)
   y=45+i*250;dr.text((10,y),row['item']+' / actual JSON '+layer,fill='white');page.paste(large,(60,y+25),large)
  if name in ['primordial_helmet','monstrous_helm']:
   old=next(p for p in prior if p['current_reference']==('VIS-440' if name=='primordial_helmet' else 'VIS-468'))
   oldim=Image.open(R/old['prior_local_png']).convert('RGBA')
   row['prior_item_source']=old['prior'];row['prior_local_png']=old['prior_local_png']
   row['prior_exact_png_equal']=row['source_pngs'][0]['sha256']==old['prior']['sha256']
   dr.text((570,y),'prior index / '+Path(old['prior']['jar']).name[:56],fill='white')
   oldim=oldim.resize((oldim.width*12,oldim.height*12),Image.Resampling.NEAREST);page.paste(oldim,(650,y+25),oldim)
  rows.append(row)
sheet=B/'items.png';page.save(sheet)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),rows=rows,inspection_sheet=str(sheet.relative_to(R)),
 new_visual_credit=0,production_changes=0,manual_review_complete=False,
 limit='Exact item JSON to PNG links only. No resource wearable geometry supplied by these archives was used; matching names do not prove slot coverage. Prior expansion icon is not the Cataclysm player item.')
(D/'held-item-source-binding.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(jsons=len(rows),source_pngs=sum(len(r['source_pngs']) for r in rows),sheet=str(sheet),equal_old_icons={r['item']:r['prior_exact_png_equal'] for r in rows if 'prior_exact_png_equal' in r})))
