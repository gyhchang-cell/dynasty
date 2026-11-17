from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
B=Path(__file__).resolve().parent;repo='Infamous-Misadventures/Dungeons-Gear';commit='9ba0075c5b2f13ef54ec914ad1327a853ecdce6f'
def curl(u,o):subprocess.run(['curl','--retry','2','-fsSL',u,'-o',str(o)],check=True)
curl(f'https://api.github.com/repos/{repo}/git/commits/{commit}',B/'commit-api.json');c=json.loads((B/'commit-api.json').read_text());assert c['sha']==commit
curl(f"https://api.github.com/repos/{repo}/git/trees/{c['tree']['sha']}?recursive=1",B/'root-tree-api.json');t=json.loads((B/'root-tree-api.json').read_text());assert not t['truncated']
shared=['gradle.properties','build.gradle','src/main/java/com/infamous/dungeons_gear/registry/ArmorSetInit.java','src/main/java/com/infamous/dungeons_gear/registry/ClientEventBusSubscriber.java','src/main/java/com/infamous/dungeons_gear/client/ClientProxy.java','src/main/java/com/infamous/dungeons_gear/client/ClientEvents.java']
names=['evocation_robes','mercenary','reinforced_mail']
paths=[]
for a in t['tree']:
 p=a['path']
 if a['type']!='blob':continue
 if p in shared or any(n in p for n in names) and any(s in p for s in ['/gearconfig/armor/','/geo/armor/','/textures/item/armor/','/textures/models/armor/','/models/item/']):paths.append(a)
def get(a):
 p=a['path'];o=B/'source'/p;o.parent.mkdir(parents=True,exist_ok=True);u=f'https://raw.githubusercontent.com/{repo}/{commit}/{p}';curl(u,o);b=o.read_bytes();g=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert g==a['sha'],p
 return {'path':p,'blob_sha1':g,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'url':f'https://github.com/{repo}/blob/{commit}/{p}'}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as e:r=list(e.map(get,paths))
(B/'provenance.json').write_text(json.dumps({'repo':repo,'commit':commit,'root_tree':c['tree']['sha'],'files':r},indent=2)+'\n')
for src,dst in [('/Users/a15356015027/.codex/user-preferences/texture-requirements.md','global-texture-requirements.txt'),('docs/art/USER_TEXTURE_REQUIREMENTS.md','project-texture-requirements.txt'),('docs/art/armor-bumblebee-whole-20261114/protected-after.json','protected-before.json'),('docs/art/armor-bumblebee-whole-20261114/priority-after.json','priority-before.json')]: (B/dst).write_bytes(Path(src).read_bytes())
print('pinned',len(r),'root',c['tree']['sha'])
