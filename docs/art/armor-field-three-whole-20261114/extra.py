from pathlib import Path
import json,hashlib,subprocess
B=Path(__file__).resolve().parent;d=json.loads((B/'provenance.json').read_text());t=json.loads((B/'root-tree-api.json').read_text());lookup={a['path']:a for a in t['tree']}
paths=['src/main/java/com/infamous/dungeons_gear/items/armor/FreezingResistanceArmorGear.java','src/main/java/com/infamous/dungeons_gear/items/armor/PetBatArmorGear.java','src/main/resources/assets/dungeons_gear/animations/armor/spelunker_armor.animation.json']
for p in paths:
 o=B/'source'/p;o.parent.mkdir(parents=True,exist_ok=True);u=f"https://raw.githubusercontent.com/{d['repo']}/{d['commit']}/{p}";subprocess.run(['curl','--retry','2','-fsSL',u,'-o',str(o)],check=True);b=o.read_bytes();g=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert g==lookup[p]['sha'];d['files'].append({'path':p,'blob_sha1':g,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'url':u})
(B/'provenance.json').write_text(json.dumps(d,indent=2)+'\n');print('total',len(d['files']))
