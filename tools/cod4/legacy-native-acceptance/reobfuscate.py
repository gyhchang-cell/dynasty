"""Build a QA-only packed SRG jar from a checked compile; no Gradle, launcher or game."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from artifact_inputs import load_resources

R = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
compile_path = R / sys.argv[1]
compiled = json.loads(compile_path.read_text())
assert compiled['status'] == 'PASS'
checks_path = R / sys.argv[2]
checks = json.loads(checks_path.read_text())
assert checks['status'] == 'PASS'
comparison_reuse = None
if checks['compile_receipt_sha256'] != sha(compile_path):
    # Extending the observer must not relabel an old comparator check as a test
    # of new code. Reuse only the exact previously checked core class bytes.
    checked_compile_path = R / checks['compile_receipt']
    assert sha(checked_compile_path) == checks['compile_receipt_sha256']
    checked_compile = json.loads(checked_compile_path.read_text())
    assert checked_compile['status'] == 'PASS'
    expected_core = {'com/dynasty/legacyqa/LegacyNativeQa.class', 'com/dynasty/legacyqa/LegacyNativeQa$Case.class'}
    assert set(checked_compile['classes']) == expected_core
    assert all(compiled['classes'][name] == digest for name, digest in checked_compile['classes'].items())
    assert all(compiled['sources'][name] == digest for name, digest in checked_compile['sources'].items())
    assert sha(R / checks['check_source']) == checks['check_source_sha256']
    for filename, digest in checks['runtime_library_files'].items():
        assert sha(Path(filename)) == digest, filename
    comparison_reuse = dict(previous_compile_sha256=sha(checked_compile_path),
                            identical_checked_classes=checked_compile['classes'],
                            scope='Prior34 comparator assertions reused only for identical core bytes; new world-reader code is not covered',
                            assertions_rerun=0)
for name, expected in compiled['sources'].items():
    assert sha(R / name) == expected, name
old = R / compiled['work']
for name, expected in compiled['classes'].items():
    assert sha(old / 'classes' / name) == expected, name
prior_path = R / 'docs/cod4/audit-20261022/legacy-migration-acceptance/legacy-migration-private-reobf08.json'
prior = json.loads(prior_path.read_text())
assert prior['status'] == 'PRIVATE_SRG_RENAMER_EXIT0_BYTECODE_REVIEW_PENDING' and prior['exit_code'] == 0
cmd = list(prior['command'])
tool = Path(cmd[cmd.index('-cp') + 1])
mapping = Path(cmd[cmd.index('--names') + 1])
assert sha(tool) == prior['tool_sha256']
assert sha(mapping) == prior['mapping_sha256']
assert sha(Path(cmd[0])) == checks['java_sha256']
assert compiled['compiler_sha256'] == checks['javac_sha256']
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
work = B / '.work' / ('reobf-' + stamp)
work.mkdir(parents=True, exist_ok=False)
dependencies = work / 'dependency-cache'
dependencies.mkdir()
for option, source, expected in [('-cp', tool, prior['tool_sha256']), ('--names', mapping, prior['mapping_sha256'])]:
    destination = work / source.name
    shutil.copyfile(source, destination)
    assert sha(destination) == expected
    cmd[cmd.index(option) + 1] = str(destination)
libraries = {}
for i, value in enumerate(cmd[:-1]):
    if value == '--lib':
        source = Path(cmd[i + 1]); digest = sha(source)
        destination = dependencies / (str(len(libraries)).zfill(4) + '-' + source.name)
        shutil.copyfile(source, destination)
        assert sha(destination) == digest
        libraries[str(destination)] = {'sha256': digest, 'origin': str(source)}
        cmd[i + 1] = str(destination)
input_jar = work / 'legacy-qa-mojmap.jar'
output_jar = work / 'dynasty-legacy-native-acceptance-1.0.jar'
payload = {name: (old / 'classes' / name).read_bytes() for name in compiled['classes']}
for name, digest in compiled['classes'].items():
    assert hashlib.sha256(payload[name]).hexdigest() == digest, name
resource_prefix = B.relative_to(R).as_posix() + '/resources/'
expected_resources = {name.removeprefix(resource_prefix): digest for name, digest in compiled['sources'].items() if name.startswith(resource_prefix)}
assert len(expected_resources) == 2
load_resources(B / 'resources', expected_resources)
payload.update(load_resources(old / 'frozen/resources', expected_resources))
payload['META-INF/MANIFEST.MF'] = b'Manifest-Version: 1.0\r\n\r\n'
assert {n for n in payload if n.endswith('.class')} == {
    'com/dynasty/legacyqa/LegacyNativeQa.class',
    'com/dynasty/legacyqa/LegacyNativeQa$Case.class',
    'com/dynasty/legacyqa/LegacyWorldRead.class',
}
assert all(n.startswith('com/dynasty/legacyqa/') for n in payload if n.endswith('.class'))
with zipfile.ZipFile(input_jar, 'x', zipfile.ZIP_DEFLATED) as z:
    for name, data in sorted(payload.items()):
        entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(entry, data)
cmd[cmd.index('--input') + 1] = str(input_jar)
cmd[cmd.index('--output') + 1] = str(output_jar)
(work / 'command.json').write_text(json.dumps(cmd, indent=2) + '\n')
run = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
(work / 'reobf.log').write_text(run.stdout + run.stderr)
for name, row in libraries.items():
    assert sha(Path(name)) == row['sha256'], name
entries = {}
if output_jar.exists():
    with zipfile.ZipFile(output_jar) as z:
        assert z.testzip() is None and len(z.namelist()) == len(set(z.namelist()))
        assert {i.filename for i in z.infolist() if not i.is_dir()} == set(payload)
        assert all(i.file_size == 0 for i in z.infolist() if i.is_dir())
        for name in payload:
            data = z.read(name)
            if not name.endswith('.class'):
                assert data == payload[name], name
            entries[name] = hashlib.sha256(data).hexdigest()
result = dict(status='PASS' if run.returncode == 0 else 'FAIL', exit_code=run.returncode,
              compile_receipt=str(compile_path.relative_to(R)), compile_receipt_sha256=sha(compile_path),
              comparison_receipt=str(checks_path.relative_to(R)), comparison_receipt_sha256=sha(checks_path),
              comparator_reuse=comparison_reuse,
              sources=compiled['sources'], output=str(output_jar.relative_to(R)),
              output_sha256=sha(output_jar) if output_jar.exists() else None,
              entries=entries, libraries=libraries, java_sha256=sha(Path(cmd[0])),
              mapping_sha256=sha(mapping), tool_sha256=sha(tool),
              prior_reobf_receipt_sha256=sha(prior_path), work=str(work.relative_to(R)),
              packaging_sources={str(p.relative_to(R)): sha(p) for p in [Path(__file__), B / 'artifact_inputs.py']},
              warnings=[line for line in (run.stdout + run.stderr).splitlines() if 'warn' in line.lower() or 'conflicting' in line.lower()],
              native_linkage_verified=False, game_starts=0, runtime_approved=False,
              production_jar_written=False, checklist_deletions=0)
target = R / 'docs/cod4/audit-20261022/legacy-native-acceptance' / ('reobf-' + stamp + '.json')
for p in [work / 'receipt.json', target]:
    with p.open('x') as f:
        json.dump(result, f, indent=2); f.write('\n')
print(json.dumps({'status': result['status'], 'receipt': str(target.relative_to(R)), 'qa_sha256': result['output_sha256'],
                  'entries': len(entries), 'warnings': len(result['warnings']), 'game_starts': 0}))
raise SystemExit(run.returncode)
