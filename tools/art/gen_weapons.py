"""扩展兵器（1.4.0 第十六轮）：10 把新武器的模型/贴图/语言/配方 + 宝箱掉落。

获取方式刻意做成多种：
  * 合成：斩马刀（环首刀 + 精钢）、屠龙刀（龙晶剑 + 龙宫玉印 + 龙帝玉玺）
  * Boss 掉落：青釭剑（宦官首脑）、倚天剑（叛将）、龙胆亮银枪（亡故始皇）、鱼肠剑（刺客稀有）
  * 条件获得：御赐金锏（官阶≥尚书）、尚方宝剑（官阶≥丞相）、七星宝刀（击败 5 种 Boss）、
              射日弓（白天击败凤凰）
  * 宝箱：斩马刀 / 鱼肠剑 / 青釭剑 会从宫殿与帝陵宝箱里开出来

运行：python3 tools/art/gen_weapons.py
"""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")

# id: (中文名, 英文名, 复用哪张现成贴图)
WEAPONS = {
    "zhanma_dao": ("斩马刀", "Horse-Cleaver", "huan_shou_dao"),
    "yuchang_dagger": ("鱼肠剑", "Yuchang Dagger", "tong_dao"),
    "qinggang_sword": ("青釭剑", "Qinggang Sword", "sword_jade"),
    "gilded_mace": ("御赐金锏", "Gilded Mace", "pojun_axe"),
    "yitian_sword": ("倚天剑", "Yitian Sword", "sword_silver"),
    "dragon_spear": ("龙胆亮银枪", "Dragon Spear", "chang_qiang"),
    "sunbow": ("射日弓", "Sunbow", "dragon_bow"),
    "seven_star_saber": ("七星宝刀", "Seven-Star Saber", "juque_sword"),
    "dragon_slayer": ("屠龙刀", "Dragon Slayer", "sword_dragon_crystal"),
    "supreme_sword": ("尚方宝剑", "Imperial Sword", "tianzi_sword"),
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def assets():
    for name, (zh, en, src) in WEAPONS.items():
        src_png = os.path.join(ASSETS, "textures/item/%s.png" % src)
        dst_png = os.path.join(ASSETS, "textures/item/%s.png" % name)
        if os.path.exists(src_png) and not os.path.exists(dst_png):
            shutil.copyfile(src_png, dst_png)
        write(os.path.join(ASSETS, "models/item/%s.json" % name),
              {"parent": "minecraft:item/handheld",
               "textures": {"layer0": "dynasty:item/%s" % name}})
    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = read(path)
        for name, values in WEAPONS.items():
            data["item.dynasty.%s" % name] = values[index]
        write(path, data)
    print("models/lang:", len(WEAPONS), "把武器")


def recipes():
    # 斩马刀：环首刀 + 精钢×3（接在环首刀之后）
    write(os.path.join(DATA, "recipes/zhanma_dao.json"),
          {"type": "minecraft:crafting_shapeless",
           "ingredients": [{"item": "dynasty:huan_shou_dao"}, {"item": "dynasty:refined_steel"},
                           {"item": "dynasty:refined_steel"}, {"item": "dynasty:refined_steel"}],
           "result": {"item": "dynasty:zhanma_dao"}})
    # 屠龙刀：龙晶剑 + 龙宫玉印 + 龙帝玉玺
    write(os.path.join(DATA, "recipes/dragon_slayer.json"),
          {"type": "minecraft:crafting_shapeless",
           "ingredients": [{"item": "dynasty:sword_dragon_crystal"}, {"item": "dynasty:sea_token"},
                           {"item": "dynasty:dragon_emperor_seal"}],
           "result": {"item": "dynasty:dragon_slayer"}})
    print("recipes: zhanma_dao / dragon_slayer")


def chest_loot():
    """把几把新武器塞进宫殿 / 帝陵 / 王府宝箱（低权重）/ rare chest loot"""
    plan = {
        "temple": [("dynasty:zhanma_dao", 3), ("dynasty:yuchang_dagger", 2)],
        "imperial_tomb": [("dynasty:qinggang_sword", 2)],
        "dynasty_palace": [("dynasty:zhanma_dao", 3), ("dynasty:qinggang_sword", 1)],
    }
    for table, entries in plan.items():
        path = os.path.join(DATA, "loot_tables/chests/%s.json" % table)
        if not os.path.exists(path):
            continue
        data = read(path)
        pool = data["pools"][0]
        names = {e.get("name") for e in pool["entries"]}
        for item, weight in entries:
            if item not in names:
                pool["entries"].append({"type": "minecraft:item", "name": item, "weight": weight})
        write(path, data)
        print("chest loot:", table, len(entries), "件")


def main():
    assets()
    recipes()
    chest_loot()
    print("扩展兵器生成完成")


if __name__ == "__main__":
    main()
