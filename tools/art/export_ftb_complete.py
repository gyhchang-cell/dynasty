#!/usr/bin/env python3
"""Offline, fail-closed export of the playable Dynasty pack, including FTB.

Run ./gradlew build first, then python3 tools/art/export_ftb_complete.py.
This is a local installation archive, not a Modrinth publication archive.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile

from export_policy import release_config, release_mod
from verify_modpack import check

REQUIRED = (
    'ftb-library-forge-2001.2.13.jar',
    'ftb-teams-forge-2001.3.2.jar',
    'ftb-quests-forge-2001.4.22.jar',
    'ftb-ultimine-forge-2001.1.8.jar',
    'item-filters-forge-2001.1.0-build.59.jar',
    'architectury-9.2.14-forge.jar',
    'cloth-config-11.1.136-forge.jar',
)
PREFIXES = ('ftb-library-', 'ftb-teams-', 'ftb-quests-', 'ftb-ultimine-',
            'item-filters-', 'architectury-', 'cloth-config-')


def digest(path, algorithm='sha256'):
    result = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def export(root):
    root = Path(root).resolve()
    properties = (root / 'gradle.properties').read_text(encoding='utf-8')
    match = re.search(r'^mod_version\s*=\s*([\w.+-]+)\s*$', properties, re.M)
    if not match:
        raise ValueError('gradle.properties 缺少合法 mod_version')
    version = match.group(1)
    own = root / 'build/libs' / ('dynasty-' + version + '.jar')
    if not own.is_file():
        raise ValueError('缺少最新构建产物，请先运行 ./gradlew build: ' + str(own))
    mods = root / 'modpack/mods'
    records = {}
    for filename in ('ftb_mods.json', 'qol_mods.json'):
        for record in json.loads((root / 'tools/art' / filename).read_text(encoding='utf-8')):
            if record['filename'] in REQUIRED:
                if record['filename'] in records and records[record['filename']] != record:
                    raise ValueError('依赖登记冲突: ' + record['filename'])
                records[record['filename']] = record
    for name in REQUIRED:
        path = mods / name
        if not path.is_file() or name not in records:
            raise ValueError('缺少任务系统依赖或版本登记: ' + name)
        record = records[name]
        if not record.get('sha1') or digest(path, 'sha1') != record['sha1']:
            raise ValueError('依赖 SHA-1 不匹配: ' + name)
        if record.get('sha512') and digest(path, 'sha512') != record['sha512']:
            raise ValueError('依赖 SHA-512 不匹配: ' + name)
        if 'size' in record and path.stat().st_size != record['size']:
            raise ValueError('依赖大小不匹配: ' + name)
    for path in mods.glob('*.jar'):
        if path.name.startswith(PREFIXES) and path.name not in REQUIRED:
            raise ValueError('检测到重复/非锁定版本，请先移出 modpack/mods: ' + path.name)

    sources = {'mods/' + own.name: own}
    for path in sorted(mods.glob('*.jar')):
        if release_mod(path.name) and not path.name.startswith('dynasty-'):
            sources['mods/' + path.name] = path
    config = root / 'modpack/config'
    quests = config / 'ftbquests/quests'
    for name in ('data.snbt', 'chapter_groups.snbt'):
        if not (quests / name).is_file() or not (quests / name).stat().st_size:
            raise ValueError('缺少任务书配置: ' + name)
    chapters = sorted((quests / 'chapters').glob('*.snbt'))
    if not chapters or any(not p.stat().st_size for p in chapters):
        raise ValueError('任务章节缺失或为空，停止导出')
    for folder in ('config', 'resourcepacks'):
        base = root / 'modpack' / folder
        for path in sorted(base.rglob('*')):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                if folder != 'config' or release_config(rel):
                    sources[folder + '/' + rel] = path

    # Check precisely the jars being exported, including the fresh core jar.
    # Links avoid copying large jars and do not modify the project or game saves.
    with tempfile.TemporaryDirectory(prefix='dynasty-ftb-check-') as temporary:
        staging = Path(temporary)
        for arcname, path in sources.items():
            if arcname.startswith('mods/'):
                with zipfile.ZipFile(path) as jar:
                    bad = jar.testzip()
                    if bad:
                        raise ValueError('损坏的 jar: ' + str(path) + ': ' + bad)
                (staging / path.name).symlink_to(path)
        if not check(str(staging)):
            raise ValueError('整合包缺少前置或存在不兼容模组，停止导出')

    receipt = {
        'version': version, 'minecraft': '1.20.1', 'forge': '47.4.10',
        'required_ftb_and_dependencies': list(REQUIRED),
        'quest_chapters': len(chapters),
        'validation': 'Offline file hashes, jar CRC and dependency declarations only; no game launch.',
        'files': {name: {'sha256': digest(path), 'size': path.stat().st_size}
                  for name, path in sources.items()},
    }
    readme = (
        'Dynasty 王朝 ' + version + ' — FTB 完整本地安装包\n'
        'Minecraft 1.20.1 / Forge 47.4.10\n\n'
        '1. 关闭游戏，建立独立的 Forge 1.20.1 测试实例。\n'
        '2. 将本包 mods、config、resourcepacks 文件夹一起复制到该实例根目录。\n'
        '3. 启动游戏，从背包的王朝任务按钮打开任务书。\n'
        '4. FTB Ultimine 的连锁采掘按键可在游戏按键设置里查询。\n\n'
        '本包包含截图中的五个模组及 Architectury / Cloth Config 前置。\n'
        '任务章节沿用工程文件；不会改写任务 ID，也不包含或覆盖 saves。\n'
        '更新旧实例前备份实例，移出旧版同名模组，避免重复安装。\n'
        '本包包含客户端模组，不是专用服务器安装包。\n'
        '这是本地完整安装包，不要作为 Modrinth 发布文件上传；\n'
        '公开发布仍使用原平台对应的导出流程。\n'
        '导出校验不等于客户端/多人实机验收，请先用独立测试世界验证。\n'
    )
    dist = root / 'dist'
    dist.mkdir(exist_ok=True)
    output = dist / ('dynasty-' + version + '-manual.zip')
    fd, tempname = tempfile.mkstemp(prefix=output.name + '.', suffix='.pending', dir=dist)
    os.close(fd)
    try:
        with zipfile.ZipFile(tempname, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, path in sources.items():
                archive.write(path, name)
            archive.writestr('安装说明-README.txt', readme)
            archive.writestr('dynasty-ftb-complete.json', json.dumps(receipt, ensure_ascii=False, indent=2))
        with zipfile.ZipFile(tempname) as archive:
            if archive.testzip():
                raise ValueError('压缩包 CRC 校验失败')
            for name, metadata in receipt['files'].items():
                data = archive.read(name)
                if len(data) != metadata['size'] or hashlib.sha256(data).hexdigest() != metadata['sha256']:
                    raise ValueError('打包期间文件发生变化: ' + name)
        os.replace(tempname, output)
    finally:
        if os.path.exists(tempname):
            os.unlink(tempname)
    # Launcher-importable local pack: every validated mod and quest is embedded.
    # No mod download or manual FTB installation is needed after importing.
    installable = dist / ('dynasty-' + version + '-complete.zip')
    manifest = {
        'minecraft': {'version': '1.20.1', 'modLoaders': [
            {'id': 'forge-47.4.10', 'primary': True}]},
        'manifestType': 'minecraftModpack', 'manifestVersion': 1,
        'name': 'Dynasty 王朝 · FTB 完整游玩包', 'version': version,
        'author': 'Newton', 'files': [], 'overrides': 'overrides',
    }
    fd, pending = tempfile.mkstemp(prefix=installable.name + '.', suffix='.pending', dir=dist)
    os.close(fd)
    try:
        # Copy the already-validated snapshot, not potentially changing source files.
        with zipfile.ZipFile(output) as snapshot, zipfile.ZipFile(
                pending, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
            for entry in snapshot.infolist():
                archive.writestr('overrides/' + entry.filename, snapshot.read(entry.filename))
        with zipfile.ZipFile(pending) as archive:
            if archive.testzip():
                raise ValueError('完整导入包 CRC 校验失败')
        os.replace(pending, installable)
    finally:
        if os.path.exists(pending):
            os.unlink(pending)
    print('直接导入启动器（包含全部 FTB，无需补装）:', installable)
    print('FTB 完整包已生成:', output)
    print('任务章节:', len(chapters), '；模组:', sum(n.startswith('mods/') for n in sources))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        export(args.root)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, 'FTB 完整包导出失败: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
