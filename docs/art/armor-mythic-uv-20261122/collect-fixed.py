from concurrent.futures import ThreadPoolExecutor
import hashlib, json, subprocess
from pathlib import Path
out=Path(__file__).resolve().parent
commit='2118186af2d5d418d2d41b91a4583ade6a1c39f6'
tree=json.loads((out/'github-tree.json').read_text())
assert tree['sha']==commit and not tree['truncated']
repo='https://github.com/Noaaan/MythicMetals'
paths={'gradle.properties'}
java='src/main/java/nourl/mythicmetals/'
paths.update(java+p+'.java' for p in ('MythicMetalsClient','armor/ArmorSet','armor/MythicArmor','armor/MythicArmorMaterials','armor/HallowedArmor','armor/HallowedArmorSet','client/models/HallowedArmorModel','client/models/MythicModelHandler','client/models/HelmetModel'))
for s in ('bronze','hallowed'):
 for slot in ('helmet','chestplate','leggings','boots'):
  paths.update(f'src/main/resources/assets/mythicmetals/{group}/{s}_{slot}.{ext}' for group,ext in [('models/item','json'),('textures/item/armor','png')])
 paths.update(f'src/main/resources/assets/minecraft/textures/models/armor/{s}_layer_{i}.png' for i in (1,2))
paths.add('src/main/resources/assets/mythicmetals/textures/models/hallowed_model.png')
entries={p['path']:p for p in tree['tree'] if p['type']=='blob'}
def collect(path):
 e=entries[path]
 assert e['size']<120000
 f=out/'source'/path
 u=f'https://raw.githubusercontent.com/Noaaan/MythicMetals/{commit}/{path}'
 data=f.read_bytes() if f.is_file() else subprocess.check_output(['curl','-fsSL','--max-time','18',u])
 assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==e['sha']
 f.parent.mkdir(parents=True,exist_ok=True)
 if not f.exists():f.write_bytes(data)
 return {'path':path,'blob_sha1':e['sha'],'sha256':hashlib.sha256(data).hexdigest(),'source_url':u}
with ThreadPoolExecutor(max_workers=5) as pool: result=list(pool.map(collect,sorted(paths)))
(out/'provenance.json').write_text(json.dumps({'repository':repo,'commit':commit,'files':result},indent=2)+'\n')
print(len(result))
