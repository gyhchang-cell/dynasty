"""让 Boss / 精英怪在世界里稀有刷新（第二个「boss 太少」的对策：不用等召唤也能遇到）。

用 Forge 的 add_spawns 生物群系修饰器，纯数据、零代码：
  * 每个维度各放自己的 Boss（权重很低，遇到算你运气好，也可以照旧用法阵召唤）；
  * 主世界会刷少量王朝军队与叛将（王朝的叛乱会打到主世界）。
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src/main/resources/data/dynasty/forge/biome_modifier")

# 文件后缀 -> (群系标签, [(实体, 权重, 最少, 最多)])
SPAWNS = {
    "boss_celestial": ("#dynasty:celestial", [("dynasty:dragon_emperor", 1, 1, 1)]),
    "boss_underworld": ("#dynasty:underworld", [("dynasty:undead_first_emperor", 1, 1, 1),
                                               ("dynasty:rebel_general", 3, 1, 1)]),
    "boss_jiuxiao": ("#dynasty:jiuxiao", [("dynasty:nine_heaven_general", 1, 1, 1)]),
    "boss_dragon_palace": ("#dynasty:dragon_palace", [("dynasty:dragon_king", 1, 1, 1)]),
    "elite_celestial": ("#dynasty:celestial", [("dynasty:eunuch_mastermind", 2, 1, 1)]),
    "elite_palace": ("#dynasty:dragon_palace", [("dynasty:rebel_general", 2, 1, 1)]),
    "overworld_army": ("#minecraft:is_overworld",
                       [("dynasty:imperial_soldier", 8, 1, 2),
                        ("dynasty:assassin", 6, 1, 1),
                        ("dynasty:archer", 6, 1, 2),
                        ("dynasty:royal_guard", 3, 1, 1)]),
    "overworld_boss": ("#minecraft:is_overworld", [("dynasty:rebel_general", 1, 1, 1)]),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for suffix, (biomes, spawners) in SPAWNS.items():
        path = os.path.join(OUT, "spawn_" + suffix + ".json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({
                "type": "forge:add_spawns",
                "biomes": biomes,
                "spawners": [
                    {"type": entity, "weight": weight, "minCount": low, "maxCount": high}
                    for entity, weight, low, high in spawners
                ],
            }, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print("spawn:", suffix, "->", biomes,
              ", ".join(s[0] for s in spawners))


if __name__ == "__main__":
    main()
