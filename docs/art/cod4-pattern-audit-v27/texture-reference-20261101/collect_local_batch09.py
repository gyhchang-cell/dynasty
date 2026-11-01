"""Read actual vanilla pixel pattern masks for coarse-layout calibration only."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image
from collect import ROOT, OUT, RAW, sheets

jar=Path('/Users/a15356015027/.gradle/caches/forge_gradle/mcp_repo/de/oceanlabs/mcp/mcp_config/1.20.1-20230612.114412/joined/downloadClient/client.jar')
payload=jar.read_bytes()
sha1=hashlib.sha1(payload).hexdigest()
assert sha1=='0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838'
jar_sha=hashlib.sha256(payload).hexdigest()
rows=[]
with zipfile.ZipFile(io.BytesIO(payload)) as z:
    entries=sorted(n for n in z.namelist() if n.startswith('assets/minecraft/textures/entity/banner/') and n.endswith('.png'))
    for i,entry in enumerate(entries,281):
        data=z.read(entry);im=Image.open(io.BytesIO(data));im.verify()
        p=RAW/'local-batch09'/Path(entry).name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        rows.append(dict(reference_id=f'VIS-{i:03}',repo='Minecraft Java1.20.1 / official archived original pixel masks',
            path=entry,jar=str(jar),jar_sha256=jar_sha,official_client_sha1=sha1,
            source_url=f'https://piston-data.mojang.com/v1/objects/{sha1}/client.jar',
            local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),
            dimensions=list(Image.open(p).size),decoded=True,status='EXTRACTED_NOT_VIEWED',
            distinct_family_proposed_credit=0))
sheets(rows,prefix='batch09')
(OUT/'batch-09-candidates.json').write_text(json.dumps(dict(
    policy='Vanilla coarse-pattern baseline, NOT1000 other-mod cases. Rotations, mirrors, halves and positions are not distinct case credit. Masks are not new Dynasty art.',
    rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(extracted=len(rows),source_sha1=sha1,credit=0)))
