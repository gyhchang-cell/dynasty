"""生成/更新王朝宝箱战利品表（建筑里开箱子能开出饰品）。

- 重写 palace_ruin / imperial_mausoleum（材料池 + 饰品池）
- 新增 temple / ritual_circle / barracks / watchtower 四张表（新建筑专用）

饰品用加权随机（weight 越大越常见），并且只有一半概率触发饰品池。
运行：python3 tools/art/gen_loot.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src/main/resources/data/dynasty/loot_tables/chests")
os.makedirs(OUT, exist_ok=True)

# 材料池：(物品, 最少, 最多, 权重)
MATERIALS = {
    "palace_ruin": [
        ("dynasty:jade", 1, 4, 10), ("dynasty:bronze_ingot", 2, 6, 10),
        ("dynasty:gold_coin", 1, 3, 8), ("dynasty:silver_coin", 2, 6, 8),
        ("minecraft:gold_ingot", 1, 3, 6), ("dynasty:talisman_paper", 1, 3, 6),
        ("dynasty:silk", 1, 4, 6), ("dynasty:official_seal", 1, 1, 3),
    ],
    "imperial_mausoleum": [
        ("dynasty:dragon_crystal", 1, 3, 8), ("dynasty:dragon_scale", 1, 4, 8),
        ("dynasty:jade_coin", 3, 8, 8), ("dynasty:jade", 2, 6, 8),
        ("dynasty:dragon_coin", 1, 3, 6), ("minecraft:diamond", 1, 3, 5),
        ("dynasty:emperor_bone", 1, 1, 3), ("minecraft:netherite_scrap", 1, 1, 2),
    ],
    "temple": [
        ("dynasty:jade", 2, 6, 10), ("dynasty:silver_ingot", 2, 5, 8),
        ("dynasty:cinnabar", 2, 5, 8), ("dynasty:brocade", 1, 3, 6),
        ("dynasty:refined_steel", 1, 3, 5), ("dynasty:blueprint", 1, 2, 5),
        ("minecraft:emerald", 2, 6, 4),
    ],
    "ritual_circle": [
        ("dynasty:jade", 2, 5, 10), ("dynasty:dragon_crystal", 1, 2, 6),
        ("dynasty:cinnabar", 2, 4, 8), ("dynasty:talisman_paper", 2, 4, 8),
        ("dynasty:jade_coin", 2, 6, 6), ("dynasty:blueprint", 1, 2, 4),
    ],
    "barracks": [
        ("minecraft:iron_ingot", 2, 6, 10), ("dynasty:bronze_ingot", 2, 6, 10),
        ("dynasty:copper_coin", 3, 8, 8), ("dynasty:refined_steel", 1, 3, 6),
        ("minecraft:arrow", 4, 12, 8), ("dynasty:silver_ingot", 1, 3, 5),
        ("minecraft:shield", 1, 1, 3),
    ],
    "watchtower": [
        ("minecraft:torch", 4, 12, 10), ("dynasty:copper_coin", 2, 6, 8),
        ("dynasty:brocade", 1, 3, 6), ("minecraft:bread", 2, 6, 6),
        ("dynasty:ink_stick", 1, 3, 5), ("minecraft:spyglass", 1, 1, 2),
    ],
}

# 饰品池：(物品, 权重, 最少, 最多)
TRINKETS = {
    "palace_ruin": [
        ("dynasty:heart_mirror", 20, 1, 1), ("dynasty:jade_cicada", 18, 1, 1),
        ("dynasty:tiger_crest", 18, 1, 1), ("dynasty:cinnabar_pouch", 16, 1, 1),
        ("dynasty:tiger_token", 16, 1, 1), ("dynasty:iron_waist_token", 14, 1, 1),
        ("dynasty:auspicious_bell", 10, 1, 1), ("dynasty:war_horse_bell", 8, 1, 1),
        ("dynasty:storm_charm", 6, 1, 1), ("dynasty:jade_crown", 6, 1, 1),
    ],
    "imperial_mausoleum": [
        ("dynasty:jade_crown", 18, 1, 1), ("dynasty:moon_pendant", 16, 1, 1),
        ("dynasty:sun_feather", 16, 1, 1), ("dynasty:dragon_whisker", 14, 1, 1),
        ("dynasty:phoenix_ring", 12, 1, 1), ("dynasty:dragon_pearl", 8, 1, 1),
        ("dynasty:heart_mirror", 8, 1, 1), ("dynasty:jade_tortoise", 6, 1, 1),
    ],
    "temple": [
        ("dynasty:jade_tortoise", 20, 1, 1), ("dynasty:moon_pendant", 18, 1, 1),
        ("dynasty:sun_feather", 18, 1, 1), ("dynasty:auspicious_bell", 16, 1, 1),
        ("dynasty:storm_charm", 14, 1, 1), ("dynasty:cinnabar_pouch", 14, 1, 1),
        ("dynasty:dragon_pearl", 6, 1, 1), ("dynasty:dragon_whisker", 6, 1, 1),
    ],
    "ritual_circle": [
        ("dynasty:war_drum_charm", 20, 1, 1), ("dynasty:cinnabar_pouch", 18, 1, 1),
        ("dynasty:jade_cicada", 16, 1, 1), ("dynasty:tiger_crest", 14, 1, 1),
        ("dynasty:phoenix_ring", 10, 1, 1), ("dynasty:dragon_pearl", 8, 1, 1),
        ("dynasty:jade_tortoise", 8, 1, 1),
    ],
    "barracks": [
        ("dynasty:tiger_token", 22, 1, 1), ("dynasty:iron_waist_token", 20, 1, 1),
        ("dynasty:war_horse_bell", 18, 1, 1), ("dynasty:war_drum_charm", 14, 1, 1),
        ("dynasty:tiger_crest", 12, 1, 1), ("dynasty:heart_mirror", 10, 1, 1),
        ("dynasty:auspicious_bell", 8, 1, 1),
    ],
    "watchtower": [
        ("dynasty:tiger_crest", 20, 1, 1), ("dynasty:jade_cicada", 18, 1, 1),
        ("dynasty:cinnabar_pouch", 16, 1, 1), ("dynasty:south_pointing_compass", 14, 1, 1),
        ("dynasty:auspicious_bell", 12, 1, 1), ("dynasty:tiger_token", 10, 1, 1),
    ],
}

ROLLS = {"palace_ruin": 3, "imperial_mausoleum": 5, "temple": 4,
         "ritual_circle": 3, "barracks": 3, "watchtower": 3}


def count(minimum, maximum):
    return [{"function": "minecraft:set_count",
             "count": {"min": minimum, "max": maximum}}]


def build(name):
    material_entries = [
        {"type": "minecraft:item", "name": item, "weight": weight, "functions": count(low, high)}
        for item, low, high, weight in MATERIALS[name]
    ]
    trinket_entries = [
        {"type": "minecraft:item", "name": item, "weight": weight, "functions": count(low, high)}
        for item, weight, low, high in TRINKETS[name]
    ]
    table = {
        "type": "minecraft:chest",
        "pools": [
            {"rolls": ROLLS[name], "entries": material_entries},
            {"rolls": 1, "entries": trinket_entries,
             "conditions": [{"condition": "minecraft:random_chance", "chance": 0.5}]},
        ],
    }
    path = os.path.join(OUT, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("loot table:", name, len(material_entries), "materials +",
          len(trinket_entries), "trinkets")


if __name__ == "__main__":
    for key in MATERIALS:
        build(key)
