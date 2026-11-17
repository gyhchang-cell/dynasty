"""Compile a new frozen QA probe offline; never invokes Gradle, game or production code."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess

B = Path(__file__).resolve().parent
R = B.parents[2]
O = R / 'docs/cod4/audit-20261022/legacy-native-acceptance'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
W = B / '.work' / ('compile-' + stamp)
W.mkdir(parents=True, exist_ok=False)
old = R / 'tools/cod4/sweep-receipt-research/.work/receipt-fix/native-compile'
origin = R / 'docs/cod4/audit-20261022/sweep-receipt-research/offline-compile-receipt.json'
baseline = json.loads(origin.read_text())
for group, folder in [('private_dependency_snapshots', 'dependency-cache'),
                      ('baseline_classes_sha256', 'baseline'), ('affected_classes_sha256', 'classes')]:
    for relative, digest in baseline[group].items():
        p = R / digest['snapshot'] if group == 'private_dependency_snapshots' else old / folder / relative
        digest = digest['sha256'] if isinstance(digest, dict) else digest
        if not p.is_file() or sha(p) != digest:
            raise SystemExit('Frozen dependency changed: ' + str(p))
inputs = {}
for folder in ['src', 'resources']:
    for p in sorted((B / folder).rglob('*')):
        if p.is_file():
            q = W / 'frozen' / p.relative_to(B)
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, q)
            inputs[str(p.relative_to(R))] = sha(q)
cp = [old / 'classes', old / 'baseline'] + sorted((old / 'dependency-cache').glob('*.jar'))
if len(cp) != 903:
    raise SystemExit('Unexpected frozen dependency count')
classes, empty = W / 'classes', W / 'empty'
classes.mkdir()
empty.mkdir()
javac = Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javac')
cmd = [str(javac), '-J-Djava.awt.headless=true', '--release', '17', '-proc:none', '-encoding', 'UTF-8',
       '-sourcepath', str(empty), '-classpath', ':'.join(map(str, cp)), '-d', str(classes)]
cmd += [str(p) for p in sorted((W / 'frozen/src').rglob('*.java'))]
(W / 'command.json').write_text(json.dumps(cmd, indent=2) + '\n')
run = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
(W / 'compile.log').write_text(run.stdout + run.stderr)
receipt = dict(status='PASS' if run.returncode == 0 else 'FAIL', exit_code=run.returncode,
               recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), sources=inputs,
               classes={str(p.relative_to(classes)): sha(p) for p in sorted(classes.rglob('*.class'))},
               compiler=str(javac), compiler_sha256=sha(javac), work=str(W.relative_to(R)),
               classpath_snapshot=str(origin.relative_to(R)), classpath_snapshot_sha256=sha(origin),
               verified_dependency_files=sum(len(baseline[k]) for k in ['private_dependency_snapshots', 'baseline_classes_sha256', 'affected_classes_sha256']),
               native_event_executed=False, game_starts=0, production_mutations=0,
               reobfuscated=False, runtime_approved=False,
               scope='QA-only javac/API verification; no loading of Minecraft classes or event execution')
O.mkdir(parents=True, exist_ok=True)
target = O / ('offline-compile-' + stamp + '.json')
for p in [W / 'receipt.json', target]:
    with p.open('x') as f:
        json.dump(receipt, f, indent=2)
        f.write('\n')
print(run.stdout + run.stderr)
print(json.dumps({'status': receipt['status'], 'receipt': str(target.relative_to(R)), 'work': receipt['work'],
                  'classes': len(receipt['classes']), 'game_starts': 0}))
raise SystemExit(run.returncode)
