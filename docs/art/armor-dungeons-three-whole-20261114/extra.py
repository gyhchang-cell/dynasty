from pathlib import Path
import json,hashlib,subprocess
B=Path(__file__).resolve().parent;d=json.loads((B/'provenance.json').read_text());t=json.loads((B/'root-tree-api.json').read_text());lookup={x['path']:x for x in t['tree']}
for p in ['src/main/java/com/infamous/dungeons_gear/registry/ItemInit.java','src/main/java/com/infamous/dungeons_gear/datagen/ModItemModelProvider.java']:
 o=B/'source'/p;o.parent.mkdir(parents=True,exist_ok=True);u=f"https://raw.githubusercontent.com/{d['repo']}/{d['commit']}/{p}";subprocess.run(['curl','-fsSL',u,'-o',str(o)],check=True);b=o.read_bytes();s=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert s==lookup[p]['sha'];d['files'].append({'path':p,'blob_sha1':s,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'url':u})
(B/'provenance.json').write_text(json.dumps(d,indent=2)+'\n');print('total',len(d['files']))
