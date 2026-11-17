"""Read-only local scroll/seal-face study; states/carriers are not designs."""
from pathlib import Path
import hashlib, io, json, zipfile
from PIL import Image
from collect import ROOT, OUT, RAW, sheets

base = Path('/Users/a15356015027/Public/.minecraft/versions')
jobs = [
 ('剑痕纪元', '[神秘遗物] EnigmaticLegacy-2.30.1.jar',
  lambda n: '/textures/item/' in n and ('scroll' in n or n.endswith('/insignia.png'))),
 ('剑痕纪元', '[神秘遗物扩展] enigmaticaddons-1.2.6.jar',
  lambda n: '/textures/item/' in n and ('scroll' in n or 'insignia' in n)),
 ('乌托邦探险之旅3.5.2', 'runes-0.9.13+1.20.1.jar',
  lambda n: '/textures/item/' in n and n.endswith('_stone.png')),
]
rows = []
for pack, name, select in jobs:
 jar = base/pack/'mods'/name
 archive_sha = hashlib.sha256(jar.read_bytes()).hexdigest()
 with zipfile.ZipFile(jar) as z:
  for entry in sorted(n for n in z.namelist() if n.endswith('.png') and select(n)):
   data = z.read(entry)
   im = Image.open(io.BytesIO(data)).convert('RGBA')
   dst = RAW/'local-batch17'/name/entry
   dst.parent.mkdir(parents=True, exist_ok=True)
   dst.write_bytes(data)
   rows.append(dict(reference_id=f'VIS-{586+len(rows):03}',repo=name,path=entry,
    jar=str(jar),jar_sha256=archive_sha,local_path=str(dst.relative_to(ROOT)),
    sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
    dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch17')
(OUT/'batch-17-candidates.json').write_text(json.dumps(dict(
 policy='Study inner stroke composition only, not a scroll/stones count. Recolors, carriers, unused and states merge/exclude. No production or automatically accepted visual credit.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(pngs=len(rows), sheets=sorted({r['review_sheet'] for r in rows}), entries=[(r['reference_id'],r['path']) for r in rows])))
