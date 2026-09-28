#!/usr/bin/env python3
"""解谜遗迹的**唯一配置源**：三座结构 + 结构集 + 九张主题奖励表。

为什么会有一个生成器：奖励数量 / 权重 / 结构间距都集中在这张表里，
Java 里只留「机关类型 + 难度档 → 战利品表 id」的映射，不散落常量。

可重复运行（覆盖式写出）；只写下面列出的文件，不碰其它数据。
用法：python3 tools/puzzle/gen_ruin_loot.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOOT_DIR = os.path.join(ROOT, "src/main/resources/data/dynasty/loot_tables/puzzles")
STRUCTURE_DIR = os.path.join(ROOT, "src/main/resources/data/dynasty/worldgen/structure")
SET_DIR = os.path.join(ROOT, "src/main/resources/data/dynasty/worldgen/structure_set")

# ---------------------------------------------------------------- 三座遗迹
# spacing / separation 都比既有建筑更稀疏（既有 stone_grove 是 42/14），避免建筑扎堆。
RUINS = {
    "star_vault": {"biomes": "#dynasty:jiuxiao", "salt": 551000101, "spacing": 48, "separation": 18},
    "music_ruin": {"biomes": "#minecraft:is_overworld", "salt": 551000102, "spacing": 56, "separation": 20},
    "seal_vault": {"biomes": "#dynasty:underworld", "salt": 551000103, "spacing": 44, "separation": 14},
}

# ---------------------------------------------------------------- 奖励（难度越高越厚）
# 每个条目：(物品 id, 权重, 最少, 最多)；同一池内按权重抽一条。
REWARDS = {
    "star": {                      # 观星密室：符纸 / 玉 / 少量符箓材料
        0: [("dynasty:talisman_paper", 1, 2, 4),
            ("dynasty:jade", 3, 1, 1),
            ("minecraft:paper", 3, 4, 8),
            ("minecraft:gunpowder", 2, 1, 2)],
        1: [("dynasty:talisman_paper", 1, 3, 6),
            ("dynasty:jade", 3, 1, 2),
            ("dynasty:cinnabar", 2, 1, 2),
            ("minecraft:paper", 2, 6, 12)],
        2: [("dynasty:talisman_paper", 1, 4, 8),
            ("dynasty:jade", 3, 2, 3),
            ("dynasty:cinnabar", 1, 2, 3),
            ("minecraft:gunpowder", 2, 3, 6)],
    },
    "music": {                     # 古乐遗址：书院 / 科举材料 + 货币 + 补给
        0: [("dynasty:exam_paper", 1, 1, 1),
            ("dynasty:bamboo_slip", 3, 1, 2),
            ("minecraft:bread", 3, 2, 4),
            ("minecraft:torch", 2, 4, 8)],
        1: [("dynasty:exam_paper", 1, 1, 2),
            ("dynasty:bamboo_slip", 3, 2, 3),
            ("dynasty:ink_stick", 2, 1, 2),
            ("minecraft:emerald", 3, 2, 4),
            ("minecraft:bread", 2, 3, 5)],
        2: [("dynasty:exam_paper", 1, 2, 2),
            ("dynasty:silk", 2, 1, 2),
            ("dynasty:ink_stick", 2, 1, 3),
            ("minecraft:emerald", 3, 4, 6),
            ("minecraft:bread", 2, 4, 6)],
    },
    "seal": {                      # 四象封印室：探索 / 锻造材料 + 补给
        0: [("dynasty:refined_steel", 1, 1, 2),
            ("minecraft:iron_ingot", 3, 2, 4),
            ("minecraft:bread", 3, 2, 4),
            ("minecraft:arrow", 2, 8, 16)],
        1: [("dynasty:refined_steel", 1, 2, 3),
            ("dynasty:bronze_ingot", 2, 2, 3),
            ("minecraft:iron_ingot", 3, 3, 6),
            ("minecraft:arrow", 2, 12, 24),
            ("minecraft:torch", 2, 6, 12)],
        2: [("dynasty:refined_steel", 1, 3, 4),
            ("dynasty:jade", 2, 1, 2),
            ("dynasty:bronze_ingot", 2, 3, 5),
            ("minecraft:emerald", 3, 3, 5),
            ("minecraft:bread", 2, 4, 6)],
    },
}

# 每张表都保证保底一件「主题招牌」，所以永远不会空手
SIGNATURE = {"star": "dynasty:talisman_paper", "music": "dynasty:bamboo_slip", "seal": "dynasty:refined_steel"}


def item_entry(item, weight, low, high):
    entry = {"type": "minecraft:item", "name": item}
    if weight != 1:
        entry["weight"] = weight
    if low != high:
        entry["functions"] = [{"function": "minecraft:set_count", "count": {"min": low, "max": high}}]
    elif low > 1:
        entry["functions"] = [{"function": "minecraft:set_count", "count": low}]
    return entry


def loot_table(theme, tier):
    entries = [item_entry(item, weight, low, high) for item, weight, low, high in REWARDS[theme][tier]]
    return {
        "type": "minecraft:generic",
        "pools": [
            {"rolls": 1, "entries": [item_entry(SIGNATURE[theme], 1, 1, 2)]},
            {"rolls": 1, "entries": entries},
            {"rolls": 1 + tier, "entries": list(entries)},
        ],
    }


def structure(ruin, spec):
    return {
        "type": "dynasty:" + ruin,
        "biomes": spec["biomes"],
        "step": "surface_structures",
        "terrain_adaptation": "beard_thin",
        "spawn_overrides": {},
    }


def structure_set(ruin, spec):
    return {
        "placement": {
            "type": "minecraft:random_spread",
            "salt": spec["salt"],
            "separation": spec["separation"],
            "spacing": spec["spacing"],
        },
        "structures": [{"structure": "dynasty:" + ruin, "weight": 1}],
    }


def write(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print("  写出", os.path.relpath(path, ROOT))


def main():
    print("== 结构 + 结构集 ==")
    for ruin, spec in RUINS.items():
        write(os.path.join(STRUCTURE_DIR, ruin + ".json"), structure(ruin, spec))
        write(os.path.join(SET_DIR, ruin + ".json"), structure_set(ruin, spec))
    print("== 主题奖励表（3 主题 × 3 难度）==")
    for theme in REWARDS:
        for tier in REWARDS[theme]:
            write(os.path.join(LOOT_DIR, "%s_tier%d.json" % (theme, tier)), loot_table(theme, tier))
    write(os.path.join(LOOT_DIR, 'treasury_materials.json'), treasury_materials())
    print("完成：3 结构 / 3 结构集 / 9 奖励表")


def treasury_materials():
    """Sealed side caches: guaranteed upgrade supplies, one finite roll per chest."""
    return {'type': 'minecraft:chest', 'pools': [
        {'rolls': 1, 'entries': [item_entry('dynasty:jade', 1, 4, 8)]},
        {'rolls': 1, 'entries': [item_entry('dynasty:dragon_crystal', 1, 2, 4)]},
        {'rolls': 1, 'entries': [item_entry('dynasty:xuantian_jade', 1, 1, 2)]},
        {'rolls': 1, 'entries': [item_entry('minecraft:experience_bottle', 1, 8, 16)]},
    ]}


if __name__ == "__main__":
    main()
