"""Delete the specialist's exact app backup duplicates and derived SDK module cache."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, stat, subprocess

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/maintenance/storage-cleanup-20261116'
MACRO=ROOT/'tools/mc-macro'
AUDIT=OUT/'mc-macro-audit.json'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def tree(root):
 assert root.is_dir() and root.resolve()==root
 rows=[]
 for base,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   p=Path(base)/name;s=p.lstat()
   row={'path':str(p.relative_to(root)),'mode':stat.S_IMODE(s.st_mode)}
   if stat.S_ISLNK(s.st_mode):row.update(type='symlink',target=os.readlink(p))
   elif stat.S_ISDIR(s.st_mode):row.update(type='directory')
   elif stat.S_ISREG(s.st_mode):
    row.update(type='file',bytes=s.st_size,sha256=sha(p))
    assert p.stat().st_mtime_ns==s.st_mtime_ns
   else:raise ValueError(str(p))
   rows.append(row)
 return sorted(rows,key=lambda r:r['path'])

assert not (OUT/'macro-deletion-report.json').exists()
audit_hash=sha(AUDIT);d=json.loads(AUDIT.read_text())
apps=[r for r in d['safe_deletion_candidates_for_coordinator_review'] if r['kind']=='exact_duplicate_app_backup']
assert len(apps)==25
cache=MACRO/'.build/module-cache'
assert cache.resolve()==cache and cache.is_dir()
assert (MACRO/'Sources').is_dir() and (MACRO/'Tests').is_dir() and (MACRO/'.build/sdk-compat').exists()
delete_roots=[Path(r['path']) for r in apps]+[cache]
for r in apps:
 p,k=Path(r['path']),Path(r['keep'])
 assert p.is_relative_to(MACRO/'.build/backups') and p.suffix=='.app'
 assert k.is_relative_to(MACRO) and all(not k.is_relative_to(x) for x in delete_roots)
opened=subprocess.run(['/usr/sbin/lsof','-nP','-Fpn'],capture_output=True,text=True)
assert opened.returncode==0
hits=[line[1:] for line in opened.stdout.splitlines() if line.startswith('n') and any(line[1:]==str(p) or line[1:].startswith(str(p)+'/') for p in delete_roots)]
assert not hits,hits
keepers={}; app_plans=[]
for r in apps:
 p,k=Path(r['path']),Path(r['keep'])
 a=tree(p);b=keepers.setdefault(str(k),tree(k))
 assert a==b and sum(x.get('bytes',0) for x in a)==r['logical_bytes']
 app_plans.append({'path':str(p),'keeper':str(k),'tree':a,'bytes':r['logical_bytes']})
cache_rows=d['module_cache_manifest'];actual=tree(cache)
assert not any(x['type']=='symlink' for x in actual)
actual_files={str(cache/x['path']):x for x in actual if x['type']=='file'}
assert set(actual_files)=={r['path'] for r in cache_rows}
assert len(actual_files)==444
for r in cache_rows:
 p=Path(r['path']);assert p.suffix in {'.pcm','.swiftmodule','.timestamp'}
 assert actual_files[r['path']]['sha256']==r['sha256'] and actual_files[r['path']]['bytes']==r['bytes']
assert sha(AUDIT)==audit_hash
plan={'audit_sha256':audit_hash,'apps':app_plans,'module_cache':actual,'module_cache_root':str(cache),'source_and_sdk_preserved':True}
with (OUT/'macro-verified-deletion-plan.json').open('x') as f:json.dump(plan,f,indent=2)
free_before=shutil.disk_usage(ROOT).free
for row in app_plans:
 p=Path(row['path']);k=Path(row['keeper'])
 assert tree(p)==row['tree']==tree(k)
 shutil.rmtree(p)
 assert tree(k)==row['tree'] and not p.exists()
assert tree(cache)==actual
shutil.rmtree(cache)
assert not cache.exists()
for k,rows in keepers.items():assert tree(Path(k))==rows
report={'at':datetime.datetime.now().astimezone().isoformat(),'audit_sha256':audit_hash,'app_backups_deleted':len(app_plans),'app_backup_logical_bytes':sum(r['bytes'] for r in app_plans),'derived_module_cache_files_deleted':len(actual_files),'module_cache_logical_bytes':sum(x['bytes'] for x in actual_files.values()),'all_kept_app_trees_verified_after':True,'source_sdk_and_dist_preserved':True,'free_before':free_before,'free_after':shutil.disk_usage(ROOT).free,'permanent_delete_no_trash':True}
with (OUT/'macro-deletion-report.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(report),flush=True)
