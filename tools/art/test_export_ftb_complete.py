"""Offline export regression tests with synthetic jars; not game tests."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from export_ftb_complete import REQUIRED, export


class CompletePackTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('modpack/mods', 'tools/art', 'build/libs',
                     'modpack/config/ftbquests/quests/chapters'):
            (self.root / name).mkdir(parents=True)
        (self.root / 'gradle.properties').write_text('mod_version=1.4.0\n')
        records = []
        for index, name in enumerate(REQUIRED):
            path = self.root / 'modpack/mods' / name
            self.jar(path, 'dependency_' + str(index))
            data = path.read_bytes()
            records.append({'filename': name, 'sha1': hashlib.sha1(data).hexdigest(),
                            'sha512': hashlib.sha512(data).hexdigest(), 'size': len(data)})
        (self.root / 'tools/art/ftb_mods.json').write_text(json.dumps(records))
        (self.root / 'tools/art/qol_mods.json').write_text('[]')
        self.core = self.root / 'build/libs/dynasty-1.4.0.jar'
        self.jar(self.core, 'dynasty')
        self.jar(self.root / 'modpack/mods/dynasty-1.3.0.jar', 'stale_core')
        quests = self.root / 'modpack/config/ftbquests/quests'
        for name in ('data.snbt', 'chapter_groups.snbt', 'chapters/original.snbt'):
            (quests / name).write_text('{ id: "1234567890ABCDEF" }')

    def jar(self, path, mod_id, extra=''):
        with zipfile.ZipFile(path, 'w') as jar:
            jar.writestr('META-INF/mods.toml',
                         '[[mods]]\nmodId="' + mod_id + '"\nversion="1.0"\n' + extra)

    def test_complete_pack_keeps_quests_and_fresh_core(self):
        output = export(self.root)
        with zipfile.ZipFile(output) as archive:
            self.assertTrue(all('mods/' + n in archive.namelist() for n in REQUIRED))
            self.assertNotIn('mods/dynasty-1.3.0.jar', archive.namelist())
            self.assertEqual(archive.read('mods/dynasty-1.4.0.jar'), self.core.read_bytes())
            self.assertEqual(archive.read('config/ftbquests/quests/chapters/original.snbt'),
                             b'{ id: "1234567890ABCDEF" }')

    def test_launcher_import_contains_all_ftb_and_identical_configuration(self):
        output = export(self.root)
        with zipfile.ZipFile(output) as manual, zipfile.ZipFile(
                self.root / 'dist/dynasty-1.4.0-complete.zip') as complete:
            manifest = json.loads(complete.read('manifest.json'))
            self.assertEqual('minecraftModpack', manifest['manifestType'])
            self.assertEqual('forge-47.4.10', manifest['minecraft']['modLoaders'][0]['id'])
            self.assertEqual([], manifest['files'])
            for name in manual.namelist():
                self.assertEqual(manual.read(name), complete.read('overrides/' + name))
            for name in REQUIRED:
                self.assertIn('overrides/mods/' + name, complete.namelist())

    def test_missing_dependency_preserves_previous_export(self):
        output = export(self.root)
        previous = output.read_bytes()
        (self.root / 'modpack/mods' / REQUIRED[0]).unlink()
        with self.assertRaisesRegex(ValueError, '缺少任务系统依赖'):
            export(self.root)
        self.assertEqual(output.read_bytes(), previous)

    def test_corrupt_dependency_rejected(self):
        (self.root / 'modpack/mods' / REQUIRED[2]).write_bytes(b'not the locked jar')
        with self.assertRaisesRegex(ValueError, 'SHA-1'):
            export(self.root)

    def test_duplicate_ftb_version_rejected(self):
        self.jar(self.root / 'modpack/mods/ftb-quests-forge-old.jar', 'ftbquests')
        with self.assertRaisesRegex(ValueError, '重复/非锁定'):
            export(self.root)

    def test_missing_chapters_rejected(self):
        (self.root / 'modpack/config/ftbquests/quests/chapters/original.snbt').unlink()
        with self.assertRaisesRegex(ValueError, '任务章节'):
            export(self.root)

    def test_missing_build_rejected(self):
        self.core.unlink()
        with self.assertRaisesRegex(ValueError, '最新构建产物'):
            export(self.root)

    def test_missing_transitive_dependency_rejected(self):
        self.jar(self.core, 'dynasty', '\n[[dependencies.dynasty]]\n'
                 'modId="missing_required_mod"\nmandatory=true\nversionRange="[1,)"\n')
        with self.assertRaisesRegex(ValueError, '缺少前置'):
            export(self.root)


if __name__ == '__main__':
    unittest.main()
