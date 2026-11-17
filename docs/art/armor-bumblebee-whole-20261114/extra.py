from pathlib import Path
import json,hashlib,subprocess
B=Path(__file__).resolve().parent;d=json.loads((B/'provenance.json').read_text());t=json.loads((B/'root-tree-api.json').read_text());lookup={x['path']:x for x in t['tree']};names=['/BumblezoneClient.java','/NeoForgeClientEventManager.java','/StinglessBeeHelmet.java','/BumbleBeeChestplate.java','/HoneyBeeLeggings.java','/CarpenterBeeBoots.java']
for p,a in lookup.items():
 if not any(p.endswith(n) for n in names):continue
 o=B/'source'/p;o.parent.mkdir(parents=True,exist_ok=True);url=f"https://raw.githubusercontent.com/{d['repo']}/{d['commit']}/{p}"
 subprocess.run(['curl','-fsSL',url,'-o',str(o)],check=True);b=o.read_bytes();s=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert s==a['sha']
 d['files'].append({'path':p,'blob_sha1':s,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'url':url})
(B/'provenance.json').write_text(json.dumps(d,indent=2)+'\n');print('total',len(d['files']))
