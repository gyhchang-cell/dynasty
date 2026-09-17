#!/usr/bin/env python3
"""1.4.0 第三十二轮：再扩 30 件饰品（89 → 119 件），分六类各 5 件。

流程与 `gen_trinkets3.py` 完全一致（可重复运行、不覆盖已有文件）：

* 贴图：从最接近的旧饰品**复制 + 染色**，每件都不一样；
* 模型 / 配方 / 中英词条一次生成；Curios 标签一起写（否则物品戴不上）；
* Java 侧只需在 `DynastyTrinkets.EXTRA_TABLE` 追加同 id 的行：
  注册、属性与效果的结算都是表驱动的（`tools/art/verify_gear.py` 会核对三处一致）。

属性编码（与 Java 表一致）：
  0 生命 1 护甲 2 抗击退 3 移速% 4 攻击% 5 攻速% 6 击退 7 距离 11 幸运
效果编码：1 夜视 2 水下呼吸 3 抗火 4 抗性 5 再生 8 缓降 11 幸运 12 生命恢复
条件编码：0 常驻 1 白天 2 夜晚 3 水下 4 残血 5 骑乘

运行：python3 tools/art/gen_trinkets4.py
"""
import json
import os

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
CURIOS = os.path.join(ROOT, "src/main/resources/data/curios/tags/items/dynasty_trinket.json")

