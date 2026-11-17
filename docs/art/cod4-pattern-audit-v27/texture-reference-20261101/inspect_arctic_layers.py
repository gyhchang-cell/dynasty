"""Read actual layered item texture references; no assumed dye or runtime output."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import io
import json
import zipfile
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[3]
B=R/'build/art-reference-20261101/arctic-layer-binding';B.mkdir(parents=True,exist_ok=True)
pair=next(r for r in json.loads((D/'prior-batch07-semantic-review.json').read_text())['rows'] if r['current_reference']=='VIS-224')
jar=Path(pair['prior']['jar']);sha=hashlib.sha256(jar.read_bytes()).hexdigest();assert sha==pair['prior_jar_sha256']
page=Image.new('RGB',(1080,1060),'#454b50');dr=ImageDraw.Draw(page)
dr.text((8,8),'ARCTIC ITEM SOURCE LAYERS / RAW ALPHA COMPOSITE WITHOUT DYE / NOT GAME',fill='white')
rows=[]
with zipfile.ZipFile(jar) as z:
    for i,slot in enumerate(['helmet','chestplate','leggings','boots']):
        entry=f'assets/twilightforest/models/item/arctic_{slot}.json';data=z.read(entry);model=json.loads(data)
        target=B/Path(entry).name;target.write_bytes(data)
        row={'slot':slot,'model_entry':entry,'model_local_path':str(target.relative_to(R)),
            'model_sha256':hashlib.sha256(data).hexdigest(),'parent':model['parent'],
            'raw_textures':model['textures'],'override_count':len(model.get('overrides',[])),'source_pngs':[]}
        ims=[]
        for layer in ['layer0','layer1']:
            ns,rel=model['textures'][layer].split(':');png=f'assets/{ns}/textures/{rel}.png';payload=z.read(png)
            path=B/Path(png).name;path.write_bytes(payload);im=Image.open(io.BytesIO(payload)).convert('RGBA');ims.append(im)
            row['source_pngs'].append({'layer':layer,'entry':png,'local_path':str(path.relative_to(R)),
                'sha256':hashlib.sha256(payload).hexdigest(),'dimensions':list(im.size)})
        assert ims[0].size==ims[1].size
        composite=Image.alpha_composite(*ims)  # diagnostic only, no in-game tint inferred
        y=40+i*250
        for j,im in enumerate([*ims,composite]):
            dr.text((j*360+8,y),slot+' / '+['source layer0','source layer1','raw alpha composite'][j],fill='white')
            im=im.resize((im.width*12,im.height*12),Image.Resampling.NEAREST);page.paste(im,(j*360+65,y+25),im)
        rows.append(row)
sheet=B/'layers.png';page.save(sheet)
out={'recorded_at':datetime.now(timezone.utc).isoformat(),'source_archive':str(jar),'source_archive_sha256':sha,
    'rows':rows,'inspection_sheet':str(sheet.relative_to(R)),'new_credit':0,'production_changes':0,
    'manual_review_complete':False,'limit':'Item JSON proves two texture references; alpha composite is untinted diagnostic, not default appearance, dye/trim shader or wearable UV/runtime verification.'}
(D/'arctic-item-layer-binding.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'source_model_jsons':4,'source_pngs':8,'new_equipment_case_credit':0,'sheet':str(sheet)}))
