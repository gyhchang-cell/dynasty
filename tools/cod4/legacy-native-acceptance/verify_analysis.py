"""Check the descriptive old-world analysis tool offline, using typed NBT only."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess

R = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
basis_path = R / 'docs/cod4/audit-20261022/legacy-native-acceptance/comparison-checks-20261102T122757-214883Z.json'
assert sha(basis_path) == 'c0013610865e049fa53c86814cdc01330430c9b32cbedd9740238b30bce5d7e9'
basis = json.loads(basis_path.read_text())
for filename, expected in basis['runtime_library_files'].items():
    assert sha(Path(filename)) == expected, filename
java_bin = Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin')
assert sha(java_bin / 'java') == basis['java_sha256'] and sha(java_bin / 'javac') == basis['javac_sha256']
input_path = B / '.work/input-20261102T122852-069354Z/native-input.json'
assert sha(input_path) == '24fab4f75478434beea34d092ed831210fa7f4fcc09636ab12c0bdf643bb0e13'
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
work = B / '.work' / ('analysis-checks-' + stamp)
work.mkdir(parents=True, exist_ok=False)
sources = {}
for name in ['AnalyzeWorldRead.java', 'AnalysisChecks.java']:
    source = B / 'checks' / name
    frozen = work / name
    shutil.copy2(source, frozen)
    assert sha(source) == sha(frozen)
    sources[str(source.relative_to(R))] = sha(frozen)
fixture = work / 'historical-input.json'
shutil.copy2(input_path, fixture)
assert sha(fixture) == sha(input_path)
classes, empty = work / 'classes', work / 'empty'
classes.mkdir(); empty.mkdir()
cp = ':'.join(basis['runtime_library_files'])
compile_cmd = [str(java_bin / 'javac'), '-J-Djava.awt.headless=true', '--release', '17', '-proc:none',
               '-sourcepath', str(empty), '-classpath', cp, '-d', str(classes)] + [str(work / name) for name in ['AnalyzeWorldRead.java', 'AnalysisChecks.java']]
run_cmd = [str(java_bin / 'java'), '-Xmx256M', '-Djava.awt.headless=true', '-classpath', str(classes) + ':' + cp,
           'com.dynasty.legacyqa.AnalysisChecks', str(fixture)]
(work / 'commands.json').write_text(json.dumps([compile_cmd, run_cmd], indent=2) + '\n')
compiled = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=45)
(work / 'compile.log').write_text(compiled.stdout + compiled.stderr)
ran = subprocess.run(run_cmd, capture_output=True, text=True, timeout=30) if compiled.returncode == 0 else None
if ran is not None:
    (work / 'checks.log').write_text(ran.stdout + ran.stderr)
result = dict(status='PASS' if ran is not None and ran.returncode == 0 else 'FAIL',
              sources=sources, wrapper_sha256=sha(Path(__file__)), historical_input_sha256=sha(fixture),
              compile_exit=compiled.returncode, run_exit=None if ran is None else ran.returncode,
              output=compiled.stdout + compiled.stderr + ('' if ran is None else ran.stdout + ran.stderr),
              work=str(work.relative_to(R)), runtime_library_files=basis['runtime_library_files'],
              classes={str(p.relative_to(classes)): sha(p) for p in classes.rglob('*.class')},
              java_sha256=sha(java_bin / 'java'), javac_sha256=sha(java_bin / 'javac'),
              scope='New analysis-tool synthetic cases over actual historical input; no live result comparison, registry, world, player or event',
              game_starts=0, native_acceptance=False, checklist_deletions=0)
target = R / 'docs/cod4/audit-20261022/legacy-native-acceptance' / ('analysis-checks-' + stamp + '.json')
with target.open('x') as f:
    json.dump(result, f, indent=2); f.write('\n')
print(result['output'])
print(json.dumps({'status': result['status'], 'receipt': str(target.relative_to(R)), 'game_starts': 0}))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
