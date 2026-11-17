#!/usr/bin/env python3
"""Create a separate CF-only archive; never modify the source or local mods."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import zipfile

REMOVED = 'overrides/mods/noisium-forge-2.3.0+mc1.20-1.20.1.jar'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def export(source, target, validation):
    if target.exists() or source.resolve() == target.resolve():
        raise ValueError('Refusing to overwrite an existing archive')
    original_hash = digest(source.read_bytes())
    provenance = json.loads(validation.read_text())
    records = {r['filename']: r for r in provenance['files']}
    with zipfile.ZipFile(source) as old:
        assert old.testzip() is None
        assert len(old.namelist()) == len(set(old.namelist()))
        assert REMOVED in old.namelist()
        manifest = json.loads(old.read('manifest.json'))
        assert manifest['minecraft']['version'] == '1.20.1'
        assert manifest['minecraft']['modLoaders'] == [{'id': 'forge-47.4.10', 'primary': True}]
        # The removed JAR was an override, not a CF manifest download.
        expected = {(r['projectID'], r['fileID']) for r in records.values()
                    if r['kind'] == 'curseforge' and 'noisium' not in r['filename'].lower()}
        actual = {(r['projectID'], r['fileID']) for r in manifest['files']}
        assert actual == expected and len(actual) == len(manifest['files'])
        assert not any(c['dependency'] == 'noisium' and c['owner'] != 'noisium'
                       for c in provenance['dependency_coverage']['mandatory_checks'])
        audit = []
        for name in old.namelist():
            if not name.startswith('overrides/mods/') or not name.endswith('.jar') or name == REMOVED:
                continue
            data = old.read(name)
            with zipfile.ZipFile(io.BytesIO(data)) as jar:
                assert jar.testzip() is None
                # Check current bytes as well as the previous dependency audit.
                if 'META-INF/mods.toml' in jar.namelist():
                    text = jar.read('META-INF/mods.toml').decode('utf-8')
                    assert 'modId="noisium"' not in text.replace(' ', '')
            filename = name.split('/')[-1]
            record = records.get(filename)
            if filename.startswith('dynasty-'):
                kind = 'own-project'
            else:
                assert record and record['kind'] == 'approved-override', filename
                assert digest(data) == record['hashes']['sha256'], filename
                kind = record['kind']
            audit.append({'file': name, 'sha256': digest(data), 'kind': kind})
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation leaves the original published ZIP as its backup.
        with target.open('xb') as output:
            with zipfile.ZipFile(output, 'w') as new:
                new.comment = old.comment
                for info in old.infolist():
                    if info.filename != REMOVED:
                        new.writestr(copy.copy(info), old.read(info.filename))
        with zipfile.ZipFile(target) as new:
            assert new.testzip() is None
            assert set(old.namelist()) - set(new.namelist()) == {REMOVED}
            assert set(new.namelist()) - set(old.namelist()) == set()
            for name in new.namelist():
                assert new.read(name) == old.read(name), name
                assert 'noisium' not in name.lower(), name
    assert digest(source.read_bytes()) == original_hash
    report = {'source': str(source), 'source_sha256': original_hash,
              'output': str(target), 'output_sha256': digest(target.read_bytes()),
              'bytes': target.stat().st_size, 'removed': [REMOVED],
              'manifest_references': len(actual), 'manifest_changed': False,
              'other_entries_byte_identical': True, 'source_preserved': True,
              'mandatory_noisium_dependents': [], 'embedded_jar_audit': audit,
              'archive_crc': 'PASS', 'platform_approval': 'not submitted / not claimed',
              'runtime_launch': 'not performed; archive and dependency validation only'}
    # Keep delivery folders limited to the upload ZIP, with QA records internal.
    report_dir = Path(__file__).resolve().parents[2] / 'build' / 'curseforge-export-reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / (report['output_sha256'] + '.json')
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('target', type=Path)
    parser.add_argument('--validation', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.source, args.target, args.validation), ensure_ascii=False, indent=2))
