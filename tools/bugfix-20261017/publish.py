"""Publish only this fix's compiled classes, languages, atlas and quest definitions."""
from pathlib import Path
import json,zipfile,hashlib,shutil,os,io
R=Path(__file__).resolve().parents[2];O=R/'docs/bugfix-20261017';B=O/'install-backup';B.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'deployment.json').exists()
keys=['com/dynasty/DynastyCompassBridge.class','com/dynasty/DynastyUsables$PillItem.class','com/dynasty/client/DynastyHealthHud.class','com/dynasty/client/DynastyInfoKeys.class','com/dynasty/client/DynastyItemUsage.class','assets/dynasty/lang/zh_cn.json','assets/dynasty/lang/en_us.json','assets/minecraft/atlases/blocks.json']
with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:patch={k:z.read(k) for k in keys}
for k,v in patch.items():
 if k.startswith('assets/'):assert v==(R/'src/main/resources'/k).read_bytes(),('stale build',k)
quests={p.relative_to(R/'modpack').as_posix():p.read_bytes() for p in (R/'modpack/config/ftbquests/quests').rglob('*.snbt')}
records=[];cache={}
def save(): (O/'deployment-in-progress.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
def rewrite(p,changes):
 before=sha(p)
 with zipfile.ZipFile(p) as z:
  assert set(changes)<=set(z.namelist()),('missing existing member',str(p),set(changes)-set(z.namelist()))
  if all(z.read(k)==v for k,v in changes.items()):return
 backup=B/before/p.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(p,backup)
 temp=p.with_name(p.name+'.bugfix17-pending')
 cachekey=(before,tuple((k,hashlib.sha256(v).hexdigest()) for k,v in sorted(changes.items())))
 if cachekey in cache:shutil.copy2(cache[cachekey],temp)
 else:
  with zipfile.ZipFile(p) as z,zipfile.ZipFile(temp,'w') as out:
   out.comment=z.comment
   for entry in z.infolist():out.writestr(entry,changes.get(entry.filename,z.read(entry.filename)))
 with zipfile.ZipFile(p) as z,zipfile.ZipFile(temp) as out:
  for entry in z.infolist():
   if entry.filename in changes:assert out.read(entry.filename)==changes[entry.filename]
   else:assert out.getinfo(entry.filename).CRC==entry.CRC
 assert sha(p)==before,('concurrent edit',str(p))
 os.replace(temp,p);cache[cachekey]=p;records.append({'path':str(p),'before':before,'after':sha(p),'changed':list(changes)});save();print('Updated',p,flush=True)
base=Path('/Users/a15356015027/Public/.minecraft')
jars=[R/'modpack/mods/dynasty-1.4.0.jar',R/'整合包实例/mods/dynasty-1.4.0.jar',base/'mods/dynasty-1.4.0.jar',Path('/Users/a15356015027/Desktop/导出/Dynasty模组/dynasty-1.4.0.jar')]+list((base/'versions').glob('Dynasty*/mods/dynasty-1.4.0.jar'))
for p in jars:
 if p.exists():rewrite(p,patch)
exports=[]
for root in [R/'dist',Path('/Users/a15356015027/Desktop/导出/Dynasty整合包')]:
 for name in ['dynasty-1.4.0.mrpack','dynasty-1.4.0-modrinth.mrpack','dynasty-modpack-1.4.0.zip']:
  p=root/name
  if not p.exists():continue
  with zipfile.ZipFile(p) as z:blob=z.read('overrides/mods/dynasty-1.4.0.jar')
  tmp=B/('embedded-'+hashlib.sha256(blob).hexdigest()+'.jar')
  if not tmp.exists():tmp.write_bytes(blob);rewrite(tmp,patch)
  changes={'overrides/mods/dynasty-1.4.0.jar':tmp.read_bytes()};changes.update({'overrides/'+k:v for k,v in quests.items()});rewrite(p,changes);exports.append(p)
# Existing unpacked release instance: preserve its options and saves.
for root in [R/'整合包实例']:
 for k,data in quests.items():
  p=root/k
  if not p.exists():continue
  if p.read_bytes()==data:continue
  dest=B/'instance-config'/k;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);p.write_bytes(data)
for p in jars+exports:
 if not p.exists():continue
 with zipfile.ZipFile(p) as z:
  jar=z if p.suffix=='.jar' else zipfile.ZipFile(io.BytesIO(z.read('overrides/mods/dynasty-1.4.0.jar')))
  assert all(jar.read(k)==v for k,v in patch.items()),p
  if p in exports:assert all(z.read('overrides/'+k)==v for k,v in quests.items()),p
(O/'deployment.json').write_text(json.dumps({'records':records,'verified_jars':len([p for p in jars if p.exists()]),'verified_exports':len(exports),'patch_members':keys,'quest_files':len(quests),'game_client_started':False,'github_pushed':False},ensure_ascii=False,indent=2))
print('Verified narrowly published bug fixes and quest exports.')
