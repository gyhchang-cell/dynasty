"""新建筑的世界生成 JSON（configured_feature / placed_feature / biome_modifier）。"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WG = os.path.join(ROOT, "src/main/resources/data/dynasty/worldgen")
BM = os.path.join(ROOT, "src/main/resources/data/dynasty/forge/biome_modifier")

# id -> (出现概率分母, 放到哪些群系标签, 落点高度图)
BUILDINGS = {
    "great_wall": (110, ["#dynasty:celestial"], "WORLD_SURFACE_WG"),
    "pagoda": (240, ["#dynasty:celestial", "#dynasty:underworld"], "WORLD_SURFACE_WG"),
    "heaven_altar": (300, ["#dynasty:celestial"], "WORLD_SURFACE_WG"),
    "post_station": (150, ["#dynasty:celestial"], "WORLD_SURFACE_WG"),
    "paifang": (80, ["#dynasty:celestial", "#dynasty:underworld"], "WORLD_SURFACE_WG"),
    # 第二批：法阵 / 神庙 / 兵营 / 烽火台
    "ritual_circle": (200, ["#dynasty:celestial", "#dynasty:underworld"], "WORLD_SURFACE_WG"),
    "temple": (280, ["#dynasty:celestial"], "WORLD_SURFACE_WG"),
    "barracks": (190, ["#dynasty:celestial"], "WORLD_SURFACE_WG"),
    "watchtower": (130, ["#dynasty:celestial", "#dynasty:underworld"], "WORLD_SURFACE_WG"),
    # 第三批：各维度新建筑（中式构件拼的：台基/重檐/翘檐/院落）
    "hall": (230, ["#dynasty:celestial"], "WORLD_SURFACE_WG"),
    "observatory": (330, ["#dynasty:celestial"], "WORLD_SURFACE_WG"),
    "market": (260, ["#dynasty:celestial"], "WORLD_SURFACE_WG"),
    "ghost_gate": (190, ["#dynasty:underworld"], "WORLD_SURFACE_WG"),
    "judge_hall": (300, ["#dynasty:underworld"], "WORLD_SURFACE_WG"),
    "bridge": (210, ["#dynasty:underworld"], "WORLD_SURFACE_WG"),
    "sky_stair": (240, ["#dynasty:jiuxiao"], "WORLD_SURFACE_WG"),
    "thunder_pool": (300, ["#dynasty:jiuxiao"], "WORLD_SURFACE_WG"),
    "dragon_hall": (240, ["#dynasty:dragon_palace"], "OCEAN_FLOOR_WG"),
    "pearl_tower": (280, ["#dynasty:dragon_palace"], "OCEAN_FLOOR_WG"),
}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


for name, (chance, biomes, heightmap) in BUILDINGS.items():
    write(os.path.join(WG, "configured_feature", name + ".json"),
          {"type": "dynasty:" + name, "config": {}})
    write(os.path.join(WG, "placed_feature", name + ".json"), {
        "feature": "dynasty:" + name,
        "placement": [
            {"type": "minecraft:rarity_filter", "chance": chance},
            {"type": "minecraft:in_square"},
            {"type": "minecraft:heightmap", "heightmap": heightmap},
            {"type": "minecraft:biome"},
        ],
    })
    for index, biome in enumerate(biomes):
        # 注意：**不再**生成「加建筑」的 biome modifier。
        # 修饰器注入的特征在 biome JSON 里看不到，自检查不出来，直接崩过三次
        # （Feature order cycle，天境/地狱/九霄）。现在只保留 placed/configured 特征，
        # 由 tools/art/fix_building_placement.py 写进静态 stage 4（顺序统一、可自检）。
        # Building placement is static-only on purpose; see fix_building_placement.py.
        pass
    print("building json:", name, "->", ", ".join(biomes))
print("done")
