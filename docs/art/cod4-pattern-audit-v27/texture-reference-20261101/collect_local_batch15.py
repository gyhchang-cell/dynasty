"""Three local armor sources; exact unread atlases, no icon/name substitutions."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
folder=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods')
names=['[生于混沌] born_in_chaos_[Forge]1.20.1_1.7.4.jar','[坚固地牢] stalwart-dungeons-1.20.1-1.2.8.jar','[地牢进行时] Dungeon Now Loading-forge-1.20.1-2.11.jar']
rows=[]
for name in names:
 jar=folder/name;sha=hashlib.sha256(jar.read_bytes()).hexdigest()
 with zipfile.ZipFile(jar) as z:
  for entry in sorted(n for n in z.namelist() if n.endswith('.png') and '/textures/models/armor/' in n):
   data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA')
   target=RAW/'local-batch15'/name/Path(entry).name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   rows.append(dict(reference_id=f'VIS-{545+len(rows):03}',repo=name,path=entry,jar=str(jar),jar_sha256=sha,
    local_path=str(target.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
    dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch15')
(OUT/'batch-15-candidates.json').write_text(json.dumps(dict(policy='Local primary atlases only; upper/lower parts and base/encrusted upgrades must not automatically become independent designs.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(pngs=len(rows),sheets=sorted({r['review_sheet'] for r in rows}))))
