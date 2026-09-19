"""战利品表自检：结构引用的箱子表必须存在，表里的物品必须真实存在，权重与数量范围合法。

为什么要有它：结构箱子写的是 `new ResourceLocation("dynasty", "chests/xxx")`，
表名打错一个字母，游戏里箱子就是空的（不报错、不崩，最难查）；表里物品名打错同理。
运行：python3 tools/art/verify_loot.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RES = os.path.join(ROOT, "src/main/resources")
JAVA = os.path.join(ROOT, "src/main/java/com/dynasty")
ASSETS = os.path.join(RES, "assets/dynasty")
TABLES = os.path.join(RES, "data/dynasty/loot_tables/chests")

problems = []


def verify():
    items = {os.path.basename(f)[:-5]
             for f in glob.glob(os.path.join(ASSETS, "models/item/*.json"))}

    # 1) 每个结构引用的表都要存在
    used = set()
    for piece in glob.glob(os.path.join(JAVA, "structure/*.java")):
        text = open(piece, encoding="utf-8").read()
        for match in re.finditer(r'new ResourceLocation\("dynasty", "(chests/[a-z_]+)"\)', text):
            used.add(match.group(1))
            path = os.path.join(RES, "data/dynasty/loot_tables/%s.json" % match.group(1))
            if not os.path.exists(path):
                problems.append("%s 引用的战利品表不存在：%s（箱子会是空的）"
                                % (os.path.basename(piece), match.group(1)))

    # 2) 表内容：物品存在 / 权重为正 / 数量范围合理
    for path in sorted(glob.glob(os.path.join(TABLES, "*.json"))):
        data = json.load(open(path, encoding="utf-8"))
        name = os.path.basename(path)
        for pool in data.get("pools", []):
            if pool.get("rolls", 0) <= 0:
                problems.append("%s 有空池（rolls <= 0）" % name)
            for entry in pool.get("entries", []):
                item = entry.get("name", "")
                if item.startswith("dynasty:") and item.split(":")[1] not in items:
                    problems.append("%s 里的 %s 不存在" % (name, item))
                if entry.get("weight", 1) <= 0:
                    problems.append("%s 里的 %s 权重非法（<= 0）" % (name, item))
                for function in entry.get("functions", []):
                    span = function.get("count", {})
                    if "min" in span and "max" in span and span["min"] > span["max"]:
                        problems.append("%s 里的 %s 数量范围反了（%s > %s）"
                                        % (name, item, span["min"], span["max"]))

    print("战利品表自检：结构引用 %d 张表 / 实际存在 %d 张"
          % (len(used), len(glob.glob(os.path.join(TABLES, "*.json")))))
    unused = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(TABLES, "*.json")))
    unused = [u for u in unused if ("chests/" + u) not in used]
    if unused:
        print("   （没被结构引用的表：%s）" % "、".join(unused))
    if problems:
        print("战利品表自检：发现问题 ❌")
        for problem in problems[:25]:
            print("   -", problem)
        sys.exit(1)
    print("战利品表自检：通过 ✅（引用的表都在、物品都存在、权重与数量范围合法）")


if __name__ == "__main__":
    verify()
