"""新增内容（1.4.0 第十一轮）：九霄天界维度 + 九霄传送门 + 天将令 + 3 种新建筑 + 成就。

运行：python3 tools/art/gen_jiuxiao.py
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


def clone_dimension():
    # 维度类型：天空更亮、时间固定在正午 / dimension type
    dtype = read(os.path.join(DATA, "dimension_type/celestial_dynasty.json"))
    dtype["ambient_light"] = 0.35
    dtype["fixed_time"] = 6000
    write(os.path.join(DATA, "dimension_type/jiuxiao.json"), dtype)

    # 维度：换成九霄的噪声设置与群系 / dimension
    dim = read(os.path.join(DATA, "dimension/celestial_dynasty.json"))
    dim["type"] = "dynasty:jiuxiao"
    dim["generator"]["settings"] = "dynasty:jiuxiao"
    dim["generator"]["biome_source"]["biomes"] = [
        {"biome": "dynasty:jiuxiao_cloud_sea",
         "parameters": {"temperature": 0.0, "humidity": 0.0, "continentalness": -1.0,
                        "erosion": 0.0, "depth": [-1.0, 1.0], "weirdness": 0.0, "offset": 0.0}},
        {"biome": "dynasty:jiuxiao_skyland",
         "parameters": {"temperature": 0.0, "humidity": 0.0, "continentalness": 0.2,
                        "erosion": 0.2, "depth": [0.0, 1.0], "weirdness": 0.0, "offset": 0.0}},
        {"biome": "dynasty:jiuxiao_skyland",
         "parameters": {"temperature": 0.0, "humidity": 0.0, "continentalness": 1.0,
                        "erosion": 0.5, "depth": [0.0, 1.0], "weirdness": 1.0, "offset": 0.0}}
    ]
    write(os.path.join(DATA, "dimension/jiuxiao.json"), dim)

    # 噪声设置：地形换成汉白玉（云上浮岛质感）/ noise settings
    noise = read(os.path.join(DATA, "worldgen/noise_settings/celestial_dynasty.json"))
    noise["default_block"] = {"Name": "dynasty:marble_block"}
    noise["default_fluid"] = {"Name": "minecraft:water", "Properties": {"level": "0"}}
    write(os.path.join(DATA, "worldgen/noise_settings/jiuxiao.json"), noise)


def clone_biomes():
    skyland = read(os.path.join(DATA, "worldgen/biome/celestial_plains.json"))
    skyland["effects"]["sky_color"] = 8445439
    skyland["effects"]["fog_color"] = 12438783
    skyland["effects"]["water_color"] = 4159204
    skyland["effects"]["grass_color"] = 12282200
    skyland["effects"]["foliage_color"] = 10262422
    skyland["temperature"] = 0.7
    skyland["downfall"] = 0.2
    # 建筑：九霄宝塔 / 云台 / 演武场 / just-in-case 前一批建筑
    for features in skyland.get("features", []):
        if isinstance(features, list) and "dynasty:temple" in features:
            features.extend(["dynasty:sky_pagoda", "dynasty:cloud_platform", "dynasty:sky_dojo"])
    write(os.path.join(DATA, "worldgen/biome/jiuxiao_skyland.json"), skyland)

    sea = read(os.path.join(DATA, "worldgen/biome/celestial_sea.json"))
    sea["effects"]["sky_color"] = 8445439
    sea["effects"]["fog_color"] = 12438783
    write(os.path.join(DATA, "worldgen/biome/jiuxiao_cloud_sea.json"), sea)

    write(os.path.join(DATA, "tags/worldgen/biome/jiuxiao.json"), {
        "replace": False,
        "values": ["dynasty:jiuxiao_skyland", "dynasty:jiuxiao_cloud_sea"],
    })


def buildings():
    names = {
        "sky_pagoda": 300,      # 九霄宝塔
        "cloud_platform": 240,  # 云台
        "sky_dojo": 320,        # 演武场
    }
    for name, chance in names.items():
        write(os.path.join(DATA, "worldgen/configured_feature/%s.json" % name),
              {"type": "dynasty:%s" % name, "config": {}})
        write(os.path.join(DATA, "worldgen/placed_feature/%s.json" % name),
              {"feature": "dynasty:%s" % name,
               "placement": [
                   {"type": "minecraft:rarity_filter", "chance": chance},
                   {"type": "minecraft:in_square"},
                   {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"},
                   {"type": "minecraft:biome"}]})
        write(os.path.join(DATA, "forge/biome_modifier/building_%s.json" % name),
              {"type": "forge:add_features", "biomes": "#dynasty:jiuxiao",
               "features": "dynasty:%s" % name, "step": "surface_structures"})
    # 云台也放到天朝 / cloud platforms also appear in the celestial realm
    write(os.path.join(DATA, "forge/biome_modifier/building_cloud_platform_celestial.json"),
          {"type": "forge:add_features", "biomes": "#dynasty:celestial",
           "features": "dynasty:cloud_platform", "step": "surface_structures"})


def portal_assets():
    # 九霄传送门：复用天朝传送门的贴图风格 / cloud gate block
    write(os.path.join(ASSETS, "blockstates/cloud_portal.json"),
          {"variants": {"": {"model": "dynasty:block/cloud_portal"}}})
    write(os.path.join(ASSETS, "models/block/cloud_portal.json"),
          {"parent": "block/cube_all", "textures": {"all": "dynasty:block/cloud_portal"}})
    write(os.path.join(ASSETS, "models/item/cloud_portal.json"),
          {"parent": "dynasty:block/cloud_portal"})
    src_png = os.path.join(ASSETS, "textures/block/jade_portal.png")
    dst_png = os.path.join(ASSETS, "textures/block/cloud_portal.png")
    if os.path.exists(src_png) and not os.path.exists(dst_png):
        shutil.copyfile(src_png, dst_png)
        print("texture copied:", os.path.relpath(dst_png, ROOT))

    # 天将令 / sky token
    src = os.path.join(ASSETS, "textures/item/eunuch_token.png")
    dst = os.path.join(ASSETS, "textures/item/sky_token.png")
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copyfile(src, dst)
        print("texture copied:", os.path.relpath(dst, ROOT))
    write(os.path.join(ASSETS, "models/item/sky_token.json"),
          {"parent": "minecraft:item/generated",
           "textures": {"layer0": "dynasty:item/sky_token"}})
    write(os.path.join(DATA, "recipes/cloud_portal.json"),
          {"type": "minecraft:crafting_shapeless",
           "ingredients": [{"item": "dynasty:jade_block"}, {"item": "dynasty:jade_block"},
                           {"item": "dynasty:jade_block"}, {"item": "dynasty:jade_block"},
                           {"item": "dynasty:dragon_crystal"}, {"item": "dynasty:phoenix_feather"}],
           "result": {"item": "dynasty:cloud_portal"}})


def advancements():
    for name, icon in (("entered_jiuxiao", "dynasty:cloud_portal"),
                       ("slay_sky_general", "dynasty:sky_token")):
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


def lang():
    zh = {
        "item.dynasty.sky_token": "天将令",
        "item.dynasty.nine_heaven_general_spawn_egg": "九霄天将刷怪蛋",
        "block.dynasty.cloud_portal": "九霄传送门",
        "entity.dynasty.nine_heaven_general": "九霄天将",
        "advancements.dynasty.entered_jiuxiao.title": "登临九霄",
        "advancements.dynasty.entered_jiuxiao.description": "穿过九霄传送门进入九霄天界",
        "advancements.dynasty.slay_sky_general.title": "天将伏诛",
        "advancements.dynasty.slay_sky_general.description": "击败九霄天将",
    }
    en = {
        "item.dynasty.sky_token": "Sky Token",
        "item.dynasty.nine_heaven_general_spawn_egg": "Nine-Heaven General Spawn Egg",
        "block.dynasty.cloud_portal": "Cloud Gate",
        "entity.dynasty.nine_heaven_general": "Nine-Heaven General",
        "advancements.dynasty.entered_jiuxiao.title": "Reach the Nine Heavens",
        "advancements.dynasty.entered_jiuxiao.description": "Enter the nine-heaven realm",
        "advancements.dynasty.slay_sky_general.title": "Sky General Slain",
        "advancements.dynasty.slay_sky_general.description": "Defeat the Nine-Heaven General",
    }
    for filename, extra in (("zh_cn.json", zh), ("en_us.json", en)):
        path = os.path.join(ASSETS, "lang", filename)
        data = read(path)
        data.update(extra)
        write(path, data)


def main():
    clone_dimension()
    clone_biomes()
    buildings()
    portal_assets()
    advancements()
    lang()
    print("九霄天界内容生成完成")


if __name__ == "__main__":
    main()

