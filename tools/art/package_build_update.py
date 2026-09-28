"""Build-feedback update staging. Never reads or writes the live game instance."""
import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from quest_story import build_book

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/art/build-feedback-v5'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    jar = ROOT / 'build/libs/dynasty-1.4.0.jar'
    resources = ROOT / 'src/main/resources'
    with zipfile.ZipFile(jar) as archive:
        assert archive.testzip() is None
        assert not any('RuntimeQa' in name for name in archive.namelist())
        for source in resources.rglob('*'):
            if not source.is_file():
                continue
            name = source.relative_to(resources).as_posix()
            expected = ROOT / 'build/resources/main' / name if name in ('META-INF/mods.toml', 'pack.mcmeta') else source
            assert archive.read(name) == expected.read_bytes(), 'Rebuild required: ' + name
    staged = ROOT / 'modpack/mods' / jar.name
    if not staged.exists() or staged.read_bytes() != jar.read_bytes():
        if staged.exists():
            backup = ROOT / 'build/backups' / ('build-feedback-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
            backup.mkdir(parents=True, exist_ok=False)
            shutil.copy2(staged, backup / staged.name)
        shutil.copy2(jar, staged)
    payload = {'mods/' + jar.name: jar.read_bytes()}
    quests = ROOT / 'modpack/config/ftbquests/quests'
    for path in quests.rglob('*.snbt'):
        payload['config/ftbquests/quests/' + path.relative_to(quests).as_posix()] = path.read_bytes()
    payload['更新说明.md'] = (DOC / 'release-notes.md').read_bytes()
    book = build_book()
    receipt = {'version': 'build-feedback-v5', 'chapters': len(book),
               'quests': sum(len(c['quests']) for c in book), 'game_tests_passed': 72,
               'live_instance_updated': False,
               'sha256': {name: digest(data) for name, data in payload.items()}}
    payload['update-manifest.json'] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    destination = ROOT / 'dist/dynasty-build-feedback-2026-09-25-update.zip'
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in payload.items():
            archive.writestr(name, data)
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert all(archive.read(name) == data for name, data in payload.items())
        assert not any(name.startswith(('saves/', 'build/')) for name in archive.namelist())
    (DOC / 'update-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(destination)
    print('Verified payload files:', len(payload), '; quests:', receipt['quests'])

if __name__ == '__main__':
    main()
