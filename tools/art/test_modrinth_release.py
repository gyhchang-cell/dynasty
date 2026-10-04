import hashlib
from pathlib import Path
import tempfile
import unittest

from modrinth_release import MANUAL, manual_guide, prepare_release, unique_sources


class ReleasePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        data = b"fixture-not-a-mod"
        self.name = "example.jar"
        (self.root / self.name).write_bytes(data)
        self.hashes = {a: hashlib.new(a, data).hexdigest() for a in ("sha1", "sha512")}
        self.version = {"files": [{"hashes": self.hashes, "size": len(data),
                                  "url": "https://cdn.modrinth.com/data/id/version/example.jar"}],
                        "game_versions": ["1.20.1"], "loaders": ["forge"],
                        "environment": "client_only"}
        self.lookup = {self.hashes["sha1"]: self.version}

    def release(self):
        return prepare_release([(self.name, "https://old.invalid/example.jar")], self.root, self.lookup)

    def test_exact_official_source_and_client_only_environment(self):
        files, manual, embedded = self.release()
        self.assertEqual([], manual + embedded)
        self.assertEqual(self.version["files"][0]["url"], files[0]["downloads"][0])
        self.assertEqual("unsupported", files[0]["env"]["server"])

    def test_no_silent_drop_of_unresolved_mod(self):
        self.lookup.clear()
        with self.assertRaisesRegex(ValueError, "不会擅自删模组"):
            self.release()

    def test_server_logic_utilities_remain_for_integrated_server(self):
        self.version['environment'] = 'server_only'
        files, _, _ = self.release()
        self.assertEqual({'client': 'required', 'server': 'required'}, files[0]['env'])

    def test_reject_wrong_game_version(self):
        self.version["game_versions"] = ["1.21"]
        with self.assertRaises(ValueError):
            self.release()

    def test_reject_wrong_full_hash(self):
        self.version["files"][0]["hashes"] = {**self.hashes, "sha512": "0" * 128}
        with self.assertRaises(ValueError):
            self.release()

    def test_manual_dependency_not_redistributed_and_documented(self):
        name = next(iter(MANUAL))
        (self.root / name).write_bytes(b"manual dependency fixture")
        files, manual, embedded = prepare_release([(name, "https://maven.ftb.dev/example")], self.root, {})
        self.assertEqual([], files + embedded)
        self.assertEqual(name, manual[0]["filename"])
        guide = manual_guide(manual)
        self.assertIn(name, guide)
        self.assertIn("不是完整开箱即用版", guide)

    def test_unreviewed_ftb_version_fails_closed(self):
        name = "ftb-quests-forge-unreviewed.jar"
        (self.root / name).write_bytes(b"fixture")
        with self.assertRaisesRegex(ValueError, "未经许可"):
            prepare_release([(name, "https://github.com/example.jar")], self.root, {})

    def test_duplicate_paths_removed_but_conflicts_rejected(self):
        self.assertEqual([("a.jar", "https://a")], unique_sources([("a.jar", "https://a")] * 2))
        with self.assertRaises(ValueError):
            unique_sources([("a.jar", "https://a"), ("a.jar", "https://b")])


if __name__ == "__main__":
    unittest.main()
