import json, os, shutil, glob

ART = "/tmp/dyn_art/out"
REPO = os.path.expanduser("~/Desktop/dynasty/src/main/resources/assets/dynasty/textures")

MAP = {
    "block": os.path.join(REPO, "block"),
    "item": os.path.join(REPO, "item"),
    "mob_effect": os.path.join(REPO, "mob_effect"),
    "entity": os.path.join(REPO, "entity"),
    "armor": os.path.join(REPO, "models/armor"),
}

installed = 0
for src_dir, dst_dir in MAP.items():
    os.makedirs(dst_dir, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(ART, src_dir, "*.png"))):
        name = os.path.basename(path)
        shutil.copy2(path, os.path.join(dst_dir, name))
        installed += 1

# 删除旧内容遗留的死贴图 / remove leftovers from previous mod content
DEAD = [
    "block/kaishen_block.png", "block/pujing_back.png", "block/pujing_bottom.png",
    "block/pujing_front.png", "block/pujing_left.png", "block/pujing_right.png",
    "block/pujing_top.png", "block/stone_base.png",
    "mob_effect/gali.png", "mob_effect/wula_shield.png",
    "models/armor/pujing_layer_1.png", "models/armor/renminbi_layer_1.png",
    "models/armor/renminbi_layer_2.png", "models/armor/zhaoming_layer_1.png",
    "models/armor/zhaoming_layer_2.png",
]
for rel in DEAD:
    p = os.path.join(REPO, rel)
    if os.path.exists(p):
        os.remove(p)

# 死物品贴图（旧模组内容 + 未使用的刷怪蛋贴图）
DEAD_ITEMS = ["gali", "jingwei", "jingweiprotect", "kaishen_coin", "laote_coin", "pujing",
              "pujingprotect", "qingde_coin", "renminbi", "wula", "zaomiao_coin", "zgprotect",
              "zhaoming", "terracotta_warrior_spawn_egg", "imperial_soldier_spawn_egg",
              "undead_first_emperor_spawn_egg"]
for n in DEAD_ITEMS:
    p = os.path.join(REPO, "item", n + ".png")
    if os.path.exists(p):
        os.remove(p)

counts = {k: len(glob.glob(os.path.join(v, "*.png"))) for k, v in MAP.items()}
print("installed:", installed)
print("now present:", counts)
