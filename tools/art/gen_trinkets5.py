#!/usr/bin/env python3
"""1.4.0 第三十四轮：再扩 50 件饰品（119 → 169 件），按主题分五类各 10 件。

**新格式（v2）** —— 一行最多 11 格：

    (属性1, 值1, 属性2, 值2, 效果, 等级, 条件, 属性3, 值3, 条件3)

前两格属性共用「条件」，**第三格带自己的条件**，所以一件饰品能同时写
「白天 +22% 攻击、夜里 +10% 移速」这种双面设计；老批次的行只有 8 格，
照旧生效（Java 侧按列数判断）。

属性编码：0 生命 1 护甲 2 抗击退 3 移速% 4 攻击% 5 攻速% 6 击退 7 距离
         9 生命上限% 11 幸运      （-1 = 这一格空着）
效果编码：21 龙威 22 铁壁 23 疾风 24 威慑 25 天命 26 忠诚 —— **模组自有效果**
         27 内伤 —— 兼作「代价」（和 4 攻击% 同用就是拿命换伤害）
         0 = 不带效果；1~12 是旧批次的原版效果，新饰品一律不用
条件编码：0 常驻 1 白天 2 夜晚 3 水下 4 残血（<40%） 5 骑乘 6 满血 7 雷雨

贴图：从最接近的旧饰品**复制 + 染色**（可重复运行，不覆盖已有文件）；
模型 / 配方 / 中英词条 / Curios 标签 + 分槽一次生成。

运行：python3 tools/art/gen_trinkets5.py
"""
import json
import os

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/dynasty")
DATA = os.path.join(ROOT, "src/main/resources/data/dynasty")
CURIOS = os.path.join(ROOT, "src/main/resources/data/dynasty/tags/items/accessories.json")

