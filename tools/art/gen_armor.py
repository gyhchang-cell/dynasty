"""新增护甲（1.4.0 第十七轮）：鲛绡甲 + 玄铁重铠（各 4 件）。

* 鲛绡甲：龙鳞套同部位 + 龙鳞×2 + 丝绸×2 → 水战轻甲（减伤 26%/件、生命 +420）
* 玄铁重铠：鲛绡套同部位 + 精钢×3 + 玄天玉 → 护甲最高的终盘重甲（减伤 30%/件、生命 +500）

顺带把中英名字与贴图、模型、配方一次生成。

运行：python3 tools/art/gen_armor.py
"""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")

PIECES = ("helmet", "chestplate", "leggings", "boots")
PIECE_ZH = {"helmet": "头盔", "chestplate": "胸甲", "leggings": "护腿", "boots": "靴子"}
PIECE_EN = {"helmet": "Helmet", "chestplate": "Chestplate", "leggings": "Leggings", "boots": "Boots"}

# 套装 id: (中文套名, 英文套名, 贴图来源套, 上一套, 升级材料)
SETS = {
    "sea_silk": ("鲛绡甲", "Sea Silk", "dragon_scale", "dragon_scale",
                 ["dynasty:dragon_scale", "dynasty:dragon_scale",
                  "dynasty:silk", "dynasty:silk"]),
    "dark_iron": ("玄铁重铠", "Dark Iron", "xuantian", "sea_silk",
                  ["dynasty:refined_steel", "dynasty:refined_steel",
                   "dynasty:refined_steel", "dynasty:xuantian_jade"]),
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    for set_id, (zh, en, texture_from, prev, materials) in SETS.items():
        for piece in PIECES:
            name = "%s_%s" % (set_id, piece)
            # 贴图：复用上一套的样式 / reuse the previous set's texture
            src_png = os.path.join(ASSETS, "textures/item/%s_%s.png" % (texture_from, piece))
            dst_png = os.path.join(ASSETS, "textures/item/%s.png" % name)
            if os.path.exists(src_png) and not os.path.exists(dst_png):
                shutil.copyfile(src_png, dst_png)
            write(os.path.join(ASSETS, "models/item/%s.json" % name),
                  {"parent": "minecraft:item/generated",
                   "textures": {"layer0": "dynasty:item/%s" % name}})
            # 配方：上一套同部位 + 材料 → 这一套同部位
            write(os.path.join(DATA, "recipes/%s.json" % name),
                  {"type": "minecraft:crafting_shapeless",
                   "ingredients": [{"item": "dynasty:%s_%s" % (prev, piece)}]
                                  + [{"item": item} for item in materials],
                   "result": {"item": "dynasty:%s" % name}})
        print("set:", set_id, len(PIECES), "件")

    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = read(path)
        for set_id, values in SETS.items():
            for piece in PIECES:
                name = "%s_%s" % (set_id, piece)
                data["item.dynasty.%s" % name] = (values[0] + "·" + PIECE_ZH[piece]
                                                  if index == 0 else
                                                  "%s %s" % (values[1], PIECE_EN[piece]))
        write(path, data)
    print("护甲生成完成")


if __name__ == "__main__":
    main()
