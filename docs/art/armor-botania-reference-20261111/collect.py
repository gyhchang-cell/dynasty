from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 tree=json.loads((D/'tree-root.json').read_text());commit=json.loads((D/'commit.json').read_text());assert commit['commit']['tree']['sha']==tree['sha'] and not tree['truncated'];items=[]
 for a in tree['tree']:
  p=a['path'];name=p.rsplit('/',1)[-1]
  pick=('/client/model/armor/' in p and p.endswith('.java')) or '/common/item/equipment/armor/' in p and p.endswith('.java') or p.endswith('BotaniaItems.java') or p.endswith('ItemManasteelArmorForgeMixin.java')
  pick=pick or ('/textures/item/' in p and name.endswith('.png') and any(name==f'{m}_{s}.png' for m in ['manasteel','elementium','terrasteel','manaweave'] for s in ['helmet','chestplate','leggings','boots'])) or ('/textures/model/armor_' in p and name in [f'armor_{m}.png' for m in ['manasteel','elementium','terrasteel','manaweave']])
  pick=pick or name in ['BotaniaModelLayers.java','BotaniaLayerDefinitions.java','ClientProxy.java','ResourcesLib.java','LibItemNames.java'] or ('/models/item/' in p and name.endswith('.json') and any(name==f'{m}_{t}.json' for m in ['manasteel','elementium','terrasteel','manaweave'] for t in ['helmet','chestplate','leggings','boots']))
  if pick:items.append(a)
 def fetch(a):
  p=a['path'];local=D/'source'/p;local.parent.mkdir(parents=True,exist_ok=True);url=f'https://raw.githubusercontent.com/VazkiiMods/Botania/{commit["sha"]}/{p}'
  if not local.exists():subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--max-time','30',url,'-o',str(local)],check=True)
  b=local.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==a['sha'],p
  return {'path':p,'local':str(local.relative_to(D)),'url':url,'git_blob_sha1':a['sha'],'sha256':sha(b),'bytes':len(b)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(fetch,items))
 out={'repository':'https://github.com/VazkiiMods/Botania','commit':commit['sha'],'tree':tree['sha'],'sources':rows,'fetch_method':'system curl default TLS verification; git blob SHA1 additionally checked','production_changes':0,'game_starts':0,'credit_from_collection':0};(D/'provenance.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(f'{len(rows)} pinned native source/PNG files; no design credit from collection.')
if __name__=='__main__':main()
