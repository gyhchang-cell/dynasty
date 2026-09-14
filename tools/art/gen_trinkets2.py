#!/usr/bin/env python3
"""1.4.0 第二十轮：再扩 10 件饰品（29 → 39 件）。

贴图从最接近的旧饰品复制一份再染色；模型 / 配方 / 中英名字一次生成。
Java 侧（注册、Curios、效果）在 DynastyTrinkets.java 里按同一张表对应，
改这里也要同步改那边。

运行：python3 tools/art/gen_trinkets2.py
"""
import json
import os

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")

# id: (中文名, 英文名, 贴图来源, 染色, [材料…])
TRINKETS = {
    "cloud_brocade": ("云锦囊", "Cloud Pouch", "silk_pouch", (0x9F, 0xD2, 0xF0),
                      ["dynasty:brocade", "dynasty:brocade", "dynasty:silk"]),
    "star_compass": ("星盘", "Astrolabe", "south_pointing_compass", (0xE8, 0xD0, 0x6A),
                     ["dynasty:dragon_crystal", "dynasty:gold_coin", "dynasty:gold_coin"]),
    "dragon_king_scale": ("龙王逆鳞", "Dragon King Scale", "dragon_scale_charm", (0x8C, 0x5C, 0xD6),
                          ["dynasty:sea_token", "dynasty:dragon_scale", "dynasty:dragon_scale"]),
    "sky_feather": ("天羽", "Sky Feather", "phoenix_feather_charm", (0x9C, 0xD8, 0xFF),
                    ["dynasty:sky_token", "dynasty:phoenix_feather", "dynasty:phoenix_feather"]),
    "imperial_seal_charm": ("御玺佩", "Imperial Seal Charm", "gold_seal_charm", (0xE0, 0x6A, 0x50),
                            ["dynasty:jade_seal", "dynasty:gold_seal_charm"]),
    "tomb_candle": ("长明烛", "Tomb Candle", "cinnabar_pouch", (0xFF, 0xE8, 0xA8),
                    ["dynasty:cinnabar", "dynasty:talisman_paper", "dynasty:talisman_paper"]),
    "inkstone": ("砚台", "Inkstone", "bronze_mirror", (0x6A, 0x6E, 0x78),
                 ["dynasty:ink_stick", "dynasty:ink_stick", "dynasty:jade"]),
    "bamboo_flute": ("竹笛", "Bamboo Flute", "jade_bi_disc", (0xA8, 0xD8, 0x7A),
                     ["dynasty:bamboo_slip", "dynasty:bamboo_slip", "dynasty:silk"]),
    "merit_badge": ("功牌", "Merit Badge", "tiger_crest", (0xE8, 0xB0, 0x50),
                    ["dynasty:official_seal", "dynasty:silver_ingot", "dynasty:silver_ingot"]),
    "sea_conch": ("海螺", "Sea Conch", "sea_pearl", (0x6E, 0xD8, 0xD0),
                  ["dynasty:sea_pearl", "minecraft:nautilus_shell", "minecraft:nautilus_shell"]),
}


def tint(src, dst, color):
    if not os.path.exists(src):
        print("!! 缺少源贴图", src)
        return
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


def main():
    for item_id, (zh, en, texture_from, color, materials) in TRINKETS.items():
        tint(os.path.join(ASSETS, "textures/item/%s.png" % texture_from),
             os.path.join(ASSETS, "textures/item/%s.png" % item_id), color)
        write(os.path.join(ASSETS, "models/item/%s.json" % item_id),
              {"parent": "minecraft:item/generated",
               "textures": {"layer0": "dynasty:item/%s" % item_id}})
        write(os.path.join(DATA, "recipes/%s.json" % item_id),
              {"type": "minecraft:crafting_shapeless",
               "ingredients": [{"item": item} for item in materials],
               "result": {"item": "dynasty:%s" % item_id}})
        print("trinket:", item_id, zh)

    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = json.load(open(path, encoding="utf-8"))
        for item_id, values in TRINKETS.items():
            data["item.dynasty.%s" % item_id] = values[0] if index == 0 else values[1]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("饰品扩充完成：%d 件" % len(TRINKETS))


if __name__ == "__main__":
    main()
