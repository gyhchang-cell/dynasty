"""生成/更新王朝宝箱战利品表（建筑里开箱子能开出饰品与高阶材料）。

- palace_ruin / imperial_mausoleum（材料池 + 饰品池）
- temple / ritual_circle / barracks / watchtower 四张表（新建筑专用）
- 第三十四轮起：dynasty_palace / imperial_tomb 两张表也由这里生成（原来手写），
  并且所有表都补上「异版饰品 + 高阶材料」——新饰品不再只能靠合成。

饰品用加权随机（weight 越大越常见），并且只有一半概率触发饰品池。
运行：python3 tools/art/gen_loot.py，之后跑 python3 tools/art/verify_loot.py
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

# ============================================================================
# 第三十四轮：把「新结构专用」的两张表（帝宫 / 皇陵）也收进生成器，
# 并给所有表补上「异版饰品」与高阶材料 —— 之前新饰品只能靠合成，探索没有回报。
# Round 34: bring the two hand-written tables into the generator and add the new
# accessories + high-tier materials so exploring a structure actually pays off.
# ============================================================================

# 帝宫（金銮殿 / 皇宫）：天朝敕令系饰品 + 图纸 + 帝骸骨
MATERIALS["dynasty_palace"] = [
    ("dynasty:gold_coin", 2, 6, 10), ("dynasty:jade_coin", 3, 8, 9),
    ("dynasty:brocade", 1, 4, 8), ("dynasty:official_seal", 1, 1, 6),
    ("dynasty:ink_stick", 1, 3, 6), ("dynasty:blueprint", 1, 2, 5),
    ("dynasty:emperor_bone", 1, 2, 4), ("dynasty:taiyi_jade", 1, 1, 3),
    ("dynasty:hunyuan_pearl", 1, 1, 2),
]
TRINKETS["dynasty_palace"] = [
    ("dynasty:edict_of_mandate", 16, 1, 1), ("dynasty:edict_of_loyalty", 16, 1, 1),
    ("dynasty:seal_of_two_heavens", 12, 1, 1), ("dynasty:throne_inheritance_charm", 10, 1, 1),
    ("dynasty:merit_badge", 10, 1, 1), ("dynasty:gold_seal_charm", 8, 1, 1),
    ("dynasty:imperial_seal_charm", 8, 1, 1), ("dynasty:war_deity_signet", 4, 1, 1),
]
ROLLS["dynasty_palace"] = 4

# 皇陵（守陵石像群）：幽冥献祭系饰品 + 帝骸骨 + 图纸
MATERIALS["imperial_tomb"] = [
    ("dynasty:emperor_bone", 1, 3, 10), ("dynasty:jade", 2, 6, 9),
    ("dynasty:talisman_paper", 2, 6, 8), ("dynasty:cinnabar", 2, 5, 8),
    ("dynasty:jade_coin", 3, 8, 7), ("dynasty:blueprint", 1, 2, 5),
    ("minecraft:netherite_scrap", 1, 1, 2), ("dynasty:hunyuan_pearl", 1, 1, 2),
]
TRINKETS["imperial_tomb"] = [
    ("dynasty:tomb_warden_seal", 16, 1, 1), ("dynasty:candle_of_the_dead", 14, 1, 1),
    ("dynasty:ghost_ferry_tally", 14, 1, 1), ("dynasty:bone_chill_pendant", 10, 1, 1),
    ("dynasty:jade_shroud_charm", 8, 1, 1), ("dynasty:sacrificial_blade_charm", 5, 1, 1),
    ("dynasty:tomb_candle", 10, 1, 1),
]
ROLLS["imperial_tomb"] = 4

# ---- 既有六张表：补「异版饰品」与高阶材料（权重压低，只是探索彩蛋）----
TRINKETS["imperial_mausoleum"] += [
    ("dynasty:bone_reaper_tally", 6, 1, 1), ("dynasty:blood_iron_sash", 5, 1, 1),
    ("dynasty:soul_candle_charm", 4, 1, 1), ("dynasty:deathbed_talisman", 3, 1, 1),
]
MATERIALS["imperial_mausoleum"] += [
    ("dynasty:blueprint", 1, 2, 5), ("dynasty:hunyuan_pearl", 1, 1, 2),
    ("dynasty:taiyi_jade", 1, 1, 3),
]
TRINKETS["temple"] += [
    ("dynasty:ranging_compass_charm", 8, 1, 1), ("dynasty:wound_binder_charm", 6, 1, 1),
    ("dynasty:iron_ration_charm", 5, 1, 1),
]
MATERIALS["temple"] += [("dynasty:zhuque_feather", 1, 1, 3), ("dynasty:qinglong_scale", 1, 1, 3)]
TRINKETS["ritual_circle"] += [
    ("dynasty:eclipse_bead", 6, 1, 1), ("dynasty:moonlit_mirror", 6, 1, 1),
    ("dynasty:starless_night_ring", 4, 1, 1),
]
MATERIALS["ritual_circle"] += [("dynasty:thunder_token", 1, 1, 3), ("dynasty:taiyi_jade", 1, 1, 2)]
TRINKETS["barracks"] += [
    ("dynasty:cavalry_sash", 8, 1, 1), ("dynasty:siege_hammer_charm", 6, 1, 1),
    ("dynasty:dusk_raider_badge", 6, 1, 1),
]
MATERIALS["barracks"] += [("dynasty:baihu_fang", 1, 1, 3), ("dynasty:xuanwu_shell", 1, 1, 3)]
TRINKETS["watchtower"] += [("dynasty:quickdraw_glove", 6, 1, 1)]
MATERIALS["watchtower"] += [("dynasty:blueprint", 1, 1, 3)]
TRINKETS["palace_ruin"] += [
    ("dynasty:sun_chaser_ring", 6, 1, 1), ("dynasty:dawn_drum", 5, 1, 1),
    ("dynasty:noon_pendant", 5, 1, 1),
]
MATERIALS["palace_ruin"] += [("dynasty:blueprint", 1, 2, 5)]


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
