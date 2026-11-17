"""Delete only explicitly verified duplicates; preserve all other files."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
from datetime import datetime, timezone

PROJECT = Path('/Users/a15356015027/Desktop/dynasty')
OUT = PROJECT / 'docs/maintenance/storage-cleanup-20261115'
ROOTS = [Path('/Users/a15356015027/Documents/MC-maintenance-20261024/uncommitted-backup'), Path('/Users/a15356015027/Documents/MC-upload-20261026/backup')]
PLAN = OUT / 'verified-backup-duplicate-plan.json'
EXPECTED = '42e3621fef77ed712e10cb268c8c60b58a4a0d84bf0332f62bf7b6428eaa349a'
APP_KEEP = Path('/Applications/SakuraLauncher 2.app')
APP_DELETE = Path('/Applications/SakuraLauncher 3.app')

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def signature(p):
    s = p.lstat()
    if not stat.S_ISREG(s.st_mode):
        raise ValueError('Not regular file: ' + str(p))
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]

def app_tree(root):
    assert root.is_dir() and root.resolve() == root
    records = []
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            p = Path(base) / name
            s = p.lstat()
            row = {'path': p.relative_to(root).as_posix(), 'mode': stat.S_IMODE(s.st_mode)}
            if stat.S_ISLNK(s.st_mode):
                row.update(type='symlink', target=os.readlink(p))
            elif stat.S_ISDIR(s.st_mode):
                row.update(type='directory')
            elif stat.S_ISREG(s.st_mode):
                before = signature(p)
                row.update(type='file', bytes=s.st_size, sha256=digest(p))
                assert signature(p) == before
            else:
                raise ValueError('Unexpected bundle entry ' + str(p))
            records.append(row)
    return sorted(records, key=lambda r: r['path'])

def save(p, data):
    with p.open('x') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

assert digest(PLAN) == EXPECTED
plan = json.loads(PLAN.read_text())
assert not (OUT / 'deletion-report.json').exists()
assert not (OUT / 'deleted-files.jsonl').exists()
assert all(r.resolve() == r for r in ROOTS)
assert PROJECT.resolve() == PROJECT
# Refuse deletion if any target is in use. Never stop a user process.
opened = subprocess.run(['/usr/sbin/lsof', '-nP', '-Fpn'], capture_output=True, text=True)
assert opened.returncode == 0, opened.stderr
targets = [str(r) + '/' for r in ROOTS] + [str(APP_DELETE) + '/']
in_use = [line[1:] for line in opened.stdout.splitlines() if line.startswith('n') and any(t in line[1:] for t in targets)]
assert not in_use, in_use
apps_keep_before = app_tree(APP_KEEP)
apps_delete_before = app_tree(APP_DELETE)
assert apps_keep_before == apps_delete_before and apps_keep_before
save(OUT / 'duplicate-software-verification.json', {'keeper': str(APP_KEEP), 'duplicate': str(APP_DELETE), 'entries': apps_keep_before, 'equal': True})
before_free = shutil.disk_usage(PROJECT).free
deleted_count = deleted_bytes = deleted_allocated = 0
skipped = []
post_failures = []
with (OUT / 'deleted-files.jsonl').open('x') as log:
    for row in plan['duplicates']:
        p, keeper = Path(row['path']), Path(row['keeper'])
        root = next((r for r in ROOTS if p.is_relative_to(r)), None)
        assert root is not None
        assert keeper == PROJECT / p.relative_to(root)
        try:
            assert p.resolve() == p and keeper.resolve() == keeper
            assert not row['same_inode']
            assert signature(p) == row['backup_stat']
            assert signature(keeper) == row['keeper_stat']
            assert digest(p) == row['sha256'] == digest(keeper)
            assert signature(p) == row['backup_stat']
            assert signature(keeper) == row['keeper_stat']
        except (OSError, AssertionError, ValueError) as e:
            skipped.append({'path': str(p), 'reason': type(e).__name__ + ': ' + str(e)})
            continue
        p.unlink()
        deleted_count += 1
        deleted_bytes += row['bytes']
        deleted_allocated += row['allocated_bytes']
        keeper_ok = keeper.exists() and signature(keeper) == row['keeper_stat']
        event = {'deleted': str(p), 'retained': str(keeper), 'sha256': row['sha256'], 'bytes': row['bytes'], 'retained_stat_unchanged': keeper_ok}
        log.write(json.dumps(event, ensure_ascii=False) + '\n')
        if not keeper_ok:
            post_failures.append(event)
            raise RuntimeError('Retained file changed; stopping')
        if deleted_count % 5000 == 0:
            log.flush()
            print(json.dumps({'deleted_files': deleted_count, 'deleted_bytes': deleted_bytes}), flush=True)
    log.flush()
    os.fsync(log.fileno())
removed_empty_dirs = 0
for root in ROOTS:
    for base, dirs, files in os.walk(root, topdown=False, followlinks=False):
        p = Path(base)
        if p != root and not p.is_symlink():
            try:
                p.rmdir()
                removed_empty_dirs += 1
            except OSError:
                pass
# Recheck both full application trees immediately before permanent removal.
assert app_tree(APP_KEEP) == apps_keep_before == app_tree(APP_DELETE)
shutil.rmtree(APP_DELETE)
assert not APP_DELETE.exists()
assert app_tree(APP_KEEP) == apps_keep_before
assert Path('/Applications/SakuraLauncher.app').is_dir()
preserved_missing = [r['path'] for r in plan['preserved'] if not Path(r['path']).exists()]
assert not preserved_missing, preserved_missing
after_free = shutil.disk_usage(PROJECT).free
report = {
    'at': datetime.now(timezone.utc).isoformat(),
    'plan_sha256': EXPECTED,
    'permanent_delete_no_trash': True,
    'backup_files_deleted': deleted_count,
    'backup_logical_bytes_deleted': deleted_bytes,
    'backup_allocated_bytes_before_delete': deleted_allocated,
    'empty_backup_subdirectories_removed': removed_empty_dirs,
    'skipped': skipped,
    'different_backup_files_preserved': len(plan['preserved']),
    'retained_original_stat_failures': post_failures,
    'software_deleted': str(APP_DELETE),
    'software_retained_identical': str(APP_KEEP),
    'software_bytes_deleted': sum(r.get('bytes', 0) for r in apps_delete_before),
    'software_remaining_tree_verified': True,
    'free_bytes_before': before_free,
    'free_bytes_after': after_free,
    'observed_free_bytes_change': after_free - before_free,
    'limitations': 'APFS sharing and unrelated system writes mean logical/allocated sizes need not equal physical space reclaimed. No Trash, running apps, user game instances, unique backups, or normal project files were removed.'
}
save(OUT / 'deletion-report.json', report)
print(json.dumps(report, ensure_ascii=False), flush=True)
