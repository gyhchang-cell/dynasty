"""Unchanged local armor atlases: cultural construction/material reading only."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
folder=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods')
jobs=[('[时代铠甲] Armor of the Ages-forge-1.20.1-1.3.11.jar',lambda n:n.startswith('assets/armoroftheages/textures/models/armor/')),
      ('[深入天境] deep_aether-1.20.1-1.1.7.jar',lambda n:n.startswith('assets/deep_aether/textures/models/armor/')),
      ('[天境：遗失之物] lost_aether_content-1.20.1-1.2.3.jar',lambda n:('/textures/models/armor/' in n or '/textures/trims/models/armor/' in n))]
prior={}
for p in ['docs/art/accessories-mc-v11/references/sources.json','docs/art/armor-vanilla-v23/research/index.json','docs/art/armor-imperial-v24/research/index.json']:
 d=json.loads((ROOT/p).read_text())
 for r in d.get('sources',[]) if isinstance(d,dict) else d:
  prior.setdefault(r['sha256'],[]).append(dict(index=p,jar=r['jar'],path=r.get('texture',r.get('entry',r.get('path')))))
rows=[]
for base,predicate in jobs:
 jar=folder/base; archive_sha=hashlib.sha256(jar.read_bytes()).hexdigest()
 with zipfile.ZipFile(jar) as z:
  meta=z.read('META-INF/mods.toml').decode('utf-8',errors='replace')
  for entry in sorted(n for n in z.namelist() if n.endswith('.png') and predicate(n)):
   data=z.read(entry);sha=hashlib.sha256(data).hexdigest();im=Image.open(io.BytesIO(data)).convert('RGBA')
   target=RAW/'local-batch14'/base/entry
   target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   rows.append(dict(reference_id=f'VIS-{515+len(rows):03}',repo=base,path=entry,jar=str(jar),jar_sha256=archive_sha,
    archive_metadata_excerpt=meta[:2200],local_path=str(target.relative_to(ROOT)),sha256=sha,
    rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',
    distinct_family_proposed_credit=0,exact_prior_png_matches_not_semantic_acceptance=prior.get(sha,[])))
sheets(rows,prefix='batch14')
(OUT/'batch-14-candidates.json').write_text(json.dumps(dict(policy='Local primary sources; slim/normal, layers, classics and recolors must merge. Cultural design must not be copied into Dynasty. Atlases alone do not prove model/UV/runtime.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(pngs=len(rows),dimensions=sorted(set(tuple(r['dimensions']) for r in rows)),sheets=sorted({r['review_sheet'] for r in rows}))))
