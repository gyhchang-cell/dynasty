from pathlib import Path
import json,subprocess,hashlib
B=Path(__file__).resolve().parent;d=json.loads((B/'provenance.json').read_text());t=json.loads((B/'root-tree-api.json').read_text());L={a['path']:a for a in t['tree']}
for p in ['src/main/java/de/teamlapen/vampirism/util/ArmorMaterial.java','src/main/java/de/teamlapen/vampirism/mixin/client/HumanoidArmorLayerMixin.java']:
 o=B/'source'/p;o.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['curl','-fsSL',f"https://raw.githubusercontent.com/{d['repo']}/{d['commit']}/{p}",'-o',str(o)],check=True);b=o.read_bytes();g=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert g==L[p]['sha'];d['files'].append({'path':p,'blob_sha1':g,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'url':f"https://github.com/{d['repo']}/blob/{d['commit']}/{p}"})
(B/'provenance.json').write_text(json.dumps(d,indent=2)+'\n');print('files',len(d['files']))
