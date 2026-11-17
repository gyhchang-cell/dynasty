"""Read-only comparison: only two known old Dynasty backups versus live project."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import os
import stat

PROJECT = Path('/Users/a15356015027/Desktop/dynasty')
REPORT = PROJECT / 'docs/maintenance/storage-cleanup-20261115'
CASES = [
    ('MC-maintenance-20261024', 'uncommitted-backup'),
    ('MC-upload-20261026', 'backup'),
]
DOCS = Path('/Users/a15356015027/Documents')
OUT = REPORT / 'verified-backup-duplicate-plan.json'
assert not OUT.exists(), 'Keep prior comparison; never silently replace plan'
cache = {}
def signature(s): return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]
def digest(p):
    before = p.stat(follow_symlinks=False)
    assert stat.S_ISREG(before.st_mode), str(p)
    key = tuple(signature(before))
    if key not in cache:
        h = hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
        assert signature(before) == signature(p.stat(follow_symlinks=False)), 'Changed while hashing: '+str(p)
        cache[key] = h.hexdigest()
    return cache[key], before

duplicate=[]; preserve=[]; summaries=[]
for folder,subdir in CASES:
    base=DOCS/folder; backup=base/subdir
    assert backup.is_dir() and not backup.is_symlink()
    manifest=json.loads((base/'backup-manifest.json').read_text())
    rows=manifest['records'] if isinstance(manifest,dict) else manifest
    expected={r['path']:r for r in rows if 'sha256' in r and 'bytes' in r}
    counts=collections.Counter(); by_reason=collections.Counter(); sizes=collections.Counter()
    for walkroot,dirs,files in os.walk(backup,followlinks=False):
        for name in list(dirs):
            p=Path(walkroot)/name
            if p.is_symlink(): dirs.remove(name);preserve.append(dict(path=str(p),reason='symlink'));counts['preserve']+=1
        for name in files:
            p=Path(walkroot)/name; relative=str(p.relative_to(backup)); keeper=PROJECT/relative
            s=p.lstat(); reason=None
            if not stat.S_ISREG(s.st_mode):reason='not_regular'
            elif relative not in expected:reason='not_in_original_backup_manifest'
            elif s.st_size != expected[relative]['bytes']:reason='backup_differs_from_original_manifest_size'
            elif not keeper.is_file():reason='no_live_project_counterpart'
            elif keeper.is_symlink() or keeper.resolve()!=keeper:reason='live_symlink_or_symlink_parent'
            elif s.st_size!=keeper.stat().st_size:reason='different_live_size'
            else:
                a,actual=digest(p);b,live=digest(keeper)
                if a!=expected[relative]['sha256']:reason='backup_differs_from_original_manifest_hash'
                elif a!=b:reason='different_live_content'
                else:
                    duplicate.append(dict(path=str(p),keeper=str(keeper),sha256=a,bytes=s.st_size,allocated_bytes=s.st_blocks*512,backup_stat=signature(actual),keeper_stat=signature(live),backup_manifest=str(base/'backup-manifest.json'),reason='Pinned backup bytes exactly equal retained live project counterpart',same_inode=(actual.st_dev,actual.st_ino)==(live.st_dev,live.st_ino)))
                    counts['duplicate']+=1;sizes['duplicate_bytes']+=s.st_size;sizes['duplicate_allocated']+=s.st_blocks*512
            if reason:
                preserve.append(dict(path=str(p),reason=reason,bytes=s.st_size));counts['preserve']+=1;by_reason[reason]+=1;sizes['preserved_bytes']+=s.st_size
    summary=dict(root=str(backup),counts=dict(counts),bytes=dict(sizes),preserve_reasons=dict(by_reason));summaries.append(summary);print(json.dumps(summary),flush=True)
o=dict(schema='Dynasty-exact-retained-live-backup-duplicate-plan-v1',recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),user_authorized_direct_permanent_delete=True,scan_readonly=True,scope='Only exact identical files in two known backup roots. Keep all changed, missing, unknown, unmanifested and symbolic-link files. No mcmod/video/CrossOver/project originals touched.',summaries=summaries,duplicates=duplicate,preserved=preserve,planned_file_count=len(duplicate),planned_bytes=sum(x['bytes'] for x in duplicate))
with OUT.open('x')as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(plan=str(OUT),sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),files=len(duplicate),bytes=o['planned_bytes'],preserve=len(preserve))))
