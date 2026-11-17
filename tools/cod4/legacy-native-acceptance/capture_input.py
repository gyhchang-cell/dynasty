"""Read the already-prepared original-world copy with native NBT, never load/write a game save."""
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
basis_path = R / sys.argv[1]
basis = json.loads(basis_path.read_text())
assert basis['status'] == 'PASS' and basis['native_acceptance'] is False
libraries = basis['runtime_library_files']
for filename, digest in libraries.items():
    assert sha(Path(filename)) == digest, filename
java_bin = Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin')
assert sha(java_bin / 'java') == basis['java_sha256']
assert sha(java_bin / 'javac') == basis['javac_sha256']
input_path = R / 'docs/cod4/audit-20261022/old-world-acceptance/post-fix-fresh-copy-input.json'
original_manifest_path = R / 'docs/cod4/audit-20261022/old-world-acceptance/original-file-sha256.json'
input_receipt = json.loads(input_path.read_text())
original = Path(input_receipt['source'])
copy = Path(input_receipt['copy'])
expected = input_receipt['source_files_sha256']
assert expected == json.loads(original_manifest_path.read_text())


def manifest(root):
    assert root.resolve(strict=True) == root
    result = {}
    for p in sorted(root.rglob('*')):
        assert not p.is_symlink(), p
        if p.is_file():
            result[str(p.relative_to(root))] = sha(p)
    return result


assert manifest(original) == manifest(copy) == expected
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
work = B / '.work' / ('input-' + stamp)
work.mkdir(parents=True, exist_ok=False)
classes, empty = work / 'classes', work / 'empty'
classes.mkdir(); empty.mkdir()
source = B / 'checks/ReadLegacyInput.java'
frozen = work / source.name
shutil.copy2(source, frozen)
cp = ':'.join(libraries)
compile_cmd = [str(java_bin / 'javac'), '-J-Djava.awt.headless=true', '--release', '17', '-proc:none', '-sourcepath', str(empty),
               '-classpath', cp, '-d', str(classes), str(frozen)]
capture = work / 'native-input.json'
run_cmd = [str(java_bin / 'java'), '-Xmx256M', '-Djava.awt.headless=true', '-classpath', str(classes) + ':' + cp,
           'com.dynasty.legacyqa.ReadLegacyInput', str(copy / 'level.dat'),
           str(copy / 'playerdata/380df991-f603-344c-a090-369bad2a924a.dat'), str(capture)]
(work / 'commands.json').write_text(json.dumps([compile_cmd, run_cmd], indent=2) + '\n')
compiled = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=45)
(work / 'compile.log').write_text(compiled.stdout + compiled.stderr)
ran = subprocess.run(run_cmd, capture_output=True, text=True, timeout=30) if compiled.returncode == 0 else None
if ran is not None:
    (work / 'capture.log').write_text(ran.stdout + ran.stderr)
assert manifest(original) == manifest(copy) == expected, 'Read-only inputs changed during capture'
native = json.loads(capture.read_text()) if capture.exists() else None
result = dict(status='PASS_READ_ONLY_NATIVE_NBT_INPUT' if ran is not None and ran.returncode == 0 else 'FAIL',
              compile_exit_code=compiled.returncode, run_exit_code=None if ran is None else ran.returncode,
              output=compiled.stdout + compiled.stderr + ('' if ran is None else ran.stdout + ran.stderr),
              work=str(work.relative_to(R)), source=str(source.relative_to(R)), source_sha256=sha(frozen),
              basis=str(basis_path.relative_to(R)), basis_sha256=sha(basis_path),
              input_receipt_sha256=sha(input_path), original_manifest_sha256=sha(original_manifest_path),
              original_files_verified=len(expected), original_and_copy_unchanged=True,
              native_capture=None if native is None else {'path': str(capture.relative_to(R)), 'sha256': sha(capture)},
              native_input=native, runtime_libraries_verified=len(libraries),
              game_starts=0, world_or_player_constructed=False, native_remap_or_clone_executed=False,
              native_acceptance=False, reference_credit=0, checklist_deletions=0)
target = R / 'docs/cod4/audit-20261022/legacy-native-acceptance' / ('native-input-' + stamp + '.json')
for p in [work / 'receipt.json', target]:
    with p.open('x') as f:
        json.dump(result, f, indent=2); f.write('\n')
print(result['output'])
print(json.dumps({'status': result['status'], 'receipt': str(target.relative_to(R)), 'verified_original_files': len(expected), 'game_starts': 0}))
raise SystemExit(0 if result['status'] == 'PASS_READ_ONLY_NATIVE_NBT_INPUT' else 1)
