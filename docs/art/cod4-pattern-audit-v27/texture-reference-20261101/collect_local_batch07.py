"""Local wearable material atlases; variants/layers are extraction records, not cases."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image
from collect import ROOT, OUT, RAW, sheets

prior=[dict(r,prior_index=i) for i in ['docs/art/armor-vanilla-v23/research/index.json','docs/art/armor-imperial-v24/research/index.json'] for r in json.loads((ROOT/i).read_text())]
jars=sorted({r['jar'] for r in prior if Path(r['jar']).is_file()})
jobs=[
 ('twilightforest-1.20.1-4.3.2508',lambda n:'/textures/armor/' in n),
 ('[灵灾(ino配方)]',lambda n:'/textures/armor/' in n and Path(n).stem in ['ancient_soul_hunter','ancient_soul_stained_steel','malignant_stronghold','malignant_stronghold_glow','soul_stained_steel_reforged','spirit_hunter_reforged']),
 ('[诡厄巫法]',lambda n:'/textures/trims/models/armor/crypt' in n),
]
rows=[]
for key,predicate in jobs:
    jar=next(j for j in jars if key in j); sha=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
    with zipfile.ZipFile(jar) as z:
        meta=z.read('META-INF/mods.toml').decode('utf-8',errors='replace')
        for entry in sorted(n for n in z.namelist() if n.endswith('.png') and predicate(n)):
            data=z.read(entry); im=Image.open(io.BytesIO(data)); im.verify()
            ns=entry.split('/')[1]; target=RAW/'local-batch07'/ns/Path(entry).name
            target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
            rows.append(dict(reference_id=f'VIS-{224+len(rows):03}',repo=ns+' / local archived original art',path=entry,
                jar=jar,jar_sha256=sha,archive_metadata_excerpt=meta[:1800],local_path=str(target.relative_to(ROOT)),
                sha256=hashlib.sha256(data).hexdigest(),dimensions=list(Image.open(io.BytesIO(data)).size),decoded=True,
                status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch07')
(OUT/'batch-07-candidates.json').write_text(json.dumps(dict(policy='Wearable atlas/layer extraction only, no new cases or model/UV binding inferred.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(extracted=len(rows),oversize=[r['reference_id'] for r in rows if r.get('sheet_requires_fullsize_inspection')],credit=0)))
