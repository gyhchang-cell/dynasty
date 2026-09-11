import json, os, shutil

ART = "/tmp/dyn_art/out/item"
REPO = os.path.expanduser("~/Desktop/dynasty/src/main/resources")
ASSETS = os.path.join(REPO, "assets/dynasty")
DATA = os.path.join(REPO, "data")
TEX = os.path.join(ASSETS, "textures/item")
MODELS = os.path.join(ASSETS, "models/item")
LANGS = os.path.join(ASSETS, "lang")
RECIPES = os.path.join(DATA, "dynasty/recipes")
os.makedirs(RECIPES, exist_ok=True)

NEW = {
    # 武器 / weapons
    "tang_dao": ("唐刀", "Tang Dao", "攻速最快（2.8 次/秒），命中后短时加速"),
    "huan_shou_dao": ("环首刀", "Huan Shou Dao", "受击后反击：获得力量 II"),
    "chang_qiang": ("长枪", "Chang Qiang", "攻击距离 +3，命中挑飞目标"),
    "yu_di": ("玉笛", "Jade Flute", "右键吹奏：范围虚弱与缓慢"),
    "juque_sword": ("巨阙重剑", "Juque Greatsword", "命中击退并施加缓慢"),
    "pojun_axe": ("破军战斧", "Po Jun Axe", "破甲：无视目标一半士气减伤"),
    "dragon_bow": ("龙吟弓", "Dragon Bow", "重箭：伤害三倍余、穿透 3、强击退"),
    # 饰品 / accessories
    "jade_pendant": ("玉佩", "Jade Pendant", "额外 8% 减伤"),
    "jade_bi_disc": ("玉璧", "Jade Bi Disc", "最大生命 +150"),
    "gold_seal_charm": ("金印", "Gold Seal Charm", "功名获取 +25%，每秒回忠诚"),
    "dragon_scale_charm": ("龙鳞护符", "Dragon Scale Charm", "护甲 +12、抗击退 +0.4"),
    "phoenix_feather_charm": ("凤羽翎", "Phoenix Plume", "移动速度 +10%、缓降"),
    "qilin_horn_charm": ("麒麟角坠", "Qilin Horn Charm", "幸运 +3、持续生命恢复"),
    "fox_tail_charm": ("狐尾坠", "Fox Tail Charm", "跳跃提升 II、移速 +5%"),
    "silk_pouch": ("锦囊", "Silk Pouch", "水下呼吸 + 夜视"),
    "south_pointing_compass": ("司南", "South-Pointing Compass", "抗性提升，并显示坐标"),
    "trinket_box": ("百宝妆匣", "Trinket Box", "右键打开 6 个饰品槽"),
    "dynasty_manual": ("王朝说明书", "Dynasty Manual", "开局赠送，右键阅读玩法"),
}

for name in NEW:
    shutil.copy2(os.path.join(ART, name + ".png"), os.path.join(TEX, name + ".png"))
    with open(os.path.join(MODELS, name + ".json"), "w", encoding="utf-8") as f:
        json.dump({"parent": "item/generated", "textures": {"layer0": "dynasty:item/" + name}},
                  f, ensure_ascii=False, indent=2)

for lang, idx in (("zh_cn", 0), ("en_us", 1)):
    path = os.path.join(LANGS, lang + ".json")
    data = json.load(open(path, encoding="utf-8"))
    for name, names in NEW.items():
        data["item.dynasty." + name] = names[idx]
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 配方 / recipes
D, M = "dynasty:", "minecraft:"


def recipe(name, ingredients, result, count=1):
    json.dump({
        "type": "minecraft:crafting_shapeless",
        "ingredients": [{"item": i} for i in ingredients],
        "result": {"item": result, "count": count},
    }, open(os.path.join(RECIPES, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


recipe("tang_dao", [D + "sword_bronze", D + "bronze_ingot", D + "bronze_ingot", D + "silk"], D + "tang_dao")
recipe("huan_shou_dao", [D + "tang_dao", D + "bronze_ingot", D + "bronze_ingot",
                         D + "bronze_ingot", D + "gold_coin", D + "gold_coin"], D + "huan_shou_dao")
recipe("chang_qiang", [D + "huan_shou_dao", D + "silver_ingot", D + "silver_ingot",
                       D + "silver_ingot", D + "bamboo_slip"], D + "chang_qiang")
recipe("yu_di", [D + "jade", D + "jade", D + "jade", D + "bamboo_slip", D + "bamboo_slip"], D + "yu_di")
recipe("juque_sword", [D + "sword_jade", D + "jade", D + "jade", D + "jade",
                       D + "bronze_ingot", D + "bronze_ingot"], D + "juque_sword")
recipe("pojun_axe", [D + "juque_sword", D + "dragon_scale", D + "dragon_scale",
                     D + "dragon_scale", D + "dragon_crystal"], D + "pojun_axe")
recipe("dragon_bow", [D + "dragon_crystal", D + "dragon_crystal", D + "silk",
                      D + "silk", M + "stick", M + "stick"], D + "dragon_bow")

recipe("jade_pendant", [D + "jade", D + "jade", D + "silk"], D + "jade_pendant")
recipe("jade_bi_disc", [D + "jade", D + "jade", D + "jade", M + "gold_ingot"], D + "jade_bi_disc")
recipe("gold_seal_charm", [D + "gold_coin", D + "gold_coin", D + "gold_coin",
                           D + "gold_coin", D + "official_seal", D + "silk"], D + "gold_seal_charm")
recipe("dragon_scale_charm", [D + "dragon_scale", D + "dragon_scale", D + "silk"], D + "dragon_scale_charm")
recipe("phoenix_feather_charm", [D + "phoenix_feather", D + "silk", D + "gold_coin"], D + "phoenix_feather_charm")
recipe("qilin_horn_charm", [D + "qilin_horn", D + "silk", D + "jade"], D + "qilin_horn_charm")
recipe("fox_tail_charm", [D + "fox_tail", D + "silk", D + "jade"], D + "fox_tail_charm")
recipe("silk_pouch", [D + "silk", D + "silk", D + "silk", M + "string"], D + "silk_pouch")
recipe("south_pointing_compass", [D + "bronze_mirror", D + "bronze_ingot",
                                  D + "bronze_ingot", M + "redstone"], D + "south_pointing_compass")
recipe("trinket_box", [D + "silk", D + "silk", D + "bamboo_slip", D + "bamboo_slip", M + "gold_ingot"],
       D + "trinket_box")
recipe("dynasty_manual", [M + "book", D + "ink_stick", D + "bamboo_slip", D + "bamboo_slip"], D + "dynasty_manual")

# Curios 兼容标签 / Curios-compatible item tags
CURIOS = os.path.join(DATA, "curios/tags/items")
os.makedirs(CURIOS, exist_ok=True)
slots = {
    "charm": ["jade_pendant", "fox_tail_charm", "qilin_horn_charm", "gold_seal_charm"],
    "necklace": ["jade_bi_disc", "dragon_scale_charm", "jade_pendant"],
    "ring": ["gold_seal_charm", "south_pointing_compass"],
    "belt": ["silk_pouch"],
    "head": ["phoenix_feather_charm"],
    "curio": ["bronze_mirror", "jade_bi_disc", "silk_pouch", "fox_tail_charm"],
}
for slot, ids in slots.items():
    json.dump({"replace": False, "values": ["dynasty:" + i for i in ids]},
              open(os.path.join(CURIOS, slot + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

print("installed", len(NEW), "items; recipes:", len(os.listdir(RECIPES)), "curios slots:", len(slots))
