from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
D=Path(__file__).resolve().parent;COMMIT='2c74064bc753600d9b6600f102f8163e2d6764dd'
def main():
 t=json.loads((D/'tree.json').read_text());assert t['sha']==COMMIT and not t['truncated'];selected=[]
 for a in t['tree']:
  p=a['path'];n=p.rsplit('/',1)[-1];pick=n in ['AnimatedMagicArmor.java','ArmorRenderer.java','GenericModel.java','ItemsRegistry.java','RegistryHelper.java','Materials.java','LibItemNames.java','ClientHandler.java','ItemModelGenerator.java']
  pick=pick or '/geo/' in p and n in ['heavy_armor.geo.json','medium_armor.geo.json','light_armor.geo.json'] or '/textures/item/' in p and any(f'/{m}_armor/' in p for m in ['heavy','medium','light']) and (n.endswith(('_tint.png','_gold.png','_blue.png','_purple.png')) or n in ['light_armor.png','medium_armor.png']) or '/models/item/' in p and n.endswith('.json') and n.startswith(('arcanist_','sorcerer_','battlemage_'))
  if pick:selected.append(a)
 def fetch(a):
  p=D/'source'/a['path'];p.parent.mkdir(parents=True,exist_ok=True);url=f'https://raw.githubusercontent.com/baileyholl/Ars-Nouveau/{COMMIT}/{a["path"]}'
  if not p.exists():subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--max-time','30',url,'-o',str(p)],check=True)
  b=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==a['sha'];return {'path':a['path'],'local':str(p.relative_to(D)),'url':url,'git_blob_sha1':a['sha'],'sha256':hashlib.sha256(b).hexdigest()}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(fetch,selected))
 (D/'provenance.json').write_text(json.dumps({'repository':'https://github.com/baileyholl/Ars-Nouveau','commit':COMMIT,'sources':rows,'collection_credit':0},ensure_ascii=False,indent=2)+'\n');print(len(rows),'pinned source declarations and native assets')
if __name__=='__main__':main()
