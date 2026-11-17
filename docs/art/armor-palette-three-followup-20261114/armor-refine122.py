from pathlib import Path
import json,hashlib,zipfile,shutil
r=Path.cwd();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for key in ['gravitite','obsidian','zanite']:
 b=r/'docs/art'/f'armor-{key}-whole-20261114';p=json.load(open(b/'provenance.json'));removed=[];keep=[]
 for e in p['entries']:
  if '/models/item/' in e['entry'] and not any(key+'_'+s in e['entry'] for s in ['helmet','chestplate','leggings','boots']):
   removed.append(e);(b/e['local']).unlink()
  else:keep.append(e)
 p['entries']=keep;p['pre_freeze_scope_refinement']={'removed_unrelated_item_models':[e['entry'] for e in removed],'reason':'bounded full armor only; ore/tool/pendant not armor evidence, no production or historic file removed'}
 z=zipfile.ZipFile(p['archive']);ids=['aether:'+key+'_'+s for s in ['helmet','chestplate','leggings','boots']];extra=[n for n in z.namelist() if n.startswith('data/aether/') and '/loot_tables/' in n and n.endswith('.json') and any(i.encode() in z.read(n) for i in ids) and n not in [x['entry'] for x in keep]]
 for n in extra:
  f=b/'source'/n;f.parent.mkdir(exist_ok=True,parents=True);f.write_bytes(z.read(n));p['entries'].append({'entry':n,'local':str(f.relative_to(b)),'sha256':H(f)})
 (b/'provenance.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
 old=r/'docs/art/armor-neptune-whole-20261114';c=json.load(open(old/'consumer-provenance.json'));assert H(Path(c['archive']))==c['archive_sha256']
 for e in c['files']:
  src=old/e['local'];assert H(src)==e['sha256'];dst=b/e['local'];dst.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(src,dst)
 c['reused_context_from']={'path':str(old/'consumer-provenance.json'),'sha256':H(old/'consumer-provenance.json'),'scope':'same vanilla engine and native AetherArmorItem contract reused, no PNGs reopened, no additional design credit'}
 (b/'consumer-provenance.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print(key,'kept',len(p['entries']),'filtered',len(removed),'addedloottables',extra)
