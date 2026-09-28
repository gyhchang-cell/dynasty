#!/usr/bin/env python3
"""大型建筑交付物生成器：战利品表 / 成就 / 结构 JSON / 任务素材 / 语言增量 / 接入补丁。

可重复运行（覆盖式写出）；只写下面列出的文件，不碰公共注册与语言总表。
用法：python3 tools/megabuild/gen_deliverables.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def write(path, payload):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print("  写出", path)


def item(name, weight=1, low=1, high=1):
    entry = {"type": "minecraft:item", "name": name}
    if weight != 1:
        entry["weight"] = weight
    if low != high:
        entry["functions"] = [{"function": "minecraft:set_count", "count": {"min": low, "max": high}}]
    elif low > 1:
        entry["functions"] = [{"function": "minecraft:set_count", "count": low}]
    return entry


def chest_table(entries, rolls):
    # Separate pools guarantee both mod and vanilla supplies in every fresh chest.
    vanilla=[e for e in entries if e["name"].startswith("minecraft:")]
    modded=[e for e in entries if e["name"].startswith("dynasty:")]
    return {"type": "minecraft:chest", "pools": [
        {"rolls": max(1,rolls-1), "entries": vanilla},
        {"rolls": 1, "entries": modded}]}


def main():
    write("src/main/resources/data/dynasty/loot_tables/chests/tiangong_common.json", chest_table([
        item("minecraft:bread", 3, 2, 4), item("minecraft:torch", 2, 4, 8),
        item("minecraft:iron_ingot", 3, 1, 3), item("minecraft:copper_ingot", 2, 2, 4),
        item("minecraft:coal", 2, 2, 6), item("dynasty:jade", 1, 1, 1)], 3))
    write("src/main/resources/data/dynasty/loot_tables/chests/tiangong_rich.json", chest_table([
        item("dynasty:refined_steel", 2, 1, 2), item("dynasty:bronze_ingot", 2, 2, 4),
        item("dynasty:cinnabar", 2, 1, 3), item("dynasty:jade", 3, 1, 2),
        item("dynasty:silk", 1, 1, 2), item("minecraft:emerald", 2, 2, 4),
        item("minecraft:gold_ingot",3,2,5), item("minecraft:diamond",1,1,2),
        item("minecraft:golden_apple",1),item("minecraft:experience_bottle",3,3,6)], 4))

    write("src/main/resources/data/dynasty/worldgen/structure/tiangong_citadel.json", {
        "type": "dynasty:tiangong_citadel", "biomes": ["minecraft:plains","minecraft:sunflower_plains","minecraft:meadow"],
        "step": "surface_structures", "terrain_adaptation": "beard_thin", "spawn_overrides": {}})
    write("src/main/resources/data/dynasty/worldgen/structure/tiangong_mining_estate.json", {
        "type": "dynasty:tiangong_mining_estate", "biomes": ["minecraft:plains","minecraft:forest","minecraft:birch_forest"],
        "step": "surface_structures", "terrain_adaptation": "beard_thin", "spawn_overrides": {}})
    write("src/main/resources/data/dynasty/worldgen/structure_set/tiangong_citadel.json", {
        "placement": {"type": "minecraft:random_spread", "salt": 661000101, "spacing": 96, "separation": 48},
        "structures": [{"structure": "dynasty:tiangong_citadel", "weight": 1}]})
    write("src/main/resources/data/dynasty/worldgen/structure_set/tiangong_mining_estate.json", {
        "placement": {"type": "minecraft:random_spread", "salt": 661000102, "spacing": 64, "separation": 32},
        "structures": [{"structure": "dynasty:tiangong_mining_estate", "weight": 1}]})

    write("src/main/resources/data/dynasty/advancements/tiangong_citadel.json", {
        "display": {"icon": {"item": "minecraft:stone_bricks"},
                    "title": {"translate": "advancements.dynasty.tiangong_citadel.title"},
                    "description": {"translate": "advancements.dynasty.tiangong_citadel.description"},
                    "frame": "task", "show_toast": True, "announce_to_chat": True, "hidden": False},
        "criteria": {"found": {"trigger": "minecraft:location",
                               "conditions": {"player":[{"condition":"minecraft:location_check","predicate":{"dimension":"minecraft:overworld","structure":"dynasty:tiangong_citadel"}}]}}},
        "requirements": [["found"]]})
    write("src/main/resources/data/dynasty/advancements/tiangong_mining_estate.json", {
        "display": {"icon": {"item": "minecraft:iron_pickaxe"},
                    "title": {"translate": "advancements.dynasty.tiangong_mining_estate.title"},
                    "description": {"translate": "advancements.dynasty.tiangong_mining_estate.description"},
                    "frame": "task", "show_toast": True, "announce_to_chat": True, "hidden": False},
        "criteria": {"found": {"trigger": "minecraft:location",
                               "conditions": {"player":[{"condition":"minecraft:location_check","predicate":{"dimension":"minecraft:overworld","structure":"dynasty:tiangong_mining_estate"}}]}}},
        "requirements": [["found"]]})

    write("docs/megabuild/lang-additions.json", {
        "_merge_targets": ["src/main/resources/assets/dynasty/lang/zh_cn.json",
                           "src/main/resources/assets/dynasty/lang/en_us.json"],
        "zh_cn": {
            "structure.dynasty.tiangong_citadel": "天工山城",
            "structure.dynasty.tiangong_mining_estate": "山麓采矿庄园",
            "advancements.dynasty.tiangong_citadel.title": "踏足天工山城",
            "advancements.dynasty.tiangong_citadel.description": "发现并走进这座山地城寨",
            "advancements.dynasty.tiangong_mining_estate.title": "造访采矿庄园",
            "advancements.dynasty.tiangong_mining_estate.description": "发现山麓的采矿庄园",
        },
        "en_us": {
            "structure.dynasty.tiangong_citadel": "Tiangong Citadel",
            "structure.dynasty.tiangong_mining_estate": "Mining Estate at the Foothills",
            "advancements.dynasty.tiangong_citadel.title": "Enter the Tiangong Citadel",
            "advancements.dynasty.tiangong_citadel.description": "Discover this mountain fortress",
            "advancements.dynasty.tiangong_mining_estate.title": "Visit the Mining Estate",
            "advancements.dynasty.tiangong_mining_estate.description": "Discover the foothill mining estate",
        },
    })

    additions=json.load(open(os.path.join(ROOT,"docs/megabuild/lang-additions.json"),encoding="utf-8"))
    for locale in ("zh_cn","en_us"):
        target="src/main/resources/assets/dynasty/lang/"+locale+".json"
        with open(os.path.join(ROOT,target),encoding="utf-8") as handle: current=json.load(handle)
        current.update(additions[locale])
        write(target,current)
    print("完成：结构、成就、战利品与语言合并")


if __name__ == "__main__":
    main()
