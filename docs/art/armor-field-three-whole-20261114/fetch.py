from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
B=Path(__file__).resolve().parent;prior=Path('docs/art/armor-dungeons-three-whole-20261114').resolve();d=json.loads((prior/'provenance.json').read_text());repo=d['repo'];commit=d['commit']
for n in ['commit-api.json','root-tree-api.json']:(B/n).write_bytes((prior/n).read_bytes())
t=json.loads((B/'root-tree-api.json').read_text());lookup={x['path']:x for x in t['tree']};names=['climbing','spelunker','snow'];paths=[]
for n in names:
 paths += [f'src/main/resources/data/dungeons_gear/gearconfig/armor/{n}_armor.json',f'src/main/resources/assets/dungeons_gear/geo/armor/{n}_armor.geo.json',f'src/main/resources/assets/dungeons_gear/textures/models/armor/{n}_armor.png']
 for slot in ['helmet','chestplate','leggings','boots']:
  paths += [f'src/main/resources/assets/dungeons_gear/textures/item/armor/{n}_{slot}.png',f'src/generated/resources/assets/dungeons_gear/models/item/{n}_{slot}.json']
assert all(p in lookup for p in paths),[p for p in paths if p not in lookup]
def get(p):
 o=B/'source'/p;o.parent.mkdir(parents=True,exist_ok=True);url=f'https://raw.githubusercontent.com/{repo}/{commit}/{p}';subprocess.run(['curl','--retry','2','-fsSL',url,'-o',str(o)],check=True);b=o.read_bytes();g=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();assert g==lookup[p]['sha'];return {'path':p,'blob_sha1':g,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'url':f'https://github.com/{repo}/blob/{commit}/{p}'}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as e:rows=list(e.map(get,paths))
shared=['gradle.properties','build.gradle','src/main/java/com/infamous/dungeons_gear/registry/ItemInit.java','src/main/java/com/infamous/dungeons_gear/registry/ArmorSetInit.java']
for p in shared:
 a=next(x for x in d['files'] if x['path']==p);o=B/'source'/p;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes((prior/'source'/p).read_bytes());assert hashlib.sha256(o.read_bytes()).hexdigest()==a['sha256'];rows.append(dict(a,reused_from=str(prior/'source'/p)))
(B/'provenance.json').write_text(json.dumps({'repo':repo,'commit':commit,'root_tree':d['root_tree'],'files':rows,'root_api_reused_from':str(prior)},indent=2)+'\n')
for src,dst in [('/Users/a15356015027/.codex/user-preferences/texture-requirements.md','global-texture-requirements.txt'),('docs/art/USER_TEXTURE_REQUIREMENTS.md','project-texture-requirements.txt'),(str(prior/'protected-after.json'),'protected-before.json'),(str(prior/'priority-after.json'),'priority-before.json')]: (B/dst).write_bytes(Path(src).read_bytes())
# Prior references are directly discoverable, and read-only: no redoing completed study.
old_review=json.loads((prior/'viewed-image-paths.json').read_text());originals=[]
for row in old_review:
 p=Path(row['path']).resolve();assert p.is_file();originals.append(dict(row,absolute_path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
pages=[]
for n in ['evocation_robes','mercenary','reinforced_mail']:
 p=prior/f'{n}-source-study.png';pages.append({'design':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'upstream integer-NN research page, NOT Dynasty production or game'})
index={'batch':'D88','receipt':str(next(prior.glob('bounded-receipt-*.json'))),'delivery':str(prior/'coordinator-delivery.json'),'review':str(prior/'semantic-review.json'),'readme':str(prior/'README.md'),'study_pages':pages,'originals':originals,'consumer_context':{'provenance':str(prior/'consumer-provenance.json'),'sha256':hashlib.sha256((prior/'consumer-provenance.json').read_bytes()).hexdigest(),'requested_vs_context':'D88 Gear requests3.0.10/Gecko3.1.40; context3.0.12/Gecko3.1.39, equivalence still unproven; no new acceptance'}}
(B/'prior-D88-view-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n');print('pinned',len(rows),'new references',names,'D88 pages',len(pages),'D88 originals',len(originals))
