from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
D=Path(__file__).resolve().parent;COMMIT='2639a983eb9e3352517aed6dc03994a50e84883f';REPO='TeamPneumatic/pnc-repressurized'
def main():
 tree=json.loads((D/'tree.json').read_text());assert not tree['truncated'];selected=[]
 for a in tree['tree']:
  p=a['path'];name=p.rsplit('/',1)[-1];pick=name in ['ModItems.java','PneumaticArmorItem.java','CompressedIronArmorItem.java','ClientSetup.java','Textures.java','Names.java','ColorHandlers.java','EnderVisorClientHandler.java']
  pick=pick or '/textures/armor/' in p and name.startswith(('pneumatic_','compressed_iron_')) or '/textures/item/' in p and name.startswith(('pneumatic_helmet','pneumatic_chestplate','pneumatic_leggings','pneumatic_boots','compressed_iron_helmet','compressed_iron_chestplate','compressed_iron_leggings','compressed_iron_boots')) and name.endswith('.png')
  pick=pick or '/models/item/' in p and name in [f'{f}_{s}.json' for f in ['pneumatic','compressed_iron'] for s in ['helmet','chestplate','leggings','boots']]
  if pick:selected.append(a)
 def fetch(a):
  p=D/'source'/a['path'];p.parent.mkdir(parents=True,exist_ok=True);url=f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/{a["path"]}'
  if not p.exists():subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--max-time','25',url,'-o',str(p)],check=True)
  b=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==a['sha'];return {'path':a['path'],'local':str(p.relative_to(D)),'url':url,'git_blob_sha1':a['sha'],'sha256':hashlib.sha256(b).hexdigest()}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(fetch,selected))
 (D/'provenance.json').write_text(json.dumps({'repository':'https://github.com/'+REPO,'commit':COMMIT,'sources':rows,'collection_credit':0},indent=2)+'\n');print(len(rows),'fixed native source files')
if __name__=='__main__':main()
