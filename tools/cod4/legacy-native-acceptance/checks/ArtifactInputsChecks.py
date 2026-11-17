"""Exercise the reported frozen-resource exploit without running Java or changing real inputs."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import tempfile
import zipfile

B = Path(__file__).resolve().parents[1]
R = B.parents[2]
sys.path.insert(0, str(B))
from artifact_inputs import load_resources

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = 0


def rejected(root, expected):
    global checks
    try:
        load_resources(root, expected)
    except ValueError:
        checks += 1
        return
    raise AssertionError('Unreviewed resource mutation accepted')


with tempfile.TemporaryDirectory(prefix='legacy-artifact-check-', dir=B / '.work') as directory:
    root = Path(directory)
    metadata = root / 'META-INF/mods.toml'
    metadata.parent.mkdir()
    metadata.write_bytes(b'original synthetic metadata')
    expected = {'META-INF/mods.toml': sha(metadata)}
    assert load_resources(root, expected)['META-INF/mods.toml'] == metadata.read_bytes(); checks += 1
    metadata.write_bytes(b'changed synthetic metadata'); rejected(root, expected)
    metadata.write_bytes(b'original synthetic metadata')
    extra = root / 'unreviewed.txt'; extra.write_bytes(b'addition'); rejected(root, expected); extra.unlink()
    metadata.unlink(); rejected(root, expected)
    elsewhere = root / 'elsewhere'; elsewhere.write_bytes(b'original synthetic metadata')
    metadata.symlink_to(elsewhere); rejected(root, expected)

compile_path = R / sys.argv[1]
reobf_path = R / sys.argv[2]
compiled, reobf = [json.loads(p.read_text()) for p in [compile_path, reobf_path]]
prefix = B.relative_to(R).as_posix() + '/resources/'
expected = {n.removeprefix(prefix): digest for n, digest in compiled['sources'].items() if n.startswith(prefix)}
current = load_resources(B / 'resources', expected)
frozen = load_resources(R / compiled['work'] / 'frozen/resources', expected)
assert current == frozen; checks += 1
jar = R / reobf['output']
assert sha(jar) == reobf['output_sha256']
with zipfile.ZipFile(jar) as archive:
    for name, data in frozen.items():
        assert archive.read(name) == data; checks += 1
result = dict(status='PASS_FROZEN_RESOURCE_REJECTION_AND_CURRENT_ARTIFACT_BINDING', checks=checks,
              compile_receipt=str(compile_path.relative_to(R)), compile_receipt_sha256=sha(compile_path),
              reobf_receipt=str(reobf_path.relative_to(R)), reobf_receipt_sha256=sha(reobf_path),
              resource_files=expected, qa_sha256=sha(jar), existing_jar_unchanged=True,
              tool_sources={str(p.relative_to(R)): sha(p) for p in [Path(__file__), B / 'artifact_inputs.py', B / 'reobfuscate.py']},
              java_runs=0, game_starts=0, native_acceptance=False, checklist_deletions=0)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
target = R / 'docs/cod4/audit-20261022/legacy-native-acceptance' / ('resource-bindings-' + stamp + '.json')
with target.open('x') as f:
    json.dump(result, f, indent=2); f.write('\n')
print(json.dumps({'status': result['status'], 'checks': checks, 'receipt': str(target.relative_to(R)), 'qa_sha256': result['qa_sha256']}))
