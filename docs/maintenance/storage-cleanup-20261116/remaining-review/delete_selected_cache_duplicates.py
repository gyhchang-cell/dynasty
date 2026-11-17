"""Delete only SHA-verified duplicate derived subtrees from the frozen plan."""
from pathlib import Path
import ast, datetime, hashlib, json, os, shutil, stat, subprocess

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/maintenance/storage-cleanup-20261116/remaining-review'
REPORT=OUT/'coordinator-cache-deletion-report.json'
JOURNAL=OUT/'coordinator-cache-deletion-journal.jsonl'
assert not REPORT.exists() and not JOURNAL.exists()
plan_path=OUT/'cache-duplicate-selection.json'
plan=json.loads(plan_path.read_text())
module=ast.parse((OUT.parent/'delete_repeated_forge_cache.py').read_text())
fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='tree')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<manifest-only>','exec'))
KEEP=ROOT/'tools/cod4/ecology-acceptance/.work/gradle-home/caches'
assert plan['keeper']==str(KEEP)
allowed=[ROOT/h/'caches' for h in [
 'tools/cod4/ecology-acceptance/.work/client-build/gradle-home',
 'tools/cod4/ecology-acceptance/.work/cross-build/gradle-home',
 'tools/cod4/interaction-acceptance/.work/gradle-home',
 'tools/cod4/mob-load-acceptance/.work/gradle-home',
 'tools/cod4/armor-acceptance/.work/gradle-home']]
assert plan['selected']
def verify_copy(s):
 # Some retained trees are strict supersets, as documented by the read-only plan.
 # Require every candidate path/content/mode/link to exist unchanged in keeper.
 a=tree(Path(s['path']));b={r['path']:r for r in tree(Path(s['keeper']))}
 assert a==s['rows'] and all(b.get(r['path'])==r for r in a)
paths=sorted(s['path'] for s in plan['selected'])
assert len(paths)==len(set(paths))
assert not any(b.startswith(a+'/') for a,b in zip(paths,paths[1:]))
for part,rows in plan['keeper_manifests'].items():
 assert tree(KEEP/part)==rows
for s in plan['selected']:
 p=Path(s['path']);k=Path(s['keeper'])
 assert s['part'] in ['jars-9','8.8','8.12.1','9.7.1']
 assert p.resolve()==p and k.resolve()==k
 assert any(p.is_relative_to(base/s['part']) for base in allowed)
 assert k.is_relative_to(KEEP/s['part'])
 verify_copy(s)
opened=subprocess.run(['/usr/sbin/lsof','-nP','-Fpn'],capture_output=True,text=True)
assert opened.returncode==0
# Reject handles in every selected tree and every retained comparison tree.
# Forge source/assets and bound modules are outside this deletion scope.
handle_roots=set(paths)|{s['keeper'] for s in plan['selected']}
participating_homes=[str(p) for p in allowed+[KEEP]]
open_paths=[l[1:] for l in opened.stdout.splitlines() if l.startswith('n')
            and '/tools/cod4/' in l
            and any(l[1:]==p or l[1:].startswith(p+'/') for p in participating_homes)]
def busy(s):
 return [n for n in open_paths if any(n==r or n.startswith(r+'/') for r in [s['path'],s['keeper']])]
skipped_busy=[{'path':s['path'],'keeper':s['keeper'],'open_paths':busy(s),'bytes':s['bytes']} for s in plan['selected'] if busy(s)]
selected=[s for s in plan['selected'] if not busy(s)]
assert selected
free_before=shutil.disk_usage(ROOT).free
removed=[]
with JOURNAL.open('x') as journal:
 for i,s in enumerate(selected):
  p=Path(s['path']);k=Path(s['keeper'])
  verify_copy(s)
  shutil.rmtree(p)
  assert not p.exists() and k.is_dir()
  rec={'path':str(p),'keeper':str(k),'bytes':s['bytes'],'files':sum(r['type']=='file' for r in s['rows'])}
  removed.append(rec);journal.write(json.dumps(rec)+'\n');journal.flush()
  if (i+1)%500==0:print('deleted_verified_subtrees',i+1,flush=True)
for part,rows in plan['keeper_manifests'].items():
 assert tree(KEEP/part)==rows
report={'at':datetime.datetime.now().astimezone().isoformat(),'plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),'deleted_subtrees':len(removed),'deleted_files':sum(r['files'] for r in removed),'logical_bytes_deleted':sum(r['bytes'] for r in removed),'skipped_busy_and_preserved':skipped_busy,'keeper_manifests_verified_before_and_after':True,'no_open_handles_in_deleted_or_keeper_trees_at_predelete_check':True,'bound_modules_and_forge_source_caches_preserved':True,'permanent_delete_no_trash':True,'free_before':free_before,'free_after':shutil.disk_usage(ROOT).free,'note':'Only unbound exact duplicate Gradle derived subtrees. Any busy selected tree is skipped. Different entries and all path-bound dependencies remain. APFS and concurrent specialist cleanup mean free-space delta is observational, not exclusive physical reclaim. Retained canonical Gradle home must be checked before future authorized builds; do not automatically reseed clones.'}
with REPORT.open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(report),flush=True)
