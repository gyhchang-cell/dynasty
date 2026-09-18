#!/usr/bin/env python3
"""1.4.0 第三十一轮：再扩 50 件饰品（39 → 89 件），分五类各 10 件。

* 贴图：从最接近的旧饰品复制一份再**染色**，每件都不一样；
* 模型 / 配方 / 中英名字一次生成；Curios 标签由 gen_trinkets3 一起写；
* Java 侧（注册 + 数值表）在 DynastyTrinkets.EXTRA_TABLE 里按同一张表对应，
  两边的 id / 属性编码必须一致（tools/art/verify_trinkets.py 会核对）。

属性编码（与 Java 表一致）：
  0 生命 1 护甲 2 抗击退 3 移速% 4 攻击% 5 攻速% 6 击退 7 距离 11 幸运
效果编码：1 夜视 2 水下呼吸 3 抗火 4 抗性 5 再生 8 缓降 11 幸运 12 生命恢复
条件编码：0 常驻 1 白天 2 夜晚 3 水下 4 残血 5 骑乘

运行：python3 tools/art/gen_trinkets3.py
"""
import json
import os

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
CURIOS = os.path.join(ROOT, "src/main/resources/data/dynasty/tags/items/accessories.json")

# id: (中文名, 英文名, 贴图来源, 染色, [材料…], (属性1, 值1, 属性2, 值2, 效果, 等级, 条件))
TRINKETS = {
    # ---- 六、玉器（10）----
    "jade_marrow_charm": ("玉髓佩", "Jade Marrow Charm", "jade_pendant", (0x9E, 0xE0, 0xC0),
                          ["dynasty:jade", "dynasty:jade", "dynasty:silk"], (0, 180.0, 1, 5.0, 0, 0, 0)),
    "jade_ruyi": ("玉如意", "Jade Ruyi", "jade_bi_disc", (0xF0, 0xE8, 0xC0),
                  ["dynasty:jade", "dynasty:jade_block", "dynasty:gold_coin"], (11, 2.0, -1, 0.0, 11, 0, 0)),
    "jade_ring": ("玉扳指", "Jade Ring", "jade_cicada", (0xC8, 0xE8, 0xB0),
                  ["dynasty:jade", "dynasty:silk"], (5, 0.10, 7, 1.0, 0, 0, 0)),
    "jade_belt_hook": ("玉带钩", "Jade Belt Hook", "jade_tortoise", (0xB8, 0xD8, 0xC8),
                       ["dynasty:jade", "dynasty:bronze_ingot"], (1, 8.0, 2, 0.3, 0, 0, 0)),
    "jade_flying_apsara": ("玉飞天", "Jade Apsara", "sky_feather", (0xE0, 0xF0, 0xD8),
                           ["dynasty:jade", "dynasty:silk", "dynasty:gold_coin"], (3, 0.08, -1, 0.0, 8, 0, 0)),
    "jade_bixie": ("玉辟邪", "Jade Bixie", "jade_crown", (0xA8, 0xD0, 0xA8),
                   ["dynasty:jade", "dynasty:cinnabar"], (6, 0.4, 4, 0.08, 0, 0, 0)),
    "jade_kylin": ("玉麒麟", "Jade Kylin", "qilin_horn_charm", (0x90, 0xE0, 0xB0),
                   ["dynasty:jade", "dynasty:qilin_horn"], (0, 220.0, 4, 0.10, 0, 0, 0)),
    "jade_silkworm": ("玉蚕", "Jade Silkworm", "jade_pendant", (0xC0, 0xE8, 0xD0),
                      ["dynasty:jade", "dynasty:raw_silk", "dynasty:silk"], (0, 120.0, -1, 0.0, 12, 0, 4)),
    "jade_cong": ("玉琮", "Jade Cong", "heart_mirror", (0x9C, 0xD8, 0xC8),
                  ["dynasty:jade", "dynasty:jade_block", "dynasty:bronze_ingot"], (1, 12.0, 2, 0.4, 0, 0, 0)),
    "jade_zhang": ("玉璋", "Jade Zhang", "star_compass", (0xB0, 0xE8, 0xE0),
                   ["dynasty:jade", "dynasty:jade_block", "dynasty:gold_coin"], (4, 0.12, 5, 0.08, 0, 0, 0)),
    # ---- 七、兵器配饰（10）----
    "saber_tassel": ("刀穗", "Saber Tassel", "dragon_whisker", (0xE0, 0x5A, 0x4A),
                     ["dynasty:silk", "dynasty:cinnabar"], (4, 0.07, 5, 0.05, 0, 0, 0)),
    "sword_tassel": ("剑穗", "Sword Tassel", "dragon_whisker", (0x6A, 0xA0, 0xE0),
                     ["dynasty:silk", "dynasty:silver_ingot"], (4, 0.06, 7, 1.0, 0, 0, 0)),
    "arrow_quiver": ("箭囊", "Arrow Quiver", "silk_pouch", (0xA0, 0x7A, 0x4A),
                     ["minecraft:leather", "dynasty:silk", "minecraft:arrow"], (4, 0.08, 3, 0.04, 0, 0, 0)),
    "bow_string": ("弓弦护腕", "Bowstring Bracer", "iron_waist_token", (0xC8, 0xA8, 0x6A),
                   ["dynasty:silk", "minecraft:string", "dynasty:refined_steel"], (5, 0.12, 4, 0.05, 0, 0, 0)),
    "wrist_guard": ("护腕", "Wrist Guard", "iron_waist_token", (0xB0, 0xB0, 0xB8),
                    ["dynasty:refined_steel", "dynasty:silk"], (1, 10.0, 2, 0.3, 0, 0, 0)),
    "knee_guard": ("护膝", "Knee Guard", "tiger_crest", (0xC0, 0x9A, 0x60),
                   ["dynasty:refined_steel", "minecraft:leather"], (3, 0.05, 2, 0.2, 0, 0, 0)),
    "belt_buckle": ("腰带扣", "Belt Buckle", "gold_seal_charm", (0xE8, 0xC8, 0x70),
                    ["dynasty:bronze_ingot", "dynasty:silver_ingot"], (1, 6.0, 0, 120.0, 0, 0, 0)),
    "scale_plate": ("甲片", "Scale Plate", "dragon_scale_charm", (0x8A, 0xA0, 0x90),
                    ["dynasty:dragon_scale", "dynasty:refined_steel"], (1, 9.0, 2, 0.25, 0, 0, 0)),
    "iron_pauldron": ("铁护肩", "Iron Pauldron", "iron_waist_token", (0x88, 0x90, 0x9A),
                      ["dynasty:refined_steel", "dynasty:refined_steel"], (1, 14.0, 4, 0.05, 0, 0, 0)),
    "horse_stirrup": ("马镫", "Horse Stirrup", "war_horse_bell", (0xC8, 0xC0, 0x90),
                      ["dynasty:bronze_ingot", "minecraft:leather"], (3, 0.10, -1, 0.0, 0, 0, 5)),
    # ---- 八、灵兽（10）----
    "crane_feather": ("鹤羽", "Crane Feather", "phoenix_feather_charm", (0xF0, 0xF0, 0xE8),
                      ["dynasty:phoenix_feather", "dynasty:silk"], (3, 0.10, -1, 0.0, 8, 0, 0)),
    "tiger_claw": ("虎爪", "Tiger Claw", "tiger_token", (0xE0, 0xA0, 0x50),
                   ["minecraft:bone", "dynasty:refined_steel"], (4, 0.12, 6, 0.4, 0, 0, 0)),
    "leopard_tail": ("豹尾", "Leopard Tail", "fox_tail_charm", (0xE8, 0xC8, 0x70),
                     ["dynasty:silk", "dynasty:raw_silk", "minecraft:bone"], (3, 0.12, 5, 0.06, 0, 0, 0)),
    "deer_antler": ("鹿角", "Deer Antler", "qilin_horn_charm", (0xD8, 0xC0, 0x90),
                    ["minecraft:bone", "dynasty:jade"], (0, 260.0, -1, 0.0, 5, 0, 0)),
    "snake_gall": ("蛇胆", "Snake Gall", "cinnabar_pouch", (0x70, 0xB0, 0x60),
                   ["dynasty:cinnabar", "dynasty:healing_salve"], (4, 0.10, -1, 0.0, 0, 0, 3)),
    "bear_paw": ("熊掌", "Bear Paw", "dragon_bone_ring", (0xA0, 0x7A, 0x5A),
                 ["minecraft:leather", "dynasty:refined_steel"], (0, 300.0, 4, 0.08, 0, 0, 0)),
    "turtle_shell": ("龟甲", "Turtle Shell", "jade_tortoise", (0x80, 0xA8, 0x80),
                     ["minecraft:scute", "dynasty:jade"], (1, 16.0, 2, 0.5, 0, 0, 0)),
    "rhino_horn": ("犀角", "Rhino Horn", "qilin_horn_charm", (0xC0, 0xB0, 0xA0),
                   ["minecraft:bone", "dynasty:refined_steel", "dynasty:jade"], (4, 0.14, 1, 6.0, 0, 0, 0)),
    "ivory_tusk": ("象牙", "Ivory Tusk", "imperial_seal_charm", (0xF0, 0xE8, 0xD8),
                   ["minecraft:bone", "dynasty:silver_ingot", "dynasty:jade"], (7, 2.0, 4, 0.06, 0, 0, 0)),
    "hawk_eye": ("鹰眼", "Hawk Eye", "star_compass", (0xE0, 0xC0, 0x60),
                 ["dynasty:jade", "dynasty:gold_coin"], (4, 0.10, 7, 2.0, 0, 0, 0)),
    # ---- 九、文人（10）----
    "poem_scroll": ("诗文卷轴", "Poem Scroll", "silk_pouch", (0xF0, 0xE8, 0xC8),
                    ["dynasty:talisman_paper", "dynasty:ink_stick", "dynasty:silk"], (11, 2.0, -1, 0.0, 11, 0, 0)),
    "seal_charm": ("印章坠", "Seal Charm", "gold_seal_charm", (0xE0, 0xB0, 0x80),
                   ["dynasty:official_seal", "dynasty:silk"], (0, 100.0, 11, 1.0, 0, 0, 0)),
    "go_board": ("棋盘坠", "Go Board Charm", "bronze_mirror", (0x70, 0x70, 0x60),
                 ["dynasty:ink_stick", "dynasty:jade", "dynasty:bronze_ingot"], (5, 0.10, -1, 0.0, 0, 0, 0)),
    "guqin_string": ("古琴弦", "Guqin String", "bamboo_flute", (0xC8, 0xA8, 0x88),
                     ["dynasty:silk", "dynasty:raw_silk"], (5, 0.08, -1, 0.0, 0, 0, 0)),
    "tea_cup": ("茶盏", "Tea Cup", "inkstone", (0xC0, 0xD8, 0xC0),
                ["dynasty:jade", "dynasty:tea"], (0, 200.0, -1, 0.0, 12, 0, 0)),
    "wine_gourd": ("酒葫芦", "Wine Gourd", "cloud_brocade", (0xD8, 0xB0, 0x70),
                   ["dynasty:wine", "dynasty:jade"], (0, 240.0, 6, 0.3, 0, 0, 0)),
    "incense_sachet": ("香囊", "Incense Sachet", "cinnabar_pouch", (0xE0, 0xC8, 0xE8),
                       ["dynasty:cinnabar", "dynasty:silk", "dynasty:brocade"], (0, 160.0, -1, 0.0, 5, 0, 0)),
    "folding_fan": ("折扇", "Folding Fan", "cloud_brocade", (0xE8, 0xD8, 0xB8),
                    ["dynasty:talisman_paper", "dynasty:bamboo_slip", "dynasty:silk"], (3, 0.06, 5, 0.08, 0, 0, 0)),
    "mirror_pouch": ("铜镜袋", "Mirror Pouch", "heart_mirror", (0xC8, 0xC8, 0xD0),
                     ["dynasty:bronze_mirror", "dynasty:silk"], (1, 10.0, -1, 0.0, 4, 0, 0)),
    "brush_rack": ("笔架坠", "Brush Rack Charm", "inkstone", (0x80, 0x80, 0x90),
                   ["dynasty:ink_brush", "dynasty:jade", "dynasty:bronze_ingot"], (5, 0.14, 4, 0.06, 0, 0, 0)),
    # ---- 十、道家（10）----
    "bagua_mirror": ("八卦镜", "Bagua Mirror", "bronze_mirror", (0xC8, 0xB8, 0x70),
                     ["dynasty:bronze_mirror", "dynasty:cinnabar", "dynasty:jade"], (1, 14.0, -1, 0.0, 4, 0, 0)),
    "peach_sword": ("桃木剑", "Peach Wood Sword", "dragon_bone_ring", (0xD0, 0x90, 0x70),
                    ["dynasty:bamboo_slip", "dynasty:cinnabar"], (4, 0.16, -1, 0.0, 0, 0, 0)),
    "talisman_pouch": ("符纸包", "Talisman Pouch", "silk_pouch", (0xF0, 0xD8, 0x90),
                       ["dynasty:talisman_paper", "dynasty:talisman_paper", "dynasty:silk"], (11, 3.0, -1, 0.0, 11, 0, 0)),
    "alchemy_pendant": ("炼丹坠", "Alchemy Pendant", "cinnabar_pouch", (0xE8, 0xC0, 0x90),
                        ["dynasty:cinnabar", "dynasty:pill_longevity"], (0, 200.0, -1, 0.0, 5, 1, 0)),
    "golden_pill": ("金丹", "Golden Pill", "gold_seal_charm", (0xFF, 0xD8, 0x50),
                    ["dynasty:pill_longevity", "dynasty:dragon_crystal", "dynasty:gold_coin"], (0, 400.0, -1, 0.0, 5, 2, 0)),
    "cloud_pattern": ("云纹佩", "Cloud Pattern Charm", "cloud_brocade", (0xC0, 0xD8, 0xF0),
                      ["dynasty:cloud_brocade", "dynasty:jade", "dynasty:silk"], (3, 0.12, 2, 0.3, 0, 0, 0)),
    "star_dial": ("星斗盘", "Star Dial", "star_compass", (0xB0, 0xB8, 0xF0),
                  ["dynasty:star_compass", "dynasty:jade", "dynasty:dragon_crystal"], (4, 0.12, 5, 0.10, 0, 0, 0)),
    "tiangang_talisman": ("天罡符", "Tiangang Talisman", "storm_charm", (0x80, 0xC0, 0xE0),
                          ["dynasty:sky_token", "dynasty:talisman_paper", "dynasty:cinnabar"], (4, 0.18, 2, 0.4, 0, 0, 0)),
    "disha_talisman": ("地煞符", "Disha Talisman", "tomb_candle", (0xE0, 0x90, 0x60),
                       ["dynasty:emperor_bone", "dynasty:talisman_paper", "dynasty:cinnabar"], (1, 18.0, 6, 0.4, 0, 0, 0)),
    "purple_qi_pearl": ("紫气珠", "Purple Qi Pearl", "sea_pearl", (0xA0, 0x70, 0xE0),
                        ["dynasty:sea_pearl", "dynasty:xuantian_jade", "dynasty:dragon_crystal"], (0, 320.0, 4, 0.14, 0, 0, 0)),
}