# id: (中文名, 英文名, 贴图来源, 染色, [材料…], (属性1…条件3 共 10 格))
TRINKETS = {
    # ---- 一、昼夜双生（10）：白天与夜里各有一套本事 ----
    "dawn_blade_charm": ("破晓刃坠", "Dawn Blade Charm", "saber_tassel", (0xF0, 0xC8, 0x90),
                         ["dynasty:refined_steel", "dynasty:silk", "dynasty:gold_coin"],
                         (4, 0.22, -1, 0.0, 0, 0, 1, 3, 0.10, 2)),
    "dusk_veil_charm": ("暮色帷幕", "Dusk Veil Charm", "cloud_brocade", (0x90, 0x80, 0xC8),
                        ["dynasty:silk", "dynasty:ink_stick", "dynasty:cinnabar"],
                        (4, 0.26, -1, 0.0, 0, 0, 2, 9, -0.20, 1)),
    "noon_pendant": ("正阳佩", "Noon Pendant", "moon_pendant", (0xF0, 0xE0, 0x80),
                     ["dynasty:jade", "dynasty:gold_coin", "dynasty:silk"],
                     (0, 240.0, -1, 0.0, 0, 0, 1, 0, -160.0, 2)),
    "moonlit_mirror": ("月华镜", "Moonlit Mirror", "bronze_mirror", (0xB0, 0xC8, 0xF0),
                       ["dynasty:bronze_mirror", "dynasty:dragon_crystal", "dynasty:silk"],
                       (5, 0.14, -1, 0.0, 0, 0, 2, 11, 2.0, 1)),
    "sun_chaser_ring": ("追阳戒", "Sun Chaser Ring", "dragon_bone_ring", (0xF0, 0xD0, 0x70),
                        ["dynasty:gold_coin", "dynasty:jade", "dynasty:cinnabar"],
                        (3, 0.12, 4, 0.10, 0, 0, 1, -1, 0.0, 0)),
    "night_heron_feather": ("夜鹭羽", "Night Heron Feather", "crane_feather", (0x80, 0x90, 0xC0),
                            ["dynasty:crane_feather", "dynasty:silk", "dynasty:gold_coin"],
                            (4, 0.18, 6, 0.35, 0, 0, 2, -1, 0.0, 0)),
    "twilight_cicada": ("蝉蜕影", "Twilight Cicada", "jade_cicada", (0xA0, 0xB8, 0x90),
                        ["dynasty:jade", "dynasty:silk", "dynasty:talisman_paper"],
                        (2, 0.40, -1, 0.0, 0, 0, 1, 7, 1.0, 2)),
    "eclipse_bead": ("蚀月珠", "Eclipse Bead", "dragon_pearl", (0x88, 0x70, 0xB0),
                     ["dynasty:sea_pearl", "dynasty:dragon_crystal", "dynasty:cinnabar"],
                     (4, 0.30, -1, 0.0, 0, 0, 2, 1, -6.0, 1)),
    "dawn_drum": ("晨钟坠", "Dawn Bell Charm", "auspicious_bell", (0xF0, 0xD8, 0xA0),
                  ["dynasty:gold_coin", "dynasty:bronze_mirror", "dynasty:silk"],
                  (5, 0.12, 3, 0.08, 0, 0, 1, -1, 0.0, 0)),
    "starless_night_ring": ("无星夜戒", "Starless Night Ring", "dragon_bone_ring", (0x60, 0x68, 0x98),
                            ["dynasty:emperor_bone", "dynasty:jade", "dynasty:gold_coin"],
                            (0, 220.0, -1, 0.0, 0, 0, 2, 4, 0.16, 2)),
    # ---- 二、生死代价（10）：把命押上去换伤害 ----
    "blood_oath_seal": ("血誓印", "Blood Oath Seal", "imperial_seal_charm", (0xC0, 0x50, 0x50),
                        ["dynasty:cinnabar", "dynasty:dragon_crystal", "dynasty:gold_coin"],
                        (9, -0.30, 4, 0.35, 0, 0, 0, -1, 0.0, 0)),
    "bone_reaper_tally": ("白骨算筹", "Bone Reaper Tally", "tiger_token", (0xE0, 0xE0, 0xD0),
                          ["dynasty:emperor_bone", "dynasty:bamboo_slip", "dynasty:cinnabar"],
                          (9, -0.20, 4, 0.25, 0, 0, 0, 6, 0.5, 0)),
    "internal_injury_talisman": ("内伤符", "Internal Injury Talisman", "talisman_pouch", (0xD0, 0x60, 0x70),
                                 ["dynasty:talisman_paper", "dynasty:cinnabar", "dynasty:thunder_token"],
                                 (4, 0.45, -1, 0.0, 27, 0, 0, -1, 0.0, 0)),
    "lifedrain_ring": ("汲生戒", "Lifedrain Ring", "dragon_bone_ring", (0xB0, 0x40, 0x60),
                       ["dynasty:emperor_bone", "dynasty:cinnabar", "dynasty:jade"],
                       (4, 0.30, 5, 0.10, 27, 1, 0, -1, 0.0, 0)),
    "crimson_pact_charm": ("血契坠", "Crimson Pact Charm", "jade_marrow_charm", (0xD0, 0x40, 0x50),
                           ["dynasty:hunyuan_pearl", "dynasty:cinnabar", "dynasty:gold_coin"],
                           (9, -0.40, 4, 0.50, 0, 0, 0, -1, 0.0, 0)),
    "flesh_gamble_dice": ("血肉骰", "Flesh Gamble Dice", "tiger_crest", (0xE0, 0xA0, 0x90),
                          ["dynasty:emperor_bone", "dynasty:gold_coin", "dynasty:cinnabar"],
                          (4, 0.20, -1, 0.0, 0, 0, 0, 4, 0.40, 4)),
    "deathbed_talisman": ("榻前符", "Deathbed Talisman", "talisman_pouch", (0xE0, 0xE0, 0xC0),
                          ["dynasty:talisman_paper", "dynasty:emperor_bone", "dynasty:cinnabar"],
                          (4, 0.30, 3, 0.30, 0, 0, 4, -1, 0.0, 0)),
    "scarlet_lotus": ("血莲", "Scarlet Lotus", "jade_ruyi", (0xE0, 0x70, 0x80),
                      ["dynasty:jade", "dynasty:cinnabar", "dynasty:silk"],
                      (1, 14.0, 5, 0.15, 0, 0, 4, -1, 0.0, 0)),
    "blood_iron_sash": ("血铁腰带", "Blood Iron Sash", "iron_waist_token", (0xA0, 0x60, 0x60),
                        ["dynasty:refined_steel", "dynasty:dragon_scale", "dynasty:silk"],
                        (9, -0.15, 1, 18.0, 0, 0, 0, -1, 0.0, 0)),
    "soul_candle_charm": ("命烛坠", "Soul Candle Charm", "tomb_candle", (0xC8, 0xB0, 0x70),
                          ["dynasty:emperor_bone", "dynasty:cinnabar", "dynasty:talisman_paper"],
                          (9, -0.25, -1, 0.0, 0, 0, 0, 4, 0.28, 2)),
    # ---- 三、天朝敕令（10）：全部用模组自有效果，不碰原版药水 ----
    "edict_of_dragon": ("龙威敕令", "Edict of Dragon Might", "dragon_emperor_seal", (0xE0, 0xC0, 0x60),
                        ["dynasty:dragon_emperor_seal", "dynasty:gold_coin", "dynasty:blueprint"],
                        (4, 0.10, -1, 0.0, 21, 0, 0, -1, 0.0, 0)),
    "edict_of_iron": ("铁壁敕令", "Edict of Iron Wall", "jade_seal", (0xA8, 0xC0, 0xD8),
                      ["dynasty:refined_steel", "dynasty:gold_coin", "dynasty:blueprint"],
                      (1, 8.0, -1, 0.0, 22, 0, 0, -1, 0.0, 0)),
    "edict_of_swift": ("疾风敕令", "Edict of Swift Wind", "official_seal", (0xB8, 0xE0, 0xC0),
                       ["dynasty:zhuque_feather", "dynasty:gold_coin", "dynasty:blueprint"],
                       (3, 0.06, -1, 0.0, 23, 0, 0, -1, 0.0, 0)),
    "edict_of_mandate": ("天命敕令", "Edict of Mandate", "imperial_seal_charm", (0xF0, 0xD8, 0x90),
                         ["dynasty:taiyi_jade", "dynasty:gold_coin", "dynasty:blueprint"],
                         (11, 2.0, -1, 0.0, 25, 0, 0, -1, 0.0, 0)),
    "edict_of_dread": ("威慑敕令", "Edict of Dread", "seal_charm", (0xB0, 0x80, 0x90),
                       ["dynasty:baihu_fang", "dynasty:gold_coin", "dynasty:blueprint"],
                       (4, 0.10, -1, 0.0, 24, 0, 0, -1, 0.0, 0)),
    "edict_of_loyalty": ("忠诚敕令", "Edict of Loyalty", "merit_badge", (0xE8, 0xD0, 0xA0),
                         ["dynasty:gold_seal_charm", "dynasty:gold_coin", "dynasty:blueprint"],
                         (0, 180.0, -1, 0.0, 26, 0, 0, -1, 0.0, 0)),
    "seal_of_two_heavens": ("双天印", "Seal of Two Heavens", "gold_seal_charm", (0xF0, 0xE0, 0xB0),
                            ["dynasty:hunyuan_pearl", "dynasty:gold_coin", "dynasty:blueprint"],
                            (4, 0.12, -1, 0.0, 21, 0, 0, 3, 0.06, 1)),
    "throne_inheritance_charm": ("承天佩", "Throne Inheritance Charm", "dragon_emperor_seal", (0xE0, 0xD0, 0x90),
                                 ["dynasty:taiyi_jade", "dynasty:jade", "dynasty:gold_coin"],
                                 (0, 260.0, -1, 0.0, 25, 0, 0, -1, 0.0, 0)),
    "war_deity_signet": ("战神印", "War Deity Signet", "dragon_king_scale", (0xD0, 0x70, 0x60),
                         ["dynasty:qinglong_scale", "dynasty:gold_coin", "dynasty:blueprint"],
                         (4, 0.15, -1, 0.0, 21, 1, 0, -1, 0.0, 0)),
    "unbroken_wall_charm": ("不倾之壁", "Unbroken Wall Charm", "xuanwu_shell", (0x90, 0xA8, 0x90),
                            ["dynasty:xuanwu_shell", "dynasty:refined_steel", "dynasty:blueprint"],
                            (2, 0.50, -1, 0.0, 22, 1, 0, -1, 0.0, 0)),
    # ---- 四、幽冥献祭（10）：内伤当代价，越痛越狠 ----
    "sacrificial_blade_charm": ("祭刃坠", "Sacrificial Blade Charm", "sword_tassel", (0x90, 0x60, 0x70),
                                ["dynasty:emperor_bone", "dynasty:refined_steel", "dynasty:cinnabar"],
                                (4, 0.38, -1, 0.0, 27, 0, 0, -1, 0.0, 0)),
    "nether_binding_ring": ("幽冥缚戒", "Nether Binding Ring", "dragon_bone_ring", (0x50, 0x50, 0x70),
                            ["dynasty:emperor_bone", "dynasty:cinnabar", "dynasty:dragon_crystal"],
                            (4, 0.40, -1, 0.0, 0, 0, 2, 9, -0.20, 1)),
    "ghost_ferry_tally": ("渡鬼符", "Ghost Ferry Tally", "talisman_pouch", (0x70, 0x80, 0x70),
                          ["dynasty:talisman_paper", "dynasty:emperor_bone", "dynasty:cinnabar"],
                          (5, 0.30, -1, 0.0, 27, 0, 0, 9, -0.25, 0)),
    "bone_chill_pendant": ("寒骨佩", "Bone Chill Pendant", "jade_marrow_charm", (0x88, 0xB0, 0xC0),
                           ["dynasty:emperor_bone", "dynasty:sea_pearl", "dynasty:jade"],
                           (4, 0.25, -1, 0.0, 27, 1, 3, -1, 0.0, 0)),
    "candle_of_the_dead": ("亡者烛", "Candle of the Dead", "tomb_candle", (0x90, 0xB0, 0x80),
                           ["dynasty:emperor_bone", "dynasty:talisman_paper", "dynasty:cinnabar"],
                           (4, 0.30, -1, 0.0, 0, 0, 2, 0, -150.0, 1)),
    "tomb_warden_seal": ("守陵印", "Tomb Warden Seal", "scale_plate", (0x80, 0x90, 0x80),
                         ["dynasty:emperor_bone", "dynasty:refined_steel", "dynasty:gold_coin"],
                         (1, 25.0, -1, 0.0, 27, 0, 0, -1, 0.0, 0)),
    "jade_shroud_charm": ("玉殓佩", "Jade Shroud Charm", "cloud_brocade", (0xA0, 0xC0, 0xA8),
                          ["dynasty:taiyi_jade", "dynasty:silk", "dynasty:emperor_bone"],
                          (0, 400.0, 3, -0.10, 27, 0, 0, -1, 0.0, 0)),
    "karma_ledger_charm": ("因果牒", "Karma Ledger Charm", "bamboo_slip", (0xC8, 0xB8, 0x90),
                           ["dynasty:bamboo_slip", "dynasty:ink_stick", "dynasty:cinnabar"],
                           (4, 0.30, -1, 0.0, 0, 0, 0, 1, 30.0, 4)),
    "abyss_pearl": ("深渊珠", "Abyss Pearl", "sea_pearl", (0x50, 0x70, 0x90),
                    ["dynasty:hunyuan_pearl", "dynasty:sea_pearl", "dynasty:cinnabar"],
                    (4, 0.35, 6, 0.40, 0, 0, 2, -1, 0.0, 0)),
    "underworld_gate_key": ("鬼门钥", "Underworld Gate Key", "dragon_whisker", (0x60, 0x60, 0x80),
                            ["dynasty:emperor_bone", "dynasty:thunder_token", "dynasty:talisman_paper"],
                            (4, 0.45, -1, 0.0, 0, 0, 7, -1, 0.0, 0)),
    # ---- 五、巧匠边塞（10）：条件型小件，看场合戴 ----
    "ranging_compass_charm": ("望距罗盘", "Ranging Compass Charm", "south_pointing_compass", (0xC8, 0xB8, 0x80),
                              ["dynasty:bronze_mirror", "dynasty:jade", "dynasty:refined_steel"],
                              (7, 2.0, 4, 0.08, 0, 0, 0, -1, 0.0, 0)),
    "quickdraw_glove": ("疾抽手套", "Quickdraw Glove", "wrist_guard", (0xC0, 0x90, 0x70),
                        ["dynasty:silk", "dynasty:refined_steel", "dynasty:bamboo_slip"],
                        (5, 0.18, 6, 0.60, 0, 0, 0, -1, 0.0, 0)),
    "siege_hammer_charm": ("破阵锤坠", "Siege Hammer Charm", "war_drum_charm", (0xA0, 0x80, 0x60),
                           ["dynasty:refined_steel", "dynasty:dragon_scale", "dynasty:silk"],
                           (4, 0.25, -1, 0.0, 0, 0, 6, -1, 0.0, 0)),
    "dusk_raider_badge": ("夜袭徽", "Dusk Raider Badge", "tiger_token", (0x80, 0x70, 0xA0),
                          ["dynasty:refined_steel", "dynasty:silk", "dynasty:cinnabar"],
                          (4, 0.20, 3, 0.12, 0, 0, 2, -1, 0.0, 0)),
    "rain_prayer_knot": ("祈雨结", "Rain Prayer Knot", "wine_gourd", (0x80, 0xA8, 0xC8),
                         ["dynasty:silk", "dynasty:talisman_paper", "dynasty:thunder_token"],
                         (5, 0.20, 4, 0.30, 0, 0, 7, -1, 0.0, 0)),
    "diver_signet": ("潜蛟印", "Diver Signet", "sea_conch", (0x70, 0xB0, 0xB0),
                     ["dynasty:sea_conch", "dynasty:sea_pearl", "dynasty:refined_steel"],
                     (1, 20.0, 4, 0.25, 0, 0, 3, -1, 0.0, 0)),
    "cavalry_sash": ("铁骑带", "Cavalry Sash", "horse_stirrup", (0xB0, 0x88, 0x60),
                     ["dynasty:silk", "dynasty:refined_steel", "dynasty:dragon_scale"],
                     (4, 0.15, 3, 0.10, 0, 0, 5, -1, 0.0, 0)),
    "wound_binder_charm": ("绷带佩", "Wound Binder Charm", "knee_guard", (0xE0, 0xD8, 0xC8),
                           ["dynasty:silk", "dynasty:talisman_paper", "dynasty:jade"],
                           (1, 25.0, 5, 0.18, 0, 0, 4, -1, 0.0, 0)),
    "iron_ration_charm": ("军粮坠", "Iron Ration Charm", "bear_paw", (0xC8, 0xB0, 0x88),
                          ["dynasty:bamboo_slip", "dynasty:silk", "dynasty:gold_coin"],
                          (0, 350.0, 5, -0.08, 0, 0, 0, -1, 0.0, 0)),
    "warlord_drum_charm": ("战鼓墩", "Warlord Drum Charm", "war_drum_charm", (0xC0, 0x60, 0x50),
                           ["dynasty:refined_steel", "dynasty:silk", "dynasty:dragon_crystal"],
                           (5, 0.12, -1, 0.0, 0, 0, 6, 4, 0.40, 4)),
}

