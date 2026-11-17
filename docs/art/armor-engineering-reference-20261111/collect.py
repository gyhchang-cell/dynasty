from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
D=Path(__file__).resolve().parent
COMMIT='e63e4824800945eccf3684200a2c2270e2e1cdf2'
def main():
 t=json.loads((D/'tree.json').read_text());assert t['sha']==COMMIT and not t['truncated'];selected=[]
 for a in t['tree']:
  p=a['path'];n=p.rsplit('/',1)[-1];pick=n in ['FaradaySuitItem.java','SteelArmorItem.java','IEItems.java','ModelIEArmorBase.java']
  pick=pick or any(n==f'armor_{m}_{s}{ext}' and ('/textures/item/' in p or '/models/item/' in p) for m in ['steel','faraday'] for s in ['helmet','chestplate','leggings','boots'] for ext in ['.png','.json']) or any(n==f'armor_{m}{suffix}.png' and '/textures/models/' in p for m in ['steel','faraday'] for suffix in ['','_legs'])
  if pick:selected.append(a)
 def fetch(a):
  p=D/'source'/a['path'];p.parent.mkdir(parents=True,exist_ok=True);url=f'https://raw.githubusercontent.com/BluSunrize/ImmersiveEngineering/{COMMIT}/{a["path"]}'
  if not p.exists():subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--max-time','30',url,'-o',str(p)],check=True)
  b=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==a['sha'];return {'path':a['path'],'local':str(p.relative_to(D)),'url':url,'git_blob_sha1':a['sha'],'sha256':hashlib.sha256(b).hexdigest()}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(fetch,selected))
 (D/'provenance.json').write_text(json.dumps({'repository':'https://github.com/BluSunrize/ImmersiveEngineering','commit':COMMIT,'sources':rows,'source_collection_credit':0},ensure_ascii=False,indent=2)+'\n');print(len(rows),'pinned files')
if __name__=='__main__':main()
