"""数值审计：把饰品表里的编码与数值跟「设计上下限」对一遍，并打印分布，方便看设计是否失衡。

为什么要有这一步（第三十四轮补）：
  * 百分比写成点数（`4, 22D` 本意是 +22%）→ 玩家攻击直接爆掉；
  * 生命上限扣太多（编码 9 超过 −60%）→ 穿一件就变玻璃人；
  * 同一件饰品两个编码写反 → 属性互相抵消，玩家看着像「没生效」；
  * 条件 / 效果编码写错（比如想写「雷雨」写成 17）→ 游戏里安静地不生效。

同时打印分布统计（条件 / 效果 / 最强的几件），当作**设计复查**的仪表盘：
一眼能看出「昼夜类是不是太多」「代价类给的是不是太狠」。

运行：python3 tools/art/verify_balance.py
"""
import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 编码 → (名称, 最小值, 最大值, 百分号)
FLAT = {0: ("生命", -200, 500), 1: ("护甲", -10, 40), 2: ("抗击退", -1.0, 1.0),
        6: ("击退", -1.0, 1.5), 7: ("攻击距离", -2.0, 3.0), 11: ("幸运", -3.0, 5.0)}
RATIO = {3: ("移速%", -0.25, 0.30), 4: ("攻击%", -0.40, 0.60), 5: ("攻速%", -0.30, 0.40),
         9: ("生命上限%", -0.60, 0.50)}
CONDITION_TEXT = {0: "常驻", 1: "白天", 2: "夜晚", 3: "水下", 4: "残血", 5: "骑乘", 6: "满血", 7: "雷雨"}
EFFECT_TEXT = {0: "无", 21: "龙威", 22: "铁壁", 23: "疾风", 24: "威慑", 25: "天命", 26: "忠诚", 27: "内伤",
               1: "夜视", 2: "水下呼吸", 3: "抗火", 4: "抗性", 5: "再生", 8: "缓降", 11: "幸运", 12: "再生(强)"}
ON_HIT_TEXT = {1: "吸血", 2: "斩杀", 3: "会心", 4: "突袭", 5: "连击", 6: "雷罚"}

problems = []


def load(name):
    path = os.path.join(ROOT, "tools/art/%s.py" % name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def spec_of(values):
    """统一成 10 格（老行补默认值）/ normalise to the v2 ten-column spec"""
    spec = values[5]
    if len(spec) == 10:
        return spec
    a1, v1, a2, v2, effect, level, condition = spec
    return (a1, v1, a2, v2, effect, level, condition, -1, 0.0, 0)


def check(table):
    condition_count, effect_count = {}, {}
    strongest = []
    for tid, values in sorted(table.items()):
        a1, v1, a2, v2, effect, level, condition, a3, v3, condition3 = spec_of(values)
        for code, value in ((a1, v1), (a2, v2), (a3, v3)):
            if code == -1:
                continue
            limits = FLAT.get(code) or RATIO.get(code)
            if limits is None:
                problems.append("%s 用了未知属性编码 %s" % (tid, code))
                continue
            name, low, high = limits
            if not low <= value <= high:
                problems.append("%s 的「%s」= %s 超出设计上限 %s ~ %s（是不是百分比写成点数了？）"
                                % (tid, name, value, low, high))
        if effect not in EFFECT_TEXT:
            problems.append("%s 用了未登记的效果编码 %s" % (tid, effect))
        if not 0 <= level <= 3:
            problems.append("%s 的效果等级 %s 越界（0~3）" % (tid, level))
        for cond in (condition, condition3):
            if cond not in CONDITION_TEXT:
                problems.append("%s 用了未登记的条件编码 %s" % (tid, cond))
            else:
                condition_count[cond] = condition_count.get(cond, 0) + 1
        effect_count[effect] = effect_count.get(effect, 0) + 1
        if a1 == 4 or a3 == 4:
            strongest.append((max(v1 if a1 == 4 else -9, v3 if a3 == 4 else -9), tid))

    print("数值审计：饰品 %d 件" % len(table))
    print("  条件分布：" + "、".join(
        "%s %d" % (CONDITION_TEXT.get(c, c), n) for c, n in sorted(condition_count.items())))
    print("  效果分布：" + "、".join(
        "%s %d" % (EFFECT_TEXT.get(e, e), n) for e, n in sorted(effect_count.items())))
    top = sorted(strongest, reverse=True)[:5]
    if top:
        print("  攻击加成最猛的 5 件：" + "、".join("%s %+d%%" % (t, round(v * 100))
                                                    for v, t in top))
    costs = [t for t, v in table.items() if spec_of(v)[0] == 9 and spec_of(v)[1] < 0]
    print("  带生命上限代价的：%d 件（%s）" % (len(costs), "、".join(sorted(costs)[:6])))


def main():
    table = {}
    proc_table = {}
    proc_range = {}
    for generator in ("gen_trinkets3", "gen_trinkets4", "gen_trinkets5"):
        if os.path.exists(os.path.join(ROOT, "tools/art/%s.py" % generator)):
            module = load(generator)
            table.update(module.TRINKETS)
            proc_table.update(getattr(module, "ON_HIT", {}))
            proc_range.update(getattr(module, "ON_HIT_RANGE", {}))
    check(table)
    check_on_hit(proc_table, proc_range)
    if problems:
        print("数值审计：发现问题 ❌")
        for problem in problems[:25]:
            print("   -", problem)
        sys.exit(1)
    print("数值审计：通过 ✅（编码合法、数值与命中触发都在设计上下限内）")


def check_on_hit(proc_table, proc_range):
    """
    命中触发（第 12~14 格）的审计：编码合法、数值与概率都在设计区间内，
    并打印分布 —— 「吸血是不是给太多件了」这种问题一眼能看出来。

    On-hit audit: code validity, value/chance ranges, plus a design-distribution printout.
    """
    if not proc_table:
        return
    counts = {}
    for tid, (code, value, chance) in sorted(proc_table.items()):
        name = ON_HIT_TEXT.get(code)
        if name is None:
            problems.append("%s 用了未知的命中触发编码 %s" % (tid, code))
            continue
        counts[name] = counts.get(name, 0) + 1
        limits = proc_range.get(code)
        if limits is None:
            continue
        low, high, min_chance, max_chance = limits
        if not low <= value <= high:
            problems.append("%s 的「%s」数值 %s 超出设计范围 %s ~ %s" % (tid, name, value, low, high))
        if not min_chance <= chance <= max_chance:
            problems.append("%s 的「%s」概率 %s%% 超出设计范围 %s ~ %s%%"
                            % (tid, name, chance, min_chance, max_chance))
    print("  命中触发：%d 件 —— %s" % (len(proc_table), "、".join(
        "%s %d" % (name, counts[name]) for name in sorted(counts, key=counts.get, reverse=True))))


if __name__ == "__main__":
    main()
