"""Exact namespace/item lookup in older art indices; no fuzzy source acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,io,json,zipfile
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[3]
B=R/'build/art-reference-20261101/prior-comparison-batch21';B.mkdir(parents=True,exist_ok=True)
indices=[]
for f in ['docs/art/accessories-mc-v11/references/sources.json','docs/art/armor-vanilla-v23/research/index.json','docs/art/armor-imperial-v24/research/index.json']:
 d=json.loads((R/f).read_text())
 for a in d.get('sources',[]) if isinstance(d,dict) else d:
  r=dict(a);r['entry']=r.get('texture',r.get('entry'));r['prior_index']=f;indices.append(r)
current={r['reference_id']:r for n in [21] for r in json.loads((D/f'review-batch-{n:02}.json').read_text())['rows']}
jobs=[('VIS-798','immersive_armors','divine_chestplate'),('VIS-808','immersive_armors','heavy_chestplate'),('VIS-818','immersive_armors','robe_chestplate'),('VIS-830','immersive_armors','warrior_chestplate')]
rows=[];page=Image.new('RGB',(1120,1220),'#454b50');dr=ImageDraw.Draw(page)
dr.text((8,8),'OLDER ITEM ICON VS CURRENT SOURCE ATLAS / NOT MODEL, GAME OR NEW PRODUCTION',fill='white')
for i,(ref,ns,item) in enumerate(jobs):
 c=current[ref];entry=f'assets/{ns}/textures/item/{item}.png'
 old=next(a for a in indices if a['entry']==entry)
 jar=Path(old['jar'])
 animation=None
 with zipfile.ZipFile(jar) as z:
  data=z.read(entry)
  if entry+'.mcmeta' in z.namelist():
   meta=z.read(entry+'.mcmeta');mp=B/f'{ns}__{item}.png.mcmeta';mp.write_bytes(meta)
   animation=dict(entry=entry+'.mcmeta',local_path=str(mp.relative_to(R)),sha256=hashlib.sha256(meta).hexdigest(),metadata=json.loads(meta))
 assert hashlib.sha256(data).hexdigest()==old['sha256']
 p=B/f'{ns}__{item}.png';p.write_bytes(data)
 x=(i%2)*560;y=40+(i//2)*390
 dr.text((x+6,y),ref+' '+ns+':'+item,fill='white')
 im=Image.open(R/c['local_path']).convert('RGBA');factor=min(4,256//max(im.size))
 im=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST);page.paste(im,(x+6,y+30),im)
 im=Image.open(io.BytesIO(data)).convert('RGBA')
 if animation and im.height>im.width:
  fw=animation['metadata']['animation'].get('width',im.width);fh=animation['metadata']['animation'].get('height',im.width)
  assert im.width==fw and im.height%fh==0
  animation['source_frame_dimensions']=[fw,fh];animation['source_tile_count']=im.height//fh
  for tile in range(im.height//fh):
   frame=im.crop((0,tile*fh,fw,(tile+1)*fh)).resize((fw*3,fh*3),Image.Resampling.NEAREST)
   fx=x+340+(tile%4)*50;fy=y+45+(tile//4)*65;page.paste(frame,(fx,fy),frame)
   dr.text((fx,fy+48),str(tile),fill='white')
 else:
  im=im.resize((im.width*10,im.height*10),Image.Resampling.NEAREST);page.paste(im,(x+340,y+45),im)
 dr.text((x+6,y+305),'Source atlas / pinned current',fill='white');dr.text((x+340,y+305),'Prior tiles, ONE design' if animation else 'Prior item icon',fill='white')
 dr.text((x+6,y+325),Path(old['jar']).name[:76],fill='#ccd2d5')
 rows.append(dict(case=ns+':'+item,current_reference=ref,current_png=c['local_path'],prior=old,prior_animation_source=animation,
  prior_local_png=str(p.relative_to(R)),prior_jar_sha256=hashlib.sha256(jar.read_bytes()).hexdigest(),
  new_case_credit=0,status='PAIRED_SOURCES_NOT_YET_MANUALLY_COMPARED'))
sheet=B/'compare.png';page.save(sheet)
for r in rows:r['comparison_sheet']=str(sheet.relative_to(R))
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),rows=rows,new_credit=0,
 rejected_near_name_lookup='Allfour exactnamespace ordinary chest icons paired to full layer1sources; source material tint remains unproved.',
 policy='Exact item path lookup only. New source atlases must still be manually compared to old icons; missing old source is not proof of novelty.')
(D/'prior-batch21-pairs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(pairs=len(rows),sheet=str(sheet))))
