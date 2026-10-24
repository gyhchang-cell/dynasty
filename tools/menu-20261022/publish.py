"""Deliver only the verified menu/help classes; preserve every unrelated jar entry."""
from pathlib import Path
import json,hashlib,zipfile,io,os,shutil
R=Path(__file__).resolve().parents[2];OUT=R/'docs/menu-20261022';BACK=OUT/'backups'
OWNERS=('RoundedUi','DynastyTitleScreen','DynastyItemInfo','DynastyWorldMenus')
def digest(data):return hashlib.sha256(data).hexdigest()
def patch(data,changes):
 result=io.BytesIO()
 with zipfile.ZipFile(io.BytesIO(data)) as old,zipfile.ZipFile(result,'w',zipfile.ZIP_DEFLATED) as new:
  new.comment=old.comment
  names=set(old.namelist())
  assert len(names)==len(old.namelist()),'Duplicate source zip names'
  for info in old.infolist():new.writestr(info,changes.get(info.filename,old.read(info.filename)))
  for name,value in changes.items():
   if name not in names:new.writestr(name,value)
 data=result.getvalue()
 with zipfile.ZipFile(io.BytesIO(data)) as new:
  assert new.testzip() is None
  for name,value in changes.items():assert new.read(name)==value
 return data
records=[]
def write(path,data,changed_names):
 old=path.read_bytes()
 if old==data:return
 backup=BACK/digest(old)/(path.name+'.entries.zip');backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():
  with zipfile.ZipFile(io.BytesIO(old)) as source,zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as saved:
   for key in changed_names:
    if key in source.namelist():saved.writestr(key,source.read(key))
 assert path.read_bytes()==old,('Concurrent change',path)
 temp=path.with_name(path.name+'.menu-pending');temp.write_bytes(data);os.replace(temp,path)
 records.append({'path':str(path),'before':digest(old),'after':digest(data),'backup':str(backup)})
 print('Updated',path,flush=True)
 (OUT/'deployment.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
assert not (OUT/'native/FAIL.txt').exists()
assert (OUT/'native/PASS.txt').exists()
with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as jar:
 changes={n:jar.read(n) for n in jar.namelist() if any(n=='com/dynasty/client/'+k+'.class' or n.startswith('com/dynasty/client/'+k+'$') for k in OWNERS)}
assert all('com/dynasty/client/'+k+'.class' in changes for k in OWNERS)
BASE=Path('/Users/a15356015027/Public/.minecraft');EXPORT=Path('/Users/a15356015027/Desktop/导出')
targets=[R/'modpack/mods/dynasty-1.4.0.jar',R/'整合包实例/mods/dynasty-1.4.0.jar',BASE/'mods/dynasty-1.4.0.jar',EXPORT/'Dynasty模组/dynasty-1.4.0.jar']+list((BASE/'versions').glob('Dynasty*/mods/dynasty-1.4.0.jar'))
for p in dict.fromkeys(targets):
 if p.exists():write(p,patch(p.read_bytes(),changes),changes)
for folder in [R/'dist',EXPORT/'Dynasty整合包']:
 for name in ['dynasty-1.4.0.mrpack','dynasty-1.4.0-modrinth.mrpack','dynasty-modpack-1.4.0.zip']:
  p=folder/name
  if not p.exists():continue
  with zipfile.ZipFile(p) as z:
   key='overrides/mods/dynasty-1.4.0.jar'
   if key not in z.namelist():continue
   updated=patch(z.read(key),changes)
  write(p,patch(p.read_bytes(),{key:updated}),[key])
(OUT/'payload.json').write_text(json.dumps({k:digest(v) for k,v in changes.items()},indent=2))
print('Delivered',len(changes),'class files to',len(records),'targets',flush=True)
