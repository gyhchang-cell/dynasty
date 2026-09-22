"""Navigation-name regressions, including upstream bytecode and non-destructive generation."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import gen_dynasty3_json as generator
from verify_compass_localization import (LANG, localization_errors, registered_names,
                                        verify_actual_lookup)


class CompassLocalizationTests(unittest.TestCase):
    def setUp(self):
        self.languages = {locale: json.loads((LANG / f"{locale}.json").read_text())
                          for locale in ("zh_cn", "en_us")}

    def test_actual_shipped_compass_translation_lookups(self):
        verify_actual_lookup()

    def test_all_registry_names_have_authored_bilingual_translations(self):
        self.assertEqual([], localization_errors(self.languages))
        self.assertEqual({"palace", "academy", "imperial_tomb", "great_wall_gate",
                          "star_altar", "stone_grove"}, registered_names()["structure"])

    def test_any_missing_structure_translation_is_detected(self):
        for name in registered_names()["structure"]:
            for locale in self.languages:
                with self.subTest(name=name, locale=locale):
                    values = copy.deepcopy(self.languages)
                    del values[locale][f"structure.dynasty.{name}"]
                    self.assertTrue(localization_errors(values))

    def test_english_in_chinese_slot_is_detected(self):
        self.languages["zh_cn"]["structure.dynasty.academy"] = "Academy"
        self.assertTrue(localization_errors(self.languages))

    def test_navigation_only_generation_preserves_other_content_and_is_idempotent(self):
        with tempfile.TemporaryDirectory(prefix="dynasty-compass-lang-") as folder:
            for locale in self.languages:
                path = Path(folder) / f"{locale}.json"
                path.write_text(json.dumps({"custom.unrelated": "keep me"}))
            with patch.object(generator, "LANG_DIR", folder), contextlib.redirect_stdout(io.StringIO()):
                generator.merge_worldgen_lang()
                first = {p.name: p.read_bytes() for p in Path(folder).glob("*.json")}
                generator.merge_worldgen_lang()
            for locale in self.languages:
                path = Path(folder) / f"{locale}.json"
                self.assertEqual(first[path.name], path.read_bytes())
                self.assertEqual({"custom.unrelated": "keep me", **generator.worldgen_lang(locale)},
                                 json.loads(path.read_text()))


if __name__ == "__main__":
    unittest.main()
