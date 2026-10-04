import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from check_modrinth_pack import check_pack, safe_path


class PackPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.jar = b"test fixture only"
        (self.root / "test.jar").write_bytes(self.jar)
        self.record = {"path": "mods/test.jar", "fileSize": len(self.jar),
                       "hashes": {a: hashlib.new(a, self.jar).hexdigest() for a in ("sha1", "sha512")},
                       "downloads": ["https://cdn.modrinth.com/data/project/version/test.jar"],
                       "env": {"client": "required", "server": "unsupported"}}

    def report(self, records=None, extra=None):
        archive = self.root / "test.mrpack"
        with zipfile.ZipFile(archive, "w") as packed:
            packed.writestr("modrinth.index.json", json.dumps({
                "formatVersion": 1, "game": "minecraft", "name": "test", "versionId": "1",
                "files": records if records is not None else [self.record],
            }))
            if extra:
                packed.writestr(extra, b"test")
        return check_pack(archive, self.root)

    def test_valid_pack_and_hashes(self):
        self.assertEqual([], self.report()["errors"])

    def test_disallowed_cdn(self):
        self.record["downloads"] = ["https://edge.forgecdn.net/files/test.jar"]
        self.assertIn("disallowed download", self.report()["errors"][0])

    def test_lookalike_host_and_http(self):
        for url in ("https://cdn.modrinth.com.evil.test/x", "http://cdn.modrinth.com/x",
                    "https://user@github.com/x", "https://github.com:8080/x"):
            self.record["downloads"] = [url]
            self.assertTrue(self.report()["errors"], url)

    def test_modified_jar(self):
        (self.root / "test.jar").write_bytes(b"modified")
        self.assertIn("does not match", self.report()["errors"][0])

    def test_duplicate_install_path(self):
        self.assertTrue(self.report([self.record, self.record])["errors"])

    def test_unsafe_paths(self):
        for path in ("/mods/a.jar", "../mods/a.jar", "mods/../a.jar", "mods\\a.jar", "C:/a.jar"):
            self.assertFalse(safe_path(path), path)

    def test_restricted_mod_warning_in_overrides(self):
        report = self.report(extra="overrides/mods/ftb-quests-forge-example.jar")
        self.assertEqual([], report["errors"])
        self.assertEqual(1, len(report["warnings"]))


if __name__ == "__main__":
    unittest.main()
