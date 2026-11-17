"""Player-wearable texture material research from four fixed local archives."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image
from collect import ROOT, OUT, RAW, sheets

base=Path('/Users/a15356015027/Public/.minecraft/versions/愚者chishi/mods')
jobs=['iceandfire-2.1.13-1.20.1-beta-5.jar','alexscaves-2.0.2.jar','alexsmobs-1.22.9.jar','L_Enders_Cataclysm-3.16.jar']
rows=[]
for name in jobs:
    jar=base/name;jar_sha=hashlib.sha256(jar.read_bytes()).hexdigest()
    with zipfile.ZipFile(jar) as z:
        meta=z.read('META-INF/mods.toml').decode('utf-8',errors='replace')
        for entry in sorted(n for n in z.namelist() if n.endswith('.png') and '/textures/' in n and ('/armor/' in n or '/armors/' in n)):
            data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA');ns=entry.split('/')[1]
            target=RAW/'local-batch11'/ns/Path(entry).name
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            rows.append({'reference_id':f'VIS-{363+len(rows):03}','repo':ns+' / fixed local archived original art',
                'path':entry,'jar':str(jar),'jar_sha256':jar_sha,'archive_metadata_excerpt':meta[:1800],
                'local_path':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),
                'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'dimensions':list(im.size),
                'decoded':True,'status':'EXTRACTED_NOT_VIEWED','distinct_family_proposed_credit':0})
sheets(rows,prefix='batch11')
(OUT/'batch-11-candidates.json').write_text(json.dumps({'policy':'Atlas/layer/recolor extraction is not a unique equipment or complete UV case. Player-wearable material context only; no creature model or logic scope.', 'rows':rows},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'raw_pngs':len(rows),'requires_detail':[{'id':r['reference_id'],'path':r['local_path'],'dimensions':r['dimensions']} for r in rows if r.get('sheet_requires_fullsize_inspection')],'sheets':sorted({r['review_sheet'] for r in rows})}))
