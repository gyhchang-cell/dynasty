#!/usr/bin/env python3
"""1.4.0 第三十一轮：再扩 10 套盔甲（17 → 27 套），并补上「终盘套」的台阶。

* 贴图：从最接近的旧套复制一份再**染色**，每套一眼能分辨；
* 模型 / 配方 / 中英名字一次生成；
* Java 侧四处表（DynastyArmorMaterials / DynastyGear.EXTRA_SET_TABLE /
  DynastyBalance.SET_BONUS / DynastyTooltips.setName）按同一张表对应。

每件的减伤（SET_BONUS 第一个数）33% → 42%，生命 1100 → 3200：
玄武（防御）→ 朱雀（火）→ 青龙（攻）→ 白虎（攻+击退）→ 北斗（移速）
→ 天罡 → 地煞 → 太乙 → 紫微 → 混元（毕业）。

运行：python3 tools/art/gen_armor3.py
"""
import json
import os

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
PIECES = ("helmet", "chestplate", "leggings", "boots")
PIECE_ZH = {"helmet": "头盔", "chestplate": "胸甲", "leggings": "护腿", "boots": "靴子"}
PIECE_EN = {"helmet": "Helmet", "chestplate": "Chestplate", "leggings": "Leggings", "boots": "Boots"}

# set_id: (中文名, 英文名, 贴图来源, 上一套, 染色, [材料…])
SETS = {
    "xuanwu": ("玄武甲", "Xuanwu", "dark_iron", "dark_iron", (0x5B, 0x6E, 0x5A),
               ["dynasty:refined_steel", "dynasty:dragon_scale", "dynasty:emperor_bone"]),
    "zhuque": ("朱雀羽", "Zhuque", "phoenix", "xuanwu", (0xE0, 0x6A, 0x4A),
               ["dynasty:phoenix_feather", "dynasty:phoenix_feather", "dynasty:cinnabar"]),
    "qinglong": ("青龙鳞", "Qinglong", "dragon_scale", "zhuque", (0x3F, 0x8A, 0x62),
                 ["dynasty:dragon_scale", "dynasty:dragon_scale", "dynasty:dragon_crystal"]),
    "baihu": ("白虎铠", "Baihu", "draco_king", "qinglong", (0xE6, 0xE8, 0xEE),
              ["dynasty:refined_steel", "dynasty:refined_steel", "dynasty:jade"]),
    "beidou": ("北斗甲", "Beidou", "sky", "baihu", (0x7A, 0x86, 0xE0),
               ["dynasty:dragon_crystal", "dynasty:dragon_crystal", "dynasty:xuantian_jade"]),
    "tiangang": ("天罡甲", "Tiangang", "sky", "beidou", (0x62, 0xC8, 0xD8),
                 ["dynasty:sky_token", "dynasty:dragon_crystal", "dynasty:dragon_crystal"]),
    "disha": ("地煞甲", "Disha", "dark_iron", "tiangang", (0x8A, 0x3A, 0x3A),
              ["dynasty:emperor_bone", "dynasty:refined_steel", "dynasty:refined_steel"]),
    "taiyi": ("太乙甲", "Taiyi", "xuantian", "disha", (0xE8, 0xD8, 0x9A),
              ["dynasty:xuantian_jade", "dynasty:xuantian_jade", "dynasty:dragon_emperor_seal"]),
    "ziwei": ("紫微甲", "Ziwei", "xuantian", "taiyi", (0x8A, 0x5C, 0xD2),
              ["dynasty:dragon_emperor_seal", "dynasty:dragon_crystal", "dynasty:dragon_crystal"]),
    "hunyuan": ("混元甲", "Hunyuan", "dark_iron", "ziwei", (0xD8, 0xB0, 0x4A),
                ["dynasty:emperor_bone", "dynasty:dragon_emperor_seal", "dynasty:dragon_crystal"]),
    # ---- 第三十二轮：毕业甲「鸿蒙帝铠」----
    # 甲胄谱两条流派线的终点合体：每件 = 龙王鳞铠·同部位 + 混元甲·同部位 + 帝骸骨 + 龙帝玉玺。
    # 混元之上为鸿蒙 —— 全模组最终的一套。
    # The graduation set: each piece merges the two armour ladders' final pieces.
    "hongmeng": ("鸿蒙帝铠", "Hongmeng Imperial Armor", "hunyuan", "draco_king", (0xF2, 0xE2, 0xB6),
                 ["dynasty:emperor_bone", "dynasty:dragon_emperor_seal"]),
}

# 需要「两件上阶装备」才能做的套装：set_id -> 另一条线的终点套装
# Sets whose recipe takes a second previous piece (the other ladder's final piece).
EXTRA_PREV = {"hongmeng": "hunyuan"}

# 顺手补上一直缺失的图层贴图：天将云铠 / 龙王鳞铠（穿在身上原本是没有贴图的）
# source set -> tint colour, for the armour layers that were never generated.
MISSING_LAYERS = {
    "sky": ("xuantian", (0x9C, 0xD0, 0xF0)),
    "draco_king": ("dark_iron", (0x86, 0x62, 0xC8)),
}


def tint(src, dst, color):
    """复制并染色（保留明暗与透明）/ copy the texture and multiply by a colour."""
    if not os.path.exists(src):
        print("!! 缺少源贴图", src)
        return False
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
    return True


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    # 先把缺的源图层补出来（否则下面拿它当源会失败）
    for set_id, (texture_from, color) in MISSING_LAYERS.items():
        for layer in (1, 2):
            dst = os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png" % (set_id, layer))
            if not os.path.exists(dst):
                tint(os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png"
                                  % (texture_from, layer)), dst, color)
                print("补图层贴图:", set_id, "layer", layer)

    for set_id, (zh, en, texture_from, prev, color, materials) in SETS.items():
        for piece in PIECES:
            name = "%s_%s" % (set_id, piece)
            tint(os.path.join(ASSETS, "textures/item/%s_%s.png" % (texture_from, piece)),
                 os.path.join(ASSETS, "textures/item/%s.png" % name), color)
            write(os.path.join(ASSETS, "models/item/%s.json" % name),
                  {"parent": "minecraft:item/generated",
                   "textures": {"layer0": "dynasty:item/%s" % name}})
            write(os.path.join(DATA, "recipes/%s.json" % name),
                  {"type": "minecraft:crafting_shapeless",
                   "ingredients": [{"item": "dynasty:%s_%s" % (prev, piece)}]
                                  + ([{"item": "dynasty:%s_%s" % (EXTRA_PREV[set_id], piece)}]
                                     if set_id in EXTRA_PREV else [])
                                  + [{"item": item} for item in materials],
                   "result": {"item": "dynasty:%s" % name}})
        for layer in (1, 2):
            tint(os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png" % (texture_from, layer)),
                 os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png" % (set_id, layer)),
                 color)
        print("set:", set_id, zh, len(PIECES), "件")

    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = json.load(open(path, encoding="utf-8"))
        for set_id, values in SETS.items():
            for piece in PIECES:
                name = "%s_%s" % (set_id, piece)
                data["item.dynasty.%s" % name] = (values[0] + "·" + PIECE_ZH[piece]
                                                  if index == 0 else
                                                  "%s %s" % (values[1], PIECE_EN[piece]))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("护甲扩充完成：%d 套新盔甲（每套 4 件）" % len(SETS))


if __name__ == "__main__":
    main()