def tint(src, dst, color):
    """复制并染色（保留明暗与透明）/ copy the texture and multiply by a colour."""
    image = Image.open(src).convert("RGBA")
    pixels = image.load()
    ratio = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            pixels[x, y] = (min(255, int(r * ratio[0])), min(255, int(g * ratio[1])),
                            min(255, int(b * ratio[2])), a)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    image.save(dst)


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def local_items():
    """本模组已有的物品 id（用来检查配方材料是否真实存在）。"""
    return {os.path.basename(p)[:-5]
            for p in os.listdir(os.path.join(ASSETS, "models/item"))}


def main():
    problems = []
    items = local_items()
    for tid, (zh, en, source, color, materials, _spec) in TRINKETS.items():
        # ① 贴图（从旧饰品染色而来）
        src = os.path.join(ASSETS, "textures/item/%s.png" % source)
        if not os.path.exists(src):
            problems.append("缺少源贴图 %s（%s 用）" % (source, tid))
        else:
            tint(src, os.path.join(ASSETS, "textures/item/%s.png" % tid), color)
        # ② 模型
        write(os.path.join(ASSETS, "models/item/%s.json" % tid),
              {"parent": "minecraft:item/generated",
               "textures": {"layer0": "dynasty:item/%s" % tid}})
        # ③ 配方（材料必须真实存在）
        for material in materials:
            namespace, path = material.split(":")
            if namespace == "dynasty" and path not in items:
                problems.append("%s 的配方材料不存在：%s" % (tid, material))
        write(os.path.join(DATA, "recipes/%s.json" % tid),
              {"type": "minecraft:crafting_shapeless",
               "ingredients": [{"item": item} for item in materials],
               "result": {"item": "dynasty:%s" % tid}})
    print("饰品扩充：%d 件（贴图 / 模型 / 配方）" % len(TRINKETS))

    # ④ 中英词条
    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = json.load(open(path, encoding="utf-8"))
        for tid, values in TRINKETS.items():
            data["item.dynasty.%s" % tid] = values[0] if index == 0 else values[1]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    # ⑤ 饰品总表与标准 Curios 分类
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
    from gen_curios import build as build_curios
    build_curios()
    print("Curios 标签新增 %d 条（合计 %d 件饰品）" % (added, len(values)))

    if problems:
        print("问题 ❌")
        for problem in problems:
            print("   -", problem)
        raise SystemExit(1)
    print("饰品扩充完成 ✅")


if __name__ == "__main__":
    main()
