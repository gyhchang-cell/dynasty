"""Verify only the new QA comparator using native NBT; no mod constructor/game execution."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path = R / sys.argv[1]
compiled = json.loads(receipt_path.read_text())
assert compiled['status'] == 'PASS'
for relative, expected in compiled['sources'].items():
    assert sha(R / relative) == expected, relative
work = R / compiled['work']
for relative, expected in compiled['classes'].items():
    assert sha(work / 'classes' / relative) == expected, relative
# The discovery/compile cache contains several Minecraft versions. Use the already
# bound1.20.1 library order, not alphabetical discovery order (which selects authlib10).
basis_path = R / 'docs/cod4/audit-20261022/legacy-migration-acceptance/legacy-player-progression-field-matrix05.json'
assert sha(basis_path) == '00cadb7e277f91816230e20f919a60b1e6755ef60d01bedc4a2ad5ee74df41ea'
basis = json.loads(basis_path.read_text())['commands'][0]
classpath = ':'.join(p for p in basis[basis.index('-classpath') + 1].split(':') if Path(p).suffix == '.jar')
assert next(Path(p).name for p in classpath.split(':') if 'authlib-' in Path(p).name) == '0083-authlib-4.0.43.jar'
manifest_path = R / compiled['classpath_snapshot']
assert sha(manifest_path) == compiled['classpath_snapshot_sha256']
manifest = json.loads(manifest_path.read_text())
known_libraries = {str((R / row['snapshot']).resolve()): row['sha256'] for row in manifest['private_dependency_snapshots'].values()}
runtime_libraries = {}
for filename in classpath.split(':'):
    p = Path(filename)
    expected = known_libraries[str(p.resolve())]
    assert sha(p) == expected, filename
    runtime_libraries[filename] = expected
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
out = B / '.work' / ('comparison-' + stamp)
out.mkdir(parents=True, exist_ok=False)
source = B / 'checks/ComparisonChecks.java'
frozen = out / source.name
shutil.copy2(source, frozen)
fixture = R / 'build/cod4-legacy-fix-20261101/field-matrix05/audited-fields.snbt'
assert sha(fixture) == '269e730f3106206e6e827f4cf87ac04f889e0ee83d6a89c6dca9b4e524043c61'
shutil.copy2(fixture, out / 'audited-fields.snbt')
classes, empty = out / 'classes', out / 'empty'
classes.mkdir(); empty.mkdir()
cp = str(work / 'classes') + ':' + classpath
java_bin = Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin')
compile_cmd = [str(java_bin / 'javac'), '-J-Djava.awt.headless=true', '--release', '17', '-proc:none',
               '-sourcepath', str(empty), '-classpath', cp, '-d', str(classes), str(frozen)]
run_cmd = [str(java_bin / 'java'), '-Xmx256M', '-Djava.awt.headless=true', '-classpath', str(classes) + ':' + cp,
           'com.dynasty.legacyqa.ComparisonChecks', str(out / 'audited-fields.snbt')]
(out / 'commands.json').write_text(json.dumps([compile_cmd, run_cmd], indent=2) + '\n')
build = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=45)
(out / 'compile.log').write_text(build.stdout + build.stderr)
run = subprocess.run(run_cmd, capture_output=True, text=True, timeout=30) if build.returncode == 0 else None
if run is not None:
    (out / 'checks.log').write_text(run.stdout + run.stderr)
result = dict(status='PASS' if run is not None and run.returncode == 0 else 'FAIL',
              compile_exit_code=build.returncode, run_exit_code=None if run is None else run.returncode,
              compile_receipt=str(receipt_path.relative_to(R)), compile_receipt_sha256=sha(receipt_path),
              check_source=str(source.relative_to(R)), check_source_sha256=sha(frozen),
              fixture_sha256=sha(out / 'audited-fields.snbt'), work=str(out.relative_to(R)),
              library_order_basis=str(basis_path.relative_to(R)), library_order_basis_sha256=sha(basis_path),
              runtime_library_files=runtime_libraries,
              java_sha256=sha(java_bin / 'java'), javac_sha256=sha(java_bin / 'javac'),
              corrected_prior_failure='Alphabetical multi-version discovery cache selected authlib10; current order prioritizes1.20.1 authlib4.0.43. Original failed receipt retained.',
              output='' if run is None else run.stdout + run.stderr,
              scope='QA-only comparator with real NBT, no Mod constructor, player, Forge event, registry load or game',
              game_starts=0, native_acceptance=False, checklist_deletions=0)
target = R / 'docs/cod4/audit-20261022/legacy-native-acceptance' / ('comparison-checks-' + stamp + '.json')
for p in [out / 'receipt.json', target]:
    with p.open('x') as f:
        json.dump(result, f, indent=2); f.write('\n')
print(result['output'])
print(json.dumps({'status': result['status'], 'receipt': str(target.relative_to(R)), 'game_starts': 0}))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
