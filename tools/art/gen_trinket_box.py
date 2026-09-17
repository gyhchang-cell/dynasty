"""百宝妆匣：补齐贴图 / 模型 / 配方 / 中英词条。

背景：旧「饰品袋」界面被 Curios 槽位取代后，`trinket_box` 只剩安装脚本里的一条记录，
资源目录里查无此物（`validate_final.py` 把它列为未接线物品）。这里把它做成真正的物品：
**右键随机开出一件王朝饰品，开完即消耗**（Java 侧见 `DynastyUsables.TrinketBoxItem`
与 `DynastyTrinkets.randomGift`）。

用法：python3 tools/art/gen_trinket_box.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx  # noqa: E402
from palette import *  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
S = 32
INK = (28, 20, 16, 255)
D = "dynasty:"


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def texture():
    cv = Cv(S, S)
    cv.rect(5, 12, 26, 26, hx("6B4423"))            # 箱身 / chest body
    cv.rect(6, 13, 25, 25, hx("8B5A2B"))
    cv.rect(5, 8, 26, 12, hx("7A4E2A"))             # 箱盖 / lid
    cv.rect(6, 9, 25, 11, hx("A87A3C"))
    cv.rect(14, 10, 18, 16, GOLD_TRIM)              # 锁扣 / clasp
    cv.px(16, 13, hx("4E8A6A"))
    cv.line(7, 20, 24, 20, hx("6B4423"))
    cv.px(9, 17, hx("C9A24A"))
    cv.px(21, 17, hx("C9A24A"))
    cv.outline(INK)
    cv.save(os.path.join(ASSETS, "textures/item/trinket_box.png"))


def main():
    texture()
    write(os.path.join(ASSETS, "models/item/trinket_box.json"),
          {"parent": "minecraft:item/generated",
           "textures": {"layer0": "dynasty:item/trinket_box"}})
    write(os.path.join(DATA, "recipes/trinket_box.json"),
          {"type": "minecraft:crafting_shapeless",
           "ingredients": [{"item": D + "silk"}, {"item": D + "silk"},
                           {"item": D + "bamboo_slip"}, {"item": D + "bamboo_slip"},
                           {"item": "minecraft:gold_ingot"}],
           "result": {"item": D + "trinket_box"}})
    for filename, name in (("zh_cn.json", "百宝妆匣"), ("en_us.json", "Trinket Box")):
        path = os.path.join(ASSETS, "lang", filename)
        data = read(path)
        data["item.dynasty.trinket_box"] = name
        write(path, data)
    print("百宝妆匣：贴图 / 模型 / 配方 / 词条已就位（右键开出一件随机饰品）")


if __name__ == "__main__":
    main()
