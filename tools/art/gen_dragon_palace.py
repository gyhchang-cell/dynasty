"""新增内容（1.4.0 第十五轮）：东海龙宫维度 + 龙宫传送门 + 龙王信物/三叉戟/饰品 + 成就 + 配方。

运行：python3 tools/art/gen_dragon_palace.py
"""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("written:", os.path.relpath(path, ROOT))


def dimension():
    # 维度类型：海底宫阙，光线偏暗 / underwater palace
    dtype = read(os.path.join(DATA, "dimension_type/jiuxiao.json"))
    dtype["ambient_light"] = 0.18
    dtype["fixed_time"] = 18000
    dtype["has_skylight"] = False
    write(os.path.join(DATA, "dimension_type/dragon_palace.json"), dtype)

    dim = read(os.path.join(DATA, "dimension/jiuxiao.json"))
    dim["type"] = "dynasty:dragon_palace"
    dim["generator"]["settings"] = "dynasty:dragon_palace"
    dim["generator"]["biome_source"]["biomes"] = [
        {"biome": "dynasty:dragon_palace_deep",
         "parameters": {"temperature": 0.0, "humidity": 0.0, "continentalness": -1.0,
                        "erosion": 0.0, "depth": [-1.0, 1.0], "weirdness": 0.0, "offset": 0.0}},
        {"biome": "dynasty:dragon_palace_hall",
         "parameters": {"temperature": 0.0, "humidity": 0.0, "continentalness": 0.2,
                        "erosion": 0.2, "depth": [0.0, 1.0], "weirdness": 0.0, "offset": 0.0}},
        {"biome": "dynasty:dragon_palace_hall",
         "parameters": {"temperature": 0.0, "humidity": 0.0, "continentalness": 1.0,
                        "erosion": 0.5, "depth": [0.0, 1.0], "weirdness": 1.0, "offset": 0.0}}
    ]
    write(os.path.join(DATA, "dimension/dragon_palace.json"), dim)

    # 噪声：地表铺水，殿基是汉白玉 / watery palace floor
    noise = read(os.path.join(DATA, "worldgen/noise_settings/jiuxiao.json"))
    noise["default_fluid"] = {"Name": "minecraft:water", "Properties": {"level": "0"}}
    noise["aquifers_enabled"] = True
    write(os.path.join(DATA, "worldgen/noise_settings/dragon_palace.json"), noise)


def biomes():
    hall = read(os.path.join(DATA, "worldgen/biome/jiuxiao_skyland.json"))
    hall["effects"]["sky_color"] = 2581968
    hall["effects"]["fog_color"] = 2580898
    hall["effects"]["water_color"] = 2640002
    hall["effects"]["water_fog_color"] = 1322882
    hall["effects"]["grass_color"] = 4097173
    hall["effects"]["foliage_color"] = 3248741
    hall["temperature"] = 0.5
    write(os.path.join(DATA, "worldgen/biome/dragon_palace_hall.json"), hall)

    deep = read(os.path.join(DATA, "worldgen/biome/jiuxiao_cloud_sea.json"))
    deep["effects"]["sky_color"] = 1296528
    deep["effects"]["fog_color"] = 648064
    deep["effects"]["water_color"] = 1320002
    write(os.path.join(DATA, "worldgen/biome/dragon_palace_deep.json"), deep)

    write(os.path.join(DATA, "tags/worldgen/biome/dragon_palace.json"), {
        "replace": False,
        "values": ["dynasty:dragon_palace_hall", "dynasty:dragon_palace_deep"],
    })
    # 龙宫里也有建筑可逛（复用已有建筑）/ reuse existing buildings inside the palace
    for name in ("temple", "ritual_circle", "cloud_platform"):
        write(os.path.join(DATA, "forge/biome_modifier/building_%s_palace.json" % name),
              {"type": "forge:add_features", "biomes": "#dynasty:dragon_palace",
               "features": "dynasty:%s" % name, "step": "surface_structures"})


