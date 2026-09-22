"""王朝新增/调整配方与语言文件生成器。

- 武器：完整的进化链配方（后期需要上一把 + 稀有材料 + Boss 掉落物）
- 护甲：五套（布衣 → 将军铠 → 玉甲 → 龙鳞甲 → 玄天甲）逐件升级
- 材料：图纸、精钢、玄天玉等
- 语言：把新物品的中英文名写入 zh_cn.json / en_us.json

运行：python3 tools/art/gen_dynasty3_json.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RECIPE_DIR = os.path.join(ROOT, "src/main/resources/data/dynasty/recipes")
LANG_DIR = os.path.join(ROOT, "src/main/resources/assets/dynasty/lang")
MODEL_DIR = os.path.join(ROOT, "src/main/resources/assets/dynasty/models/item")
os.makedirs(RECIPE_DIR, exist_ok=True)


def write_model(name, parent):
    path = os.path.join(MODEL_DIR, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"parent": parent, "textures": {"layer0": "dynasty:item/" + name}},
                  f, ensure_ascii=False, indent=2)
        f.write("\n")


def write(name, obj):
    with open(os.path.join(RECIPE_DIR, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def shaped(name, pattern, key, result, count=1):
    write(name, {
        "type": "minecraft:crafting_shaped",
        "pattern": pattern,
        "key": {k: {"item": v} for k, v in key.items()},
        "result": {"item": result, "count": count},
    })


def shapeless(name, ingredients, result, count=1):
    write(name, {
        "type": "minecraft:crafting_shapeless",
        "ingredients": [{"item": i} for i in ingredients],
        "result": {"item": result, "count": count},
    })


def armour_set(prefix, material):
    """用某一材料做整套护甲 / craft a full set from one material"""
    for piece, pattern in (
            ("helmet", ["XXX", "X X"]),
            ("chestplate", ["X X", "XXX", "XXX"]),
            ("leggings", ["XXX", "X X", "X X"]),
            ("boots", ["X X", "X X"])):
        shaped(prefix + "_" + piece, pattern, {"X": material},
               "dynasty:" + prefix + "_" + piece)


def armour_upgrade(from_prefix, to_prefix, materials, gate=("dynasty:blueprint",)):
    """上一套同部位 + 材料 → 下一套同部位（进化）/ upgrade the same piece to the next set"""
    for piece in ("helmet", "chestplate", "leggings", "boots"):
        shapeless(to_prefix + "_" + piece,
                  ["dynasty:" + from_prefix + "_" + piece] + list(materials) + list(gate),
                  "dynasty:" + to_prefix + "_" + piece)


# ------------------------------------------------------------------ 武器
def weapon_recipes():
    # 基础期：原版材料即可，伤害很低（木矛 5 → 铁剑 20）
    shapeless("mu_mao", ["minecraft:stick", "minecraft:stick", "minecraft:oak_planks"],
              "dynasty:mu_mao")
    shapeless("shi_ge", ["dynasty:mu_mao", "minecraft:cobblestone", "minecraft:cobblestone",
                         "minecraft:stick"], "dynasty:shi_ge")
    shapeless("tong_dao", ["dynasty:shi_ge", "minecraft:copper_ingot", "minecraft:copper_ingot",
                           "minecraft:copper_ingot"], "dynasty:tong_dao")
    shapeless("tie_jian", ["dynasty:tong_dao", "minecraft:iron_ingot", "minecraft:iron_ingot",
                           "minecraft:iron_ingot"], "dynasty:tie_jian")
    shapeless("lie_gong", ["minecraft:stick", "minecraft:stick", "minecraft:stick",
                           "minecraft:string", "minecraft:string", "minecraft:string"],
              "dynasty:lie_gong")

    # 王朝期：从青铜剑开始需要「兵器图纸」
    shapeless("sword_bronze", ["dynasty:tie_jian", "dynasty:bronze_ingot", "dynasty:bronze_ingot",
                               "dynasty:bronze_ingot", "dynasty:blueprint"],
              "dynasty:sword_bronze")
    shapeless("tang_dao", ["dynasty:sword_bronze", "dynasty:bronze_ingot", "dynasty:bronze_ingot",
                           "dynasty:silk", "dynasty:blueprint"], "dynasty:tang_dao")
    shapeless("huan_shou_dao", ["dynasty:tang_dao", "dynasty:bronze_ingot", "dynasty:bronze_ingot",
                                "dynasty:gold_coin", "dynasty:blueprint"], "dynasty:huan_shou_dao")
    shapeless("chang_gong", ["dynasty:lie_gong", "dynasty:silk", "dynasty:silk",
                             "dynasty:refined_steel", "dynasty:blueprint"], "dynasty:chang_gong")
    # 弓·速射支线（长弓 → 神臂弓 → 落雁弓 → 天狼弓）/ rapid-fire bow branch
    shapeless("shenbi_bow", ["dynasty:chang_gong", "dynasty:refined_steel",
                             "dynasty:refined_steel", "dynasty:refined_steel",
                             "dynasty:silk", "dynasty:silk", "dynasty:blueprint"],
              "dynasty:shenbi_bow")
    shapeless("luoyan_bow", ["dynasty:shenbi_bow", "dynasty:refined_steel",
                             "dynasty:refined_steel", "dynasty:refined_steel",
                             "dynasty:refined_steel", "dynasty:silver_ingot",
                             "dynasty:silver_ingot", "dynasty:blueprint"],
              "dynasty:luoyan_bow")
    shapeless("tianlang_bow", ["dynasty:luoyan_bow", "dynasty:dragon_crystal",
                               "dynasty:dragon_crystal", "dynasty:refined_steel",
                               "dynasty:refined_steel", "dynasty:refined_steel",
                               "dynasty:refined_steel", "dynasty:refined_steel",
                               "dynasty:refined_steel"], "dynasty:tianlang_bow")
    shapeless("chang_qiang", ["dynasty:huan_shou_dao", "dynasty:silver_ingot",
                              "dynasty:silver_ingot", "dynasty:bamboo_slip", "dynasty:blueprint"],
              "dynasty:chang_qiang")
    shapeless("yu_di", ["dynasty:chang_qiang", "dynasty:jade", "dynasty:jade",
                        "dynasty:silk", "dynasty:blueprint"], "dynasty:yu_di")
    shapeless("sword_silver", ["dynasty:yu_di", "dynasty:silver_ingot", "dynasty:silver_ingot",
                               "dynasty:silver_ingot", "dynasty:blueprint"],
              "dynasty:sword_silver")
    shapeless("sword_jade", ["dynasty:sword_silver", "dynasty:jade", "dynasty:jade",
                             "dynasty:jade", "dynasty:blueprint"], "dynasty:sword_jade")
    shapeless("juque_sword", ["dynasty:sword_jade", "dynasty:jade", "dynasty:jade",
                              "dynasty:bronze_ingot", "dynasty:blueprint"], "dynasty:juque_sword")

    # 名将期：必须击败 Boss 拿信物（叛将首级 / 内廷令牌 / 凤凰羽）
    shapeless("pojun_axe", ["dynasty:juque_sword", "dynasty:dragon_scale", "dynasty:dragon_scale",
                            "dynasty:dragon_crystal", "dynasty:rebel_head"], "dynasty:pojun_axe")
    shapeless("dragon_bow", ["dynasty:chang_gong", "dynasty:dragon_scale", "dynasty:dragon_scale",
                             "dynasty:phoenix_feather", "dynasty:dragon_crystal"],
              "dynasty:dragon_bow")
    shapeless("sword_dragon_crystal", ["dynasty:juque_sword", "dynasty:dragon_crystal",
                                       "dynasty:dragon_crystal", "dynasty:dragon_scale",
                                       "dynasty:eunuch_token"],
              "dynasty:sword_dragon_crystal")

    # 帝兵期：多件 Boss 掉落物 + 玉玺（科举升官方可获得）
    shapeless("halberd_fangtian", ["dynasty:pojun_axe", "dynasty:sword_dragon_crystal",
                                   "dynasty:dragon_scale", "dynasty:dragon_scale",
                                   "dynasty:emperor_bone", "dynasty:blueprint"],
              "dynasty:halberd_fangtian")
    shapeless("xuantian_axe", ["dynasty:pojun_axe", "dynasty:dragon_crystal",
                               "dynasty:dragon_crystal", "dynasty:dragon_emperor_seal"],
              "dynasty:xuantian_axe")
    shapeless("tianzi_sword", ["dynasty:halberd_fangtian", "dynasty:xuantian_jade",
                               "dynasty:dragon_emperor_seal", "dynasty:emperor_bone",
                               "dynasty:eunuch_token", "dynasty:jade_seal"],
              "dynasty:tianzi_sword")

    # 工具
    shapeless("pickaxe_jade", ["dynasty:jade", "dynasty:jade", "minecraft:stick",
                               "minecraft:stick", "dynasty:blueprint"], "dynasty:pickaxe_jade")
    shapeless("pickaxe_dragon_crystal", ["dynasty:pickaxe_jade", "dynasty:dragon_crystal",
                                         "dynasty:dragon_crystal", "dynasty:refined_steel",
                                         "dynasty:emperor_bone"],
              "dynasty:pickaxe_dragon_crystal")


# ------------------------------------------------------------------ 护甲（进化链）
def armour_recipes():
    # 布衣：丝绸直接做（开局套）
    armour_set("cloth", "dynasty:silk")
    # 之后每一套都要上一套的同部位 + 材料（+ 图纸）
    armour_upgrade("cloth", "general",
                   ["dynasty:bronze_ingot", "dynasty:bronze_ingot", "dynasty:bronze_ingot"])
    armour_upgrade("general", "jade", ["dynasty:jade", "dynasty:jade", "dynasty:jade"])
    armour_upgrade("jade", "dragon_scale",
                   ["dynasty:dragon_scale", "dynasty:dragon_scale", "dynasty:dragon_crystal"])
    # 玄天真龙甲：需要玄天玉 + 帝骸骨 + 龙帝玉玺（终盘，不用图纸）
    armour_upgrade("dragon_scale", "xuantian",
                   ["dynasty:xuantian_jade", "dynasty:dragon_crystal", "dynasty:emperor_bone",
                    "dynasty:dragon_emperor_seal"],
                   gate=())


# ------------------------------------------------------------------ 材料与饰品
def relic_recipes():
    shapeless("blueprint", ["minecraft:paper", "dynasty:ink_stick", "dynasty:bamboo_slip"],
              "dynasty:blueprint")
    shapeless("refined_steel", ["minecraft:iron_ingot", "minecraft:iron_ingot",
                                "minecraft:iron_ingot", "dynasty:cinnabar"],
              "dynasty:refined_steel", count=2)
    shapeless("xuantian_jade", ["dynasty:emperor_bone", "dynasty:jade", "dynasty:jade",
                                "dynasty:dragon_crystal"], "dynasty:xuantian_jade")
    shapeless("heart_mirror", ["dynasty:bronze_ingot", "dynasty:bronze_ingot",
                               "dynasty:silver_ingot", "dynasty:silk"], "dynasty:heart_mirror")
    shapeless("jade_crown", ["dynasty:jade", "dynasty:jade", "dynasty:gold_coin", "dynasty:silk"],
              "dynasty:jade_crown")
    # ---- 新增饰品 / new trinkets ----
    shapeless("jade_cicada", ["dynasty:jade", "dynasty:jade", "dynasty:silk", "dynasty:cinnabar"],
              "dynasty:jade_cicada")
    shapeless("dragon_pearl", ["dynasty:dragon_crystal", "dynasty:dragon_crystal",
                               "dynasty:dragon_scale", "dynasty:jade"], "dynasty:dragon_pearl")
    shapeless("phoenix_ring", ["dynasty:phoenix_feather", "minecraft:gold_ingot",
                               "minecraft:gold_ingot", "dynasty:jade"], "dynasty:phoenix_ring")
    shapeless("storm_charm", ["dynasty:cinnabar", "minecraft:gold_ingot", "dynasty:ink_stick",
                              "dynasty:silk"], "dynasty:storm_charm")
    shapeless("moon_pendant", ["dynasty:jade", "minecraft:glowstone_dust", "minecraft:gold_ingot",
                               "dynasty:silk"], "dynasty:moon_pendant")
    shapeless("tiger_crest", ["dynasty:bronze_ingot", "dynasty:bronze_ingot",
                              "dynasty:copper_coin", "dynasty:copper_coin"], "dynasty:tiger_crest")
    # ---- 第三批饰品（建筑宝箱也能开出）/ third batch of trinkets ----
    shapeless("jade_tortoise", ["dynasty:jade", "dynasty:jade", "dynasty:bronze_ingot",
                                "minecraft:heart_of_the_sea"], "dynasty:jade_tortoise")
    shapeless("war_drum_charm", ["dynasty:bronze_ingot", "dynasty:bronze_ingot",
                                 "dynasty:silk", "dynasty:cinnabar"], "dynasty:war_drum_charm")
    shapeless("cinnabar_pouch", ["dynasty:cinnabar", "dynasty:cinnabar", "dynasty:silk",
                                 "dynasty:talisman_paper"], "dynasty:cinnabar_pouch")
    shapeless("dragon_whisker", ["dynasty:dragon_scale", "dynasty:dragon_crystal",
                                 "dynasty:silk", "dynasty:refined_steel"], "dynasty:dragon_whisker")
    shapeless("tiger_token", ["dynasty:bronze_ingot", "dynasty:silver_ingot",
                              "dynasty:copper_coin", "dynasty:silk"], "dynasty:tiger_token")
    shapeless("sun_feather", ["dynasty:phoenix_feather", "minecraft:glowstone_dust",
                              "minecraft:gold_ingot", "dynasty:brocade"], "dynasty:sun_feather")
    shapeless("war_horse_bell", ["dynasty:bronze_ingot", "dynasty:bronze_ingot",
                                 "minecraft:gold_ingot", "dynasty:silk"], "dynasty:war_horse_bell")
    shapeless("iron_waist_token", ["minecraft:iron_ingot", "minecraft:iron_ingot",
                                   "dynasty:bronze_ingot", "dynasty:silk"],
              "dynasty:iron_waist_token")
    shapeless("auspicious_bell", ["dynasty:gold_coin", "dynasty:gold_coin",
                                  "dynasty:bronze_ingot", "dynasty:silk"],
              "dynasty:auspicious_bell")


# ------------------------------------------------------------------ 语言
# Explorer's Compass 1.20.1-1.4.0 reads Util.makeDescriptionId("structure", id),
# not block names or structure_set.*. Nature's Compass uses biome.<namespace>.<path>.
# Keep the names in one bilingual table; verify_compass_localization.py compares
# this table against every worldgen registry JSON, including structure groups.
WORLDGEN_NAMES = {
    "structure": {
        "palace": ("皇家宫殿", "Imperial Palace"),
        "academy": ("国子监", "Imperial Academy"),
        "imperial_tomb": ("帝陵", "Imperial Tomb"),
        "great_wall_gate": ("长城关隘", "Great Wall Gate"),
        "star_altar": ("九霄星坛", "Nine-Heaven Star Altar"),
        "stone_grove": ("幽冥石林", "Underworld Stone Grove"),
    },
    "biome": {
        "celestial_plains": ("天朝平原", "Celestial Plains"),
        "jade_forest": ("玉林", "Jade Forest"),
        "dragon_ridge": ("龙脊山脉", "Dragon Ridge"),
        "celestial_sea": ("碧海云海", "Celestial Sea"),
        "underworld_wastes": ("幽冥荒原", "Underworld Wastes"),
        "soul_river": ("忘川河畔", "Soul River"),
        "jiuxiao_skyland": ("九霄仙岛", "Nine-Heaven Skyland"),
        "jiuxiao_cloud_sea": ("云海", "Cloud Sea"),
        "dragon_palace_hall": ("龙宫正殿", "Dragon Palace Hall"),
        "dragon_palace_deep": ("深渊", "Abyss"),
    },
    "dimension": {
        "celestial_dynasty": ("天朝·龙庭", "Celestial Dynasty"),
        "underworld": ("地府", "Underworld"),
        "jiuxiao": ("九霄天界", "Nine-Heaven Realm"),
        "dragon_palace": ("东海龙宫", "Dragon Palace"),
    },
}


def worldgen_lang(locale):
    index = {"zh_cn": 0, "en_us": 1}[locale]
    return {f"{kind}.dynasty.{name.replace('/', '.')}": pair[index]
            for kind, entries in WORLDGEN_NAMES.items()
            for name, pair in entries.items()}


def merge_worldgen_lang():
    """Refresh only navigation names, without regenerating models or recipes."""
    for locale in ("zh_cn", "en_us"):
        path = os.path.join(LANG_DIR, locale + ".json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data.update(worldgen_lang(locale))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("navigation lang:", locale, len(worldgen_lang(locale)), "keys")


ZH = {
    "item.dynasty.mu_mao": "木矛",
    "item.dynasty.shi_ge": "石戈",
    "item.dynasty.tong_dao": "铜刀",
    "item.dynasty.tie_jian": "铁剑",
    "item.dynasty.lie_gong": "猎弓",
    "item.dynasty.chang_gong": "长弓",
    "item.dynasty.shenbi_bow": "神臂弓",
    "item.dynasty.luoyan_bow": "落雁弓",
    "item.dynasty.tianlang_bow": "天狼弓",
    "item.dynasty.xuantian_axe": "玄天钺",
    "item.dynasty.tianzi_sword": "天子剑",
    "item.dynasty.cloth_helmet": "布巾",
    "item.dynasty.cloth_chestplate": "布甲",
    "item.dynasty.cloth_leggings": "布裤",
    "item.dynasty.cloth_boots": "布靴",
    "item.dynasty.xuantian_helmet": "玄天真龙盔",
    "item.dynasty.xuantian_chestplate": "玄天真龙铠",
    "item.dynasty.xuantian_leggings": "玄天真龙胫甲",
    "item.dynasty.xuantian_boots": "玄天真龙靴",
    "item.dynasty.blueprint": "兵器图纸",
    "item.dynasty.refined_steel": "精钢",
    "item.dynasty.rebel_head": "叛将首级",
    "item.dynasty.eunuch_token": "内廷令牌",
    "item.dynasty.emperor_bone": "帝骸骨",
    "item.dynasty.dragon_emperor_seal": "龙帝玉玺",
    "item.dynasty.xuantian_jade": "玄天玉",
    "item.dynasty.heart_mirror": "护心镜",
    "item.dynasty.jade_crown": "玉冠",
    "item.dynasty.vajra_talisman": "金刚符",
    "item.dynasty.soul_talisman": "摄魂符",
    "item.dynasty.jade_cicada": "玉蝉",
    "item.dynasty.dragon_pearl": "龙珠",
    "item.dynasty.phoenix_ring": "凤凰指环",
    "item.dynasty.storm_charm": "雷纹护符",
    "item.dynasty.moon_pendant": "明月佩",
    "item.dynasty.tiger_crest": "虎符残片",
    "item.dynasty.jade_tortoise": "玉龟符",
    "item.dynasty.war_drum_charm": "战鼓坠",
    "item.dynasty.cinnabar_pouch": "朱砂囊",
    "item.dynasty.dragon_whisker": "龙须穗",
    "item.dynasty.tiger_token": "虎头令",
    "item.dynasty.sun_feather": "金乌翎",
    "item.dynasty.war_horse_bell": "战马铃",
    "item.dynasty.iron_waist_token": "玄铁腰牌",
    "item.dynasty.auspicious_bell": "瑞兽铃",
    "block.dynasty.ritual_altar": "法阵·祭坛",
    "advancements.dynasty.exam_passed.title": "科举中第",
    "advancements.dynasty.exam_passed.description": "在科举中答对至少一题",
    "advancements.dynasty.rank_official.title": "官阶初授",
    "advancements.dynasty.rank_official.description": "功名晋升，获得第一个官阶",
    "advancements.dynasty.rank_scholar.title": "金榜题名",
    "advancements.dynasty.rank_scholar.description": "官阶升至举人（第 3 阶）",
    "advancements.dynasty.rank_hanlin.title": "翰苑清贵",
    "advancements.dynasty.rank_hanlin.description": "官阶升至翰林（第 10 阶）",
    "advancements.dynasty.rank_minister.title": "位列部堂",
    "advancements.dynasty.rank_minister.description": "官阶升至尚书（第 12 阶）",
    "advancements.dynasty.rank_grand_secretary.title": "天下共主",
    "advancements.dynasty.rank_grand_secretary.description": "官阶升至大学士（第 13 阶）",
    "advancements.dynasty.rank_chancellor.title": "位极人臣",
    "advancements.dynasty.rank_chancellor.description": "官阶升至丞相（第 17 阶）",
    "advancements.dynasty.rank_prince_regent.title": "摄政天下",
    "advancements.dynasty.rank_prince_regent.description": "官阶升至摄政王（第 18 阶）",
    "advancements.dynasty.rank_son_of_heaven.title": "君临天下",
    "advancements.dynasty.rank_son_of_heaven.description": "官阶升至天子（第 19 阶）",
    "advancements.dynasty.met_minister.title": "拜见大臣",
    "advancements.dynasty.met_minister.description": "与大臣交谈，听取朝堂建议",
    "advancements.dynasty.army_led.title": "虎符调兵",
    "advancements.dynasty.army_led.description": "用虎符列阵召集禁军",
    "advancements.dynasty.rebellion_calmed.title": "安抚民心",
    "advancements.dynasty.rebellion_calmed.description": "把叛乱值压到 20 以下",
    "advancements.dynasty.qilin_friend.title": "祥瑞麒麟",
    "advancements.dynasty.qilin_friend.description": "以仙桃结交麒麟",
    "advancements.dynasty.entered_celestial.title": "踏入天朝",
    "advancements.dynasty.entered_celestial.description": "穿过天朝传送门进入天朝·龙庭",
    "advancements.dynasty.entered_underworld.title": "下探地府",
    "advancements.dynasty.entered_underworld.description": "穿过地府传送门进入地府",
    "curios.identifier.curio": "万能饰品",
}

EN = {
    "item.dynasty.mu_mao": "Wooden Spear",
    "item.dynasty.shi_ge": "Stone Dagger-Axe",
    "item.dynasty.tong_dao": "Copper Sabre",
    "item.dynasty.tie_jian": "Iron Sword",
    "item.dynasty.lie_gong": "Hunting Bow",
    "item.dynasty.chang_gong": "Longbow",
    "item.dynasty.shenbi_bow": "Shenbi Bow",
    "item.dynasty.luoyan_bow": "Luoyan Bow",
    "item.dynasty.tianlang_bow": "Tianlang Bow",
    "item.dynasty.xuantian_axe": "Xuantian Axe",
    "item.dynasty.tianzi_sword": "Sword of Heaven",
    "item.dynasty.cloth_helmet": "Cloth Hood",
    "item.dynasty.cloth_chestplate": "Cloth Robe",
    "item.dynasty.cloth_leggings": "Cloth Trousers",
    "item.dynasty.cloth_boots": "Cloth Boots",
    "item.dynasty.xuantian_helmet": "Xuantian True Dragon Helm",
    "item.dynasty.xuantian_chestplate": "Xuantian True Dragon Armour",
    "item.dynasty.xuantian_leggings": "Xuantian True Dragon Greaves",
    "item.dynasty.xuantian_boots": "Xuantian True Dragon Boots",
    "item.dynasty.blueprint": "Weapon Blueprint",
    "item.dynasty.refined_steel": "Refined Steel",
    "item.dynasty.rebel_head": "Rebel General's Head",
    "item.dynasty.eunuch_token": "Palace Token",
    "item.dynasty.emperor_bone": "Emperor's Bone",
    "item.dynasty.dragon_emperor_seal": "Dragon Emperor's Seal",
    "item.dynasty.xuantian_jade": "Xuantian Jade",
    "item.dynasty.heart_mirror": "Heart Mirror",
    "item.dynasty.jade_crown": "Jade Crown",
    "item.dynasty.vajra_talisman": "Vajra Talisman",
    "item.dynasty.soul_talisman": "Soul Talisman",
    "item.dynasty.jade_cicada": "Jade Cicada",
    "item.dynasty.dragon_pearl": "Dragon Pearl",
    "item.dynasty.phoenix_ring": "Phoenix Ring",
    "item.dynasty.storm_charm": "Storm Charm",
    "item.dynasty.moon_pendant": "Moon Pendant",
    "item.dynasty.tiger_crest": "Tiger Crest",
    "item.dynasty.jade_tortoise": "Jade Tortoise",
    "item.dynasty.war_drum_charm": "War Drum Charm",
    "item.dynasty.cinnabar_pouch": "Cinnabar Pouch",
    "item.dynasty.dragon_whisker": "Dragon Whisker",
    "item.dynasty.tiger_token": "Tiger Token",
    "item.dynasty.sun_feather": "Sun Feather",
    "item.dynasty.war_horse_bell": "War Horse Bell",
    "item.dynasty.iron_waist_token": "Iron Waist Token",
    "item.dynasty.auspicious_bell": "Auspicious Bell",
    "block.dynasty.ritual_altar": "Ritual Altar",
    "advancements.dynasty.exam_passed.title": "Exam Passed",
    "advancements.dynasty.exam_passed.description": "Answer at least one exam question",
    "advancements.dynasty.rank_official.title": "First Office",
    "advancements.dynasty.rank_official.description": "Reach your first official rank",
    "advancements.dynasty.rank_scholar.title": "Scholar",
    "advancements.dynasty.rank_scholar.description": "Reach rank 3",
    "advancements.dynasty.rank_hanlin.title": "Hanlin Scholar",
    "advancements.dynasty.rank_hanlin.description": "Reach rank 10",
    "advancements.dynasty.rank_minister.title": "Minister",
    "advancements.dynasty.rank_minister.description": "Reach rank 12",
    "advancements.dynasty.rank_grand_secretary.title": "Grand Secretary",
    "advancements.dynasty.rank_grand_secretary.description": "Reach rank 13",
    "advancements.dynasty.rank_chancellor.title": "Chancellor",
    "advancements.dynasty.rank_chancellor.description": "Reach rank 17",
    "advancements.dynasty.rank_prince_regent.title": "Prince Regent",
    "advancements.dynasty.rank_prince_regent.description": "Reach rank 18",
    "advancements.dynasty.rank_son_of_heaven.title": "Son of Heaven",
    "advancements.dynasty.rank_son_of_heaven.description": "Reach rank 19",
    "advancements.dynasty.met_minister.title": "Meet the Minister",
    "advancements.dynasty.met_minister.description": "Talk to a minister",
    "advancements.dynasty.army_led.title": "Raise an Army",
    "advancements.dynasty.army_led.description": "Summon imperial guards with the tiger tally",
    "advancements.dynasty.rebellion_calmed.title": "Calm the Realm",
    "advancements.dynasty.rebellion_calmed.description": "Push rebellion below 20",
    "advancements.dynasty.qilin_friend.title": "Qilin Friend",
    "advancements.dynasty.qilin_friend.description": "Befriend a qilin with an immortal peach",
    "advancements.dynasty.entered_celestial.title": "Entered the Celestial Realm",
    "advancements.dynasty.entered_celestial.description": "Enter the celestial dynasty",
    "advancements.dynasty.entered_underworld.title": "Entered the Underworld",
    "advancements.dynasty.entered_underworld.description": "Enter the underworld",
    "curios.identifier.curio": "Universal Curio",
}


def item_models():
    handheld = ["mu_mao", "shi_ge", "tong_dao", "tie_jian", "lie_gong", "chang_gong",
                "shenbi_bow", "luoyan_bow", "tianlang_bow",
                "xuantian_axe", "tianzi_sword"]
    generated = ["cloth_helmet", "cloth_chestplate", "cloth_leggings", "cloth_boots",
                 "xuantian_helmet", "xuantian_chestplate", "xuantian_leggings", "xuantian_boots",
                 "blueprint", "refined_steel", "rebel_head", "eunuch_token", "emperor_bone",
                 "dragon_emperor_seal", "xuantian_jade", "heart_mirror", "jade_crown",
                 "vajra_talisman", "soul_talisman", "jade_cicada", "dragon_pearl",
                 "phoenix_ring", "storm_charm", "moon_pendant", "tiger_crest",
                 "jade_tortoise", "war_drum_charm", "cinnabar_pouch", "dragon_whisker",
                 "tiger_token", "sun_feather", "war_horse_bell", "iron_waist_token",
                 "auspicious_bell"]
    os.makedirs(MODEL_DIR, exist_ok=True)
    for name in handheld:
        write_model(name, "item/handheld")
    for name in generated:
        write_model(name, "item/generated")
    print("models:", len(handheld) + len(generated))


def merge_lang():
    for filename, table in (("zh_cn.json", ZH), ("en_us.json", EN)):
        path = os.path.join(LANG_DIR, filename)
        data = json.load(open(path, encoding="utf-8"))
        data.update(table)
        # 已删除的物品（回春符 → 换成金刚符）/ removed items
        for stale in ("item.dynasty.healing_talisman", "curios.identifier.dynasty_trinket"):
            data.pop(stale, None)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("lang:", filename, len(data), "keys")
    merge_worldgen_lang()


def clean_removed():
    """删掉已被替换的物品资源（回春符）/ remove assets of deleted items"""
    removed = ["healing_talisman"]
    for name in removed:
        for path in (
                os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/item", name + ".png"),
                os.path.join(MODEL_DIR, name + ".json"),
                os.path.join(RECIPE_DIR, name + ".json")):
            if os.path.exists(path):
                os.remove(path)
                print("removed:", os.path.relpath(path, ROOT))



def talisman_recipes():
    """符箓：一次性但很强（火/雷为伤害主力）"""
    shapeless("fire_talisman", ["dynasty:talisman_paper", "minecraft:gunpowder",
                                "minecraft:gunpowder", "dynasty:cinnabar"],
              "dynasty:fire_talisman")
    shapeless("thunder_talisman", ["dynasty:talisman_paper", "minecraft:gunpowder",
                                   "minecraft:gunpowder", "minecraft:gold_ingot",
                                   "dynasty:cinnabar"], "dynasty:thunder_talisman")
    shapeless("wind_talisman", ["dynasty:talisman_paper", "minecraft:feather",
                                "minecraft:feather", "dynasty:silk"], "dynasty:wind_talisman")
    shapeless("stealth_talisman", ["dynasty:talisman_paper", "dynasty:ink_stick",
                                   "minecraft:coal", "dynasty:silk"], "dynasty:stealth_talisman")
    shapeless("vajra_talisman", ["dynasty:talisman_paper", "minecraft:gold_ingot",
                                 "minecraft:gold_ingot", "dynasty:cinnabar"],
              "dynasty:vajra_talisman")
    shapeless("soul_talisman", ["dynasty:talisman_paper", "dynasty:cinnabar",
                                "dynasty:cinnabar", "dynasty:ink_stick"], "dynasty:soul_talisman")
    shapeless("return_talisman", ["dynasty:talisman_paper", "minecraft:ender_pearl"],
              "dynasty:return_talisman")


def block_resources():
    """法阵·祭坛的 blockstate / 模型 / 配方 / 名字"""
    assets = os.path.join(ROOT, "src/main/resources/assets/dynasty")
    os.makedirs(os.path.join(assets, "blockstates"), exist_ok=True)
    os.makedirs(os.path.join(assets, "models/block"), exist_ok=True)
    with open(os.path.join(assets, "blockstates/ritual_altar.json"), "w", encoding="utf-8") as f:
        json.dump({"variants": {"": {"model": "dynasty:block/ritual_altar"}}}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(os.path.join(assets, "models/block/ritual_altar.json"), "w", encoding="utf-8") as f:
        json.dump({"parent": "block/cube_all",
                   "textures": {"all": "dynasty:block/ritual_altar"}}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    write_model("ritual_altar", "dynasty:block/ritual_altar")
    # 方块物品模型要用 block 贴图（write_model 默认写 item 贴图，这里覆盖）
    model_path = os.path.join(MODEL_DIR, "ritual_altar.json")
    with open(model_path, "w", encoding="utf-8") as f:
        json.dump({"parent": "dynasty:block/ritual_altar"}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    shapeless("ritual_altar", ["dynasty:jade_block", "dynasty:jade_block", "dynasty:jade_block",
                               "dynasty:jade_block", "dynasty:dragon_crystal"],
              "dynasty:ritual_altar")
    print("block resources: ritual_altar")


def main():
    weapon_recipes()
    armour_recipes()
    relic_recipes()
    talisman_recipes()
    item_models()
    block_resources()
    merge_lang()
    clean_removed()
    print("recipes written:", len(os.listdir(RECIPE_DIR)))


if __name__ == "__main__":
    main()
