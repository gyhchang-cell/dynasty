"""世界生成自检（每次导出自动跑）。

为什么要有这个：地府崩溃过一次 —— 改地表规则时把 `noise_threshold` 里的
**噪声 id** `minecraft:netherrack` 也一起替换掉了（那是个 worldgen/noise，不是方块），
结果生成区块时抛 `Missing element ... /noise / minecraft:blackstone`，一进地府就崩。
这个脚本专查这类「引用了不存在的 id」：

  1. `"noise": "..."` 必须是真实存在的噪声（ALLOWED_NOISE = 我们用到的原版噪声白名单）
  2. 维度 / 噪声配置 / 生物群系 / 特征 / 结构 / 结构集 的交叉引用都要真实存在
  3. 生物群系 features 列表里 `dynasty:*` 必须能在 placed_feature 里找到

运行：python3 tools/art/verify_worldgen.py
"""
import glob
import json
import os
import re
import sys
from test_patrol_spawns import validate_patrol_spawns

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
WORLDGEN = os.path.join(DATA, "worldgen")

# 我们用到的原版噪声 id（是 worldgen/noise 注册表里的东西，不是方块！）
ALLOWED_NOISE = {
    "minecraft:temperature", "minecraft:vegetation", "minecraft:continents",
    "minecraft:erosion", "minecraft:depth", "minecraft:weirdness", "minecraft:ridge",
    "minecraft:jagged", "minecraft:surface", "minecraft:surface_secondary",
    "minecraft:cave_entrance", "minecraft:cave_cheese", "minecraft:cave_layer",
    "minecraft:cave", "minecraft:spaghetti_2d", "minecraft:spaghetti_2d_elevation",
    "minecraft:spaghetti_3d", "minecraft:spaghetti_3d_2", "minecraft:spaghetti_3d_rarity",
    "minecraft:spaghetti_3d_thickness", "minecraft:spaghetti_3d_2_rarity",
    "minecraft:spaghetti_3d_2_thickness", "minecraft:noodle", "minecraft:pillar",
    "minecraft:pillar_rareness", "minecraft:pillar_thickness", "minecraft:patch",
    "minecraft:nether_state_selector", "minecraft:nether_wart", "minecraft:soul_sand_layer",
    "minecraft:gravel_layer", "minecraft:netherrack", "minecraft:ice",
    "minecraft:geode_layer", "minecraft:calcite", "minecraft:powder_snow",
    "minecraft:glacier", "minecraft:swamp", "minecraft:clay_bands", "minecraft:river",
    "minecraft:forest", "minecraft:flower", "minecraft:sapling", "minecraft:clay",
    "minecraft:gravel", "minecraft:sandstone", "minecraft:snowy", "minecraft:surface_swamp",
    "minecraft:jungle", "minecraft:bamboo", "minecraft:ocean_floor",
    "minecraft:ocean_floor_deep", "minecraft:sloped_cheese", "minecraft:ore_veininess",
    "minecraft:ore_vein_a", "minecraft:ore_vein_b", "minecraft:ore_gap", "minecraft:badlands",
    # 含水层 / 浮冰相关的噪声（celestial / jiuxiao / dragon_palace 的噪声配置用到）
    "minecraft:aquifer_barrier", "minecraft:aquifer_fluid_level_floodedness",
    "minecraft:aquifer_fluid_level_spread", "minecraft:aquifer_lava", "minecraft:packed_ice",
}

problems = []


def rel(path):
    return os.path.relpath(path, ROOT)


