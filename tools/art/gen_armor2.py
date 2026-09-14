#!/usr/bin/env python3
"""1.4.0 第二十轮：再扩 10 套盔甲（7 → 17 套）。

* 贴图：从最接近的旧套复制一份再**染色**，所以每套看起来都不一样；
  同时补上一直缺失的「穿在身上」的图层贴图（鲛绡甲 / 玄铁重铠原本没有）。
* 模型 / 配方 / 中英名字（中/英）一次生成。
* Java 侧（材质、注册、套装加成、提示名）在 DynastyArmorMaterials / DynastyGear /
  DynastyBalance / DynastyTooltips 里按同一张表对应，改这里也要同步改那边。

运行：python3 tools/art/gen_armor2.py
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
    "bamboo": ("竹甲", "Bamboo", "cloth", "cloth", (0x9C, 0xCB, 0x6E),
               ["minecraft:bamboo", "minecraft:bamboo", "dynasty:silk"]),
    "leather": ("皮甲", "Leather", "cloth", "bamboo", (0xA9, 0x74, 0x4F),
                ["minecraft:leather", "minecraft:leather", "dynasty:raw_silk"]),
    "brocade": ("织锦袍", "Brocade", "cloth", "leather", (0xE0, 0xB4, 0x5C),
                ["dynasty:brocade", "dynasty:brocade", "dynasty:silk"]),
    "bronze": ("青铜甲", "Bronze", "general", "brocade", (0xC0, 0x8A, 0x45),
               ["dynasty:bronze_ingot", "dynasty:bronze_ingot", "dynasty:bronze_ingot"]),
    "silver": ("白银铠", "Silver", "general", "bronze", (0xD8, 0xDC, 0xE0),
               ["dynasty:silver_ingot", "dynasty:silver_ingot", "dynasty:silver_ingot"]),
    "cinnabar": ("朱砂符甲", "Cinnabar", "jade", "silver", (0xC0, 0x39, 0x2B),
                 ["dynasty:cinnabar", "dynasty:talisman_paper", "dynasty:talisman_paper"]),
    "phoenix": ("凤凰羽衣", "Phoenix", "jade", "cinnabar", (0xE8, 0x66, 0x3C),
                ["dynasty:phoenix_feather", "dynasty:phoenix_feather", "dynasty:silk"]),
    "qilin": ("麒麟鳞甲", "Qilin", "dragon_scale", "phoenix", (0x3F, 0xA5, 0x8F),
              ["dynasty:qilin_horn", "dynasty:dragon_scale", "dynasty:dragon_scale"]),
    "sky": ("天将云铠", "Sky General", "sea_silk", "qilin", (0x8F, 0xC7, 0xE8),
            ["dynasty:sky_token", "dynasty:xuantian_jade", "dynasty:xuantian_jade"]),
    "draco_king": ("龙王鳞铠", "Dragon King", "dark_iron", "sky", (0x7A, 0x4F, 0xBF),
                   ["dynasty:sea_token", "dynasty:dragon_crystal", "dynasty:dragon_scale"]),
}

# 顺手补上一直缺失的图层贴图（套装 id → 用哪套的图层 + 染色）
MISSING_LAYERS = {
    "sea_silk": ("dragon_scale", (0x7F, 0xC8, 0xD8)),
    "dark_iron": ("xuantian", (0x4A, 0x4A, 0x56)),
}


def tint(src, dst, color):
    """复制并染色（保留明暗与透明）/ copy the texture and multiply by a colour."""
    if not os.path.exists(src):
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
                                  + [{"item": item} for item in materials],
                   "result": {"item": "dynasty:%s" % name}})
        # 穿在身上的图层贴图（新套 + 补齐旧套）
        for layer in (1, 2):
            tint(os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png" % (texture_from, layer)),
                 os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png" % (set_id, layer)),
                 color)
        print("set:", set_id, zh, len(PIECES), "件")

    for set_id, (texture_from, color) in MISSING_LAYERS.items():
        for layer in (1, 2):
            dst = os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png" % (set_id, layer))
            if not os.path.exists(dst):
                tint(os.path.join(ASSETS, "textures/models/armor/%s_layer_%d.png"
                                  % (texture_from, layer)), dst, color)
                print("补图层贴图:", set_id, "layer", layer)

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
    print("护甲扩充完成：%d 套新盔甲" % len(SETS))


if __name__ == "__main__":
    main()
