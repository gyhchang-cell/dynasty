"""CF export regression tests; no game, shared mod lists, or network mutations."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import curseforge_export as cf


def jar(modid='sample', version='1.0', dep=''):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('META-INF/mods.toml', f'''modLoader="javafml"
loaderVersion="[47,)"
license="MIT"
[[mods]]
modId="{modid}"
version="{version}"
{dep}''')
    return out.getvalue()


class CurseForgeExportTests(unittest.TestCase):
    def test_source_missing_extra_and_changed_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mods = root / 'modpack/mods'
            mods.mkdir(parents=True)
            (mods / 'dynasty.jar').write_bytes(b'core')
            sample = mods / 'sample.jar'
            sample.write_bytes(b'original')
            lock = {'own_filename': 'dynasty.jar', 'files': [
                {'source_filename': 'sample.jar', 'source_hashes': cf.hashes(b'original')}]}
            cf.inventory(root, lock)
            sample.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'hash drift'):
                cf.inventory(root, lock)
            sample.unlink()
            with self.assertRaisesRegex(ValueError, 'missing='):
                cf.inventory(root, lock)
            sample.write_bytes(b'original')
            (mods / 'unknown.jar').write_bytes(b'unknown')
            with self.assertRaisesRegex(ValueError, 'unregistered='):
                cf.inventory(root, lock)

    def test_unavailable_and_wrong_hash_cf_files_fail(self):
        data = jar()
        row = {'source_filename': 'sample.jar', 'kind': 'curseforge', 'projectID': 1, 'fileID': 2, 'filename': 'sample.jar',
               'size': len(data), 'hashes': cf.hashes(data), 'dependencies': []}
        meta = {'modId': 1, 'id': 2, 'fileName': 'sample.jar', 'fileLength': len(data),
                'isAvailable': True, 'fileStatus': 4, 'dependencies': [],
                'hashes': [{'algo': 1, 'value': row['hashes']['sha1']}],
                'gameVersions': ['Forge', '1.20.1'], 'downloadUrl': 'https://example.test/file'}
        with patch.object(cf, 'metadata', return_value=meta), patch.object(cf, 'fetch', return_value=data):
            self.assertEqual(cf.resolve(row), ('sample.jar', data))
            meta['isAvailable'] = False
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                cf.resolve(row)
            meta['isAvailable'] = True
            meta['hashes'][0]['value'] = '0' * 40
            with self.assertRaisesRegex(ValueError, 'SHA-1 mismatch'):
                cf.resolve(row)

    def test_changed_download_bytes_fail(self):
        row = {'kind': 'approved-override', 'filename': 'sample.jar', 'download_url': 'https://example.test/a',
               'hashes': cf.hashes(b'good'), 'approval_url': 'https://example.test/list', 'approval_marker': 'Sample'}
        with patch.object(cf, 'fetch', return_value=b'bad'):
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                cf.resolve(row)

    def test_revoked_approval_fails(self):
        row = {'kind': 'approved-override', 'filename': 'sample.jar', 'download_url': 'https://example.test/a',
               'hashes': cf.hashes(b'good'), 'approval_url': 'https://example.test/list', 'approval_marker': 'Sample'}
        with patch.object(cf, 'fetch', side_effect=[b'good', b'Other mod']):
            with self.assertRaisesRegex(ValueError, 'no longer listed'):
                cf.resolve(row)

    def test_unresolved_keeps_previous_output(self):
        with tempfile.TemporaryDirectory() as temp:
            lock = Path(temp) / 'lock.json'
            lock.write_text(json.dumps({'schema_version': 1, 'minecraft': '1.20.1',
                                        'forge': '47.4.10', 'unresolved': ['missing.jar']}))
            output = Path(temp) / 'pack.zip'
            output.write_bytes(b'previous output')
            with self.assertRaisesRegex(ValueError, 'Unresolved CF dependencies'):
                cf.export(temp, destination=output, lock_path=lock)
            self.assertEqual(output.read_bytes(), b'previous output')

    def test_mandatory_dependency_cannot_disappear(self):
        data = jar(dep='''[[dependencies.sample]]
modId="missing"
mandatory=true
versionRange="[1,)"
side="BOTH"''')
        with self.assertRaisesRegex(ValueError, 'missing mandatory dependency'):
            cf.dependency_report({'sample.jar': data})

    def test_maven_range_rules_and_rejection(self):
        dep = '''[[dependencies.sample]]
modId="minecraft"
mandatory=true
versionRange="[1.20,1.20.1,)"
side="CLIENT"'''
        result = cf.dependency_report({'sample.jar': jar(dep=dep)})
        self.assertEqual(len(result['mandatory_checks']), 1)
        with self.assertRaisesRegex(ValueError, 'Unsatisfied dependency'):
            cf.dependency_report({'sample.jar': jar(dep=dep.replace('[1.20,1.20.1,)', '[1.21,)'))})

    def test_embedded_cf_jar_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.zip'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('manifest.json', json.dumps({'files': [], 'minecraft': {'version': '1.20.1',
                    'modLoaders': [{'id': 'forge-47.4.10', 'primary': True}]},
                    'manifestType': 'minecraftModpack', 'manifestVersion': 1, 'overrides': 'overrides'}))
                z.writestr('overrides/README.txt', '')
                z.writestr('overrides/mods/dynasty.jar', b'core')
                z.writestr('overrides/mods/disallowed.jar', b'cf')
            with self.assertRaisesRegex(ValueError, 'Unexpected/missing'):
                cf.validate_archive(path, {'files': [], 'own_filename': 'dynasty.jar'}, {}, {}, '', b'core')


if __name__ == '__main__':
    unittest.main()