ATTR_CODES = {-1, 0, 1, 2, 3, 4, 5, 6, 7, 9, 11}
EFFECT_CODES = {0, 21, 22, 23, 24, 25, 26, 27}
COND_CODES = {0, 1, 2, 3, 4, 5, 6, 7}
ON_HIT_CODES = {0, 1, 2, 3, 4, 5, 6}
ON_HIT_NAMES = {0: "无", 1: "吸血", 2: "斩杀", 3: "会心", 4: "突袭", 5: "连击", 6: "雷罚"}
# 每类命中触发的「设计上下限」：值、概率（%）
ON_HIT_RANGE = {
    1: (0.05, 0.25, 30, 100),     # 吸血：按伤害回血的比例
    2: (0.08, 0.30, 30, 100),     # 斩杀：血线
    3: (0.20, 0.60, 10, 40),      # 会心：额外伤害倍率 / 概率
    4: (0.20, 0.40, 80, 100),     # 突袭：只在目标满血时（第一刀）
    5: (0.03, 0.08, 100, 100),    # 连击：每层倍率
    6: (30.0, 120.0, 15, 40),     # 雷罚：附加固定伤害
}

# 命中触发（第 12~14 格）：(编码, 数值, 概率%)。没有的饰品不写，出表时补 0。
# 只给「主题对得上」的饰品：血系给吸血 / 斩杀，幽系给雷罚，昼夜给突袭 / 会心，边塞给连击。
ON_HIT = {
    # ---- 生死代价：吸血与斩杀 ----
    "lifedrain_ring": (1, 0.12, 100),
    "blood_oath_seal": (1, 0.15, 100),
    "crimson_pact_charm": (1, 0.20, 60),
    "soul_candle_charm": (1, 0.10, 50),
    "bone_reaper_tally": (2, 0.20, 100),
    "deathbed_talisman": (2, 0.25, 60),
    # ---- 幽冥献祭：雷罚与斩杀 ----
    "sacrificial_blade_charm": (2, 0.18, 80),
    "ghost_ferry_tally": (2, 0.15, 60),
    "underworld_gate_key": (6, 90.0, 25),
    "nether_binding_ring": (6, 60.0, 30),
    "bone_chill_pendant": (6, 45.0, 35),
    "abyss_pearl": (3, 0.50, 30),
    # ---- 昼夜双生：突袭（第一刀）与会心 ----
    "dawn_blade_charm": (4, 0.35, 100),
    "night_heron_feather": (4, 0.30, 100),
    "dusk_veil_charm": (3, 0.45, 25),
    "eclipse_bead": (3, 0.55, 20),
    "starless_night_ring": (1, 0.08, 100),
    # ---- 天朝敕令 / 巧匠边塞：会心与连击 ----
    "war_deity_signet": (3, 0.40, 30),
    "edict_of_dread": (2, 0.10, 100),
    "quickdraw_glove": (5, 0.05, 100),
    "warlord_drum_charm": (5, 0.06, 100),
    "siege_hammer_charm": (2, 0.12, 80),
}