# id: (中文名, 英文名, 贴图来源, 染色, [材料…], (属性1, 值1, 属性2, 值2, 效果, 等级, 条件))
TRINKETS = {
    # ---- 一、宫廷（5）----
    "phoenix_hairpin": ("凤钗", "Phoenix Hairpin", "jade_crown", (0xF0, 0xC0, 0xC8),
                        ["dynasty:phoenix_feather", "dynasty:gold_coin", "dynasty:silk"],
                        (0, 240.0, 11, 1.0, 0, 0, 0)),
    "dragon_robe_sash": ("龙袍玉带", "Dragon Robe Sash", "cloud_brocade", (0xC8, 0xD8, 0xF0),
                         ["dynasty:dragon_scale", "dynasty:jade", "dynasty:silk"],
                         (1, 14.0, 0, 200.0, 0, 0, 0)),
    "mandarin_rank_badge": ("补子官徽", "Rank Badge", "merit_badge", (0xD8, 0xC0, 0x90),
                            ["dynasty:silk", "dynasty:gold_coin", "dynasty:cinnabar"],
                            (11, 2.0, 0, 180.0, 0, 0, 0)),
    "imperial_pearl_earring": ("东珠耳坠", "Imperial Pearl Earring", "dragon_pearl", (0xF0, 0xE8, 0xD0),
                               ["dynasty:sea_pearl", "dynasty:gold_coin", "dynasty:silk"],
                               (0, 200.0, 11, 1.0, 0, 0, 0)),
    "gilded_lotus_crown": ("金莲冠", "Gilded Lotus Crown", "jade_crown", (0xF0, 0xD8, 0x80),
                           ["dynasty:gold_coin", "dynasty:gold_coin", "dynasty:jade"],
                           (4, 0.10, 3, 0.05, 0, 0, 0)),
    # ---- 二、战阵（5）----
    "war_banner_charm": ("战旗坠", "War Banner Charm", "war_drum_charm", (0xC0, 0x80, 0x70),
                         ["dynasty:silk", "dynasty:bamboo_slip", "dynasty:refined_steel"],
                         (4, 0.12, 5, 0.06, 0, 0, 0)),
    "iron_helmet_plume": ("盔缨", "Helmet Plume", "sky_feather", (0xD0, 0x50, 0x50),
                          ["dynasty:phoenix_feather", "dynasty:refined_steel", "dynasty:silk"],
                          (1, 12.0, 3, 0.06, 0, 0, 0)),
    "pike_tassel": ("枪缨", "Pike Tassel", "saber_tassel", (0xC8, 0x50, 0x50),
                    ["dynasty:silk", "dynasty:refined_steel"],
                    (4, 0.10, 7, 1.0, 0, 0, 0)),
    "drum_beater": ("鼓槌", "Drum Beater", "war_drum_charm", (0xA0, 0x70, 0x50),
                    ["dynasty:bamboo_slip", "dynasty:silk"],
                    (5, 0.15, 4, 0.05, 0, 0, 0)),
    "armor_piercer_token": ("破甲符牌", "Armour-Piercer Token", "tiger_token", (0xB0, 0xB8, 0xC8),
                            ["dynasty:refined_steel", "dynasty:dragon_crystal", "dynasty:cinnabar"],
                            (4, 0.16, 6, 0.35, 0, 0, 0)),
    # ---- 三、灵兽（5）----
    "phoenix_wing_charm": ("凤翼坠", "Phoenix Wing Charm", "phoenix_feather_charm", (0xF0, 0x90, 0x60),
                           ["dynasty:phoenix_feather", "dynasty:phoenix_feather", "dynasty:gold_coin"],
                           (3, 0.10, -1, 0.0, 8, 0, 0)),
    "qilin_hoof_charm": ("麒麟蹄", "Qilin Hoof Charm", "qilin_horn_charm", (0xC8, 0xE0, 0x90),
                         ["dynasty:qilin_horn", "dynasty:silk"],
                         (0, 260.0, 5, 0.08, 0, 0, 0)),
    "turtle_blood_charm": ("龟血符", "Turtle Blood Charm", "jade_tortoise", (0x80, 0xA8, 0x88),
                           ["dynasty:dragon_scale", "dynasty:cinnabar", "dynasty:silk"],
                           (0, 300.0, 1, 16.0, 4, 0, 4)),
    "fox_spirit_pendant": ("狐灵佩", "Fox Spirit Pendant", "fox_tail_charm", (0xE0, 0xA8, 0xC8),
                           ["dynasty:fox_tail", "dynasty:jade", "dynasty:silk"],
                           (3, 0.12, 11, 2.0, 0, 0, 0)),
    "dragon_blood_pearl": ("龙血珠", "Dragon Blood Pearl", "dragon_pearl", (0xE0, 0x70, 0x70),
                           ["dynasty:dragon_crystal", "dynasty:cinnabar", "dynasty:gold_coin"],
                           (0, 360.0, 4, 0.14, 0, 0, 0)),
    # ---- 四、文房（5）----
    "jade_brush_holder": ("玉笔筒", "Jade Brush Holder", "brush_rack", (0xA8, 0xD8, 0xB8),
                          ["dynasty:jade", "dynasty:bamboo_slip"],
                          (5, 0.12, 4, 0.06, 0, 0, 0)),
    "ink_slab_charm": ("砚台坠", "Ink Slab Charm", "inkstone", (0x70, 0x70, 0x80),
                       ["dynasty:jade", "dynasty:ink_stick", "dynasty:silk"],
                       (11, 2.0, 0, 160.0, 0, 0, 0)),
    "scroll_case_charm": ("书箱坠", "Scroll Case Charm", "poem_scroll", (0xE0, 0xD0, 0xA8),
                          ["dynasty:bamboo_slip", "dynasty:ink_stick", "dynasty:silk"],
                          (5, 0.10, 11, 1.0, 0, 0, 0)),
    "guqin_tassel": ("琴穗", "Guqin Tassel", "guqin_string", (0xC8, 0xA8, 0x88),
                     ["dynasty:silk", "dynasty:bamboo_flute"],
                     (5, 0.08, 0, 120.0, 0, 0, 0)),
    "scholar_ink_badge": ("墨玉印坠", "Scholar Ink Badge", "imperial_seal_charm", (0x88, 0x98, 0xB0),
                          ["dynasty:jade", "dynasty:cinnabar", "dynasty:gold_coin"],
                          (0, 180.0, 11, 1.0, 0, 0, 0)),
    # ---- 五、道法（5）----
    "thunder_seal_charm": ("雷印符", "Thunder Seal Charm", "storm_charm", (0xC0, 0xB0, 0xF0),
                           ["dynasty:talisman_paper", "dynasty:thunder_token", "dynasty:cinnabar"],
                           (4, 0.14, 5, 0.10, 0, 0, 0)),
    "immortal_crane_feather": ("仙鹤羽", "Immortal Crane Feather", "crane_feather", (0xF0, 0xF0, 0xE0),
                               ["dynasty:phoenix_feather", "dynasty:jade", "dynasty:silk"],
                               (3, 0.12, -1, 0.0, 8, 0, 0)),
    "star_diagram_charm": ("星图佩", "Star Chart Charm", "star_compass", (0xB0, 0xC0, 0xF0),
                           ["dynasty:dragon_crystal", "dynasty:jade", "dynasty:cinnabar"],
                           (11, 3.0, 0, 140.0, 0, 0, 0)),
    "zen_bead_string": ("禅珠串", "Zen Bead String", "auspicious_bell", (0xD8, 0xC0, 0x90),
                        ["dynasty:jade", "dynasty:silk", "dynasty:gold_coin"],
                        (0, 220.0, -1, 0.0, 12, 0, 4)),
    "alchemy_furnace_charm": ("丹炉坠", "Alchemy Furnace Charm", "cinnabar_pouch", (0xE0, 0x90, 0x80),
                              ["dynasty:cinnabar", "dynasty:talisman_paper", "dynasty:gold_coin"],
                              (0, 260.0, -1, 0.0, 5, 0, 0)),
    # ---- 六、海事（5）----
    "conch_horn": ("海螺号", "Conch Horn", "sea_conch", (0xE8, 0xD8, 0xC0),
                   ["dynasty:sea_conch", "dynasty:silk"],
                   (0, 240.0, 3, 0.08, 0, 0, 0)),
    "dragon_scale_sash": ("龙鳞带", "Dragon Scale Sash", "dragon_scale_charm", (0x70, 0xB0, 0xC0),
                          ["dynasty:dragon_scale", "dynasty:refined_steel", "dynasty:silk"],
                          (1, 16.0, 2, 0.45, 0, 0, 0)),
    "pearl_net_charm": ("珠网坠", "Pearl Net Charm", "sea_pearl", (0xE0, 0xE8, 0xF0),
                        ["dynasty:sea_pearl", "dynasty:gold_coin", "dynasty:silk"],
                        (0, 200.0, 11, 2.0, 0, 0, 0)),
    "tide_compass_charm": ("潮信坠", "Tide Compass Charm", "south_pointing_compass", (0x90, 0xC8, 0xD8),
                           ["dynasty:bronze_mirror", "dynasty:dragon_crystal", "dynasty:silk"],
                           (7, 2.0, 3, 0.06, 0, 0, 0)),
    "storm_anchor_charm": ("镇海锚坠", "Storm Anchor Charm", "moon_pendant", (0x88, 0xA8, 0xD0),
                           ["dynasty:refined_steel", "dynasty:dragon_crystal", "dynasty:sea_pearl"],
                           (1, 20.0, 6, 0.5, 0, 0, 0)),
}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def tint(src, dst, color):
    """把来源贴图按颜色染色（保留像素透明度）/ tint a copy of the source texture."""
    if not os.path.exists(src):
        print("!! 缺少源贴图", src)
        return False
    image = Image.open(src).convert("RGBA")
    r, g, b = color
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            pr, pg, pb, pa = pixels[x, y]
            if pa == 0:
                continue
            pixels[x, y] = (min(255, (pr * r) // 255), min(255, (pg * g) // 255),
                            min(255, (pb * b) // 255), pa)
    image.save(dst)
    return True


def num(value):
    return "%g" % value


def main():
    items = {os.path.basename(f)[:-5] for f in os.listdir(os.path.join(ASSETS, "models/item"))}
    problems = []
    for tid, (zh, en, source, color, materials, spec) in TRINKETS.items():
        dst = os.path.join(ASSETS, "textures/item/%s.png" % tid)
        src = os.path.join(ASSETS, "textures/item/%s.png" % source)
        if not os.path.exists(dst):
            tint(src, dst, color)
        write(os.path.join(ASSETS, "models/item/%s.json" % tid),
              {"parent": "minecraft:item/generated",
               "textures": {"layer0": "dynasty:item/%s" % tid}})
        for material in materials:
            namespace, path = material.split(":")
            if namespace == "dynasty" and path not in items:
                problems.append("%s 的配方材料不存在：%s" % (tid, material))
        write(os.path.join(DATA, "recipes/%s.json" % tid),
              {"type": "minecraft:crafting_shapeless",
               "ingredients": [{"item": item} for item in materials],
               "result": {"item": "dynasty:%s" % tid}})
    print("饰品扩充：%d 件（贴图 / 模型 / 配方）" % len(TRINKETS))

    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = json.load(open(path, encoding="utf-8"))
        for tid, values in TRINKETS.items():
            data["item.dynasty.%s" % tid] = values[0] if index == 0 else values[1]
        write(path, data)

    tag = json.load(open(CURIOS, encoding="utf-8"))
    values = tag.get("values", [])
    added = 0
    for tid in TRINKETS:
        entry = "dynasty:%s" % tid
        if entry not in values:
            values.append(entry)
            added += 1
    tag["values"] = values
    write(CURIOS, tag)
    print("Curios 标签新增 %d 条（合计 %d 件饰品）" % (added, len(values)))

    print("\n--- EXTRA_TABLE 追加行（Java，可直接粘贴）---")
    for tid, values in TRINKETS.items():
        a1, v1, a2, v2, effect, level, condition = values[5]
        print('            {"%s", %d, %sD, %d, %sD, %d, %d, %d},'
              % (tid, a1, num(v1), a2, num(v2), effect, level, condition))

    if problems:
        print("\n问题 ❌")
        for problem in problems:
            print("   -", problem)
        raise SystemExit(1)
    print("\n饰品扩充完成 ✅")


if __name__ == "__main__":
    main()
