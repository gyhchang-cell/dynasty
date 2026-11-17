"""Read-only addon focus source study. Filenames never establish design identity."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image
from collect import ROOT, OUT, RAW, sheets

jar = Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods/[诡厄灾变] goety_cataclysm-1.20-1.7.0.jar')
archive_sha = hashlib.sha256(jar.read_bytes()).hexdigest()
rows = []
with zipfile.ZipFile(jar) as z:
    entries = sorted(n for n in z.namelist() if n.startswith('assets/goety_cataclysm/textures/item/focus/') and n.endswith('.png'))
    meta = z.read('META-INF/mods.toml').decode('utf-8', errors='replace')
    for entry in entries:
        data = z.read(entry)
        im = Image.open(io.BytesIO(data)).convert('RGBA')
        target = RAW / 'local-batch12' / Path(entry).name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append(dict(reference_id=f'VIS-{469+len(rows):03}', repo='Goety Cataclysm / pinned local addon 1.7.0',
            path=entry, jar=str(jar), jar_sha256=archive_sha, archive_metadata_excerpt=meta[:2000],
            local_path=str(target.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(),
            rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(), dimensions=list(im.size), decoded=True,
            status='EXTRACTED_NOT_VIEWED', distinct_family_proposed_credit=0))
sheets(rows, prefix='batch12')
(OUT/'batch-12-candidates.json').write_text(json.dumps(dict(policy='Local extraction only, no visual credit. Must merge base-mod motifs, common carriers, recolors and states; reject irrelevant pictograms.', rows=rows), ensure_ascii=False, indent=2)+'\n')
print(json.dumps(dict(pngs=len(rows), sheets=sorted({r['review_sheet'] for r in rows}))))
