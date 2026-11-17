from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
B=Path(__file__).resolve().parent;repo='TeamLapen/Vampirism';commit='ee4f4a2635604925c7bdc3b46f91127ff950f37c'
def curl(u,p):subprocess.run(['curl','--retry','2','-fsSL',u,'-o',str(p)],check=True)
curl(f'https://api.github.com/repos/{repo}/git/commits/{commit}',B/'commit-api.json');c=json.loads((B/'commit-api.json').read_text());assert c['sha']==commit
curl(f"https://api.github.com/repos/{repo}/git/trees/{c['tree']['sha']}?recursive=1",B/'root-tree-api.json');t=json.loads((B/'root-tree-api.json').read_text());assert not t['truncated']
shared=['gradle.properties','build.gradle','src/main/java/de/teamlapen/vampirism/items/HunterCoatItem.java','src/main/java/de/teamlapen/vampirism/items/VampirismHunterArmorItem.java','src/main/java/de/teamlapen/vampirism/client/model/armor/VampirismArmorModel.java','src/main/java/de/teamlapen/vampirism/core/ModItems.java','src/main/java/de/teamlapen/vampirism/client/core/ModItemsRender.java','src/main/java/de/teamlapen/vampirism/proxy/ClientProxy.java']
paths=[]
for a in t['tree']:
 p=a['path'];selected=p in shared or 'hunter_coat_' in p and p.endswith('_normal.json') and ('/models/item/' in p or '/recipes/weapontable/' in p) or 'textures/item/hunter_coat_' in p and p.endswith('_normal.png') or p.endswith(('/hunter_coat_layer_1.png','/hunter_coat_layer_2.png'))
 if selected and a['type']=='blob':paths.append(a)
def get(a):
 p=a['path'];o=B/'source'/p;o.parent.mkdir(parents=True,exist_ok=True);curl(f'https://raw.githubusercontent.com/{repo}/{commit}/{p}',o);b=o.read_bytes();g=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert g==a['sha'];return {'path':p,'blob_sha1':g,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'url':f'https://github.com/{repo}/blob/{commit}/{p}'}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as e:rows=list(e.map(get,paths))
(B/'provenance.json').write_text(json.dumps({'repo':repo,'commit':commit,'root_tree':c['tree']['sha'],'files':rows},indent=2)+'\n')
for src,dst in [('/Users/a15356015027/.codex/user-preferences/texture-requirements.md','global-texture-requirements.txt'),('docs/art/USER_TEXTURE_REQUIREMENTS.md','project-texture-requirements.txt'),('docs/art/armor-field-three-whole-20261114/protected-after.json','protected-before.json'),('docs/art/armor-field-three-whole-20261114/priority-after.json','priority-before.json')]: (B/dst).write_bytes(Path(src).read_bytes())
p=Path('docs/cod4/audit-20261022/coordinator-armor-D88-actual-15PNG-three-geometry-consumer-HOLD0-review-20261114.json').resolve();blob=p.read_bytes();assert hashlib.sha256(blob).hexdigest()=='1b46560c9436b458b313e600ca93ce51f21744e537a20b9018f297a9c268f91a';(B/'coordinator-D88-hold-reference.json').write_text(json.dumps({'path':str(p),'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),'status':'Independent Main review HOLD0 per latest delegation; no prior credit changed; D88 not re-run','scope':'15PNG+3pages+3geos+12itemJSON+3gearconfig and bounded consumers reviewed by Main; semantic old-full-image comparison and binary/finalsignedUV/slot fiveviews remain pending'},ensure_ascii=False,indent=2)+'\n');print('pinned',len(rows),'root',c['tree']['sha'])
