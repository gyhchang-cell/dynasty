"""解谜遗迹的数据与注册契约检查（不启动游戏）。

钉住这些容易「看起来对、实际不生效」的东西：
  * 结构 JSON ↔ Java 注册 ↔ 结构集 ↔ 群系标签 是否一一对上；
  * 结构集是否真的稀疏（间距不低于既有建筑），salt 不重复；
  * 九张奖励表：条目真实存在、难度递增、没有违禁奖励；
  * PuzzleService 的表名规则与文件名一致；
  * 指南针目的地包含三座遗迹；语言片段里三座遗迹有中英名（且未擅自写入共享语言文件）。

用法：python3 tools/puzzle/test_ruin_data.py
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
STRUCTURES = {
    "star_vault": "#dynasty:jiuxiao",
    "music_ruin": "#minecraft:is_overworld",
    "seal_vault": "#dynasty:underworld",
}
THEMES = {"star": "STAR", "music": "BELL", "seal": "ELEMENTS"}
VANILLA_ITEMS = {
    "minecraft:paper", "minecraft:gunpowder", "minecraft:bread", "minecraft:torch",
    "minecraft:arrow", "minecraft:iron_ingot", "minecraft:emerald",
}
FORBIDDEN = {
    "dragon_emperor_seal", "rebel_head", "eunuch_token", "emperor_bone", "sky_token", "sea_token",
    "taiyi_sword", "longyuan_sword", "tianzi_sword", "hongmeng",
}
MIN_SPACING = 42          # 既有建筑 stone_grove 是 42/14；新遗迹只能更稀疏
MIN_SEPARATION = 14
passed, failures = 0, []


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def load(path):
    return json.loads(read(path))


def check(name, ok, detail=""):
    global passed
    if ok:
        passed += 1
    else:
        failures.append(name + (" —— " + detail if detail else ""))


def main():
    registry = read(os.path.join(ROOT, "src/main/java/com/dynasty/structure/DynastyStructures.java"))
    registered_types = set(re.findall(r'STRUCTURE_TYPES\.register\("([a-z_]+)"', registry))
    registered_pieces = set(re.findall(r'PIECE_TYPES\.register\("([a-z_]+)"', registry))
    content = read(os.path.join(ROOT, "src/main/java/com/dynasty/DynastyContent.java"))
    check("DeferredRegister 仍挂在主注册点（没有新增注册点）",
          "DynastyStructures.STRUCTURE_TYPES.register(modEventBus)" in content
          and "DynastyStructures.PIECE_TYPES.register(modEventBus)" in content)

    salts = {}
    for ruin, biome in STRUCTURES.items():
        structure_path = os.path.join(DATA, "worldgen/structure/%s.json" % ruin)
        set_path = os.path.join(DATA, "worldgen/structure_set/%s.json" % ruin)
        if not (os.path.exists(structure_path) and os.path.exists(set_path)):
            check("结构与结构集文件齐备：%s" % ruin, False, "缺少 json")
            continue
        structure = load(structure_path)
        structure_set = load(set_path)
        check("结构类型已注册：%s" % ruin, ruin in registered_types)
        check("部件类型已注册：%s" % ruin, ruin + "_piece" in registered_pieces)
        check("结构 JSON 指向自己的类型：%s" % ruin, structure.get("type") == "dynasty:" + ruin)
        check("群系标签正确：%s" % ruin, structure.get("biomes") == biome, str(structure.get("biomes")))
        check("不带常驻怪物：%s" % ruin, structure.get("spawn_overrides") == {})
        check("地表生成 + 地形贴合：%s" % ruin,
              structure.get("step") == "surface_structures"
              and structure.get("terrain_adaptation") == "beard_thin")

        placement = structure_set.get("placement", {})
        spacing = placement.get("spacing", 0)
        separation = placement.get("separation", 0)
        entries = structure_set.get("structures", [])
        check("结构集引用自己：%s" % ruin,
              len(entries) == 1 and entries[0].get("structure") == "dynasty:" + ruin)
        check("稀疏度不低于既有建筑：%s" % ruin,
              spacing >= MIN_SPACING and separation >= MIN_SEPARATION and separation < spacing,
              "spacing=%s separation=%s" % (spacing, separation))
        salt = placement.get("salt")
        check("salt 不重复：%s" % ruin, salt not in salts, "与 %s 撞车" % salts.get(salt))
        salts[salt] = ruin

        if biome.startswith("#dynasty:"):
            tag = os.path.join(DATA, "tags/worldgen/biome/%s.json" % biome.split(":")[1])
            check("王朝群系标签存在：%s" % biome, os.path.exists(tag), tag)
            if os.path.exists(tag):
                check("群系标签非空：%s" % biome, len(load(tag).get("values", [])) > 0)

    # ---------------------------------------------------------------- 奖励表
    items_src = read(os.path.join(ROOT, "src/main/java/com/dynasty/DynastyItems.java"))
    zh = load(os.path.join(ROOT, "src/main/resources/assets/dynasty/lang/zh_cn.json"))
    for theme in THEMES:
        for tier in range(3):
            path = os.path.join(DATA, "loot_tables/puzzles/%s_tier%d.json" % (theme, tier))
            check("奖励表存在：%s_tier%d" % (theme, tier), os.path.exists(path))
            if not os.path.exists(path):
                continue
            table = load(path)
            pools = table.get("pools", [])
            check("奖励表至少两池：%s_tier%d" % (theme, tier), len(pools) >= 2)
            rolls = [pool.get("rolls") for pool in pools]
            check("高难度抽得更多：%s_tier%d" % (theme, tier),
                  rolls == sorted(rolls) and (tier == 0 or rolls[-1] >= tier + 1), str(rolls))
            bad = []
            for pool in pools:
                for entry in pool.get("entries", []):
                    name = entry.get("name", "")
                    if name in VANILLA_ITEMS:
                        continue
                    if not name.startswith("dynasty:"):
                        bad.append(name)
                        continue
                    short = name.split(":")[1]
                    if any(word in short for word in FORBIDDEN):
                        bad.append(name + "(违禁奖励)")
                    elif ('"item.dynasty.%s"' % short) not in json.dumps(zh, ensure_ascii=False) \
                            and short not in items_src:
                        bad.append(name + "(物品不存在)")
            check("条目都是真实且合规的物品：%s_tier%d" % (theme, tier), not bad, str(bad))

    # ---------------------------------------------------------------- 表名规则 / 指南针 / 文案
    service = read(os.path.join(ROOT, "src/main/java/com/dynasty/puzzle/PuzzleService.java"))
    for theme, kind in THEMES.items():
        check("PuzzleService 按机关映射主题表：%s" % theme,
              re.search(r"case %s -> \"%s\"" % (kind, theme), service) is not None)
    check("表名规则与文件一致（theme + _tier + 难度）",
          '"puzzles/" + theme + "_tier" + PuzzleRules.wrap(layout)' in service)

    compass = read(os.path.join(ROOT, "src/main/java/com/dynasty/DynastyCompassBridge.java"))
    for ruin in STRUCTURES:
        check("指南针目的地包含：%s" % ruin, '"%s"' % ruin in compass)

    snippet_path = os.path.join(ROOT, "docs/content/ruin-puzzles-natural-lang-additions.json")
    check("语言片段存在（待合并，未直接改共享语言文件）", os.path.exists(snippet_path))
    if os.path.exists(snippet_path):
        snippet = load(snippet_path)
        for ruin in STRUCTURES:
            key = "structure.dynasty." + ruin
            check("语言片段含中英名：%s" % key,
                  key in snippet.get("zh_cn", {}) and key in snippet.get("en_us", {}))
            check("遗迹名称已正式合入共享汉化：%s" % key,
                  isinstance(zh.get(key), str) and bool(zh[key].strip()), "缺少玩家可见的结构名称")

    print()
    if failures:
        print("通过 %d 项，失败 %d 项" % (passed, len(failures)))
        for failure in failures:
            print("  ❌", failure)
        return 1
    print("通过 %d 项，失败 0 项" % passed)
    print("✅ 遗迹数据 / 注册 / 奖励表 / 指南针 / 文案片段 全部符合约定")
    return 0


if __name__ == "__main__":
    sys.exit(main())
