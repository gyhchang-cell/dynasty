"""Prepare a Git repack without deleting any original pack or unreachable object."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, time

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/maintenance/storage-cleanup-20261116/continued'
assert not (OUT/'repack-prepared.json').exists()
assert not (OUT/'repack-start.json').exists()

def run(args, timeout=300):
 return subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=timeout)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

for name in ['.git/index.lock','.git/gc.pid','.git/objects/pack/lock']:
 assert not (ROOT/name).exists(),name
check=run(['git','fsck','--connectivity-only','--no-dangling'])
(OUT/'repack-connectivity-before.stderr').write_text(check.stderr)
assert check.returncode==0,check.stderr
oids=run(['git','cat-file','--batch-all-objects','--batch-check=%(objectname)'])
assert oids.returncode==0,oids.stderr
before_set=set(oids.stdout.splitlines());assert all(len(x)==40 for x in before_set)
(OUT/'all-object-ids-before.txt').write_text('\n'.join(sorted(before_set))+'\n')
refs=run(['git','show-ref','--head']);assert refs.returncode==0
(OUT/'refs-before-repack.txt').write_text(refs.stdout)
old_packs=sorted((ROOT/'.git/objects/pack').glob('*.pack'))
assert not list((ROOT/'.git/objects/pack').glob('*.keep'))
assert not list((ROOT/'.git/objects/pack').glob('*.promisor'))
index_sha=sha(ROOT/'.git/index')
start={'at':datetime.datetime.now().astimezone().isoformat(),'old_packs':[{'path':str(p),'bytes':p.stat().st_size} for p in old_packs],'all_object_count_before':len(before_set),'index_sha256':index_sha,'free_before':shutil.disk_usage(ROOT).free,'command':['nice','-n','10','git','-c','gc.auto=0','-c','maintenance.auto=false','repack','-a','--keep-unreachable','--window=10','--window-memory=64m','--threads=2'],'original_packs_retained_at_this_stage':True}
assert start['free_before']>sum(p.stat().st_size for p in old_packs)*3
(OUT/'repack-start.json').write_text(json.dumps(start,indent=2)+'\n')
print(json.dumps({'stage':'building_new_pack_originals_retained','all_objects_before':len(before_set),'old_pack_count':len(old_packs)}),flush=True)
with (OUT/'repack-build.stdout').open('x') as stdout,(OUT/'repack-build.stderr').open('x') as stderr:
 proc=subprocess.Popen(start['command'],cwd=ROOT,stdout=stdout,stderr=stderr,start_new_session=True)
 began=time.monotonic()
 while proc.poll() is None:
  if time.monotonic()-began>900:
   os.killpg(proc.pid,15)
   try:proc.wait(timeout=20)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,9);proc.wait()
   raise TimeoutError('Repack stopped; original packs retained')
  time.sleep(2)
 assert proc.returncode==0,(OUT/'repack-build.stderr').read_text()[-3000:]
after_oids=run(['git','cat-file','--batch-all-objects','--batch-check=%(objectname)'])
assert after_oids.returncode==0,after_oids.stderr
after_set=set(after_oids.stdout.splitlines());assert before_set<=after_set
assert sha(ROOT/'.git/index')==index_sha
assert all(p.is_file() for p in old_packs),'Original pack unexpectedly removed'
after_packs=sorted((ROOT/'.git/objects/pack').glob('*.pack'))
new=[p for p in after_packs if p not in old_packs]
report={'at':datetime.datetime.now().astimezone().isoformat(),'all_old_objects_still_present':True,'all_object_count_before':len(before_set),'all_object_count_after':len(after_set),'index_unchanged':True,'old_packs_still_present':True,'old_pack_bytes':sum(p.stat().st_size for p in old_packs),'new_packs':[{'path':str(p),'bytes':p.stat().st_size} for p in new],'returncode':proc.returncode,'elapsed_seconds':time.monotonic()-began,'no_old_pack_deleted_yet':True}
(OUT/'repack-prepared.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
