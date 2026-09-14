"""把建筑从「生物群系修饰器」改回「静态特征表」：

原因：修饰器注入的特征在 biome JSON 里看不到，自检脚本查不出来，
天境/地狱/九霄 连续崩了三次 `Feature order cycle found`。
现在只有一个来源（静态 stage 4 列表），顺序由 BULIDING_ORDER 统一，自检能 100% 覆盖。
"""
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BIOME_DIR = os.path.join(ROOT, "src/main/resources/data/dynasty/worldgen/biome")
MOD_DIR = os.path.join(ROOT, "src/main/resources/data/dynasty/forge/biome_modifier")

# 所有王朝建筑的唯一顺序（每个群系只取自己那几座，但相对顺序都按这份来）
CANON = ["dynasty:cloud_platform", "dynasty:heaven_altar", "dynasty:pagoda", "dynasty:paifang",
         "dynasty:watchtower", "dynasty:temple", "dynasty:ritual_circle", "dynasty:great_wall",
         "dynasty:post_station", "dynasty:palace_ruin", "dynasty:hall", "dynasty:observatory",
         "dynasty:market", "dynasty:ghost_gate", "dynasty:judge_hall", "dynasty:bridge",
         "dynasty:sky_stair", "dynasty:thunder_pool", "dynasty:dragon_hall", "dynasty:pearl_tower"]

CELESTIAL = ["dynasty:cloud_platform", "dynasty:heaven_altar", "dynasty:pagoda", "dynasty:paifang",
             "dynasty:watchtower", "dynasty:temple", "dynasty:ritual_circle", "dynasty:great_wall",
             "dynasty:post_station", "dynasty:palace_ruin", "dynasty:hall", "dynasty:observatory",
             "dynasty:market", "dynasty:bridge", "dynasty:judge_hall", "dynasty:sky_stair"]
UNDERWORLD = ["dynasty:paifang", "dynasty:watchtower", "dynasty:pagoda", "dynasty:ritual_circle",
              "dynasty:palace_ruin", "dynasty:ghost_gate", "dynasty:judge_hall", "dynasty:bridge",
              "dynasty:great_wall", "dynasty:temple", "dynasty:post_station", "dynasty:market",
              "dynasty:hall", "dynasty:thunder_pool"]
JIUXIAO = ["dynasty:cloud_platform", "dynasty:sky_stair", "dynasty:thunder_pool",
           "dynasty:paifang", "dynasty:palace_ruin", "dynasty:sky_dojo", "dynasty:heaven_altar",
           "dynasty:temple", "dynasty:pagoda", "dynasty:watchtower", "dynasty:market",
           "dynasty:great_wall", "dynasty:observatory", "dynasty:post_station"]
PALACE = ["dynasty:palace_ruin", "dynasty:cloud_platform", "dynasty:dragon_hall",
          "dynasty:pearl_tower", "dynasty:ritual_circle", "dynasty:temple", "dynasty:watchtower",
          "dynasty:pagoda", "dynasty:market", "dynasty:bridge", "dynasty:post_station",
          "dynasty:great_wall", "dynasty:paifang"]

BIOME_BUILDINGS = {
    "celestial_plains": CELESTIAL, "jade_forest": CELESTIAL, "dragon_ridge": CELESTIAL,
    "celestial_sea": ["dynasty:palace_ruin"],
    "underworld_wastes": UNDERWORLD, "soul_river": UNDERWORLD,
    "jiuxiao_skyland": JIUXIAO, "jiuxiao_cloud_sea": ["dynasty:cloud_platform"],
    "dragon_palace_hall": PALACE, "dragon_palace_deep": ["dynasty:pearl_tower"],
}


def main():
    # 1) 删掉全部「加建筑」的修饰器（保留 spawn_* 那些刷怪修饰器）
    removed = 0
    for path in glob.glob(os.path.join(MOD_DIR, "building_*.json")):
        os.remove(path)
        removed += 1
    print("删除建筑修饰器:", removed, "个")

    # 2) 把建筑写进静态 stage 4（顺序统一按 CANON）
    for name, wanted in BIOME_BUILDINGS.items():
        path = os.path.join(BIOME_DIR, name + ".json")
        data = json.load(open(path, encoding="utf-8"))
        step = data["features"][4]
        kept = [f for f in step if f not in CANON]
        ordered = [f for f in CANON if f in wanted]
        data["features"][4] = kept + ordered
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print("biome %-20s stage4 = %s" % (name, ", ".join(f.split(":")[1] for f in ordered)))


if __name__ == "__main__":
    main()
