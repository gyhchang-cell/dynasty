"""Prepare an isolated current-source snapshot; never writes shared build outputs."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
WORK = BASE / '.work'
p = argparse.ArgumentParser()
p.add_argument('--refresh-source', action='store_true', help='Archive the old private snapshot and freeze current sources; do not use during a running test.')
args = p.parse_args()
WORK.mkdir(exist_ok=True)
frozen = WORK / 'frozen'
if frozen.exists() and args.refresh_source:
    frozen.rename(WORK / ('frozen-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S')))
if not frozen.exists():
    frozen.mkdir()
    for relative in ['src/main/java', 'src/main/resources', 'src/generated/resources']:
        src = ROOT / relative
        if src.exists():
            dest = frozen / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['cp', '-cR', str(src), str(dest)], check=True)
    hashes = {str(f.relative_to(frozen)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(frozen.rglob('*')) if f.is_file()}
    (BASE / 'evidence/frozen-source-sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
else:
    print('Reusing existing frozen source. Use --refresh-source for a new snapshot after a source edit.')
private_home = WORK / 'gradle-home'
private_home.mkdir(exist_ok=True)
for name in ['caches', 'wrapper', 'native', 'jdks']:
    src = Path.home() / '.gradle' / name
    dest = private_home / name
    if src.exists() and not dest.exists():
        subprocess.run(['cp', '-cR', str(src), str(dest)], check=True)
print('Private source, Gradle user home, project cache and outputs are under', WORK)
