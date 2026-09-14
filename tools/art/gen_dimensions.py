"""维度重做（第二十二轮）：把「地府」做成真正的新维度，把「天朝」做成真的天上世界。

玩家反馈（第 2、3、8 条）：
  * 进天朝 / 地府都出生在基岩层 → 落点由 DynastyPortalBlock 找安全地面（代码侧）；
    这里把地府的「基岩顶棚 + 岩浆海」去掉，地形不再长得像原版地狱。
  * 「天堂和地狱都是原版的，我要新维度」→ 地府改成：无顶棚、无岩浆海、黑石地表、
    暗色星空（the_end 天象）、并且**刷新地狱的生物**（烈焰人 / 恶魂 / 岩浆怪 /
    僵尸猪灵 / 凋灵骷髅），这样把原版地狱门关掉也不会缺资源。
  * 「别把建筑生成在地狱基岩上层」→ 地府高度改成 min_y -64 / height 384，
    帝陵的 -50~-20 落点才是「埋在地下的陵墓」，而不是被夹在基岩层；
    同时在忘川 / 荒野里补上王朝遗迹建筑（它们用 WORLD_SURFACE 落点，会站在地面上）。
  * 「天堂太像原版」→ 天朝平原去掉原版的树 / 花 / 草 / 甘蔗 / 蘑菇 / 落雪，
    换成王朝的宫殿、牌坊、云台、祭坛、塔，并把环境光调亮成「天上」。

运行：python3 tools/art/gen_dimensions.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
DIM_DIR = os.path.join(DATA, "dimension")
TYPE_DIR = os.path.join(DATA, "dimension_type")
NOISE_DIR = os.path.join(DATA, "worldgen/noise_settings")
BIOME_DIR = os.path.join(DATA, "worldgen/biome")

# 地狱的生物：放进地府，关掉原版地狱门也不会缺烈焰棒 / 恶魂之泪 / 岩浆膏
NETHER_MOBS = ["minecraft:blaze", "minecraft:ghast", "minecraft:magma_cube",
               "minecraft:zombified_piglin", "minecraft:wither_skeleton"]

# 天朝 / 地府里要放的那些王朝建筑：**所有生物群系必须用同一套顺序**。
# 原版 FeatureSorter 只给「同一个生物群系里相邻的两个特征」连边，然后全局拓扑排序；
# 如果两个生物群系里同一对特征的先后不一样，就会 `Feature order cycle found` → 生成区块崩。
# 所以这里定义一份规范顺序，所有群系的 stage 4 都按它来。
BULIDING_ORDER = ["dynasty:cloud_platform", "dynasty:heaven_altar", "dynasty:pagoda",
                  "dynasty:paifang", "dynasty:watchtower", "dynasty:temple",
                  "dynasty:ritual_circle", "dynasty:great_wall", "dynasty:post_station",
                  "dynasty:palace_ruin"]
HEAVEN_BUILDINGS = [b for b in BULIDING_ORDER if b != "dynasty:palace_ruin"]
HEAVEN_DROP = ["minecraft:trees_plains", "minecraft:flower_plains",
               "minecraft:patch_grass_plain", "minecraft:patch_sugar_cane",
               "minecraft:brown_mushroom_normal", "minecraft:freeze_top_layer",
               "minecraft:monster_room"]

# 地府：地上的遗迹（帝陵在 feature 里，用 height_range 落在地下）
UNDERWORLD_BUILDINGS = ["dynasty:palace_ruin", "dynasty:watchtower", "dynasty:paifang"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def set_step(biome, index, values):
    biome["features"][index] = values


def place_buildings(biome, wanted):
    """把王朝建筑放进 stage 4，并且**所有生物群系用同一份顺序**（否则特征顺序成环）。

    Put the dynasty buildings into stage 4 using one canonical order across all biomes.
    """
    step = biome["features"][4]
    kept = [f for f in step if f not in BULIDING_ORDER]
    ordered = [f for f in BULIDING_ORDER if f in wanted]
    biome["features"][4] = kept + ordered


def add_spawners(biome, mobs):
    monster = biome.setdefault("spawners", {}).setdefault("monster", [])
    have = {entry["type"] for entry in monster}
    for mob in mobs:
        if mob not in have:
            monster.append({"type": mob, "weight": 10, "minCount": 1, "maxCount": 2})


def clone_biome_surface_rule(sequence, src_biome, dst_biome, swaps=()):
    """把某条「按生物群系」的地表规则原样复制，换成我们的生物群系（保证格式一定合法）。

    Clone an existing per-biome surface rule (guaranteed valid) for our own biome.
    """
    for element in sequence:
        if src_biome not in json.dumps(element):
            continue
        text = json.dumps(element, ensure_ascii=False).replace(src_biome, dst_biome)
        for old, new in swaps:
            text = text.replace(old, new)
        return json.loads(text)
    return None


def swap_surface_block(node, old, new):
    """只改 result_state 里的方块名，**绝不**碰 noise 名字等其他字符串。

    踩过的坑：直接对整个 JSON 做字符串替换，会把 noise_threshold 的
    `"noise": "minecraft:netherrack"`（那是个 worldgen/noise，不是方块）也改掉，
    于是生成区块时抛 `Missing element ... /noise / minecraft:blackstone` → 进地府直接崩。
    Only rewrite block state names; never touch noise ids or other strings.
    """
    if isinstance(node, dict):
        state = node.get("result_state")
        if isinstance(state, dict) and state.get("Name") == old:
            state["Name"] = new
        for value in node.values():
            swap_surface_block(value, old, new)
    elif isinstance(node, list):
        for value in node:
            swap_surface_block(value, old, new)


def underworld():
    """地府：不是原版地狱 / the underworld is a realm of its own"""
    type_path = os.path.join(TYPE_DIR, "underworld.json")
    kind = load(type_path)
    kind.update({
        "min_y": -64,                 # 和 NoiseSettings 对齐：帝陵的 -50~-20 才是地下
        "height": 384,
        "has_ceiling": False,         # 去掉基岩顶棚
        "has_skylight": False,        # 没有日光
        "ambient_light": 0.08,
        "effects": "minecraft:the_end",   # 暗色星空，而不是地狱的红雾
        "natural": False,
        "ultrawarm": False,
        "bed_works": False,
        "respawn_anchor_works": False,
        "piglin_safe": True,
        "monster_spawn_light_level": 0,
        "monster_spawn_block_light_limit": 0,
    })
    save(type_path, kind)

    noise_path = os.path.join(NOISE_DIR, "underworld.json")
    noise = load(noise_path)
    noise["noise"]["min_y"] = -64
    noise["noise"]["height"] = 384
    noise["sea_level"] = -64          # 干掉「一望无际的岩浆海」
    noise["aquifers_enabled"] = False
    sequence = noise["surface_rule"]["sequence"]
    # ① 删掉「基岩顶棚」那条规则
    sequence = [el for el in sequence if "bedrock_roof" not in json.dumps(el)]
    # ② 地表默认块 netherrack → blackstone（和下界岩区分开；只动方块名）
    swap_surface_block(sequence, "minecraft:netherrack", "minecraft:blackstone")
    # ③ 忘川：地表铺灵魂土（复制 vanilla 的灵魂沙谷规则，格式一定合法）
    #    先去掉上次生成的同名规则，保证脚本可以重复运行 / idempotent
    sequence = [el for el in sequence if "dynasty:soul_river" not in json.dumps(el)]
    soul = clone_biome_surface_rule(sequence, "minecraft:soul_sand_valley",
                                    "dynasty:soul_river",
                                    (('"minecraft:soul_sand"', '"minecraft:soul_soil"'),))
    if soul is not None:
        sequence = [sequence[0], soul] + sequence[1:]
    noise["surface_rule"]["sequence"] = sequence
    save(noise_path, noise)

    # 生物群系：加地狱生物 + 地上遗迹
    for name in ("underworld_wastes", "soul_river"):
        path = os.path.join(BIOME_DIR, name + ".json")
        biome = load(path)
        add_spawners(biome, NETHER_MOBS)
        place_buildings(biome, UNDERWORLD_BUILDINGS)
        save(path, biome)


def celestial():
    """天朝：从「原版平原」变成「天上宫阙」 / the celestial realm gets its palaces"""
    type_path = os.path.join(TYPE_DIR, "celestial_dynasty.json")
    kind = load(type_path)
    kind["ambient_light"] = 0.55          # 天光大亮，没有黑夜
    kind["has_skylight"] = True
    kind["effects"] = "minecraft:overworld"
    save(type_path, kind)

    for name in ("celestial_plains", "jade_forest"):
        path = os.path.join(BIOME_DIR, name + ".json")
        biome = load(path)
        for index in (4, 7, 9, 10):
            kept = [f for f in biome["features"][index] if f not in HEAVEN_DROP]
            set_step(biome, index, kept)
        place_buildings(biome, HEAVEN_BUILDINGS + ["dynasty:palace_ruin"])
        save(path, biome)


def main():
    underworld()
    celestial()
    for path in (os.path.join(TYPE_DIR, "underworld.json"),
                 os.path.join(TYPE_DIR, "celestial_dynasty.json"),
                 os.path.join(NOISE_DIR, "underworld.json")):
        print("ok:", os.path.relpath(path, ROOT))
    for name in ("underworld_wastes", "soul_river", "celestial_plains", "jade_forest"):
        biome = load(os.path.join(BIOME_DIR, name + ".json"))
        monsters = [e["type"] for e in biome["spawners"]["monster"]]
        print("biome %-18s 怪物: %s" % (name, ", ".join(monsters)))
        print("      地表建筑: %s" % ", ".join(biome["features"][4]))


if __name__ == "__main__":
    main()
