#!/usr/bin/env python3
"""把**全部表驱动饰品**（gen_trinkets3/4/5，共 130 件）写进「王朝图鉴」。

为什么要有它：图鉴（Shift 悬停 + 图鉴页）原来只覆盖了部分装备，130 件表驱动饰品一件都没有 ——
玩家在背包里只能看到属性和命中说明，看不到「怎么来、配方是什么」。这里从生成器表里直接算：
中英物品名取 lang 文件，属性 / 效果 / 条件 / 命中触发 / 连携组全部翻成人话。

输出：src/main/java/com/dynasty/DynastyCodexAll.java（不要手改，改生成器）
运行：python3 tools/art/gen_codex_all.py
"""
import importlib.util
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
OUT = os.path.join(ROOT, "src/main/java/com/dynasty/DynastyCodexAll.java")

ATTR = {
    0: ("生命", "health", False), 1: ("护甲", "armour", False), 2: ("抗击退", "knockback resistance", False),
    3: ("移速", "movement speed", True), 4: ("攻击", "attack", True), 5: ("攻速", "attack speed", True),
    6: ("击退", "attack knockback", False), 7: ("攻击距离", "attack range", False),
    9: ("生命上限", "max health", True), 11: ("幸运", "luck", False),
}
EFFECT = {
    21: ("龙威", "Dragon Might"), 22: ("铁壁", "Iron Wall"), 23: ("疾风", "Swift Wind"),
    24: ("威慑", "Intimidation"), 25: ("天命", "Mandate of Heaven"), 26: ("忠诚", "Loyalty"),
    27: ("内伤", "Internal Injury"),
    1: ("夜视", "Night Vision"), 2: ("水下呼吸", "Water Breathing"), 3: ("抗火", "Fire Resistance"),
    4: ("抗性", "Resistance"), 5: ("再生", "Regeneration"), 8: ("缓降", "Slow Falling"),
    11: ("幸运", "Luck"), 12: ("生命恢复", "Regeneration"),
}
CONDITION = {0: ("常驻", "always"), 1: ("白天", "in daylight"), 2: ("夜晚", "at night"),
             3: ("水下", "underwater"), 4: ("残血", "at low health"), 5: ("骑乘", "while mounted"),
             6: ("满血", "at full health"), 7: ("雷雨", "in a thunderstorm")}
ON_HIT = {
    1: ("命中吸血 %s", "%s lifesteal on hit"), 2: ("命中斩杀 %s 血线以下的目标", "executes below %s health"),
    3: ("命中 %s 会心", "%s critical on hit"), 4: ("命中满血目标 %s", "%s against full-health targets"),
    5: ("连击每层 %s", "%s per combo stack"), 6: ("命中附加 %s 点雷罚", "%s extra thunder damage on hit"),
}
GROUP = {1: ("昼夜双生", "Day & Night"), 2: ("生死代价", "Life for Power"),
         3: ("天朝敕令", "Imperial Edict"), 4: ("幽冥献祭", "Underworld Sacrifice"),
         5: ("匠边塞", "Frontier Craft")}
GROUP[5] = ("巧匠边塞", "Frontier Craft")


