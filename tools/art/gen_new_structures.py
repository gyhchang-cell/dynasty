"""四个新结构的世界生成 JSON（structure + structure_set）。

对应 Java：`com.dynasty.structure.{Academy,WallGate,StoneGrove,StarAltar}Structure`
与 `DynastyStructures` 里的注册。生成后可直接 `/locate structure dynasty:<id>`。

用法：python3 tools/art/gen_new_structures.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WG = os.path.join(ROOT, "src/main/resources/data/dynasty/worldgen")

# id -> (群系标签, 地形贴合, 盐, 间距, 间隔)
STRUCTURES = {
    "academy": ("#dynasty:celestial", "beard_thin", 460000001, 46, 14),
    "great_wall_gate": ("#dynasty:celestial", "beard_thin", 460000002, 34, 8),
    "stone_grove": ("#dynasty:underworld", "beard_thin", 460000003, 30, 6),
    "star_altar": ("#dynasty:jiuxiao", "beard_thin", 460000004, 40, 10),
}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    for name, (biomes, adapt, salt, spacing, separation) in STRUCTURES.items():
        write(os.path.join(WG, "structure/%s.json" % name), {
            "type": "dynasty:%s" % name,
            "biomes": biomes,
            "step": "surface_structures",
            "terrain_adaptation": adapt,
            "spawn_overrides": {},
        })
        write(os.path.join(WG, "structure_set/%s.json" % name), {
            "placement": {
                "type": "minecraft:random_spread",
                "salt": salt,
                "separation": separation,
                "spacing": spacing,
            },
            "structures": [{"structure": "dynasty:%s" % name, "weight": 1}],
        })
        print("structure wired:", name, biomes, "spacing", spacing)


if __name__ == "__main__":
    main()
