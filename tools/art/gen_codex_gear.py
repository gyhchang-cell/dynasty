#!/usr/bin/env python3
"""把第三十一轮新增的 10 套甲（40 件）与 50 件饰品写进「王朝图鉴」（图鉴页 + Shift 提示）。

图鉴条目 `DynastyCodex.Entry(id, zhSource, enSource, zhUse, enUse, ingredients…)`
里最容易写错的就是「材料」和「数值」，所以这里**从生成器表里直接算**，
中英物品名从 lang 文件里取 —— 手写 90 条不现实，交给脚本最稳。

输出：src/main/java/com/dynasty/DynastyCodexGear3.java（不要手改，改生成器）
运行：python3 tools/art/gen_codex_gear.py
"""
import importlib.util
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
OUT = os.path.join(ROOT, "src/main/java/com/dynasty/DynastyCodexGear3.java")
PIECES = ("helmet", "chestplate", "leggings", "boots")

# 每套甲的「每件减伤 / 每件生命 / 定位」（与 DynastyBalance.SET_BONUS 一致）
ARMOR_STATS = {
    "xuanwu": ("33%", 1100, "极致防御，抗击退 +0.5", "pure defence, +0.5 knockback resistance"),
    "zhuque": ("30%", 1000, "抗火轻甲，火里来火里去", "fire-resistant light armour"),
    "qinglong": ("34%", 1200, "攻守兼备，攻击 +10%", "balanced, +10% attack"),
    "baihu": ("35%", 1300, "攻杀流，攻击 +15%、击退 +0.3", "+15% attack, +0.3 attack knockback"),
    "beidou": ("36%", 1500, "星石铸甲，移速 +8%", "star-forged, +8% movement speed"),
    "tiangang": ("37%", 1700, "天罡星力，攻击 +18%", "+18% attack"),
    "disha": ("38%", 1900, "地煞重甲，护甲 +40、抗击退 +0.6", "+40 armour, +0.6 knockback resistance"),
    "taiyi": ("39%", 2200, "全属性小幅提升", "small boost to every stat"),
    "ziwei": ("40%", 2600, "帝星紫微，幸运 +3", "+3 luck"),
    "hunyuan": ("42%", 3200, "毕业套（四件封顶 92%）", "the graduation set (capped at 92%)"),
    "hongmeng": ("45%", 3600, "毕业甲：甲胄谱两条流派线的终点合体（四件封顶 92%）",
                 "the graduation set — both armour ladders merged (capped at 92%)"),
}
ATTR_ZH = {0: "生命", 1: "护甲", 2: "抗击退", 3: "移速", 4: "攻击", 5: "攻速",
           6: "击退", 7: "攻击距离", 11: "幸运"}
ATTR_EN = {0: "health", 1: "armour", 2: "knockback resistance", 3: "movement speed",
           4: "attack", 5: "attack speed", 6: "attack knockback", 7: "attack range", 11: "luck"}
PERCENT = {3, 4, 5}
EFF_ZH = {1: "夜视", 2: "水下呼吸", 3: "抗火", 4: "抗性", 5: "再生", 8: "缓降",
          11: "幸运", 12: "生命恢复"}
EFF_EN = {1: "Night Vision", 2: "Water Breathing", 3: "Fire Resistance", 4: "Resistance",
          5: "Regeneration", 8: "Slow Falling", 11: "Luck", 12: "Regeneration"}
