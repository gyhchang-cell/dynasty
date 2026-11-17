"""Sync the verified Dynasty JAR and existing three exports, without UI/config/save changes."""
from pathlib import Path
import hashlib,json,shutil,zipfile,os
R=Path(__file__).resolve().parents[3];D=R/'docs/art/original-runtime-v7'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def replace(source,target):
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and sha(target)!=sha(source):
  backup=D/'installed-before'/sha(target)/target.name
  if not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
 temporary=target.with_name(target.name+'.dynasty-pending')
 shutil.copy2(source,temporary);os.replace(temporary,target)
 assert sha(source)==sha(target)
 return {'path':str(target),'sha256':sha(target)}
def sync():
 jar=R/'build/libs/dynasty-1.4.0.jar';blob=jar.read_bytes();jarsha=sha(jar)
 packs=['dynasty-1.4.0.mrpack','dynasty-1.4.0-modrinth.mrpack','dynasty-modpack-1.4.0.zip']
 for name in packs:
  with zipfile.ZipFile(R/'dist'/name) as z:
   assert z.read('overrides/mods/dynasty-1.4.0.jar')==blob,name+': stale embedded mod'
 base=Path('/Users/a15356015027/Public/.minecraft')
 targets=[R/'modpack/mods',R/'整合包实例/mods',Path('/Users/a15356015027/Desktop/导出/Dynasty模组')]
 if base.is_dir():
  targets.append(base/'mods')
  targets.extend(p/'mods' for p in (base/'versions').iterdir() if p.is_dir() and 'Dynasty' in p.name)
 results=[replace(jar,d/jar.name) for d in targets]
 out=Path('/Users/a15356015027/Desktop/导出/Dynasty整合包')
 results.extend(replace(R/'dist'/name,out/name) for name in packs)
 (D/'installed.json').write_text(json.dumps({'jarSha256':jarsha,'verifiedNestedJars':packs,'files':results,'runningReferenceInstance':'愚者chishi has no Dynasty JAR; untouched','clientRestarted':False,'savesModified':False},ensure_ascii=False,indent=2)+'\n')
 print('Verified and synchronized',len(results),'local game/export files; no UI or save changes')
if __name__=='__main__':sync()
