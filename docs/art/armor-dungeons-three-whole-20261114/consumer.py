from pathlib import Path
import json,hashlib,subprocess
B=Path(__file__).resolve().parent;repo='Infamous-Misadventures/Dungeons-Libraries';commit='28bd58c43ac1bf18ad421a2dd943eb756e8e0076'
def curl(u,p):subprocess.run(['curl','--retry','2','-fsSL',u,'-o',str(p)],check=True)
curl(f'https://api.github.com/repos/{repo}/git/commits/{commit}',B/'consumer-commit-api.json');c=json.loads((B/'consumer-commit-api.json').read_text());assert c['sha']==commit
curl(f"https://api.github.com/repos/{repo}/git/trees/{c['tree']['sha']}?recursive=1",B/'consumer-root-tree-api.json');t=json.loads((B/'consumer-root-tree-api.json').read_text());assert not t['truncated'];lookup={x['path']:x for x in t['tree']};rows=[]
paths=['gradle.properties','src/main/java/com/infamous/dungeons_libraries/client/renderer/gearconfig/ArmorGearModel.java','src/main/java/com/infamous/dungeons_libraries/client/renderer/gearconfig/ArmorGearRenderer.java','src/main/java/com/infamous/dungeons_libraries/init/ClientEventBusSubscriber.java','src/main/java/com/infamous/dungeons_libraries/items/gearconfig/ArmorGear.java','src/main/resources/assets/dungeons_libraries/animations/armor/armor_default.animation.json']
for p in paths:
 o=B/'consumer-source'/p;o.parent.mkdir(parents=True,exist_ok=True);curl(f'https://raw.githubusercontent.com/{repo}/{commit}/{p}',o);b=o.read_bytes();g=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert g==lookup[p]['sha'];rows.append({'path':p,'blob_sha1':g,'sha256':hashlib.sha256(b).hexdigest(),'url':f'https://github.com/{repo}/blob/{commit}/{p}'})
(B/'consumer-provenance.json').write_text(json.dumps({'repo':repo,'commit':commit,'root_tree':c['tree']['sha'],'files':rows,'runtime_or_requested_library_binary_match':'Not proven; branch source context only'},indent=2)+'\n');print('pinned consumer files',len(rows))
