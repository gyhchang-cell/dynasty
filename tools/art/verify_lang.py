"""词条覆盖自检：每个有模型的物品、每个模组效果都要有中文与英文词条。

踩过的坑（第三十四轮补）：
  * 只查 `item.dynasty.*` 会把方块判成「缺词条」—— 方块玩家看到的名字在 `block.dynasty.*`，
    反过来只查 block 也会漏物品；两边都要认，否则自检会天天误报。
  * 加了新效果（`EFFECTS.register("xxx")`）忘了写 `effect.dynasty.xxx` → 游戏里显示的是
    `effect.dynasty.xxx` 这种原始 id，玩家一脸问号。

运行：python3 tools/art/verify_lang.py
"""
import glob
import json
import os
import re
import sys

from verify_compass_localization import localization_errors

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
JAVA = os.path.join(ROOT, "src/main/java/com/dynasty")

problems = []

# Render-only overrides are not registered items. Keep this explicit (no broad suffix exemption).
RENDER_VARIANTS = {f"{bow}_pulling_{stage}": bow
                   for bow in ("houyi_bow", "zhuxing_bow", "shenbi_bow", "dragon_bow", "fengling_bow", "chang_gong") for stage in range(3)}
# PuzzleBlocks deliberately gives the BlockItem a distinct registry ID: star_dial already names a Curio.
# BlockItem.getDescriptionId uses its underlying block's ID, not its item registry ID.
BLOCK_ITEM_NAMES = {"puzzle_star_dial": "star_dial"}
# Shared display/texture parents, not inventory items. Require actual child references below.
MODEL_PARENTS = {"solid_handheld", "solid_bow"}


def read(path):
    return open(path, encoding="utf-8").read()


def check():
    models = {os.path.basename(f)[:-5]
              for f in glob.glob(os.path.join(ASSETS, "models/item/*.json"))}
    lang = {name: json.load(open(os.path.join(ASSETS, "lang", name + ".json"), encoding="utf-8"))
            for name in ("zh_cn", "en_us")}

    for item in sorted(models):
        if item in MODEL_PARENTS:
            path = os.path.join(ASSETS, "models/item", item + ".json")
            parent = json.load(open(path, encoding="utf-8"))
            children = [json.load(open(os.path.join(ASSETS, "models/item", name + ".json"), encoding="utf-8"))
                        for name in models - {item}]
            if not any(child.get("parent") == f"dynasty:item/{item}" for child in children):
                problems.append(f"共享模型 {item} 没有实际子模型")
            if "elements" in parent or "overrides" in parent:
                problems.append(f"共享模型 {item} 不应包含物品几何或覆盖项")
            continue
        if item in RENDER_VARIANTS:
            base = RENDER_VARIANTS[item]
            path = os.path.join(ASSETS, "models/item", base + ".json")
            parent = json.load(open(path, encoding="utf-8"))
            references = {entry.get("model") for entry in parent.get("overrides", [])}
            if f"dynasty:item/{item}" not in references:
                problems.append(f"渲染变体 {item} 未被 {base} 的 overrides 引用")
            # The base weapon remains subject to the full bilingual item-name check below.
            continue
        for name, data in lang.items():
            block_id = BLOCK_ITEM_NAMES.get(item, item)
            if ("item.dynasty." + item) not in data and ("block.dynasty." + block_id) not in data:
                problems.append("%s 缺 %s 词条（item. 或 block. 前缀都认）" % (item, name))

    puzzle_source = read(os.path.join(JAVA, "puzzle/PuzzleBlocks.java"))
    for item, block in BLOCK_ITEM_NAMES.items():
        if not re.search(r'itemBlock\("' + item + r'",\s*BLOCKS\.register\("' + block + r'"', puzzle_source):
            problems.append(f"方块物品语言映射 {item} → {block} 与真实注册不符")

    effects = set(re.findall(r'EFFECTS\.register\("([a-z0-9_]+)"',
                             read(os.path.join(JAVA, "DynastyEffects.java"))))
    for effect in sorted(effects):
        for name, data in lang.items():
            if ("effect.dynasty." + effect) not in data:
                problems.append("效果 %s 缺 %s 词条（effect.dynasty.%s）" % (effect, name, effect))

    problems.extend(localization_errors(lang))

    print("词条自检：物品模型 %d 个、模组效果 %d 个" % (len(models), len(effects)))
    if problems:
        print("词条自检：发现问题 ❌")
        for problem in problems[:25]:
            print("   -", problem)
        sys.exit(1)
    print("词条自检：通过 ✅（物品、效果及罗盘所用结构/群系/维度都有中英词条）")


if __name__ == "__main__":
    check()