def load_all(folder):
    out = {}
    for path in glob.glob(os.path.join(folder, "*.json")):
        try:
            out[os.path.basename(path)[:-5]] = json.load(open(path, encoding="utf-8"))
        except Exception as error:                       # JSON 都坏了，肯定要报
            problems.append("%s 不是合法 JSON：%s" % (rel(path), error))
    return out


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def main():
    problems.extend(validate_patrol_spawns())
    dimension_types = load_all(os.path.join(DATA, "dimension_type"))
    dimensions = load_all(os.path.join(DATA, "dimension"))
    noises = load_all(os.path.join(WORLDGEN, "noise_settings"))
    biomes = load_all(os.path.join(WORLDGEN, "biome"))
    configured = load_all(os.path.join(WORLDGEN, "configured_feature"))
    placed = load_all(os.path.join(WORLDGEN, "placed_feature"))
    structures = load_all(os.path.join(WORLDGEN, "structure"))
    structure_sets = load_all(os.path.join(WORLDGEN, "structure_set"))

    if not dimension_types or not noises or not biomes:
        problems.append("维度 / 噪声 / 生物群系 文件缺失")

    # ---- 1) 噪声 id：所有世界生成文件里出现的 "noise" 都必须是真噪声 ----
    checked_noise = 0
    for folder in ("dimension_type", "worldgen", "dimension"):
        for path in glob.glob(os.path.join(DATA, folder, "**", "*.json"), recursive=True):
            try:
                data = json.load(open(path, encoding="utf-8"))
            except Exception:
                continue
            for node in walk(data):
                value = node.get("noise")
                if isinstance(value, str):
                    checked_noise += 1
                    if value not in ALLOWED_NOISE:
                        problems.append("%s：噪音 id %s 不存在（生成区块时会直接崩）"
                                        % (rel(path), value))

    # ---- 2) 维度引用：type / settings / biome ----
    for name, data in dimensions.items():
        kind = data.get("type", "")
        settings = data.get("generator", {}).get("settings")
        if kind.startswith("dynasty:") and kind.split(":")[1] not in dimension_types:
            problems.append("dimension/%s.json：dimension_type %s 不存在" % (name, kind))
        if isinstance(settings, str) and settings.startswith("dynasty:"):
            if settings.split(":")[1] not in noises:
                problems.append("dimension/%s.json：noise_settings %s 不存在" % (name, settings))
        source = data.get("generator", {}).get("biome_source", {})
        for entry in source.get("biomes", []):
            biome = entry.get("biome", "")
            if biome.startswith("dynasty:") and biome.split(":")[1] not in biomes:
                problems.append("dimension/%s.json：生物群系 %s 不存在" % (name, biome))

    # ---- 3) 生物群系 features：dynasty:* 必须在 placed_feature 里 ----
    for name, data in biomes.items():
        for step in data.get("features", []):
            for feature in step:
                if feature.startswith("dynasty:") and feature.split(":")[1] not in placed:
                    problems.append("biome/%s.json：placed_feature %s 不存在" % (name, feature))

    # ---- 4) placed_feature -> configured_feature ----
    for name, data in placed.items():
        feature = data.get("feature", "")
        if feature.startswith("dynasty:") and feature.split(":")[1] not in configured:
            problems.append("placed_feature/%s.json：configured_feature %s 不存在"
                            % (name, feature))

    # ---- 5) 结构集 -> 结构 ----
    for name, data in structure_sets.items():
        for entry in data.get("structures", []):
            ref = entry.get("structure", "")
            if ref.startswith("dynasty:") and ref.split(":")[1] not in structures:
                problems.append("structure_set/%s.json：结构 %s 不存在" % (name, ref))

    # ---- 6) 地表规则里的 biome_is 引用 ----
    for name, data in noises.items():
        text = json.dumps(data, ensure_ascii=False)
        for group in re.findall(r'"biome_is":\s*\[([^\]]*)\]', text):
            for biome in re.findall(r'"(dynasty:[a-z_]+)"', group):
                if biome.split(":")[1] not in biomes:
                    problems.append("noise_settings/%s.json：地表规则引用了不存在的生物群系 %s"
                                    % (name, biome))

    print("世界生成自检：维度 %d / 噪声配置 %d / 生物群系 %d / 特征 %d / 结构 %d，"
          "噪声 id %d 处"
          % (len(dimensions), len(noises), len(biomes), len(configured) + len(placed),
             len(structures), checked_noise))
    if problems:
        print("世界生成自检：发现问题 ❌")
        for problem in problems[:20]:
            print("   -", problem)
        sys.exit(1)
    print("世界生成自检：通过 ✅（没有引用不存在的噪声 / 生物群系 / 特征 / 结构）")


if __name__ == "__main__":
    main()
