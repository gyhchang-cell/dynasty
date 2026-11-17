"""Archive-only large glyph references, shown at full original pixel size."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw
from collect import ROOT, OUT, RAW

jar = Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods/[血魔法] bloodmagic-1.20.1-3.3.7-49.jar')
jar_sha = hashlib.sha256(jar.read_bytes()).hexdigest()
names = 'basearray bindingarray bindinglightningarray airsigil divinationsigil elementalaffinitysigil growthsigil hastesigil lightsigil magnetismsigil movementarray moonarray moonarrayinside moonarrayoutside moonarraysymbols sunarray sunarraycircle sunarrayspikes suppressionsigil teleportation teleportationarray updraftarray voidsigil watersigil'.split()
rows = []
with zipfile.ZipFile(jar) as z:
    metadata = z.read('META-INF/mods.toml').decode('utf-8', errors='replace')
    for i, name in enumerate(names, 200):
        entry = f'assets/bloodmagic/textures/models/alchemyarrays/{name}.png'
        data = z.read(entry)
        im = Image.open(io.BytesIO(data)); im.verify()
        p = RAW/'local-batch06'/ (name+'.png'); p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
        rows.append(dict(reference_id=f'VIS-{i:03}', repo='WayofTime/BloodMagic / archived original art', path=entry,
            jar=str(jar), jar_sha256=jar_sha, archive_metadata_excerpt=metadata[:1800],
            local_path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(),
            dimensions=list(Image.open(io.BytesIO(data)).size), status='EXTRACTED_NOT_VIEWED', decoded=True,
            distinct_family_proposed_credit=0))
for start in range(0,len(rows),4):
    sheet=Image.new('RGB',(1100,1190),'#41474c'); d=ImageDraw.Draw(sheet)
    d.text((10,8),'REFERENCE ONLY / original 512x512 pixels / NOT Dynasty production or game / extraction adds ZERO study credit',fill='white')
    for pos,r in enumerate(rows[start:start+4]):
        im=Image.open(ROOT/r['local_path']).convert('RGBA')
        assert im.size == (512,512)
        x,y=20+(pos%2)*550,40+(pos//2)*575
        sheet.paste(im,(x,y),im)
        d.text((x,y+520),r['reference_id']+' '+Path(r['path']).name,fill='white')
        d.text((x,y+538),'BloodMagic 3.3.7-49 / 512x512 / full source',fill='#bfc8ce')
        r['review_sheet']=str((RAW/f'batch06-{start//4+1:02}.png').relative_to(ROOT))
    sheet.save(RAW/f'batch06-{start//4+1:02}.png')
(OUT/'batch-06-candidates.json').write_text(json.dumps(dict(policy='Source archive read only; no code or game execution. Full source pixel sheets must actually be viewed before review.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(extracted=len(rows),sheets=6,credit=0)))
