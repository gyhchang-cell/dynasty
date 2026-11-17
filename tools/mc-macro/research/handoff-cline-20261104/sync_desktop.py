"""Install the explicitly requested, verified candidate without launching it."""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import os
import plistlib
import stat
import subprocess

ROOT = Path('/Users/a15356015027/Desktop/dynasty/tools/mc-macro')
SOURCE = ROOT / '.build/candidates/cline-audit-20261104/app/mcPvPmax.app'
DESKTOP = Path('/Users/a15356015027/Desktop/mcPvPmax.app')
OLD_HASH = '246264c33f76c9f3e6fe720ff5932ac92d073f4288ced118f35af40aea4d1b56'
NEW_HASH = 'b841ce415b53ac3eb3df2286d2a61e870c628dc15d94b6f07d3de6f79284130a'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(app):
    result = {}
    for path in sorted(app.rglob('*')):
        relative = str(path.relative_to(app))
        if path.is_symlink():
            result[relative] = {'link': os.readlink(path)}
        elif path.is_file():
            result[relative] = {
                'sha256': digest(path),
                'mode': stat.S_IMODE(path.stat().st_mode),
            }
    return result


def running():
    for line in subprocess.check_output(['/bin/ps', '-axo', 'pid=,comm='], text=True).splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and Path(parts[1]).name == 'MCMacro':
            return True
    return False


def verify(app):
    subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(app)], check=True)


def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def main():
    if SOURCE.is_symlink() or DESKTOP.is_symlink():
        raise SystemExit('Refusing symlink application path')
    if digest(SOURCE / 'Contents/MacOS/MCMacro') != NEW_HASH:
        raise SystemExit('Candidate changed; no installation')
    if digest(DESKTOP / 'Contents/MacOS/MCMacro') != OLD_HASH:
        raise SystemExit('Desktop differs from expected baseline; no installation')
    if running():
        raise SystemExit('Application is running; no installation')
    metadata = plistlib.loads((SOURCE / 'Contents/Info.plist').read_bytes())
    expected = ('local.mc-macro.assistant', '1.10.1', '31')
    actual = tuple(metadata[key] for key in (
        'CFBundleIdentifier', 'CFBundleShortVersionString', 'CFBundleVersion'))
    if actual != expected:
        raise SystemExit('Unexpected application metadata')
    verify(SOURCE)
    verify(DESKTOP)
    stamp = datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')
    backup = ROOT / '.build/backups' / ('desktop-sync-1101-' + stamp)
    backup.mkdir(parents=True, exist_ok=False)
    stage = backup / 'staged-mcPvPmax.app'
    original = backup / 'mcPvPmax-1.10.0.app'
    source_manifest = manifest(SOURCE)
    old_manifest = manifest(DESKTOP)
    subprocess.run(['/usr/bin/ditto', str(SOURCE), str(stage)], check=True)
    verify(stage)
    if manifest(stage) != source_manifest:
        raise SystemExit('Staged bundle differs; desktop unchanged')
    if running() or manifest(DESKTOP) != old_manifest:
        raise SystemExit('Desktop started or changed while staging; no replacement')
    record = {
        'time': datetime.now().astimezone().isoformat(),
        'authorization': 'User explicitly requested synchronization into desktop application',
        'scope': 'desktop only; dist and zip unchanged',
        'source': str(SOURCE), 'destination': str(DESKTOP), 'backup': str(original),
        'previous_version': '1.10.0', 'version': '1.10.1', 'build': '31',
        'previous_sha256': OLD_HASH, 'installed_sha256': NEW_HASH,
        'uses_game_api_reader': True, 'pure_visual_integrated': False,
        'launched': False, 'permissions_changed': False, 'live_game_test_this_sync': False,
        'offline_checks': {'combat': 105, 'sprint': 21, 'inventory': 102,
                           'visual_prototype_only': 102, 'legacy_core': 'passed'},
        'status': 'prepared',
    }
    receipt = backup / 'sync.json'
    write_json(receipt, record)
    write_json(backup / 'old-bundle-manifest.json', old_manifest)
    write_json(backup / 'installed-bundle-manifest.json', source_manifest)
    try:
        DESKTOP.rename(original)
        if manifest(original) != old_manifest:
            raise RuntimeError('Backup verification failed')
        stage.rename(DESKTOP)
        verify(DESKTOP)
        if manifest(DESKTOP) != source_manifest:
            raise RuntimeError('Installed bundle differs from candidate')
        if digest(ROOT / 'dist/mcPvPmax.app/Contents/MacOS/MCMacro') != OLD_HASH:
            raise RuntimeError('Unexpected dist change')
        record['status'] = 'installed_and_verified'
        record['bundle_entries_verified'] = len(source_manifest)
        write_json(receipt, record)
    except BaseException as error:
        if original.exists():
            if DESKTOP.exists():
                DESKTOP.rename(backup / 'failed-install.app')
            original.rename(DESKTOP)
        record['status'] = 'rolled_back'
        record['error'] = str(error)
        write_json(receipt, record)
        raise
    write_json(ROOT / 'research/handoff-cline-20261104/desktop-sync-latest.json', record)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()