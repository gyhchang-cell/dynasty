"""Material study of straps/cuffs/cloak/boots, using fixed local wearable PNGs."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
folder=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods')
jobs=[('[遗物] relics-1.20.1-0.8.0.9.jar','/textures/models/items/',
       ['boot','belt','robe','glove','quiver','locket','necklace','aqua_walker','magma_walker']),
      ('[奇异饰品] artifacts-forge-9.5.16.jar','/textures/entity/wearable/',
       ['boot','glove','necklace','claw','gauntlet','scarf','pendant','spikes'])]
rows=[]
for base,folder_marker,terms in jobs:
 jar=folder/base;sha=hashlib.sha256(jar.read_bytes()).hexdigest()
 with zipfile.ZipFile(jar) as z:
  for entry in sorted(n for n in z.namelist() if n.endswith('.png') and folder_marker in n and any(s in n for s in terms)):
   data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA')
   target=RAW/'local-batch16'/base/entry;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   rows.append(dict(reference_id=f'VIS-{555+len(rows):03}',repo=base,path=entry,jar=str(jar),jar_sha256=sha,
    local_path=str(target.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
    dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch16')
(OUT/'batch-16-candidates.json').write_text(json.dumps(dict(policy='Wearable material sources only. Narrow/wide arms, glow overlays and states merge. Item icons and in-world wearable atlases of one object are not separate new equipment designs.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(pngs=len(rows),dimensions=sorted(set(tuple(r['dimensions']) for r in rows)),sheets=sorted({r['review_sheet'] for r in rows}))))
