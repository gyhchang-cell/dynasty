"""Local byte-preserving reference extraction; never executed upstream source."""
from pathlib import Path
import zipfile,json,hashlib,math
from PIL import Image,ImageDraw
ROOT=Path.cwd();BASE=ROOT/'docs/art/armor-material-three-20261112'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def extract(archive,folder,predicate,repo,commit):
 b=ROOT/'docs/art'/folder;b.mkdir(exist_ok=True);z=zipfile.ZipFile(archive);prefix=z.namelist()[0];entries={}
 for n in z.namelist():
  rel=n[len(prefix):]
  if not n.endswith('/') and predicate(rel):
   p=b/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n));entries[rel]=sha(p)
 save(b/'provenance.json',{'repository':repo,'commit':commit,'archive':str(archive),'archive_sha256':sha(archive),'entries':entries,'external_source_executed':False})
 return b
if __name__=='__main__':
 a=BASE/'Atum2-fixed.zip';m=json.loads((BASE/'Atum2-inventory.json').read_text())
 b=extract(a,'armor-wanderer-whole-20261112',lambda p: (p.endswith('.java') and any(s in p for s in ['WandererDyeableArmor','TexturedArmorItem','AtumArmorMaterials','Atum.java','ItemRegistry.java','AtumRegistry.java','ClientProxy.java','RegistryHandler.java','AtumItems.java','RegistryEventHandler.java'])) or ('wanderer' in p and p.endswith(('.json','.png'))) or p.endswith(('gradle.properties','mods.toml','LICENSE')),m['repository'],m['commit'])
 print(b)
