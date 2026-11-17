"""Delete only whole, verified-identical, unused cache trees from a fixed allowlist."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, stat, subprocess

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/maintenance/storage-cleanup-20261116'
KEEP=ROOT/'tools/cod4/ecology-acceptance/.work/gradle-home/caches/minecraftforge'
ALLOWED={str(ROOT/p/'caches/minecraftforge') for p in [
 'tools/cod4/ecology-acceptance/.work/client-build/gradle-home',
 'tools/cod4/ecology-acceptance/.work/cross-build/gradle-home',
 'tools/cod4/mob-load-acceptance/.work/gradle-home',
 'tools/cod4/armor-acceptance/.work/gradle-home']}

def tree(root):
 assert root.resolve()==root and root.is_dir()
 rows=[]
 for base,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   p=Path(base)/name;s=p.lstat()
   row={'path':str(p.relative_to(root)),'mode':stat.S_IMODE(s.st_mode)}
   if stat.S_ISLNK(s.st_mode):row.update(type='symlink',target=os.readlink(p))
   elif stat.S_ISDIR(s.st_mode):row.update(type='directory')
   elif stat.S_ISREG(s.st_mode):
    h=hashlib.sha256()
    with p.open('rb') as f:
     for b in iter(lambda:f.read(1048576),b''):h.update(b)
    assert p.stat().st_mtime_ns==s.st_mtime_ns and p.stat().st_size==s.st_size
    row.update(type='file',bytes=s.st_size,sha256=h.hexdigest())
   else:raise ValueError(str(p))
   rows.append(row)
 return sorted(rows,key=lambda r:r['path'])

assert not (OUT/'forge-cache-deletion-report.json').exists()
plan_path=OUT/'repeated-forge-cache-plan.json'
plan_sha=hashlib.sha256(plan_path.read_bytes()).hexdigest()
plan=json.loads(plan_path.read_text())
expected=json.loads((OUT/'retained-forge-cache-tree.json').read_text())
assert plan['retained']==str(KEEP)
assert tree(KEEP)==expected['rows']
copies=[r for r in plan['copies'] if r.get('equal_to_retained') and r.get('older_than_seven_days')]
assert {r['root'] for r in copies}==ALLOWED
opened=subprocess.run(['/usr/sbin/lsof','-nP','-Fpn'],capture_output=True,text=True)
assert opened.returncode==0
hits=[line[1:] for line in opened.stdout.splitlines() if line.startswith('n') and any(line[1:]==p or line[1:].startswith(p+'/') for p in ALLOWED)]
assert not hits,hits
for r in copies:
 p=Path(r['root']); manifest=json.loads(Path(r['manifest']).read_text())
 assert manifest['rows']==expected['rows']==tree(p)
 assert p.is_relative_to(ROOT/'tools/cod4') and p.name=='minecraftforge' and p.parent.name=='caches'
free_before=shutil.disk_usage(ROOT).free
deleted=[]
for r in copies:
 p=Path(r['root']);assert tree(p)==expected['rows']
 shutil.rmtree(p)
 assert not p.exists() and KEEP.is_dir()
 deleted.append(r)
 print(json.dumps({'deleted_cache':str(p),'logical_bytes':r['logical_bytes']}),flush=True)
assert tree(KEEP)==expected['rows']
assert (ROOT/'tools/cod4/interaction-acceptance/.work/gradle-home/caches/minecraftforge').is_dir()
report={'at':datetime.datetime.now().astimezone().isoformat(),'plan_sha256':plan_sha,'deleted_roots':[r['root'] for r in deleted],'logical_bytes_deleted':sum(r['logical_bytes'] for r in deleted),'allocated_bytes_before_delete':sum(r['allocated_bytes'] for r in deleted),'retained':str(KEEP),'retained_tree_sha256':expected['tree_sha256'],'retained_tree_verified_after':True,'reference_bound_interaction_cache_preserved':True,'free_before':free_before,'free_after':shutil.disk_usage(ROOT).free,'permanent_delete_no_trash':True,'note':'These were historical cp -cR cache seeds, so APFS shared blocks mean apparent directory size reduction may exceed physical space reclaimed. Existing source and QA receipts, frozen trees, worlds and forge_gradle cache source archives are untouched.'}
with (OUT/'forge-cache-deletion-report.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(report),flush=True)
