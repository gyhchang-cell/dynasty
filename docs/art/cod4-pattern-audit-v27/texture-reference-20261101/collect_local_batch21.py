"""Four reference equipment families, component layers and overlays not whole sets."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
jar=Path('/Users/a15356015027/Public/.minecraft/versions/锻造之旅/mods/[沉浸式盔甲] immersive_armors-1.7.2+1.20.1-forge.jar')
sha=hashlib.sha256(jar.read_bytes()).hexdigest();rows=[]
with zipfile.ZipFile(jar) as z:
 names=z.namelist();entries=[]
 for family in ['divine','heavy','robe','warrior']:
  entries+=sorted(n for n in names if n.startswith(f'assets/immersive_armors/textures/models/armor/{family}/') and n.endswith('.png'))
  entries+=sorted(n for n in names if n.startswith(f'assets/minecraft/textures/models/armor/{family}_layer_') and n.endswith('.png'))
 for entry in entries:
  data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA');dst=RAW/'local-batch21'/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
  rows.append(dict(reference_id=f'VIS-{789+len(rows):03}',repo=jar.name,path=entry,jar=str(jar),jar_sha256=sha,local_path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch21')
(OUT/'batch-21-candidates.json').write_text(json.dumps(dict(policy='Four equipment source families. Body parts, capes, base and overlay PNGs merge, no texture file-count credit. Vanilla namespace files are MOD PROVIDED files, not claimed vanilla Minecraft.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(count=len(rows),rows=[(r['reference_id'],r['path'],r['dimensions']) for r in rows]),ensure_ascii=False))