# 连携（第 15 格 = 组号）：同系一起戴才有加成，集齐越多档位越高（**取达到的最高档，不叠层**）
LINK_GROUPS = {
    1: ("昼夜双生", [
        "dawn_blade_charm", "dusk_veil_charm", "noon_pendant", "moonlit_mirror", "sun_chaser_ring",
        "night_heron_feather", "twilight_cicada", "eclipse_bead", "dawn_drum", "starless_night_ring",
    ]),
    2: ("生死代价", [
        "blood_oath_seal", "bone_reaper_tally", "internal_injury_talisman", "lifedrain_ring",
        "crimson_pact_charm", "flesh_gamble_dice", "deathbed_talisman", "scarlet_lotus",
        "blood_iron_sash", "soul_candle_charm",
    ]),
    3: ("天朝敕令", [
        "edict_of_dragon", "edict_of_iron", "edict_of_swift", "edict_of_mandate", "edict_of_dread",
        "edict_of_loyalty", "seal_of_two_heavens", "throne_inheritance_charm", "war_deity_signet",
        "unbroken_wall_charm",
    ]),
    4: ("幽冥献祭", [
        "sacrificial_blade_charm", "nether_binding_ring", "ghost_ferry_tally", "bone_chill_pendant",
        "candle_of_the_dead", "tomb_warden_seal", "jade_shroud_charm", "karma_ledger_charm",
        "abyss_pearl", "underworld_gate_key",
    ]),
    5: ("巧匠边塞", [
        "ranging_compass_charm", "quickdraw_glove", "siege_hammer_charm", "dusk_raider_badge",
        "rain_prayer_knot", "diver_signet", "cavalry_sash", "wound_binder_charm", "iron_ration_charm",
        "warlord_drum_charm",
    ]),
}
LINK_OF = {tid: gid for gid, (_name, _ids) in LINK_GROUPS.items() for tid in _ids}