def load(name):
    path = os.path.join(ROOT, "tools/art/%s.py" % name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pct(value):
    return "%g%%" % (value * 100)


def attr_line(code, value, zh):
    if code < 0:
        return None
    name = ATTR[code][0] if zh else ATTR[code][1]
    if ATTR[code][2]:
        return "%s %s" % (name, ("+" if value > 0 else "") + pct(value))
    return "%s %s%g" % (name, "+" if value > 0 else "", value)


def effect_line(code, level, zh):
    if not code:
        return None
    name = EFFECT[code][0] if zh else EFFECT[code][1]
    shown = level + 2 if code == 12 else level + 1
    return ("常驻%s %s" % (name, "I" * min(shown, 3))) if zh else \
        ("permanent %s %s" % (name, "I" * min(shown, 3)))


def on_hit_line(proc, zh):
    code, value, chance = proc
    if not code:
        return None
    text = ON_HIT[code][0] if zh else ON_HIT[code][1]
    amount = pct(value) if code in (1, 2, 3, 4, 5) else "%g" % value
    line = text % amount
    if chance < 100:
        line += "（%d%% 概率）" % chance if zh else " (%d%% chance)" % chance
    return line


def use_line(values, proc, group, zh):
    """把一行饰品翻成「妙用」：三格属性 + 效果 + 命中触发 + 连携。/ effect summary"""
    spec = values[5]
    if len(spec) == 10:
        a1, v1, a2, v2, effect, level, condition, a3, v3, condition3 = spec
    else:
        a1, v1, a2, v2, effect, level, condition = spec
        a3, v3, condition3 = -1, 0.0, 0
    parts = []
    first = [p for p in (attr_line(a1, v1, zh), attr_line(a2, v2, zh)) if p]
    if first:
        joined = ("、" if zh else ", ").join(first)
        if zh:
            parts.append(("%s：%s" % (CONDITION[condition][0], joined)) if condition else joined)
        else:
            parts.append(joined + ((" (%s)" % CONDITION[condition][1]) if condition else ""))
    third = attr_line(a3, v3, zh)
    if third:
        parts.append(("%s：%s" % (CONDITION[condition3][0], third)) if zh
                     else ("%s (%s)" % (third, CONDITION[condition3][1])))
    eff = effect_line(effect, level, zh)
    if eff:
        parts.append(eff)
    hit = on_hit_line(proc, zh)
    if hit:
        parts.append(hit)
    if group:
        parts.append(("连携·%s" % GROUP[group][0]) if zh else ("synergy: %s" % GROUP[group][1]))
    return parts


def main():
    zh_lang = json.load(open(os.path.join(ASSETS, "lang", "zh_cn.json"), encoding="utf-8"))
    en_lang = json.load(open(os.path.join(ASSETS, "lang", "en_us.json"), encoding="utf-8"))

    table, procs = {}, {}
    for generator in ("gen_trinkets3", "gen_trinkets4", "gen_trinkets5"):
        module = load(generator)
        table.update(module.TRINKETS)
        procs.update(getattr(module, "ON_HIT", {}))
    links = load("gen_trinkets5")
    link_of = links.LINK_OF

    lines = []
    for tid, values in sorted(table.items()):
        zh_name = zh_lang.get("item.dynasty." + tid, tid)
        en_name = en_lang.get("item.dynasty." + tid, tid)
        materials = values[4]
        mat_zh = " + ".join(zh_lang.get("item.dynasty." + m.split(":")[1], m) for m in materials)
        mat_en = " + ".join(en_lang.get("item.dynasty." + m.split(":")[1], m) for m in materials)
        zh_parts = use_line(values, procs.get(tid, (0, 0.0, 0)), link_of.get(tid, 0), True)
        en_parts = use_line(values, procs.get(tid, (0, 0.0, 0)), link_of.get(tid, 0), False)
        lines.append(
            '        entry(l, "%s",\n'
            '                "合成：%s",\n'
            '                "Craft: %s",\n'
            '                "%s：%s。",\n'
            '                "%s: %s.",\n'
            '                %s);'
            % (tid, mat_zh, mat_en, zh_name, "、".join(zh_parts), en_name, ", ".join(en_parts),
               ", ".join('"%s"' % m for m in materials)))

    source = '''package com.dynasty;

import java.util.List;

/**
 * 图鉴·全部表驱动饰品（gen_trinkets3/4/5 共 %d 件）。
 *
 * ⚠ 本文件由 tools/art/gen_codex_all.py 生成，不要手改 —— 改生成器（或饰品表）再重跑，
 *   这样「配方材料 / 属性 / 效果 / 命中触发 / 连携组」永远和表一致。
 *   与 DynastyCodexGear3 重复的 id 由 DynastyCodex.all() 去重（先登记的优先）。
 *
 * Generated codex entries for every table-driven accessory; edit the generator, not this file.
 */
final class DynastyCodexAll {

    private DynastyCodexAll() {
    }

    private static void entry(List<DynastyCodex.Entry> l, String id, String zhSource, String enSource,
                              String zhUse, String enUse, String... ingredients) {
        l.add(new DynastyCodex.Entry(id, zhSource, enSource, zhUse, enUse, ingredients));
    }

    static void add(List<DynastyCodex.Entry> l) {
%s
    }
}
''' % (len(table), "\n".join(lines))

    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(source)
    print("图鉴条目已生成：饰品 %d 件 → %s" % (len(table), os.path.basename(OUT)))


if __name__ == "__main__":
    main()
