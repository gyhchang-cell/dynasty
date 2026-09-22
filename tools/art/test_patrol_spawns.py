"""Regression: population category, small groups and idempotent scoped generation."""
import copy
import json
from pathlib import Path
import unittest

from gen_spawns_json import PATROL_BIOMES, SOLDIER, ROOT, normalize_patrols


def validate_patrol_spawns():
    problems = []
    folder = Path(ROOT) / "src/main/resources/data/dynasty/worldgen/biome"
    for path in folder.glob("*.json"):
        biome = json.loads(path.read_text(encoding="utf-8"))
        entries = [(category, e) for category, spawns in biome["spawners"].items()
                   for e in spawns if e["type"] == SOLDIER]
        if path.stem in PATROL_BIOMES and len(entries) != 1:
            problems.append(f"{path.name}: patrol entry must occur exactly once")
        for category, entry in entries:
            if category != "creature" or entry != {"type": SOLDIER, "weight": 3, "minCount": 1, "maxCount": 1}:
                problems.append(f"{path.name}: soldier must use creature cap, weight 3, single spawn")
    modifier = Path(ROOT) / "src/main/resources/data/dynasty/forge/biome_modifier/spawn_overworld_army.json"
    soldiers = [e for e in json.loads(modifier.read_text())["spawners"] if e["type"] == SOLDIER]
    if soldiers != [{"type": SOLDIER, "weight": 3, "minCount": 1, "maxCount": 1}]:
        problems.append("Overworld patrol modifier must match the low-density policy")
    return problems


class PatrolSpawns(unittest.TestCase):
    def test_live_resources(self):
        self.assertEqual([], validate_patrol_spawns())

    def test_generator_is_scoped_and_idempotent(self):
        biome = {"features": [["dynasty:hall"]], "temperature": .8,
                 "spawners": {"monster": [{"type": SOLDIER, "weight": 30, "minCount": 1, "maxCount": 4},
                                           {"type": "dynasty:jade_guard", "weight": 30}],
                              "creature": [{"type": "minecraft:cow", "weight": 8}]}}
        original = copy.deepcopy(biome)
        normalize_patrols(biome)
        once = copy.deepcopy(biome)
        normalize_patrols(biome)
        self.assertEqual(once, biome)
        self.assertEqual(original["features"], biome["features"])
        self.assertEqual(original["temperature"], biome["temperature"])
        self.assertEqual(original["spawners"]["monster"][1:], biome["spawners"]["monster"])
        self.assertEqual(original["spawners"]["creature"], biome["spawners"]["creature"][:-1])


if __name__ == "__main__":
    unittest.main()
