"""Four-school fixed-contract regression checks; no Gradle, saves, deployment or image writes."""
import hashlib
import json
import math
import re
import unittest
from pathlib import Path

from gen_trinkets6 import CONTRACT, ITEMS, TRINKETS
from gen_curios import classifications
from gen_schools import language

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "src/main/resources"
JAVA = ROOT / "src/main/java/com/dynasty"


class SchoolContractTests(unittest.TestCase):
    def test_four_distinct_optional_loadouts(self):
        self.assertEqual(12, len(ITEMS))
        self.assertEqual(8, len(TRINKETS))
        for school in ("guard", "sword", "archer", "talisman"):
            entries = [i for i in ITEMS.values() if i["school"] == school]
            self.assertEqual(1, sum(i["kind"] == "weapon" for i in entries))
            self.assertEqual(2, sum(i["kind"] == "accessory" for i in entries))

    def test_recipes_have_existing_ingredients_and_no_hidden_gate(self):
        lang = json.loads((RES / "assets/dynasty/lang/zh_cn.json").read_text())
        for key, entry in ITEMS.items():
            recipe = json.loads((RES / f"data/dynasty/recipes/{key}.json").read_text())
            self.assertEqual("minecraft:crafting_shapeless", recipe["type"])
            self.assertEqual(entry["recipe"], [i["item"] for i in recipe["ingredients"]])
            self.assertLessEqual(len(recipe["ingredients"]), 9)
            self.assertEqual({"item": "dynasty:" + key, "count": 1}, recipe["result"])
            for ingredient in entry["recipe"]:
                namespace, item = ingredient.split(":")
                if namespace == "dynasty":
                    self.assertTrue("item.dynasty." + item in lang or "block.dynasty." + item in lang, ingredient)
                    self.assertNotIn(item, ITEMS, "Each loadout must remain independently craftable")

    def test_trinket_registry_stats_slots_and_tooltips_match_contract(self):
        source = (JAVA / "DynastyTrinkets.java").read_text()
        slots = classifications()
        for key, item in ITEMS.items():
            if item["kind"] != "accessory":
                self.assertIn('ITEMS.register("' + key + '"', (JAVA / "DynastyWeapons.java").read_text())
                continue
            row = re.search(r'\{"' + key + r'",([^}]+)\}', source).group(1)
            numbers = [float(value.strip().rstrip("D")) for value in row.split(",")]
            self.assertEqual(item["spec"], numbers, key)
            self.assertEqual(item["slot"], slots[key])
            self.assertIn('"' + key + '"', (JAVA / "DynastySchoolCombat.java").read_text())
        for locale in ("zh_cn", "en_us"):
            actual = json.loads((RES / f"assets/dynasty/lang/{locale}.json").read_text())
            for key, value in language(locale).items():
                self.assertEqual(value, actual[key])

    def test_real_operation_trials_cannot_be_claimed_for_items_or_kills(self):
        self.assertEqual({"build_guard_trial", "build_sword_trial", "build_archer_trial", "build_talisman_trial"},
                         {t["id"] for t in CONTRACT["trials"]})
        for trial in CONTRACT["trials"]:
            data = json.loads((RES / f"data/dynasty/advancements/{trial['id']}.json").read_text())
            self.assertEqual({"criteria": {"performed": {"trigger": "minecraft:impossible"}}}, data)
        source = (JAVA / "DynastySchoolCombat.java").read_text()
        for school in ("guard", "sword", "archer", "talisman"):
            self.assertIn(f'trial(player, "{school}")', source)
        self.assertNotIn("target.hurt(", source, "School bonuses must preserve one original damage event")
        self.assertNotIn("destroyBlock(", source)

    def test_fifteen_original_assets_are_128px_visible_and_distinct(self):
        from PIL import Image
        ids = list(ITEMS) + [f"zhuxing_bow_pulling_{i}" for i in range(3)]
        hashes = set()
        for key in ids:
            path = RES / f"assets/dynasty/textures/item/{key}.png"
            with Image.open(path) as image:
                self.assertEqual((128, 128), image.size, key)
                self.assertIsNotNone(image.convert("RGBA").getchannel("A").getbbox(), key)
                hashes.add(hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest())
        self.assertEqual(len(ids), len(hashes), "No duplicated static pulling frames or shared accessory pictures")

    def test_bow_models_have_three_real_draw_stages_not_registered_items(self):
        model = json.loads((RES / "assets/dynasty/models/item/zhuxing_bow.json").read_text())
        self.assertEqual([0, .65, .9], [entry["predicate"].get("dynasty:pull", 0) for entry in model["overrides"]])
        for stage in range(3):
            key = f"zhuxing_bow_pulling_{stage}"
            draw = json.loads((RES / f"assets/dynasty/models/item/{key}.json").read_text())
            self.assertEqual(f"minecraft:item/bow_pulling_{stage}", draw["parent"])
            self.assertEqual("dynasty:item/" + key, draw["textures"]["layer0"])
            self.assertNotIn(key, ITEMS)
            for side, hand in (("righthand", 1), ("lefthand", -1)):
                pose = draw["display"]["firstperson_" + side]
                self.assertLessEqual(max(pose["scale"]), .68, "Drawn bow should fit the held-item view")
                # The approved drawn sprite's arrow points right in its 2D model (+X).
                # Compose the actual vanilla 1.20.1 draw rotations to confirm that
                # both hands aim the arrow into the scene and slightly toward centre.
                vector = [1.0, 0.0, 0.0]
                def turn(axis, degrees):
                    x, y, z = vector
                    sine, cosine = math.sin(math.radians(degrees)), math.cos(math.radians(degrees))
                    if axis == "x": vector[:] = (x, cosine * y - sine * z, sine * y + cosine * z)
                    elif axis == "y": vector[:] = (cosine * x + sine * z, y, -sine * x + cosine * z)
                    else: vector[:] = (cosine * x - sine * y, sine * x + cosine * y, z)
                turn("z", pose["rotation"][2] * hand)
                turn("y", pose["rotation"][1] * hand)
                turn("x", pose["rotation"][0])
                turn("y", -45 * hand)
                vector[2] *= 1.2
                turn("z", -9.785 * hand)
                turn("y", 35.3 * hand)
                turn("x", -13.935)
                magnitude = math.sqrt(sum(v * v for v in vector))
                forward = [v / magnitude for v in vector]
                self.assertLess(forward[2], -.98, f"{key}: arrow faces away from crosshair")
                self.assertGreater(forward[1], .04, f"{key}: arrow slopes downward")
                self.assertLess(forward[0] * hand, -.04, f"{key}: arrow diverges from crosshair")


if __name__ == "__main__":
    unittest.main(verbosity=2)