COND_ZH = {1: "白天", 2: "夜晚", 3: "水下", 4: "残血", 5: "骑乘"}
COND_EN = {1: "day", 2: "night", 3: "underwater", 4: "low health", 5: "mounted"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def attr_text(code, value, zh_side):
    """属性编码 → 一行可读文字 / attribute code to a readable line"""
    if code is None or code < 0:
        return None
    names = ATTR_ZH if zh_side else ATTR_EN
    amount = "%d%%" % round(value * 100) if code in PERCENT else "%g" % value
    return "%s +%s" % (names[code], amount)


def main():
    armor3 = load("gen_armor3", os.path.join(ROOT, "tools/art/gen_armor3.py"))
    armor = armor3.SETS
    extra_prev = armor3.EXTRA_PREV
    trinkets = load("gen_trinkets3", os.path.join(ROOT, "tools/art/gen_trinkets3.py")).TRINKETS
    zh = json.load(open(os.path.join(ASSETS, "lang/zh_cn.json"), encoding="utf-8"))
    en = json.load(open(os.path.join(ASSETS, "lang/en_us.json"), encoding="utf-8"))

    def name_of(item, table):
        key = item.split(":")[-1]
        return table.get("item.dynasty." + key, key)

    lines = []
    for set_id, (zh_name, en_name, _src, prev, _color, materials) in armor.items():
        cut, health, note, en_note = ARMOR_STATS[set_id]
        mat_zh = " + ".join(name_of(m, zh) for m in materials)
        mat_en = " + ".join(name_of(m, en) for m in materials)
        extra = extra_prev.get(set_id)
        for piece in PIECES:
            prev_piece = "dynasty:%s_%s" % (prev, piece)
            if extra:
                # 合体套：两件上阶同部位 + 材料（甲胄谱两条线的终点）
                src_zh = "合成：%s + %s + %s" % (name_of(prev_piece, zh),
                                              name_of("dynasty:%s_%s" % (extra, piece), zh), mat_zh)
                src_en = "Craft: %s + %s + %s" % (name_of(prev_piece, en),
                                                 name_of("dynasty:%s_%s" % (extra, piece), en), mat_en)
                ingredients = [prev_piece, "dynasty:%s_%s" % (extra, piece)] + list(materials)
            else:
                src_zh = "合成：上阶同部位 + %s" % mat_zh
                src_en = "Craft: previous piece + %s" % mat_en
                ingredients = [prev_piece] + list(materials)
            lines.append(
                '        entry(l, "%s_%s",\n'
                '                "%s",\n'
                '                "%s",\n'
                '                "%s：每件减伤 %s、生命 +%d（%s）。",\n'
                '                "%s: %s reduction and +%d health per piece (%s).",\n'
                '                %s);'
                % (set_id, piece, src_zh, src_en, zh_name, cut, health, note,
                   en_name, cut, health, en_note,
                   ", ".join('"%s"' % m for m in ingredients)))

    for tid, values in trinkets.items():
        zh_name, en_name, _src, _color, materials, spec = values
        a1, v1, a2, v2, eff, amp, cond = spec
        parts_zh = [p for p in (attr_text(a1, v1, True), attr_text(a2, v2, True)) if p]
        parts_en = [p for p in (attr_text(a1, v1, False), attr_text(a2, v2, False)) if p]
        if eff:
            level = " II" if amp == 1 else (" III" if amp >= 2 else "")
            parts_zh.append("常驻%s%s" % (EFF_ZH[eff], level.strip()))
            parts_en.append("permanent %s%s" % (EFF_EN[eff], level))
        if cond:
            parts_zh.append("条件：" + COND_ZH[cond])
            parts_en.append("only while " + COND_EN[cond])
        mat_zh = " + ".join(name_of(m, zh) for m in materials)
        mat_en = " + ".join(name_of(m, en) for m in materials)
        lines.append(
            '        entry(l, "%s",\n'
            '                "合成：%s",\n'
            '                "Craft: %s",\n'
            '                "%s：%s。",\n'
            '                "%s: %s.",\n'
            '                %s);'
            % (tid, mat_zh, mat_en, zh_name, "、".join(parts_zh), en_name, ", ".join(parts_en),
               ", ".join('"%s"' % m for m in materials)))

    source = '''package com.dynasty;

import java.util.List;

/**
 * 图鉴·第三十一轮新增装备（10 套甲 / 50 件饰品）。
 *
 * ⚠ 本文件由 tools/art/gen_codex_gear.py 生成，不要手改 —— 改生成器再重跑，
 *   这样「配方材料 / 数值」永远和 gen_armor3.py / gen_trinkets3.py 一致。
 *
 * Generated codex entries for the gear added in round 31; edit the generator, not this file.
 */
final class DynastyCodexGear3 {

    private DynastyCodexGear3() {
    }

    private static void entry(List<DynastyCodex.Entry> l, String id, String zhSource, String enSource,
                              String zhUse, String enUse, String... ingredients) {
        l.add(new DynastyCodex.Entry(id, zhSource, enSource, zhUse, enUse, ingredients));
    }

    static void add(List<DynastyCodex.Entry> l) {
%s
    }
}
''' % "\n".join(lines)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(source)
    print("图鉴条目已生成：护甲 %d 件 + 饰品 %d 件 → %s"
          % (len(armor) * 4, len(trinkets), os.path.basename(OUT)))


if __name__ == "__main__":
    main()
