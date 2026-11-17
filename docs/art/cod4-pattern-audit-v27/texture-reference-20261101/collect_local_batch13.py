"""Extract only unread local Blood Magic sigils/slates; excludes earlier paths."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image
from collect import ROOT, OUT, RAW, sheets
jar=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods/[血魔法] bloodmagic-1.20.1-3.3.7-49.jar')
seen=set()
for file in OUT.glob('review-batch-*.json'):
    for row in json.loads(file.read_text())['rows']:
        for a in row.get('assets',[row]): seen.add(a.get('path',a.get('archive_entry','')))
sha=hashlib.sha256(jar.read_bytes()).hexdigest()
rows=[]
with zipfile.ZipFile(jar) as z:
    entries=sorted(n for n in z.namelist() if n.endswith('.png') and '/textures/item/' in n and any(x in n for x in ['sigil','slate']) and n not in seen)
    for entry in entries:
        data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA')
        target=RAW/'local-batch13'/Path(entry).name
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        rows.append(dict(reference_id=f'VIS-{497+len(rows):03}',repo='WayofTime/BloodMagic / pinned 3.3.7-49',path=entry,
            jar=str(jar),jar_sha256=sha,local_path=str(target.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),
            rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),dimensions=list(im.size),decoded=True,
            status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch13')
(OUT/'batch-13-candidates.json').write_text(json.dumps(dict(policy='Only unread exact paths extracted. Slate tiers, states, carriers and repeated glyph organization are not independent target designs.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(pngs=len(rows),sheets=sorted({r['review_sheet'] for r in rows}))))
