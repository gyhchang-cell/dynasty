"""Remove only stale temporary objects explicitly classified as Git garbage."""
from pathlib import Path
import datetime, hashlib, json, os, re, shutil, stat, subprocess, time

ROOT = Path('/Users/a15356015027/Desktop/dynasty')
OUT = ROOT / 'docs/maintenance/storage-cleanup-20261116'

def run(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def sig(p):
    s=p.lstat()
    assert stat.S_ISREG(s.st_mode)
    return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]

assert ROOT.resolve() == ROOT
assert not (OUT/'git-garbage-deletion.json').exists()
check=run(['git','fsck','--connectivity-only','--no-dangling'])
assert check.returncode==0, check.stderr
refs=run(['git','show-ref','--head']); assert refs.returncode==0
assert refs.stdout==(OUT/'git-refs-before.stdout').read_text()
index=ROOT/'.git/index'; index_sha=sha(index)
count=run(['git','count-objects','-v']); assert count.returncode==0
paths=[]
for line in count.stderr.splitlines():
    m=re.fullmatch(r'warning: garbage found: (\.git/objects/(?:pack/tmp_pack_[A-Za-z0-9]+|[0-9a-f]{2}/tmp_obj_[A-Za-z0-9]+))',line)
    assert m, line
    paths.append(ROOT/m.group(1))
assert paths and len(paths)==len(set(paths))
for p in paths:
    assert p.resolve()==p and p.is_relative_to(ROOT/'.git/objects')
    assert time.time()-p.stat().st_mtime > 7*86400
for name in ['.git/index.lock','.git/gc.pid','.git/objects/pack/lock']:
    assert not (ROOT/name).exists(), name
opened=run(['/usr/sbin/lsof','-nP','-Fpn']); assert opened.returncode==0
assert not any(line[1:] in {str(p) for p in paths} for line in opened.stdout.splitlines() if line.startswith('n'))
normal_packs=sorted(p.name for p in (ROOT/'.git/objects/pack').iterdir() if not p.name.startswith('tmp_'))
plan=[]
for p in paths:
    before=sig(p); digest=sha(p); assert sig(p)==before
    plan.append({'path':str(p),'bytes':p.stat().st_size,'allocated_bytes':p.stat().st_blocks*512,'stat':before,'sha256':digest,'reason':'Git count-objects explicitly classified abandoned temporary object as garbage; older than seven days, no open handle; repository connectivity passes.'})
with (OUT/'git-garbage-plan.json').open('x') as f: json.dump(plan,f,indent=2)
free_before=shutil.disk_usage(ROOT).free
for row in plan:
    p=Path(row['path']); assert sig(p)==row['stat']
    p.unlink()
    print(json.dumps({'deleted':str(p),'bytes':row['bytes']}),flush=True)
after=run(['git','fsck','--connectivity-only','--no-dangling'])
(OUT/'git-fsck-after.stdout').write_text(after.stdout)
(OUT/'git-fsck-after.stderr').write_text(after.stderr)
assert after.returncode==0, after.stderr
assert run(['git','show-ref','--head']).stdout==refs.stdout
assert sha(index)==index_sha
assert sorted(p.name for p in (ROOT/'.git/objects/pack').iterdir())==normal_packs
after_count=run(['git','count-objects','-v'])
(OUT/'git-count-after.stdout').write_text(after_count.stdout)
(OUT/'git-count-after.stderr').write_text(after_count.stderr)
assert 'garbage: 0\n' in after_count.stdout and not after_count.stderr
report={'at':datetime.datetime.now().astimezone().isoformat(),'deleted_files':len(plan),'deleted_logical_bytes':sum(x['bytes'] for x in plan),'deleted_allocated_bytes':sum(x['allocated_bytes'] for x in plan),'free_before':free_before,'free_after':shutil.disk_usage(ROOT).free,'git_connectivity_before_and_after_pass':True,'all_refs_and_index_unchanged':True,'normal_pack_files_unchanged':True,'permanent_delete_no_trash':True}
with (OUT/'git-garbage-deletion.json').open('x') as f: json.dump(report,f,indent=2)
print(json.dumps(report),flush=True)
