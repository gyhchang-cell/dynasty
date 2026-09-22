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


def read(path):
    return open(path, encoding="utf-8").read()


def check():
    models = {os.path.basename(f)[:-5]
              for f in glob.glob(os.path.join(ASSETS, "models/item/*.json"))}
    lang = {name: json.load(open(os.path.join(ASSETS, "lang", name + ".json"), encoding="utf-8"))
            for name in ("zh_cn", "en_us")}

    for item in sorted(models):
        for name, data in lang.items():
            if ("item.dynasty." + item) not in data and ("block.dynasty." + item) not in data:
                problems.append("%s 缺 %s 词条（item. 或 block. 前缀都认）" % (item, name))

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
