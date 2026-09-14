"""装备自检：新增的护甲 / 饰品必须「表、贴图、模型、配方、词条、Curios 标签」六处齐全。

为什么要有这一步（踩过的坑）：
  * 饰品的 id 只写在 Python 表里、忘了注册进 Java → 物品根本不存在；
  * 注册了却没进 `dynasty_trinket` Curios 标签 → 玩家戴不上；
  * 贴图忘了生成 → 游戏里是紫黑格；
  * 护甲的四处 Java 表（材质 / 注册 / 套装加成 / 提示名）少改一处 →
    要么合成不出来，要么不显示「套装加成」。

所以这里把 gen_armor3.py / gen_trinkets3.py 的表当成唯一真源，逐项核对产物。
运行：python3 tools/art/verify_gear.py
"""
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
CURIOS = os.path.join(ROOT, "src/main/resources/data/curios/tags/items/dynasty_trinket.json")
SRC = os.path.join(ROOT, "src/main/java/com/dynasty")
PIECES = ("helmet", "chestplate", "leggings", "boots")

problems = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return open(path, encoding="utf-8").read()


def check_trinkets():
    table = load("gen_trinkets3", os.path.join(ROOT, "tools/art/gen_trinkets3.py")).TRINKETS
    java = read(os.path.join(SRC, "DynastyTrinkets.java"))
    java_ids = re.findall(r'\{"([a-z_]+)", -?\d+, ', java)
    missing_java = [t for t in table if t not in java_ids]
    extra_java = [t for t in java_ids if t not in table]
    for tid in missing_java:
        problems.append("饰品 %s 没写进 DynastyTrinkets.EXTRA_TABLE（物品不会被注册）" % tid)
    for tid in extra_java:
        problems.append("DynastyTrinkets.EXTRA_TABLE 里的 %s 不在 gen_trinkets3.py 表里" % tid)
    if len(java_ids) != len(set(java_ids)):
        problems.append("EXTRA_TABLE 里有重复 id")

    tag = json.load(open(CURIOS, encoding="utf-8"))
    values = set(tag.get("values", []))
    lang_zh = json.load(open(os.path.join(ASSETS, "lang/zh_cn.json"), encoding="utf-8"))
    lang_en = json.load(open(os.path.join(ASSETS, "lang/en_us.json"), encoding="utf-8"))
    for tid in table:
        if "dynasty:%s" % tid not in values:
            problems.append("饰品 %s 没进 Curios 标签（戴不上）" % tid)
        if not os.path.exists(os.path.join(ASSETS, "textures/item/%s.png" % tid)):
            problems.append("饰品 %s 缺贴图" % tid)
        if not os.path.exists(os.path.join(ASSETS, "models/item/%s.json" % tid)):
            problems.append("饰品 %s 缺模型" % tid)
        if not os.path.exists(os.path.join(DATA, "recipes/%s.json" % tid)):
            problems.append("饰品 %s 缺配方" % tid)
        for lang, name in ((lang_zh, "zh_cn"), (lang_en, "en_us")):
            if "item.dynasty.%s" % tid not in lang:
                problems.append("饰品 %s 缺 %s 词条" % (tid, name))
    print("饰品自检：表 %d 件，Java 注册 %d 件，Curios 标签 %d 件"
          % (len(table), len(java_ids), len(values)))


def check_armor():
    table = load("gen_armor3", os.path.join(ROOT, "tools/art/gen_armor3.py")).SETS
    materials = read(os.path.join(SRC, "DynastyArmorMaterials.java"))
    gear = read(os.path.join(SRC, "DynastyGear.java"))
    balance = read(os.path.join(SRC, "DynastyBalance.java"))
    tooltips = read(os.path.join(SRC, "client/DynastyTooltips.java"))
    lang_zh = json.load(open(os.path.join(ASSETS, "lang/zh_cn.json"), encoding="utf-8"))
    lang_en = json.load(open(os.path.join(ASSETS, "lang/en_us.json"), encoding="utf-8"))
    for set_id in table:
        if not re.search(r'public static final ArmorMaterial %s =' % set_id.upper(), materials):
            problems.append("护甲 %s 没有材质常量（DynastyArmorMaterials）" % set_id)
        if ('{"%s", DynastyArmorMaterials.%s}' % (set_id, set_id.upper())) not in gear:
            problems.append("护甲 %s 没有进 DynastyGear.EXTRA_SET_TABLE（物品不会注册）" % set_id)
        if 'SET_BONUS.put("%s"' % set_id not in balance:
            problems.append("护甲 %s 没有进 DynastyBalance.SET_BONUS（没有套装加成）" % set_id)
        if 'path.startsWith("%s")' % set_id not in tooltips:
            problems.append("护甲 %s 没有进 DynastyTooltips.setName（提示不显示套装名）" % set_id)
        for piece in PIECES:
            name = "%s_%s" % (set_id, piece)
            if not os.path.exists(os.path.join(ASSETS, "textures/item/%s.png" % name)):
                problems.append("护甲 %s 缺贴图" % name)
            if not os.path.exists(os.path.join(ASSETS, "models/item/%s.json" % name)):
                problems.append("护甲 %s 缺模型" % name)
            if not os.path.exists(os.path.join(DATA, "recipes/%s.json" % name)):
                problems.append("护甲 %s 缺配方" % name)
            for lang, tag in ((lang_zh, "zh_cn"), (lang_en, "en_us")):
                if "item.dynasty.%s" % name not in lang:
                    problems.append("护甲 %s 缺 %s 词条" % (name, tag))
        for layer in (1, 2):
            path = os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png" % (set_id, layer))
            if not os.path.exists(path):
                problems.append("护甲 %s 缺穿在身上的图层贴图 layer_%d" % (set_id, layer))
    print("护甲自检：表 %d 套（%d 件）" % (len(table), len(table) * len(PIECES)))


def main():
    check_trinkets()
    check_armor()
    if problems:
        print("装备自检：发现问题 ❌")
        for problem in problems[:25]:
            print("   -", problem)
        sys.exit(1)
    print("装备自检：通过 ✅（护甲与饰品的表 / 贴图 / 模型 / 配方 / 词条 / Curios 标签六处齐全）")


if __name__ == "__main__":
    main()
