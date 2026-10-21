"""Integrate approved saved originals, with content-aware 14px sizing."""
from pathlib import Path
import json,shutil,hashlib,runpy
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v2';V1=R/'docs/art/inventory-refresh-v1';A=R/'src/main/resources/assets/dynasty'
expected={x[0] for file in ['selection.json','extra-selection.json','material-second-review.json'] for x in json.loads((D/file).read_text())}
files={p.stem:p for p in (D/'generated').glob('*.json')};missing=expected-files.keys()
if missing:raise SystemExit('Pending generation: '+','.join(sorted(missing)))
for row in json.loads((D/'target-baseline.json').read_text()):
 p=R/row['path']
 if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise SystemExit('Concurrent change; inspect before publishing '+str(p))
m=json.loads((V1/'generated-manifest.json').read_text());updated=set()
for id in sorted(expected):
 row=json.loads(files[id].read_text());dest=D/'sources'/row['group']/(id+'.png');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(row['path'],dest)
 entry={'id':id,'source':str(dest.relative_to(R)),'prompt':row['prompt'],'fit':'content14'};rows=m[row['group']];index=next((i for i,x in enumerate(rows) if x['id']==id),None)
 if index is None:rows.append(entry)
 else:rows[index]=entry
 updated.add(id)
for row in m['materials']:row['fit']='content14';updated.add(row['id'])
(V1/'generated-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(D/'updated-ids.json').write_text(json.dumps(sorted(updated),indent=2)+'\n')
runpy.run_path(str(R/'tools/art/inventory-refresh/install.py'))['publish'](updated)
print('Published original artwork for',len(expected),'items; total size/identity updates',len(updated))
