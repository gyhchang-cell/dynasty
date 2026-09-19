"""装备自检：新增的护甲 / 饰品必须「表、贴图、模型、配方、词条、Curios 标签」六处齐全。

为什么要有这一步（踩过的坑）：
  * 饰品的 id 只写在 Python 表里、忘了注册进 Java → 物品根本不存在；
  * 注册了却没有标准 Curios 分类 → 玩家戴不上（分类由 verify_curios 补充核对）；
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
CURIOS = os.path.join(ROOT, "src/main/resources/data/dynasty/tags/items/accessories.json")
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
    # 真源 = 所有饰品生成器（每批一张表）/ source of truth: every trinket generator table
    table = {}
    for generator in ("gen_trinkets3", "gen_trinkets4", "gen_trinkets5"):
        path = os.path.join(ROOT, "tools/art/%s.py" % generator)
        if os.path.exists(path):
            table.update(load(generator, path).TRINKETS)
    java = read(os.path.join(SRC, "DynastyTrinkets.java"))
    java_ids = re.findall(r'\{"([a-z_]+)", -?\d+, ', java)
    missing_java = [t for t in table if t not in java_ids]
    extra_java = [t for t in java_ids if t not in table]
    for tid in missing_java:
        problems.append("饰品 %s 没写进 DynastyTrinkets.EXTRA_TABLE（物品不会被注册）" % tid)
    for tid in extra_java:
        problems.append("DynastyTrinkets.EXTRA_TABLE 里的 %s 不在饰品生成器表里" % tid)
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
        else:
            from PIL import Image
            with Image.open(os.path.join(ASSETS, "textures/item/%s.png" % tid)) as image:
                if image.size != (32, 32):
                    problems.append("饰品 %s 的贴图不是 32×32（实际 %s）"
                                    % (tid, "×".join(str(n) for n in image.size)))
                if image.convert("RGBA").getchannel("A").getextrema()[1] == 0:
                    problems.append("饰品 %s 的贴图全透明（画失败？）" % tid)
        if not os.path.exists(os.path.join(ASSETS, "models/item/%s.json" % tid)):
            problems.append("饰品 %s 缺模型" % tid)
        if not os.path.exists(os.path.join(DATA, "recipes/%s.json" % tid)):
            problems.append("饰品 %s 缺配方" % tid)
        for lang, name in ((lang_zh, "zh_cn"), (lang_en, "en_us")):
            if "item.dynasty.%s" % tid not in lang:
                problems.append("饰品 %s 缺 %s 词条" % (tid, name))
    print("饰品自检：表 %d 件，Java 注册 %d 件，Curios 标签 %d 件"
          % (len(table), len(java_ids), len(values)))
    return table


def switch_codes(java, method):
    """取某个方法里 switch 的 case 编码集合（支持 `case 5, 12 ->`）。"""
    body = java[java.index("private static String %s(" % method):]
    body = body[:body.index("\n    }")]
    codes = set()
    for group in re.findall(r'case ([0-9,\s]+) ->', body):
        codes |= {int(n) for n in re.findall(r"\d+", group)}
    return codes


def check_tooltips(table):
    """
    悬浮说明覆盖自检（第三十四轮补的两道防漏）：

    1) 手写饰品（`charm("...")` + 铜镜）必须在 `DynastyTrinketTips.LEGACY` 里有说明，
       否则玩家在背包里什么都看不到；
    2) 表里用到的属性 / 效果 / 条件编码，必须在 `DynastyTrinketTips` 的中文表里有对应文案
       （attrText / effectName / CONDITION_TEXT）—— 加编码忘了加文案，是这一轮差点踩的坑。

    Tooltip coverage: every hand-written accessory needs a LEGACY line, and every code used in
    the tables needs a Chinese label in DynastyTrinketTips.
    """
    tips = read(os.path.join(SRC, "DynastyTrinketTips.java"))
    registry = read(os.path.join(SRC, "DynastyTrinkets.java"))

    legacy_java = set(re.findall(r'charm\("([a-z_]+)"\)', registry)) | {"bronze_mirror"}
    legacy_tips = set(re.findall(r'Map\.entry\("([a-z_]+)"', tips))
    for tid in sorted(legacy_java - legacy_tips):
        problems.append("手写饰品 %s 没有悬浮说明（补 DynastyTrinketTips.LEGACY）" % tid)
    for tid in sorted(legacy_tips - legacy_java):
        problems.append("DynastyTrinketTips.LEGACY 里的 %s 不是已注册的手写饰品" % tid)

    attr_labels = switch_codes(tips, "attrText")
    effect_labels = switch_codes(tips, "effectName")
    block = tips[tips.index("private static final String[] CONDITION_TEXT"):]
    condition_labels = len(re.findall(r'"[^"]+"', block[:block.index("};")]))

    used_attrs, used_effects, used_conds = set(), set(), set()
    for values in table.values():
        spec = values[5]
        if len(spec) == 10:
            a1, _v1, a2, _v2, effect, _level, condition, a3, _v3, condition3 = spec
        else:
            a1, _v1, a2, _v2, effect, _level, condition = spec
            a3, condition3 = -1, 0
        used_attrs |= {a1, a2, a3}
        used_effects.add(effect)
        used_conds |= {condition, condition3}

    for code in sorted(used_attrs - {-1}):
        if code not in attr_labels:
            problems.append("属性编码 %d 用在饰品表里，但 DynastyTrinketTips.attrText 没有文案" % code)
    for code in sorted(used_effects - {0}):
        if code not in effect_labels:
            problems.append("效果编码 %d 用在饰品表里，但 DynastyTrinketTips.effectName 没有文案" % code)
    for code in sorted(used_conds):
        if code >= condition_labels:
            problems.append("条件编码 %d 用在饰品表里，但 CONDITION_TEXT 只有 %d 条"
                            % (code, condition_labels))

    # 命中触发（第 12~14 格）也要有中文文案：ON_HIT 里的编码必须能在 onHitName 里找到
    proc_labels = switch_codes(tips, "onHitName")
    on_hit = getattr(
        load("gen_trinkets5", os.path.join(ROOT, "tools/art/gen_trinkets5.py")), "ON_HIT", {})
    for tid, proc in on_hit.items():
        if proc[0] not in proc_labels:
            problems.append("饰品 %s 的命中触发编码 %d 没有文案（DynastyTrinketTips.onHitName）"
                            % (tid, proc[0]))
    print("悬浮说明自检：手写 %d 件 / 表驱动 %d 件；文案覆盖 属性 %d 种、效果 %d 种、条件 %d 种、命中触发 %d 种"
          % (len(legacy_java), len(table), len(attr_labels), len(effect_labels),
             condition_labels, len(proc_labels)))


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


def check_links():
    """
    连携表三方一致自检：生成器（LINK_GROUPS / LINKS）↔ Java（每行的第 15 格 / LINK_TABLE）。

    这两处只要有一处改漏，就会出现「戒指上写着连携组 3，但 Java 里那组没有加成」或者
    「加成档位和文档不一样」这种静默偏差 —— 所以像饰品主表一样逐行核对。

    Synergy cross-check between the generator and the Java table.
    """
    generator = load("gen_trinkets5", os.path.join(ROOT, "tools/art/gen_trinkets5.py"))
    java = read(os.path.join(SRC, "DynastyTrinkets.java"))
    # 只看 EXTRA_TABLE 这一段：文件里还有别的表（比如百宝妆匣的权重表）也是 {"id", 数字} 形状
    trinkets = java[java.index("EXTRA_TABLE = {"):]
    trinkets = trinkets[:trinkets.index("\n    };")]
    links = java[java.index("LINK_TABLE = {"):]
    links = links[:links.index("\n    };")]

    java_groups = {}
    for match in re.finditer(r'\{"([a-z_]+)",([^}]*)\},', trinkets):
        fields = [field.strip() for field in match.group(2).split(",")]
        if len(fields) != 14:               # 15 个值 - id = 14；老批次（8/11 格）跳过
            continue
        java_groups[match.group(1)] = int(fields[-1])
    for tid, group in generator.LINK_OF.items():
        if java_groups.get(tid) != group:
            problems.append("饰品 %s 的连携组不一致：生成器 %s / Java %s"
                            % (tid, group, java_groups.get(tid)))
    for tid, group in java_groups.items():
        if group != 0 and tid not in generator.LINK_OF:
            problems.append("Java 里 %s 写了连携组 %s，但生成器没把它编进任何组" % (tid, group))

    java_links = set()
    for match in re.finditer(r"\{(\d+), (\d+), (\d+), (\d+), ([\d.]+)D, (\d+)\},", links):
        java_links.add((int(match.group(1)), int(match.group(2)), int(match.group(3)),
                        int(match.group(4)), float(match.group(5)), int(match.group(6))))
    generator_links = {(g, need, kind, code, float(value), cond)
                       for g, need, kind, code, value, cond in generator.LINKS}
    for missing in sorted(generator_links - java_links):
        problems.append("连携加成没写进 Java LINK_TABLE：%s" % (missing,))
    for extra in sorted(java_links - generator_links):
        problems.append("Java LINK_TABLE 里有生成器没有的连携加成：%s" % (extra,))
    print("连携自检：%d 组 / %d 件入组 / %d 条加成，生成器与 Java 一致"
          % (len(generator.LINK_GROUPS), len(generator.LINK_OF), len(generator.LINKS)))


def main():
    from verify_curios import verify
    verify()
    table = check_trinkets()
    check_tooltips(table)
    check_links()
    check_armor()
    if problems:
        print("装备自检：发现问题 ❌")
        for problem in problems[:25]:
            print("   -", problem)
        sys.exit(1)
    print("装备自检：通过 ✅（护甲与饰品的表 / 贴图 / 模型 / 配方 / 词条 / Curios 标签 / 悬浮说明七处齐全）")


if __name__ == "__main__":
    main()
