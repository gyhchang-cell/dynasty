from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
B=Path(__file__).resolve().parent
repo='TelepathicGrunt/Bumblezone';commit='727844606bf41de151af9ae71e82caeaa72d04ce'
def curl(url,out):
 subprocess.run(['curl','--retry','2','-fsSL',url,'-o',str(out)],check=True)
curl(f'https://api.github.com/repos/{repo}/git/commits/{commit}',B/'commit-api.json')
c=json.loads((B/'commit-api.json').read_text());assert c['sha']==commit
curl(f"https://api.github.com/repos/{repo}/git/trees/{c['tree']['sha']}?recursive=1",B/'root-tree-api.json')
t=json.loads((B/'root-tree-api.json').read_text());assert not t['truncated']
paths=[]
for a in t['tree']:
 p=a['path']
 if a['type']!='blob':continue
 selected=p in ['gradle.properties','build.gradle'] or p.endswith(('/BeeArmorModel.java','/BeeArmorModelProvider.java','/ArmorModelProvider.java','/BzArmor.java','/BeeArmor.java','/BzArmorMaterials.java','/BzItems.java','/ForgeArmorProviders.java','/BzArmorMixin.java','/RegisterArmorProviderEvent.java'))
 selected|='assets/the_bumblezone/models/item/' in p and any(v in p for v in ['stingless_bee_helmet','bumble_bee_chestplate','honey_bee_leggings','carpenter_bee_boots'])
 selected|='textures/item/' in p and p.endswith('.png') and any(v in p for v in ['stingless_bee_helmet','bumble_bee_chestplate','honey_bee_leggings','carpenter_bee_boots'])
 selected|=p.endswith(('/bee_material_layer_1.png','/bee_material_layer_2.png','/repair_items/bee_armor.json'))
 if selected:paths.append(a)
def get(a):
 p=a['path'];out=B/'source'/p;out.parent.mkdir(parents=True,exist_ok=True)
 curl(f'https://raw.githubusercontent.com/{repo}/{commit}/{p}',out)
 b=out.read_bytes();g=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert g==a['sha'],p
 return {'path':p,'blob_sha1':g,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'url':f'https://github.com/{repo}/blob/{commit}/{p}'}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as e:rows=list(e.map(get,paths))
(B/'provenance.json').write_text(json.dumps({'repo':repo,'commit':commit,'root_tree':c['tree']['sha'],'files':rows},indent=2)+'\n')
for src,dst in [('/Users/a15356015027/.codex/user-preferences/texture-requirements.md','global-texture-requirements.txt'),('docs/art/USER_TEXTURE_REQUIREMENTS.md','project-texture-requirements.txt'),('docs/art/armor-arctic-whole-20261114/protected-after.json','protected-before.json'),('docs/art/armor-arctic-whole-20261114/priority-after.json','priority-before.json')]:
 (B/dst).write_bytes(Path(src).read_bytes())
print('Fetched',len(rows),'pinned files; root',c['tree']['sha'])