def portal_and_items():
    for name, src in (("dragon_gate", "jade_portal"), ("sea_token", "eunuch_token"),
                      ("sea_trident", "halberd_fangtian"), ("sea_pearl", "jade_pendant"),
                      ("dragon_bone_ring", "iron_waist_token")):
        src_dir = "block" if name == "dragon_gate" else "item"
        src_png = os.path.join(ASSETS, "textures/%s/%s.png" % (src_dir, src))
        dst_png = os.path.join(ASSETS, "textures/%s/%s.png" % (src_dir, name))
        if os.path.exists(src_png) and not os.path.exists(dst_png):
            shutil.copyfile(src_png, dst_png)
            print("texture copied:", os.path.relpath(dst_png, ROOT))
        if name != "dragon_gate":
            write(os.path.join(ASSETS, "models/item/%s.json" % name),
                  {"parent": "minecraft:item/handheld" if name == "sea_trident"
                   else "minecraft:item/generated",
                   "textures": {"layer0": "dynasty:%s/%s" % (src_dir, name)}})

    write(os.path.join(ASSETS, "blockstates/dragon_gate.json"),
          {"variants": {"": {"model": "dynasty:block/dragon_gate"}}})
    write(os.path.join(ASSETS, "models/block/dragon_gate.json"),
          {"parent": "block/cube_all", "textures": {"all": "dynasty:block/dragon_gate"}})
    write(os.path.join(ASSETS, "models/item/dragon_gate.json"),
          {"parent": "dynasty:block/dragon_gate"})

    write(os.path.join(DATA, "recipes/dragon_gate.json"),
          {"type": "minecraft:crafting_shapeless",
           "ingredients": [{"item": "dynasty:jade_block"}, {"item": "dynasty:jade_block"},
                           {"item": "dynasty:jade_block"}, {"item": "dynasty:jade_block"},
                           {"item": "dynasty:dragon_crystal"}, {"item": "dynasty:dragon_scale"},
                           {"item": "dynasty:dragon_scale"}],
           "result": {"item": "dynasty:dragon_gate"}})
    # 分水三叉戟：龙晶剑 + 龙宫玉印 + 龙鳞×2
    write(os.path.join(DATA, "recipes/sea_trident.json"),
          {"type": "minecraft:crafting_shapeless",
           "ingredients": [{"item": "dynasty:sword_dragon_crystal"}, {"item": "dynasty:sea_token"},
                           {"item": "dynasty:dragon_scale"}, {"item": "dynasty:dragon_scale"}],
           "result": {"item": "dynasty:sea_trident"}})


def advancements_and_lang():
    for name, icon in (("entered_dragon_palace", "dynasty:dragon_gate"),
                       ("slay_dragon_king", "dynasty:sea_token")):
        write(os.path.join(DATA, "advancements/%s.json" % name), {
            "display": {
                "icon": {"item": icon},
                "title": {"translate": "advancements.dynasty.%s.title" % name},
                "description": {"translate": "advancements.dynasty.%s.description" % name},
                "frame": "task", "show_toast": True, "announce_to_chat": False, "hidden": False,
            },
            "criteria": {"code": {"trigger": "minecraft:impossible"}},
            "requirements": [["code"]],
            "parent": "dynasty:dynasty_root",
        })

    zh = {
        "item.dynasty.sea_token": "龙宫玉印",
        "item.dynasty.sea_trident": "分水三叉戟",
        "item.dynasty.sea_pearl": "避水珠",
        "item.dynasty.dragon_bone_ring": "龙骨戒",
        "item.dynasty.dragon_king_spawn_egg": "东海龙王刷怪蛋",
        "block.dynasty.dragon_gate": "龙宫传送门",
        "entity.dynasty.dragon_king": "东海龙王",
        "advancements.dynasty.entered_dragon_palace.title": "深入龙宫",
        "advancements.dynasty.entered_dragon_palace.description": "穿过龙宫传送门进入东海龙宫",
        "advancements.dynasty.slay_dragon_king.title": "沧海定波",
        "advancements.dynasty.slay_dragon_king.description": "击败东海龙王",
    }
    en = {
        "item.dynasty.sea_token": "Dragon Palace Seal",
        "item.dynasty.sea_trident": "Sea-Parting Trident",
        "item.dynasty.sea_pearl": "Water-Repelling Pearl",
        "item.dynasty.dragon_bone_ring": "Dragon Bone Ring",
        "item.dynasty.dragon_king_spawn_egg": "Dragon King Spawn Egg",
        "block.dynasty.dragon_gate": "Dragon Gate",
        "entity.dynasty.dragon_king": "Dragon King of the East Sea",
        "advancements.dynasty.entered_dragon_palace.title": "Into the Dragon Palace",
        "advancements.dynasty.entered_dragon_palace.description": "Enter the dragon palace",
        "advancements.dynasty.slay_dragon_king.title": "Calm the Eastern Sea",
        "advancements.dynasty.slay_dragon_king.description": "Defeat the Dragon King",
    }
    for filename, extra in (("zh_cn.json", zh), ("en_us.json", en)):
        path = os.path.join(ASSETS, "lang", filename)
        data = read(path)
        data.update(extra)
        write(path, data)


def curios_tag():
    path = os.path.join(ROOT, "src/main/resources/data/curios/tags/items/dynasty_trinket.json")
    data = read(path)
    for item in ("dynasty:sea_pearl", "dynasty:dragon_bone_ring"):
        if item not in data["values"]:
            data["values"].append(item)
    write(path, data)


def main():
    dimension()
    biomes()
    portal_and_items()
    advancements_and_lang()
    curios_tag()
    print("东海龙宫内容生成完成")


if __name__ == "__main__":
    main()

