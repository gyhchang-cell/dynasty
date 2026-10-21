"""Freeze approved targets before publishing; no production changes."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v2';V1=R/'docs/art/inventory-refresh-v1';A=R/'src/main/resources/assets/dynasty'
selected=json.loads((D/'selection.json').read_text());extra=json.loads((D/'extra-selection.json').read_text());second=json.loads((D/'material-second-review.json').read_text());ids={x[0] for x in selected+extra+second};m=json.loads((V1/'generated-manifest.json').read_text());ids.update(x['id'] for x in m['materials'])
report=[]
for id in sorted(ids):
 for folder,ext in [('textures/item','.png'),('models/item','.json')]:
  p=A/folder/(id+ext);target=D/'before'/p.relative_to(A)
  if p.exists():
   target.parent.mkdir(parents=True,exist_ok=True)
   if not target.exists():shutil.copy2(p,target)
   report.append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(D/'target-baseline.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(V1/'generated-manifest.json',D/'manifest-before.json')
protected=[]
for p in (A/'textures/item').glob('*.png'):
 if p.stem not in ids:protected.append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'untouched-baseline.json').write_text(json.dumps(protected,indent=2)+'\n');print(len(ids),'approved targets;',len(protected),'other item textures frozen for comparison')
