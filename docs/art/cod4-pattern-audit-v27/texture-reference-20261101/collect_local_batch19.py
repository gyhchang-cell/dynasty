"""One heraldic mask and two UV placements are not three independent designs."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
from collect import ROOT,OUT,RAW,sheets

jar=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods/[史诗骑士：盾牌，盔甲和武器] epic-knights-1.20.1-forge-10.10.jar')
sha=hashlib.sha256(jar.read_bytes()).hexdigest()
motifs=['dragon','eagle','feather','horse','lily','lion1','lion2','snake','sun','swords','tower','tree','two-headed_eagle']
rows=[];missing=[]
with zipfile.ZipFile(jar) as z:
 entries=sorted(n for n in z.namelist() if n.startswith('assets/magistuarmory/textures/entity/banner/') and n.endswith('.png'))
 for shape in ['roundshield','pavese']:
  for motif in motifs:
   entry=f'assets/magistuarmory/textures/entity/{shape}/{motif}.png'
   if entry in z.namelist():entries.append(entry)
   else:missing.append(entry)
 for entry in entries:
  data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA')
  dst=RAW/'local-batch19'/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
  rows.append(dict(reference_id=f'VIS-{702+len(rows):03}',repo=jar.name,path=entry,jar=str(jar),jar_sha256=sha,
   local_path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
   dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch19')
(OUT/'batch-19-candidates.json').write_text(json.dumps(dict(policy='Heraldic mask composition and shape adaptation only. Same motif across banner and shields remains one source family, not full target/imperial identity; cultural/religious symbols are context and not copied.',missing_exact_requested_paths=missing,rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(pngs=len(rows),dimensions=sorted({tuple(r['dimensions']) for r in rows}),missing=missing,
 sheets=sorted({r['review_sheet'] for r in rows}),entries=[(r['reference_id'],r['path']) for r in rows]),ensure_ascii=False))
