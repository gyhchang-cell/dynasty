"""Replace only the built Dynasty core JAR in the existing three exports."""
from pathlib import Path
import zipfile,hashlib,json,os,tempfile
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
jar=(R/'build/libs/dynasty-1.4.0.jar').read_bytes();member='overrides/mods/dynasty-1.4.0.jar';reports=[]
for name in ['dynasty-1.4.0.mrpack','dynasty-1.4.0-modrinth.mrpack','dynasty-modpack-1.4.0.zip']:
 p=R/'dist'/name;original=p.read_bytes();beforehash=sha(original)
 backup=D/'before/exports'/beforehash/name;backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():os.link(p,backup)
 before={};fd,temp=tempfile.mkstemp(prefix=name+'.pending-',dir=p.parent);os.close(fd)
 try:
  with zipfile.ZipFile(p) as src,zipfile.ZipFile(temp,'w') as dst:
   assert len(src.namelist())==len(set(src.namelist()))
   assert member in src.namelist();dst.comment=src.comment
   for info in src.infolist():
    b=src.read(info.filename);before[info.filename]=sha(b);dst.writestr(info,jar if info.filename==member else b)
  with zipfile.ZipFile(temp) as dst:
   assert dst.testzip() is None
   assert set(dst.namelist())==set(before)
   for k,h in before.items():assert sha(dst.read(k))==(sha(jar) if k==member else h),k
  assert sha(p.read_bytes())==beforehash,'Concurrent export changed: '+name
  os.replace(temp,p)
  reports.append({'file':name,'beforeSha256':beforehash,'afterSha256':sha(p.read_bytes()),'onlyReplacedMember':member,'otherEntriesUnchanged':len(before)-1,'coreJarSha256':sha(jar),'namesUnchanged':True,'crcVerified':True})
 finally:
  if os.path.exists(temp):os.unlink(temp)
(D/'export-validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
print('3 existing archives verified; only core JAR replaced; all other entry payloads preserved')
