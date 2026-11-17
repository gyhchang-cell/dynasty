"""Clear only recognised Gradle task-output cache archives, never dependency sources."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,stat,subprocess,tarfile

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/maintenance/storage-cleanup-20261116/continued'
assert not (OUT/'derived-cache-deletion-report.json').exists()
homes=[ROOT/p for p in [
 'tools/cod4/ecology-acceptance/.work/gradle-home',
 'tools/cod4/ecology-acceptance/.work/client-build/gradle-home',
 'tools/cod4/ecology-acceptance/.work/cross-build/gradle-home',
 'tools/cod4/interaction-acceptance/.work/gradle-home',
 'tools/cod4/mob-load-acceptance/.work/gradle-home',
 'tools/cod4/armor-acceptance/.work/gradle-home']]
roots=[p/'caches/build-cache-1' for p in homes]
assert not (OUT/'derived-build-cache-reference-files.txt').read_text().strip()
opened=subprocess.run(['/usr/sbin/lsof','-nP','-Fpn'],capture_output=True,text=True)
assert opened.returncode==0
in_use={str(p) for p in roots if any(line.startswith('n'+str(p)+'/') or line=='n'+str(p) for line in opened.stdout.splitlines())}
def sig(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
plan=[];preserved=[]
for root in roots:
 assert root.resolve()==root and root.is_dir()
 if str(root) in in_use:
  preserved.append({'path':str(root),'reason':'Open handle; preserve entire cache'});continue
 for p in root.iterdir():
  s=p.lstat()
  if not stat.S_ISREG(s.st_mode) or not re.fullmatch('[0-9a-f]{32}',p.name):
   preserved.append({'path':str(p),'reason':'Not a recognised task-output archive; retained'});continue
  before=sig(p)
  try:
   with tarfile.open(p,'r|*') as t:
    first=t.next()
    assert first and first.name=='METADATA' and first.isfile() and first.size<262144
    metadata=t.extractfile(first).read()
    assert b'buildInvocationId' in metadata or b'executionTime' in metadata
   h=hashlib.sha256()
   with p.open('rb') as f:
    for b in iter(lambda:f.read(1048576),b''):h.update(b)
   assert sig(p)==before
  except Exception as exc:
   preserved.append({'path':str(p),'reason':'Archive validation not established: '+type(exc).__name__});continue
  plan.append({'path':str(p),'bytes':s.st_size,'allocated_bytes':s.st_blocks*512,'stat':before,'sha256':h.hexdigest(),'metadata_sha256':hashlib.sha256(metadata).hexdigest(),'purpose':'Generated Gradle task output cache; original source and compiled deliverables retained; no explicit source/receipt path binding found.'})
with (OUT/'derived-cache-verified-plan.json').open('x') as f:json.dump({'delete':plan,'preserved':preserved},f,indent=2)
free_before=shutil.disk_usage(ROOT).free
for r in plan:
 p=Path(r['path']);assert sig(p)==r['stat'] and p.resolve()==p
 p.unlink()
assert all(not Path(r['path']).exists() for r in plan)
report={'at':datetime.datetime.now().astimezone().isoformat(),'deleted_archives':len(plan),'deleted_logical_bytes':sum(r['bytes'] for r in plan),'allocated_bytes_before':sum(r['allocated_bytes'] for r in plan),'preserved_non_archive_entries':preserved,'free_before':free_before,'free_after':shutil.disk_usage(ROOT).free,'permanent_delete_no_trash':True,'dependency_sources_and_forge_caches_untouched':True,'runtime_pack_unchanged':True,'effect':'A future explicitly authorised compile may take longer because task outputs must be recalculated; existing modpack/game launch is unaffected.'}
with (OUT/'derived-cache-deletion-report.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(report),flush=True)
