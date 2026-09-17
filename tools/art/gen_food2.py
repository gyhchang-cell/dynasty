"""第三十二轮：+8 种食物（贴图 / 模型 / 配方 / 中英词条）。

配方统一用原版材料（小麦 / 糖 / 蛋 / 蜂蜜 / 可可 ……），不新增材料物品，
与现有食物（月饼 / 汤圆 / 粽子 …）的配方风格一致。
Java 侧：在 `DynastyItems` 里按打印出来的行注册（营养 / 饱和度已算好）。

用法：python3 tools/art/gen_food2.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken  # noqa: E402
from palette import *  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
S = 32
INK = (28, 20, 16, 255)


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(cv, name):
    cv.outline(INK)
    cv.save(os.path.join(ASSETS, "textures/item/%s.png" % name))


def peach_bun():                       # 寿桃：桃形带叶
    cv = Cv(S, S)
    cv.disc(16, 19, 11, hx("E8A0A8"))
    cv.disc(16, 18, 10, hx("F2B8BE"))
    cv.poly([(16, 5), (21, 13), (11, 13)], hx("F2B8BE"))
    cv.line(16, 6, 16, 14, hx("D98A94"))
    cv.poly([(20, 7), (27, 9), (22, 12)], hx("5FAF52"))
    cv.disc(12, 15, 3, lighten(hx("F2B8BE"), 0.35))
    save(cv, "peach_bun")


def lotus_cake():                      # 荷花酥：多层花瓣
    cv = Cv(S, S)
    for i, r in ((0, 12), (1, 9), (2, 6)):
        cv.disc(16, 22 - i * 2, r, mix(hx("F2C0C8"), hx("F7E2B0"), i * 0.3))
    cv.ring(16, 20, 12, hx("E28AA0"))
    cv.ring(16, 18, 9, hx("E0B06A"))
    cv.disc(16, 15, 3, hx("F5E2A0"))
    cv.px(12, 14, hx("FFFFFF"))
    save(cv, "lotus_cake")


def sesame_ball():                     # 芝麻团：圆球 + 芝麻点
    cv = Cv(S, S)
    cv.disc(16, 19, 11, hx("C89650"))
    cv.disc(16, 18, 10, hx("E0B070"))
    for x, y in ((10, 14), (14, 12), (19, 13), (22, 17), (12, 20), (18, 22), (16, 25)):
        cv.px(x, y, hx("4A3A22"))
        cv.px(x + 1, y, hx("5E4A2E"))
    cv.disc(12, 15, 3, lighten(hx("E0B070"), 0.35))
    save(cv, "sesame_ball")


def sweet_soup_cake():                 # 糖油饼：圆形油饼带焦纹
    cv = Cv(S, S)
    cv.disc(16, 17, 12, hx("B07A38"))
    cv.disc(16, 16, 11, hx("D09A48"))
    cv.ring(16, 16, 8, hx("9A6428"))
    for x, y in ((10, 12), (16, 10), (22, 13), (11, 20), (20, 21)):
        cv.px(x, y, hx("7A4E1E"))
    cv.px(13, 13, hx("F0C070"))
    save(cv, "sweet_soup_cake")


def bamboo_rice():                     # 竹筒饭：竹节 + 米饭
    cv = Cv(S, S)
    cv.rect(8, 6, 23, 26, hx("5FAF52"))
    cv.rect(9, 7, 22, 25, hx("7AC46A"))
    cv.rect(8, 11, 23, 12, hx("3F7A3A"))
    cv.rect(8, 21, 23, 22, hx("3F7A3A"))
    cv.rect(11, 14, 20, 19, hx("F2EEDC"))
    for x in range(12, 20, 2):
        cv.px(x, 15, hx("FFFFFF"))
        cv.px(x + 1, 18, hx("E0D8C0"))
    cv.px(10, 8, hx("A8E09A"))
    save(cv, "bamboo_rice")


def eight_treasure_porridge():         # 八宝粥：碗 + 杂粮
    cv = Cv(S, S)
    cv.poly([(6, 15), (26, 15), (23, 28), (9, 28)], hx("C8C4B8"))
    cv.poly([(8, 17), (24, 17), (21, 26), (11, 26)], hx("E8E4D8"))
    cv.disc(16, 14, 11, hx("8A5A32"))
    cv.disc(16, 13, 10, hx("A8783C"))
    for x, y, c in ((11, 11, "C0392B"), (16, 9, "58B477"), (21, 12, "E8C24A"),
                    (13, 15, "8A5A32"), (19, 15, "C0392B"), (16, 17, "F2EEDC")):
        cv.disc(x, y, 2, hx(c))
    cv.px(12, 10, hx("FFFFFF"))
    save(cv, "eight_treasure_porridge")


def dried_persimmon():                 # 柿饼：橘色扁饼 + 白霜
    cv = Cv(S, S)
    cv.disc(16, 17, 12, hx("D07A28"))
    cv.disc(16, 16, 11, hx("E89A38"))
    cv.ring(16, 16, 8, hx("C06A20"))
    for x, y in ((12, 12), (19, 12), (10, 18), (22, 18), (14, 22), (18, 22)):
        cv.px(x, y, hx("F5F0E0"))
    cv.px(13, 13, hx("F8E0B0"))
    save(cv, "dried_persimmon")


def chrysanthemum_wine():              # 菊花酒：酒坛 + 花
    cv = Cv(S, S)
    cv.poly([(9, 12), (23, 12), (25, 26), (7, 26)], hx("8A6A3A"))
    cv.poly([(10, 13), (22, 13), (23, 25), (9, 25)], hx("A88A50"))
    cv.rect(12, 9, 20, 12, hx("6B4423"))
    cv.rect(13, 8, 19, 10, hx("8B5A2B"))
    for x, y in ((16, 15), (12, 18), (20, 18), (16, 21)):
        cv.disc(x, y, 3, hx("F5E2A0"))
    cv.disc(16, 18, 2, hx("E8C24A"))
    cv.px(11, 14, hx("D8BE86"))
    save(cv, "chrysanthemum_wine")


# id: (中文, 英文, 营养, 饱和度, 是否快吃, [配方材料], 贴图画法)
FOODS = {
    "peach_bun": ("寿桃", "Peach Bun", 8, 0.8, False,
                  ["minecraft:wheat", "minecraft:sugar", "minecraft:honey_bottle"], peach_bun),
    "lotus_cake": ("荷花酥", "Lotus Cake", 6, 0.6, False,
                   ["minecraft:wheat", "minecraft:sugar", "minecraft:egg"], lotus_cake),
    "sesame_ball": ("芝麻团", "Sesame Ball", 5, 0.6, True,
                    ["minecraft:wheat", "minecraft:sugar", "dynasty:silk"], sesame_ball),
    "sweet_soup_cake": ("糖油饼", "Sweet Fried Cake", 6, 0.7, False,
                        ["minecraft:wheat", "minecraft:sugar", "minecraft:honey_bottle"], sweet_soup_cake),
    "bamboo_rice": ("竹筒饭", "Bamboo Rice", 7, 0.8, False,
                    ["minecraft:wheat", "minecraft:cooked_porkchop", "dynasty:bamboo_slip"], bamboo_rice),
    "eight_treasure_porridge": ("八宝粥", "Eight-Treasure Porridge", 8, 0.9, False,
                                ["minecraft:wheat", "minecraft:sugar", "minecraft:sweet_berries",
                                 "minecraft:apple"], eight_treasure_porridge),
    "dried_persimmon": ("柿饼", "Dried Persimmon", 4, 0.5, True,
                        ["minecraft:sweet_berries", "minecraft:sugar"], dried_persimmon),
    "chrysanthemum_wine": ("菊花酒", "Chrysanthemum Wine", 3, 0.4, True,
                           ["minecraft:honey_bottle", "minecraft:sugar", "dynasty:wine"], chrysanthemum_wine),
}


def main():
    for fid, values in FOODS.items():
        zh, en, nutrition, saturation, fast, ingredients, draw = values
        draw()
        write(os.path.join(ASSETS, "models/item/%s.json" % fid),
              {"parent": "minecraft:item/generated",
               "textures": {"layer0": "dynasty:item/%s" % fid}})
        write(os.path.join(DATA, "recipes/%s.json" % fid),
              {"type": "minecraft:crafting_shapeless",
               "ingredients": [{"item": item} for item in ingredients],
               "result": {"item": "dynasty:%s" % fid, "count": 1}})
        print("food wired:", fid, zh)

    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = read(path)
        for fid, values in FOODS.items():
            data["item.dynasty.%s" % fid] = values[0] if index == 0 else values[1]
        write(path, data)

    print("\n--- DynastyItems 追加行（Java，可直接粘贴）---")
    for fid, (zh, en, nutrition, saturation, fast, _i, _d) in FOODS.items():
        print("""    public static final RegistryObject<Item> %s = ITEMS.register("%s",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(%d).saturationMod(%.1fF)%s.build())));
"""
              % (fid.upper(), fid, nutrition, saturation, ".fast()" if fast else ""))
    print("食物扩充完成：%d 种 ✅" % len(FOODS))


if __name__ == "__main__":
    main()
