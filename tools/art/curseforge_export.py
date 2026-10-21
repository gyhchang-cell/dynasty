#!/usr/bin/env python3
"""CurseForge-only locked export. CF builds use manifest references.
Only explicitly approved third-party releases may be embedded.

The separate lock records both installed source bytes and CF distribution bytes.
Online metadata and download verification are mandatory for a release export.
No shared mod lists, installed jars, core build, or Modrinth exports are mutated.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
import zipfile

from export_policy import release_mod, release_config
from verify_modpack import compare

ROOT = Path(__file__).resolve().parents[2]
LOCK = Path(__file__).with_name('curseforge.lock.json')
API = 'https://api.curse.tools/v1/cf/'


def fetch(url):
    return subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                           '--retry', '2', '--max-time', '60', url],
                          check=True, capture_output=True).stdout


def metadata(project, file):
    url = f'{API}mods/{project}/files/{file}'
    return json.loads(fetch(url))['data']


def hashes(data):
    return {a: hashlib.new(a, data).hexdigest() for a in ('sha1', 'sha256', 'sha512')}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def jar_metadata(data, name, installed, dependencies):
    """Parse every Forge mod and recursively parse JarJar dependencies."""
    with zipfile.ZipFile(io.BytesIO(data)) as jar:
        require(jar.testzip() is None, 'Corrupt jar: ' + name)
        if 'META-INF/mods.toml' in jar.namelist():
            doc = tomllib.loads(jar.read('META-INF/mods.toml').decode())
            manifest = jar.read('META-INF/MANIFEST.MF').decode() if 'META-INF/MANIFEST.MF' in jar.namelist() else ''
            fields = dict(line.split(': ', 1) for line in manifest.splitlines() if ': ' in line)
            for mod in doc.get('mods', []):
                modid = mod['modId']
                version = mod.get('version', '')
                if version == '${file.jarVersion}':
                    version = fields.get('Implementation-Version', '')
                require(version and '${' not in version, f'Unresolved version: {name}: {modid}')
                if modid in installed:
                    require('!META-INF/' in name, f'Duplicate mod ID: {modid}: {name}')
                    # Forge JarJar selects the newest shared library version.
                    if compare(version, installed[modid]) > 0:
                        installed[modid] = version
                else:
                    installed[modid] = version
                dependencies.extend((modid, dep) for dep in doc.get('dependencies', {}).get(modid, []))
        if 'META-INF/jarjar/metadata.json' in jar.namelist():
            for item in json.loads(jar.read('META-INF/jarjar/metadata.json')).get('jars', []):
                path = item['path'].lstrip('/')
                if not path.startswith('META-INF/'):
                    path = 'META-INF/jarjar/' + path
                jar_metadata(jar.read(path), name + '!' + path, installed, dependencies)


def dependency_report(jars):
    installed = {'minecraft': '1.20.1', 'forge': '47.4.10', 'java': '17'}
    deps = []
    for name, data in jars.items():
        jar_metadata(data, name, installed, deps)
    checked = []
    for owner, dep in deps:
        target = dep['modId']
        rng = dep.get('versionRange', '*')
        if 'NOT-COMPATIBLE' in rng:
            require(target not in installed, f'{owner} incompatible with {target}')
            continue
        if not dep.get('mandatory', False):
            continue
        require(target in installed, f'{owner} missing mandatory dependency {target}')
        version = installed[target]
        checked.append({'owner': owner, 'dependency': target, 'range': rng, 'version': version,
                        'side': dep.get('side', 'BOTH')})
    cache = Path.home() / '.gradle/caches/modules-2/files-2.1'
    def library(group, artifact, version='*'):
        paths = [p for p in (cache / group / artifact).glob(version + '/*/*.jar')
                 if not p.name.endswith(('-sources.jar', '-javadoc.jar'))]
        require(bool(paths), 'Missing Java validation library in Gradle cache: ' + artifact)
        return str(sorted(paths)[-1])
    classpath = os.pathsep.join([library('org.apache.maven', 'maven-artifact', '3.8.8'),
                                library('org.apache.commons', 'commons-lang3')])
    result = subprocess.run(['java', '--class-path', classpath,
                             str(Path(__file__).with_name('CurseForgeVersionCheck.java'))],
                            input=''.join(r['version'] + '\t' + r['range'] + '\n' for r in checked),
                            text=True, capture_output=True, check=True)
    answers = result.stdout.splitlines()
    require(len(answers) == len(checked), 'Incomplete Maven range validation')
    for row, answer in zip(checked, answers):
        require(answer == 'true', 'Unsatisfied dependency: ' + json.dumps(row))
    return {'installed_mods': installed, 'mandatory_checks': checked}


def inventory(root, lock):
    source = {p.name: p for p in (root / 'modpack/mods').glob('*.jar') if release_mod(p.name)}
    expected = {r['source_filename'] for r in lock['files']} | {lock['own_filename']}
    require(set(source) == expected,
            'Source inventory drift; missing=' + str(sorted(expected - set(source))) +
            '; unregistered=' + str(sorted(set(source) - expected)))
    for row in lock['files']:
        require(hashes(source[row['source_filename']].read_bytes()) == row['source_hashes'],
                'Source hash drift: ' + row['source_filename'])
    return source


def resolve(row):
    if row['kind'] == 'approved-override':
        data = fetch(row['download_url'])
        require(hashes(data) == row['hashes'], 'Approved override hash mismatch: ' + row['filename'])
        approval = fetch(row['approval_url']).decode()
        require(row['approval_marker'].casefold() in approval.casefold(),
                'Third-party approval no longer listed: ' + row['filename'])
        return row['filename'], data
    require(row['kind'] == 'curseforge', 'Unresolved distribution: ' + row['source_filename'])
    f = metadata(row['projectID'], row['fileID'])
    require(f['modId'] == row['projectID'] and f['id'] == row['fileID'], 'CF identity mismatch')
    require(f['isAvailable'] and f['fileStatus'] == 4, 'CF file unavailable/unapproved: ' + row['filename'])
    require(f['fileName'] == row['filename'], 'CF filename mismatch: ' + row['filename'])
    require(f['fileLength'] == row['size'], 'CF size mismatch: ' + row['filename'])
    require(any(h['algo'] == 1 and h['value'] == row['hashes']['sha1'] for h in f['hashes']),
            'CF SHA-1 mismatch: ' + row['filename'])
    require(f.get('dependencies', []) == row['dependencies'], 'CF dependency metadata drift: ' + row['filename'])
    require('Forge' in f['gameVersions'], 'CF file not tagged Forge: ' + row['filename'])
    # Some multi-version files use 1.20/1.20.4 tags; the actual Forge TOML
    # is checked against 1.20.1 below instead of trusting the filename.
    data = fetch(f['downloadUrl'])
    require(len(data) == row['size'] and hashes(data) == row['hashes'],
            'Downloaded CF bytes do not match lock: ' + row['filename'])
    return row['filename'], data


def validate_archive(path, lock, jars, configs, readme, own):
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, 'Corrupt archive')
        require(len(z.namelist()) == len(set(z.namelist())), 'Duplicate ZIP paths')
        m = json.loads(z.read('manifest.json'))
        expected = [{'projectID': r['projectID'], 'fileID': r['fileID'], 'required': True}
                    for r in lock['files'] if r['kind'] == 'curseforge']
        require(m['files'] == expected, 'Manifest differs from lock')
        require(m.get('minecraft') == {'version': '1.20.1', 'modLoaders': [
            {'id': 'forge-47.4.10', 'primary': True}]}, 'Wrong Minecraft/Forge target')
        require(m.get('manifestType') == 'minecraftModpack' and m.get('manifestVersion') == 1
                and m.get('overrides') == 'overrides', 'Invalid CF manifest schema')
        overrides = {'overrides/mods/' + lock['own_filename']: own,
                     'overrides/README.txt': readme.encode(), **configs}
        for row in lock['files']:
            if row['kind'] == 'approved-override':
                overrides['overrides/mods/' + row['filename']] = jars[row['filename']]
        require(set(z.namelist()) == {'manifest.json'} | set(overrides), 'Unexpected/missing archive content')
        for name, data in overrides.items():
            require(z.read(name) == data, 'Override bytes changed: ' + name)
    return {'manifest_references': len(expected), 'embedded_jars': len([n for n in overrides if n.endswith('.jar')]),
            'overrides_verified': len(overrides)}


def export(root=ROOT, readme='', destination=None, lock_path=LOCK):
    root = Path(root)
    lock = json.loads(Path(lock_path).read_text())
    require(lock['schema_version'] == 1 and lock['minecraft'] == '1.20.1'
            and lock['forge'] == '47.4.10', 'Unsupported CF lock target')
    require(not lock.get('unresolved'), 'Unresolved CF dependencies: ' + json.dumps(lock['unresolved']))
    source = inventory(root, lock)
    require(len({r['source_filename'] for r in lock['files']}) == len(lock['files']),
            'Duplicate locked source filename')
    require(len({r['filename'] for r in lock['files']}) == len(lock['files']),
            'Duplicate distribution filename')
    projects = [r['projectID'] for r in lock['files'] if r['kind'] == 'curseforge']
    require(len(projects) == len(set(projects)), 'Duplicate CF project')
    ignored = {(x['fileID'], x['projectID']) for x in lock.get('dependency_exceptions', [])}
    for row in lock['files']:
        for dep in row.get('dependencies', []):
            require(dep['relationType'] != 3 or dep['modId'] in projects or
                    (row['fileID'], dep['modId']) in ignored,
                    f"Uncovered CF required dependency: {row['filename']}: {dep['modId']}")
    with ThreadPoolExecutor(max_workers=10) as pool:
        jars = dict(pool.map(resolve, lock['files']))
    own = source[lock['own_filename']].read_bytes()
    jars[lock['own_filename']] = own
    dependencies = dependency_report(jars)
    config = root / 'modpack/config'
    configs = {'overrides/config/' + p.relative_to(config).as_posix(): p.read_bytes()
               for p in sorted(config.rglob('*')) if p.is_file() and release_config(p.relative_to(config))}
    m = {'minecraft': {'version': '1.20.1', 'modLoaders': [{'id': 'forge-47.4.10', 'primary': True}]},
         'manifestType': 'minecraftModpack', 'manifestVersion': 1, 'name': 'Dynasty 王朝',
         'version': lock['version'], 'author': 'Newton', 'overrides': 'overrides',
         'files': [{'projectID': r['projectID'], 'fileID': r['fileID'], 'required': True}
                   for r in lock['files'] if r['kind'] == 'curseforge']}
    destination = Path(destination or root / 'dist' / f"dynasty-modpack-{lock['version']}.zip")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=destination.name + '.', suffix='.pending', dir=destination.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('manifest.json', json.dumps(m, ensure_ascii=False, indent=2))
            z.writestr('overrides/README.txt', readme)
            z.writestr('overrides/mods/' + lock['own_filename'], own)
            for row in lock['files']:
                if row['kind'] == 'approved-override':
                    z.writestr('overrides/mods/' + row['filename'], jars[row['filename']])
            for name, data in configs.items():
                z.writestr(name, data)
        report = validate_archive(temporary, lock, jars, configs, readme, own)
        report.update({'sha256': hashes(Path(temporary).read_bytes())['sha256'],
                       'path': str(destination.resolve()), 'dependency_coverage': dependencies,
                       'lock_sha256': hashes(Path(lock_path).read_bytes())['sha256'],
                       'files': lock['files'], 'own_hashes': hashes(own),
                       'unresolved': lock['unresolved'], 'dependency_exceptions': lock.get('dependency_exceptions', [])})
        os.replace(temporary, destination)
        destination.with_suffix('.validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    print(export(destination=args.output, readme='Dynasty 1.4.0 — Minecraft 1.20.1 / Forge 47.4.10\n'))
