"""Publish second visual review results with a last-validated content guard."""
from pathlib import Path
import json,hashlib,shutil,runpy
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v2';V=R/'docs/art/inventory-refresh-v1';A=R/'src/main/resources/assets/dynasty';m=json.loads((V/'generated-manifest.json').read_text());verified={x['id']:x['sha256'] for x in json.loads((D/'validation.json').read_text())['sprites']};ids=[]
for p in sorted((D/'refinements').glob('*.json')):
 row=json.loads(p.read_text());id=row['id'];target=A/'textures/item'/(id+'.png')
 assert hashlib.sha256(target.read_bytes()).hexdigest()==verified[id],f'Concurrent art change: {id}'
 dest=D/'sources'/row['group']/(id+'-reviewed.png');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(row['path'],dest);rows=m[row['group']];idx=next(i for i,x in enumerate(rows) if x['id']==id);rows[idx]={'id':id,'source':str(dest.relative_to(R)),'prompt':row['prompt'],'fit':'content14'};ids.append(id)
(V/'generated-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');runpy.run_path(str(R/'tools/art/inventory-refresh/install.py'))['publish'](ids)
