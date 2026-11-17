"""Remove only the five previously audited duplicate Gradle distributions."""
from pathlib import Path
import ast, datetime, hashlib, json, shutil, subprocess

ROOT = Path('/Users/a15356015027/Desktop/dynasty')
OUT = ROOT/'docs/maintenance/storage-cleanup-20261116/continued'
REPORT = OUT/'wrapper-cache-deletion-report.json'
assert not REPORT.exists()
plan_path = OUT/'wrapper-cache-duplicates-plan.json'
plan = json.loads(plan_path.read_text())
# Reuse the read-only manifest implementation without executing the old cleanup.
module = ast.parse((OUT.parent/'delete_repeated_forge_cache.py').read_text())
fn = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'tree')
import os, stat
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<manifest-only>', 'exec'))
KEEP = ROOT/'tools/cod4/ecology-acceptance/.work/gradle-home/wrapper'
ALLOWED = {str(ROOT/p/'wrapper') for p in [
    'tools/cod4/ecology-acceptance/.work/client-build/gradle-home',
    'tools/cod4/ecology-acceptance/.work/cross-build/gradle-home',
    'tools/cod4/interaction-acceptance/.work/gradle-home',
    'tools/cod4/mob-load-acceptance/.work/gradle-home',
    'tools/cod4/armor-acceptance/.work/gradle-home']}
assert plan['keeper'] == str(KEEP)
assert {c['path'] for c in plan['copies']} == ALLOWED
assert tree(KEEP) == plan['keeper_rows']
keeper = {r['path']: r for r in plan['keeper_rows']}
for c in plan['copies']:
    assert c['exact_subset'] and not c['reference_hits']
    assert tree(Path(c['path'])) == c['rows']
    assert all(keeper.get(r['path']) == r for r in c['rows'])
opened = subprocess.run(['/usr/sbin/lsof', '-nP', '-Fpn'], capture_output=True, text=True)
assert opened.returncode == 0
hits = [line for line in opened.stdout.splitlines() if line.startswith('n')
        and any(line[1:] == p or line[1:].startswith(p+'/') for p in ALLOWED | {str(KEEP)})]
assert not hits, hits
free_before = shutil.disk_usage(ROOT).free
removed = []
for c in plan['copies']:
    p = Path(c['path'])
    assert p.resolve() == p and p.name == 'wrapper' and p.parent.name == 'gradle-home'
    assert tree(p) == c['rows']
    shutil.rmtree(p)
    assert not p.exists()
    removed.append({'path': str(p), 'bytes': c['bytes']})
    print(json.dumps(removed[-1]), flush=True)
assert tree(KEEP) == plan['keeper_rows']
report = {
    'at': datetime.datetime.now().astimezone().isoformat(),
    'plan_sha256': hashlib.sha256(plan_path.read_bytes()).hexdigest(),
    'removed': removed, 'logical_bytes_deleted': sum(c['bytes'] for c in removed),
    'keeper': str(KEEP), 'keeper_verified_after': True,
    'free_before': free_before, 'free_after': shutil.disk_usage(ROOT).free,
    'permanent_delete_no_trash': True,
    'note': 'Only derived Gradle wrapper distributions. Project gradlew, wrapper configuration/JAR, game files, source dependencies and frozen QA snapshots are unchanged. Future development must use the retained complete project Gradle home instead of blindly reseeding historical copies. APFS shared blocks can make physical recovery smaller than logical deletion.'}
with REPORT.open('x') as f:
    json.dump(report, f, indent=2)
print(json.dumps(report), flush=True)