# 连携加成：(组, 需要件数, 类型, 编码, 数值, 条件)  类型 0 = 属性（编码同属性表）/ 1 = 模组效果（数值 = 等级）
LINKS = [
    # 昼夜双生：越齐全，白天黑夜都强
    (1, 2, 0, 3, 0.05, 0),
    (1, 3, 0, 4, 0.08, 0), (1, 3, 0, 3, 0.05, 0),
    (1, 4, 0, 4, 0.12, 0), (1, 4, 0, 3, 0.08, 0),
    # 生死代价：越押越狠，4 件回一点血作补偿
    (2, 2, 0, 4, 0.06, 0),
    (2, 3, 0, 4, 0.12, 0),
    (2, 4, 0, 4, 0.16, 0), (2, 4, 0, 0, 200.0, 0),
    # 天朝敕令：3 件起功名气运，4 件常驻龙威
    (3, 2, 0, 11, 2.0, 0),
    (3, 3, 0, 11, 3.0, 0), (3, 3, 0, 0, 200.0, 0),
    (3, 4, 1, 21, 0.0, 0), (3, 4, 0, 4, 0.10, 0),
    # 幽冥献祭：幽气越重，伤害越高、血越厚
    (4, 2, 0, 4, 0.08, 0),
    (4, 3, 0, 4, 0.12, 0),
    (4, 4, 0, 4, 0.16, 0), (4, 4, 0, 0, 250.0, 0),
    # 巧匠边塞：手脚越快，伸得越远
    (5, 2, 0, 5, 0.06, 0),
    (5, 3, 0, 5, 0.10, 0), (5, 3, 0, 3, 0.06, 0),
    (5, 4, 0, 5, 0.14, 0), (5, 4, 0, 7, 1.0, 0),
]


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def tint(src, dst, color):
    """把来源贴图按颜色染色（保留像素透明度）/ tint a copy of the source texture."""
    if not os.path.exists(src):
        print("!! 缺少源贴图", src)
        return False
    image = Image.open(src).convert("RGBA")
    r, g, b = color
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            pr, pg, pb, pa = pixels[x, y]
            if pa == 0:
                continue
            pixels[x, y] = (min(255, (pr * r) // 255), min(255, (pg * g) // 255),
                            (pb * b) // 255, pa)
    image.save(dst)
    return True


def num(value):
    return "%g" % value


def check_spec(tid, spec):
    """新格式自检：编码越界、数值写串、命中触发参数越界，都直接拦下。"""
    if len(spec) != 14:
        return ["%s 的 spec 不是 14 格（10 格属性 + 3 格命中 + 1 格连携组）：%r" % (tid, spec)]
    problems = []
    (a1, v1, a2, v2, effect, level, condition,
     a3, v3, condition3, on_hit, on_hit_value, on_hit_chance, link) = spec
    if link != 0 and link not in LINK_GROUPS:
        problems.append("%s 的连携组 %s 没定义（见 LINK_GROUPS）" % (tid, link))
    for code in (a1, a2, a3):
        if code not in ATTR_CODES:
            problems.append("%s 用了未知属性编码 %s" % (tid, code))
    if effect not in EFFECT_CODES:
        problems.append("%s 用了未登记的效果编码 %s（新饰品只用 21~27 的模组效果）" % (tid, effect))
    for cond in (condition, condition3):
        if cond not in COND_CODES:
            problems.append("%s 用了未知条件编码 %s" % (tid, cond))
    if not 0 <= level <= 3:
        problems.append("%s 的效果等级 %s 超出 0~3" % (tid, level))
    if abs(v1) > 500 or abs(v3) > 500:
        problems.append("%s 的数值过大（%s / %s），确认是不是把百分比写成了点数" % (tid, v1, v3))
    if on_hit not in ON_HIT_CODES:
        problems.append("%s 用了未知的命中触发编码 %s（1 吸血 2 斩杀 3 会心 4 突袭 5 连击 6 雷罚）"
                        % (tid, on_hit))
    elif on_hit != 0:
        low, high, min_chance, max_chance = ON_HIT_RANGE[on_hit]
        if not low <= on_hit_value <= high:
            problems.append("%s 的「%s」数值 %s 超出设计范围 %s ~ %s"
                            % (tid, ON_HIT_NAMES[on_hit], on_hit_value, low, high))
        if not min_chance <= on_hit_chance <= max_chance:
            problems.append("%s 的「%s」概率 %s%% 超出设计范围 %s ~ %s%%"
                            % (tid, ON_HIT_NAMES[on_hit], on_hit_chance, min_chance, max_chance))
    return problems


def main():
    items = {os.path.basename(f)[:-5] for f in os.listdir(os.path.join(ASSETS, "models/item"))}
    problems = []
    for tid in ON_HIT:
        if tid not in TRINKETS:
            problems.append("ON_HIT 里的 %s 不在 TRINKETS 表里（拼错了？）" % tid)
    for tid, (zh, en, source, color, materials, spec) in TRINKETS.items():
        problems += check_spec(tid, spec + ON_HIT.get(tid, (0, 0.0, 0)) + (LINK_OF.get(tid, 0),))

    # 连携表自检：组必须存在、件数不超过该组件数、属性 / 效果编码必须已在别处登记
    for group, need, kind, code, value, _condition in LINKS:
        if group not in LINK_GROUPS:
            problems.append("连携表里的组 %s 没定义" % group)
            continue
        if not 2 <= need <= len(LINK_GROUPS[group][1]):
            problems.append("连携表 %s 的档位 %d 件不合理（该组只有 %d 件）"
                            % (LINK_GROUPS[group][0], need, len(LINK_GROUPS[group][1])))
        if kind == 0 and code not in ATTR_CODES - {-1}:
            problems.append("连携表 %s 用了未知属性编码 %s" % (LINK_GROUPS[group][0], code))
        if kind == 1 and code not in EFFECT_CODES - {0}:
            problems.append("连携表 %s 用了未登记的效果编码 %s" % (LINK_GROUPS[group][0], code))
        if kind == 1 and not 0.0 <= value <= 3.0:
            problems.append("连携表 %s 的效果等级 %s 超出 0~3" % (LINK_GROUPS[group][0], value))
        if kind == 0 and abs(value) > 500.0:
            problems.append("连携表 %s 的数值 %s 过大（百分比写成点数了？）" % (LINK_GROUPS[group][0], value))
        dst = os.path.join(ASSETS, "textures/item/%s.png" % tid)
        src = os.path.join(ASSETS, "textures/item/%s.png" % source)
        if not os.path.exists(dst) and not tint(src, dst, color):
            problems.append("%s 的源贴图 %s 不存在" % (tid, source))
        write(os.path.join(ASSETS, "models/item/%s.json" % tid),
              {"parent": "minecraft:item/generated",
               "textures": {"layer0": "dynasty:item/%s" % tid}})
        for material in materials:
            namespace, path = material.split(":")
            if namespace == "dynasty" and path not in items:
                problems.append("%s 的配方材料不存在：%s" % (tid, material))
        write(os.path.join(DATA, "recipes/%s.json" % tid),
              {"type": "minecraft:crafting_shapeless",
               "ingredients": [{"item": item} for item in materials],
               "result": {"item": "dynasty:%s" % tid}})
    print("饰品扩充：%d 件（贴图 / 模型 / 配方）" % len(TRINKETS))

    for filename, index in (("zh_cn.json", 0), ("en_us.json", 1)):
        path = os.path.join(ASSETS, "lang", filename)
        data = json.load(open(path, encoding="utf-8"))
        for tid, values in TRINKETS.items():
            data["item.dynasty.%s" % tid] = values[0] if index == 0 else values[1]
        write(path, data)

    tag = json.load(open(CURIOS, encoding="utf-8"))
    values = tag.get("values", [])
    added = 0
    for tid in TRINKETS:
        entry = "dynasty:%s" % tid
        if entry not in values:
            values.append(entry)
            added += 1
    tag["values"] = values
    write(CURIOS, tag)
    from gen_curios import build as build_curios
    build_curios()
    print("Curios 标签新增 %d 条（合计 %d 件饰品）" % (added, len(values)))

    print("\n--- EXTRA_TABLE 追加行（Java，15 格新格式，可直接粘贴）---")
    for tid, values in TRINKETS.items():
        a1, v1, a2, v2, effect, level, condition, a3, v3, condition3 = values[5]
        on_hit, on_hit_value, on_hit_chance = ON_HIT.get(tid, (0, 0.0, 0))
        print('            {"%s", %d, %sD, %d, %sD, %d, %d, %d, %d, %sD, %d, %d, %sD, %d, %d},'
              % (tid, a1, num(v1), a2, num(v2), effect, level, condition,
                 a3, num(v3), condition3, on_hit, num(on_hit_value), on_hit_chance,
                 LINK_OF.get(tid, 0)))

    print("\n--- LINK_TABLE 行（连携加成，Java，可直接粘贴）---")
    for group, need, kind, code, value, condition in LINKS:
        print('            {%d, %d, %d, %d, %sD, %d},'
              % (group, need, kind, code, num(value), condition))

    counts = {}
    for tid in ON_HIT:
        counts[ON_HIT[tid][0]] = counts.get(ON_HIT[tid][0], 0) + 1
    print("\n命中触发分布：" + "、".join(
        "%s %d 件" % (ON_HIT_NAMES[code], counts[code]) for code in sorted(counts)))
    print("连携：" + "、".join(
        "%s %d 件（%d 档加成）" % (name, len(ids), len([r for r in LINKS if r[0] == gid]))
        for gid, (name, ids) in sorted(LINK_GROUPS.items())))

    if problems:
        print("\n问题 ❌")
        for problem in problems:
            print("   -", problem)
        raise SystemExit(1)
    print("\n饰品扩充完成 ✅")


if __name__ == "__main__":
    main()
