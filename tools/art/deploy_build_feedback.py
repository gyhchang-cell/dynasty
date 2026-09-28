"""Explicit, post-exit installer for the v5 payload; never touches save data."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝')

def main():
    assert TARGET.is_dir() and (TARGET / 'mods/dynasty-1.4.0.jar').is_file()
    for process in subprocess.check_output(['ps', '-axo', 'pid=,comm='], text=True).splitlines():
        fields = process.strip().split(None, 1)
        if len(fields) != 2 or Path(fields[1]).name != 'java':
            continue
        command = subprocess.run(['ps', '-ww', '-p', fields[0], '-o', 'command='], capture_output=True, text=True).stdout
        match = re.search(r'--gameDir\s+(.+?)(?=\s+--|$)', command.strip())
        if match:
            game_dir = Path(match.group(1).strip('"\''))
            if not game_dir.is_absolute():
                cwd_info = subprocess.run(['lsof', '-a', '-p', fields[0], '-d', 'cwd', '-Fn'], capture_output=True, text=True)
                process_cwd = next((line[1:] for line in cwd_info.stdout.splitlines() if line.startswith('n')), None)
                if process_cwd is None:
                    raise SystemExit('无法确认正在运行的 Minecraft 实例路径；为保护存档，本次不安装。请先退出游戏。')
                game_dir = Path(process_cwd) / game_dir
            if game_dir.resolve() == TARGET.resolve():
                raise SystemExit('Dynasty 王朝仍在运行。请先退出游戏；本次未修改任何文件。')
    payload = ROOT / 'dist/dynasty-build-feedback-2026-09-25-update.zip'
    if '--payload' in sys.argv:
        payload = Path(sys.argv[sys.argv.index('--payload') + 1]).resolve()
    with zipfile.ZipFile(payload) as archive:
        manifest = json.loads(archive.read('update-manifest.json'))
        pending = []
        for name, expected in manifest['sha256'].items():
            data = archive.read(name)
            assert hashlib.sha256(data).hexdigest() == expected, name
            relative = Path(name)
            assert not relative.is_absolute() and '..' not in relative.parts
            if name == 'mods/dynasty-1.4.0.jar' or (name.startswith('config/ftbquests/quests/') and name.endswith('.snbt')):
                pending.append((relative, data))
    if '--check' in sys.argv:
        print('更新包校验通过；仅检查，不安装。待检查文件:', len(pending))
        return
    backup = ROOT / 'build/deployment-backups' / ('build-feedback-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True, exist_ok=False)
    changed = []
    for relative, data in pending:
        destination = TARGET / relative
        if destination.exists() and destination.read_bytes() == data:
            continue
        if destination.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        assert destination.read_bytes() == data
        changed.append(str(relative))
    (backup / 'receipt.json').write_text(json.dumps({'files': changed, 'instance': str(TARGET)}, ensure_ascii=False, indent=2))
    print('更新完成。替换文件:', len(changed), '\n备份:', backup, '\n未修改存档；现在可以启动游戏。')

if __name__ == '__main__':
    main()
