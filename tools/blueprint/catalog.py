#!/usr/bin/env python3
"""Reproducible, read-only source audit and cod1 content-definition catalogue.

The catalogue is a planning/audit artifact, never a runtime registration file.
Only --generate writes generated reports under docs/blueprint-cod1. Existing
implementation evidence is preserved on regeneration; baseline evidence is frozen.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import struct
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/blueprint-cod1"
DEFAULT_SOURCE = Path("/Users/a15356015027/Desktop/code x提示词/cod1.txt")
COUNTS = {"BASIC": 30, "ELITE": 15, "BOSS": 12, "ARTIFACT": 25, "PHANTOM": 12}

# These are proposed namespaced IDs, not aliases for superficially similar old units.
IDS = {
    "BASIC": """zuwu_daoshou juma_changqiangbing liannu_zhenzu ludun_jiashi fufa_jijiu
tiesuo_chihou kuijun_sishi zhenwang_zhangqiguan pijia_panjiang_huwei yinbing_guizu
shibian_lishi fuhun_baibu_tongzi zhiren_jianke muxue_feilu shanjing_shanxiao
chimu_zhuha kumu_shujing mingsha_shixie bishui_xuanjiao_youzi jubi_shigandang
xunshan_mujiaquan qingtong_shuangtoushekui bazu_digongzhu youdeng_guimianfu
xueju_mangguyu shashui_funigui juli_bixi_kuilei baimu_mowu tongbi_feitian_yecha
yinyang_zhijiao_youhun""".split(),
    "ELITE": """xianzhen_duantoujiang guiche_jiushouniao qianji_bailian_yanshi
pilin_zhijinwu baimian_huxiangu juchui_jinjia_lishi gudu_tianzhunv yinyang_liandan_fangshi
fubo_xunhai_yecha banshan_jiazhou_shikuang mojia_jueying_cike hanshan_tongjia_juyuan
qingdeng_panguan_guichai liefeng_jindiao_yushi zhenmu_suanni_tonghou""".split(),
    "BOSS": """taoyan_zhishi gongsun_wuwang luban_yisha zhuyin_cantui zhaoming_di
shemu_niangniang heifeng_fawang xingtian_yiwei leize_juling bian_mingzhou
xuantian_jiansha hunyuan_zushou""".split(),
    "ARTIFACT": """longyin_zhanma_duanyue_dao zhanlu_rendao_bamian_jian jiuqu_tougu_hongying_qiang
fangtian_luanshi_pojun_ji zhuri_liujin_luoxing_gong tianji_xiashi_shenji_nu
jinghong_liuyun_jinsi_shan zhenyue_jiulong_shouming_yin zhaodan_tongyou_bagua_jing
jingshi_taigu_chenzhong qianji_luosha_bairen_san guangling_yixiang_jiuxiao_qin
juebi_chunqiu_panguan_bi fulong_suohun_xuantie_lian kuafu_zhuri_zhuiguang_zhang
bagua_zijin_feilong_hu fuxi_lianshan_guizang_yi pozhen_honglei_shengtie_chong
zhanye_zhuxie_shuangliuye bixie_baiyu_zhenhun_xiao fanjiang_daohai_huntian_ling
quxie_fumo_jingang_chu qingfu_jubao_jincuo_dao youdu_wangchuan_zhaohun_fan
qiankun_yinyang_liangjie_huan""".split(),
    "PHANTOM": """juling_kaishan_shenshou mingjing_zhaoshi_fashen santan_haihui_santou_liubi_faxiang
xuanwu_panshi_fudi_zhenying taibai_jianxian_qiling_chuqiao jiutian_xuannv_yintianxing
xiongsha_baihu_lietianying fuxi_bagua_kaitianzhi shanggu_kuafu_zhuri_benying
wangchuan_baidu_youmingke mojia_juzi_qianshou_tiangongshu liehuo_zhurong_jiulong_raoti_shenxiang""".split(),
}

# Eligibility is proposed until a tagged location/marker has been implemented.
# id | tag | strategy | min | max | cap | light | time | height | extra constraint
BASIC_SEEDS = """
battlefield_outer|STRUCTURE|2|4|8|0:15|ALL_NIGHT_PREFERRED|SURFACE|Structure footprint required; never unrestricted plains
fortress_gate|STRUCTURE_ENCOUNTER|1|3|5|0:15|ALL|SURFACE|Guard gate with shield/ranged allies; rare natural hook disabled
watchtower_wall|STRUCTURE_MARKER|1|3|5|0:15|ALL|ELEVATED_MARKER|Defensive high-ground marker and clear firing line
formation_corridor|ENCOUNTER|1|1|2|0:15|ALL|STRUCTURE_FLOOR|One shield with 2-4 ranged/support allies
corrupted_altar|STRUCTURE_ENCOUNTER|1|1|2|0:15|NIGHT_OR_LOW_LIGHT|STRUCTURE_FLOOR|Night/low-light weighting; legal buff ally required
mountain_pass|STRUCTURE_REGION|1|2|4|0:15|ALL|SURFACE|Forest/mountain pass; avoid cramped caves
scorched_graves|STRUCTURE_ENCOUNTER|2|4|8|0:7|NIGHT_OR_LOW_LIGHT|SURFACE|Rebel event only within battlefield/grave region
war_banner_core|ENCOUNTER_ONLY|1|1|1|0:15|ALL|STRUCTURE_FLOOR|One banner per combat group; no standalone natural spawn
rebel_armory|STRUCTURE_MARKER|1|2|2|0:15|ALL|STRUCTURE_FLOOR|Room/local cap; no general wilderness spawn
haunted_battlefield|STRUCTURE_REGION|2|5|8|0:7|NIGHT_OR_LOW_LIGHT|SURFACE_OR_UNDERGROUND|Constrained haunt region; cannot phase through terrain
wet_tomb|STRUCTURE_MARKER|1|2|3|0:7|ALL_LOW_LIGHT|UNDERGROUND|Damp tomb antechamber or hanging-coffin cliff marker
village_well_shrine|STRUCTURE_EVENT|1|1|2|0:7|NIGHT_OR_LOW_LIGHT|STRUCTURE_FLOOR|Second child only in explicit event
mortuary_paper_room|STRUCTURE_ONLY|1|3|4|0:7|ALL_LOW_LIGHT|STRUCTURE_FLOOR|No normal-village spawn
tomb_roof|STRUCTURE_REGION|1|3|4|0:7|ALL_LOW_LIGHT|UNDERGROUND|Adequate flight space under roof
forest_cliff|NATURAL_ECOLOGY|1|3|6|0:15|DUSK_NIGHT_PREFERRED|SURFACE|Forest/mountain terrain with climbable relief
wetland_water|NATURAL_ECOLOGY|1|2|4|0:15|ALL|SURFACE_OR_CAVE_WATER|Water-adjacent wetland or dark cave pool
deadwood_forest|NATURAL_ECOLOGY|1|2|4|0:15|ALL|SURFACE|Camouflage-valid wood/soil site, no exposed stone flat
sand_ravine|NATURAL_ECOLOGY|1|2|4|0:15|ALL|SURFACE|Sand/gravel substrate in dry valley
hidden_river_pool|NATURAL_ECOLOGY|1|2|3|0:15|ALL|SURFACE_OR_CAVE_WATER|Deep pool/underground river or waterfall basin
stone_gate|STRUCTURE_MARKER|1|1|2|0:15|ALL|STRUCTURE_FLOOR|Gate/crossroads/spirit-way marker
mechanism_perimeter|STRUCTURE_ONLY|1|3|5|0:15|ALL|STRUCTURE_FLOOR|Workshop or mechanism-city patrol marker
mechanism_drain|STRUCTURE_ONLY|1|2|3|0:7|ALL_LOW_LIGHT|UNDERGROUND|Drain/trap chamber; body turning clearance
mining_quarry|STRUCTURE_REGION|1|2|3|0:7|ALL_LOW_LIGHT|UNDERGROUND|Mine/quarry or lower workshop; terrain grief disabled
dark_cavern_roof|NATURAL_ECOLOGY|1|3|5|0:7|ALL_LOW_LIGHT|UNDERGROUND|Large cavern free flight volume
geothermal_spirit_vein|STRUCTURE_REGION|1|2|3|0:7|ALL_LOW_LIGHT|DEEP_UNDERGROUND|Geothermal/spirit-vein region, not arbitrary caves
stagnant_shipwreck|STRUCTURE_REGION|1|2|4|0:7|NIGHT_OR_LOW_LIGHT|UNDERWATER|Stagnant water/swamp bottom/moat/wreck
stele_spirit_way|STRUCTURE_ONLY|1|1|2|0:15|ALL|STRUCTURE_FLOOR|End of spirit way/stele forest/shrine marker
bone_pit_cellar|STRUCTURE_ONLY|1|2|3|0:7|ALL_LOW_LIGHT|DEEP_UNDERGROUND|Bone pit/alchemy cellar/deep fracture marker
abyss_cliff_walkway|STRUCTURE_REGION|1|2|3|0:7|ALL_LOW_LIGHT|CLIFF_AIR|Cliff/walkway/imperial tomb edge, flight clearance
midnight_funeral_road|STRUCTURE_EVENT|1|1|1|0:7|MIDNIGHT|SURFACE|Midnight pass or graveyard crossroads; event cap one
""".strip().splitlines()

ELITE_LOCATIONS = [
    ("古战场/大型军阵遗迹", "古战场稀有事件", "STRUCTURE_OR_RARE_EVENT"),
    ("高空山岭", "阴气古战场上空", "RARE_FLIGHT_EVENT"),
    ("机关遗迹/机关城", "相关机关工坊", "FIXED_STRUCTURE_ELITE"),
    ("帝陵/大型墓宫中层", "关键墓门", "FIXED_GUARD"),
    ("深山古寺/幻境区域", "同类结构稀有点", "RARE_STRUCTURE_ELITE"),
    ("帝陵/宫殿墓室", "重要墓门", "FIXED_GUARD"),
    ("毒沼/苗窟/深洞毒巢", "毒巢外围", "NEST_ELITE"),
    ("废弃道观/丹房/仙观", "炼丹稀有事件", "STRUCTURE_OR_RARE_EVENT"),
    ("大型河湖/水下遗迹", "海岸/水府", "WATER_STRUCTURE_ELITE"),
    ("古墓深层/重型陪葬区", "封闭陪葬室", "FIXED_STRUCTURE_ELITE"),
    ("机关遗迹/地下密道", "军械/墨家结构", "FIXED_STRUCTURE_ELITE"),
    ("高山/巨人庭院", "古代重型遗迹周边", "RARE_STRUCTURE_ELITE"),
    ("阴司/枉死城相关结构", "阴司审判场", "FIXED_STRUCTURE_ELITE"),
    ("雪山/高峰", "悬崖神殿", "RARE_STRUCTURE_ELITE"),
    ("帝陵/机关城", "重要墓门/核心机关区", "FIXED_GUARD"),
]
BOSS_TRIGGERS = [
    "进入核心祭坑并完成祭祀/机关", "古战场推进至大帐/瓮城", "悬空机关核心/结构Boss触发器",
    "进入玄潭核心并完成前置触发", "打开九重棺椁/帝棺", "完成苗窟前置机关后抵达血祭化龙潭",
    "完成残寺封印/经幢前置后进入平台", "恢复/破坏锻造核心机关", "神域祭坛引雷前置（细则待确认）",
    "忘川渡口阴司事件前置（细则待确认）", "拔出/触碰核心封魔剑", "四象贡品齐备；候选身份与入口须确认",
]
ANCHORS = """HEAD_ABOVE PLAYER_OVERLAY BACK_ABOVE GROUND_RISE WEAPON_ORIGIN SKY_ANCHOR
SHADOW_ORIGIN TARGET_ABOVE SIDE_RUNNING GROUND_PASS_THROUGH BACK_MECHANICAL_RING ORBIT_PLAYER""".split()
PHANTOM_ARTIFACTS = [1, 2, 4, 8, None, None, 3, 17, 15, 24, 6, None]
PHANTOM_TRIGGERS = ["断岳千重浪", "普通挥剑/格挡/受创", "无双乱舞破军阵", "泰山压顶", "击退/挑空后追击",
                    "拉弓/引雷锁定", "回马夺命扎/冲刺突刺", "大衍之数推演指向", "疾跑冲锋/杖击",
                    "百鬼夜行·借道", "破甲床弩轰", "烈火横扫"]

REUSE = {
    "BASIC": {1: ["rebel_soldier"], 2: ["imperial_soldier"], 3: ["archer"], 4: ["royal_guard"],
              5: ["thunder_envoy"], 6: ["assassin"], 9: ["royal_guard"], 10: ["soul_soldier"],
              15: ["nine_tailed_fox"], 19: ["merfolk"], 24: ["phoenix"]},
    "ELITE": {1: ["rebel_general"], 2: ["phoenix"], 4: ["royal_guard"], 5: ["nine_tailed_fox"],
              8: ["eunuch_mastermind"], 9: ["merfolk"], 11: ["assassin"], 13: ["soul_soldier"],
              14: ["archer"]},
    "BOSS": {5: ["undead_first_emperor", "dragon_emperor"], 9: ["nine_heaven_general"],
             10: ["dragon_king"], 12: ["zhenyuan_sovereign"]},
    "ARTIFACT": {1: ["zhanma_dao", "qinglong_dao"], 2: ["longyuan_sword"], 3: ["bawang_spear"],
                 4: ["halberd_fangtian"], 5: ["houyi_bow", "sunbow"], 7: ["zhuque_fan"],
                 13: ["chiling_brush"], 15: ["hunyuan_staff"], 20: ["yu_di"]},
    "PHANTOM": {1: ["qinglong_dao"], 6: ["houyi_bow"], 12: ["qinglong_dao"]},
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def field(block: str, name: str) -> str | None:
    match = re.search(r"^- \*\*" + re.escape(name) + r"\*\*：(.+)$", block, re.M)
    return match.group(1) if match else None


def read_spec(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    categories = iter(COUNTS)
    category = None
    entries = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^# 第[一二三四五]项：", line):
            category = next(categories)
        if line.startswith("===") and i > 1470:
            break
        match = re.match(r"^### (?:Boss )?(\d+)[.：] ?(.+)$", line)
        if not match or category is None:
            continue
        number = int(match.group(1))
        end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith("### ") or lines[j].startswith("# ") or lines[j].startswith("===")), len(lines))
        block = "\n".join(lines[i:end])
        title = match.group(2)
        name = title.split("（", 1)[0].removeprefix("【").removesuffix("】")
        arena = re.search(r"\*\*Boss场地【([^】]+)】\*\*", block)
        skills = re.findall(r"\*\*(?:特殊能力|主动能力|被动能力|技能[一二三]|技能\d+)[^【\n]*【([^】]+)】", block)
        # Boss skill names use italic, not bold.
        skills += re.findall(r"\*技能\d+【([^】]+)】", block)
        entries.append({"category": category, "number": number, "name": name, "sourceLine": i + 1,
                        "sourceEndLine": end, "sourceBlockSha256": hashlib.sha256(block.encode()).hexdigest(),
                        "sourceLocation": field(block, "出现区域"), "sourceObtain": field(block, "获得场景"),
                        "sourceDrops": field(block, "掉落物"), "sourceArtifact": field(block, "对应神器"),
                        "sourceAnchor": field(block, "出现位置"), "sourceBody": field(block, "体型") or field(block, "外形与体型") or field(block, "基础与模型特征"),
                        "arenaName": arena.group(1) if arena else None, "skills": list(dict.fromkeys(skills))})
    assert collections.Counter(e["category"] for e in entries) == COUNTS, "Blueprint section counts changed"
    return entries


def probe(path: str) -> dict:
    file = ROOT / path
    return {"path": path, "exists": file.is_file(), "sha256": digest(file) if file.is_file() else None}


def reuse_reference(old: str, category: str) -> dict:
    entity = category in ("BASIC", "ELITE", "BOSS")
    source = "src/main/java/com/dynasty/"
    if not entity:
        paths = [source + "DynastyWeapons.java"]
        if old == "qinglong_dao":
            paths += [source + "QinglongDescent.java", source + "client/ImperialWeaponRenderer.java", source + "GuanYuAvatarShape.java"]
        if old in ("houyi_bow", "sunbow"):
            paths += [source + "DynastyBowRitual.java", source + "client/HouyiAvatarRenderer.java"]
    elif old == "zhenyuan_sovereign":
        paths = [source + "ritual/ZhenyuanBosses.java", source + "ritual/ZhenyuanSovereign.java", source + "ritual/client/ZhenyuanBossModel.java"]
    else:
        owner = "DynastyMobs"
        if old in ("rebel_general", "eunuch_mastermind", "dragon_emperor", "nine_heaven_general", "dragon_king"):
            owner = "DynastyBosses"
        elif old in ("phoenix", "nine_tailed_fox"):
            owner = "DynastyBeasts"
        elif old in ("merfolk", "soul_soldier", "thunder_envoy"):
            owner = "DynastyRealmMobs"
        elif old in ("imperial_soldier", "undead_first_emperor"):
            owner = {"imperial_soldier": "ImperialSoldier", "undead_first_emperor": "UndeadFirstEmperor"}[old]
        paths = [source + "entity/DynastyEntities.java", source + "entity/" + owner + ".java"]
    resource = ("src/main/resources/data/dynasty/loot_tables/entities/" + old + ".json") if entity else ("src/main/resources/assets/dynasty/models/item/" + old + ".json")
    return {"id": "dynasty:" + old, "relationship": "REFERENCE_ONLY_NOT_SAME_CONTENT", "sources": [probe(p) for p in paths], "resources": [probe(resource)]}


def tagref(tag: str, kind: str = "structure", proposed: bool = True) -> dict:
    namespace, name = tag.split(":", 1)
    path = f"src/main/resources/data/{namespace}/tags/worldgen/{kind}/{name}.json"
    exists = (ROOT / path).is_file()
    return {"id": f"#{tag}", "kind": kind, "status": "EXISTS" if exists else "PROPOSED_PENDING",
            "path": path, "exists": exists, "activeForThisEntry": False}


def artifacts_for(identity: str, category: str) -> dict:
    suffix = identity.split(":", 1)[1]
    result = {"implementationClass": [], "skillClasses": [], "renderer": []}
    if category == "PHANTOM":
        result.update({"geo": [], "animation": [], "texture": [], "loot": [], "spawn": []})
    elif category == "ARTIFACT":
        result.update({"itemModel": [probe(f"src/main/resources/assets/dynasty/models/item/{suffix}.json")],
                       "texture": [probe(f"src/main/resources/assets/dynasty/textures/item/{suffix}.png")],
                       "rewardHook": [], "recipe": []})
    else:
        result.update({"geo": [probe(f"src/main/resources/assets/dynasty/geo/{suffix}.geo.json")],
                       "animation": [probe(f"src/main/resources/assets/dynasty/animations/{suffix}.animation.json")],
                       "texture": [probe(f"src/main/resources/assets/dynasty/textures/entity/{suffix}.png")],
                       "loot": [probe(f"src/main/resources/data/dynasty/loot_tables/entities/{suffix}.json")],
                       "spawn": []})
    return result


def attributes(spec: dict) -> dict:
    return {"status": "PENDING_TIER_BALANCE", "MAX_HEALTH": None, "ATTACK_DAMAGE": None, "ARMOR": None,
            "ARMOR_TOUGHNESS": None, "MOVEMENT_SPEED": None, "FOLLOW_RANGE": None, "KNOCKBACK_RESISTANCE": None,
            "FLYING_SPEED": None, "ATTACK_KNOCKBACK": None, "XP_REWARD": None,
            "entityDimensions": {"width": None, "height": None, "sourceLine": spec["sourceLine"]},
            "immunities": {"fire": "PENDING_SPEC_REVIEW", "water": "PENDING_SPEC_REVIEW", "fall": "PENDING_SPEC_REVIEW"},
            "reason": "Stage0 records required fields, not invented live stats. Calibrate against existing weapons/armor and phase DPS before implementation."}


def definition(spec: dict) -> dict:
    category, number = spec["category"], spec["number"]
    identity = "dynasty:" + IDS[category][number - 1]
    dimension = "minecraft:overworld"
    if category == "ELITE" and number == 13 or category == "BOSS" and number == 10:
        dimension = "dynasty:underworld"
    if category == "BOSS" and number == 9 or category == "ARTIFACT" and number == 25:
        dimension = "dynasty:jiuxiao"
    if category == "BOSS" and number == 12:
        dimension = "dynasty:zhenyuan_arena"
    data = {"id": identity, "name": spec["name"], "category": category, "number": number,
            "source": {"line": spec["sourceLine"], "endLine": spec["sourceEndLine"], "sha256": spec["sourceBlockSha256"]},
            "auditStatus": "MISSING", "implementationStatus": "NOT_STARTED", "exactExistingId": None,
            "reuseCandidates": [reuse_reference(old, category) for old in REUSE.get(category, {}).get(number, [])],
            "resources": artifacts_for(identity, category), "requiredSkills": spec["skills"],
            "definitionStatus": "PROPOSED_PENDING_IMPLEMENTATION", "naturalSpawnActive": False,
            "acquisitionActive": False, "questNode": {"id": "dynasty:cod1/" + IDS[category][number - 1], "status": "PROPOSED_PENDING"},
            "dropsReward": {"sourceText": spec["sourceDrops"], "status": "PENDING_REGISTERED_ITEM_AND_USE_MAPPING"},
            "verification": {"singlePlayer": "NOT_RUN", "twoPlayer": "NOT_RUN", "screenshots": [], "note": "未实机验证"}}
    if category in ("BASIC", "ELITE", "BOSS"):
        data["attributes"] = attributes(spec)
    if category == "BASIC":
        location, mode, low, high, cap, light, time, height, extra = BASIC_SEEDS[number - 1].split("|")
        biome_tags = []
        if number in (6, 15, 17):
            biome_tags = [tagref("minecraft:is_forest", "biome", False)]
            biome_tags[0].update(status="VANILLA_TAG", exists=True, path=None)
        if number == 18:
            biome_tags = [tagref("minecraft:is_badlands", "biome", False)]
            biome_tags[0].update(status="VANILLA_TAG", exists=True, path=None)
        underground = height in ("UNDERGROUND", "DEEP_UNDERGROUND")
        data["spawn"] = {"dimension": dimension, "regionDescription": spec["sourceLocation"],
                         "biomeTags": biome_tags, "structureTags": [tagref("dynasty:cod1/" + location)],
                         "tagLogic": "STRUCTURE_MARKER_OR_REGION_REQUIRED; biome tags are only supplementary filters",
                         "heightRange": {"min": -64 if underground else None, "max": 48 if underground else None,
                                         "profile": height, "status": "PROPOSED_PENDING_TERRAIN_VALIDATION"},
                         "lightRange": [int(x) for x in light.split(":")], "timeWindow": time,
                         "weatherCondition": "ANY", "spawnWeight": {"active": 0, "proposed": 4 if mode == "NATURAL_ECOLOGY" else 0,
                                                                       "status": "PENDING_PLAYTEST"},
                         "minGroup": int(low), "maxGroup": int(high), "localCap": int(cap),
                         "spawnReason": mode, "specialCondition": extra,
                         "despawnPolicy": "VANILLA_DISTANCE_FOR_NATURAL; ENCOUNTER_OWNED_FOR_STRUCTURE",
                         "respawnRule": "PENDING_LOCATION_COOLDOWN_AND_KILL_STATE; no active spawner"}
    elif category == "ELITE":
        primary, secondary, mode = ELITE_LOCATIONS[number - 1]
        data["spawn"] = {"dimension": dimension, "primaryLocation": primary, "secondaryRareLocation": secondary,
                         "biomeTags": [tagref("dynasty:underworld", "biome", False)] if number == 13 else [],
                         "structureTags": [tagref("dynasty:cod1/elite/" + IDS[category][number - 1])],
                         "spawnMethod": mode, "respawnRule": "ONE_SHOT_SAVEDDATA" if mode == "FIXED_GUARD" else "LONG_COOLDOWN_CONFIG_PENDING",
                         "maxAlivePerStructure": 1, "bossDependency": "PENDING_STRUCTURE_PROGRESS_HOOK",
                         "heightRange": "MATCH_STRUCTURE_MARKER", "lightRange": "MATCH_STRUCTURE", "timeWindow": "MATCH_EVENT",
                         "weatherCondition": "ANY_UNLESS_EVENT_REQUIRES", "spawnWeight": 0}
    elif category == "BOSS":
        boss = {"dimension": dimension, "arena": {"name": spec["arenaName"], "status": "PENDING_ARENA_TRIGGER_INTERFACE"},
                "structureTags": [tagref("dynasty:cod1/boss/" + IDS[category][number - 1])],
                "summonCondition": BOSS_TRIGGERS[number - 1], "requiredProgress": "PENDING_QUEST_OR_STRUCTURE_TRIGGER",
                "arenaCenterSource": "SERVER_STRUCTURE_MARKER_OR_SAVED_ENCOUNTER_CENTER",
                "firstKillReward": {"materials": "PENDING_ITEM_PURPOSE_MAPPING", "uniqueArtifact": "dynasty:" + IDS["ARTIFACT"][0] if number == 2 else None,
                                    "scope": "PER_PLAYER_FIRST_KILL"},
                "repeatKillReward": "NO_UNIQUE_ARTIFACT; MATERIAL_POLICY_PENDING",
                "respawnPolicy": "EXPLICIT_REPEAT_ENCOUNTER_ONLY; NO_NATURAL_SPAWN",
                "worldStateKey": "dynasty:cod1/boss_state/" + IDS[category][number - 1],
                "maxAlivePerArena": 1, "uuidRecovery": "REUSE_SAVED_UUID_BEFORE_SUMMON",
                "heightTimeWeather": "ARENA_TRIGGER_CONTROLLED", "spawnWeight": 0}
        if number == 12:
            boss.update(requiredProgress="PENDING_USER_CONFIRMATION; do not attach to active ritual",
                        integrationStatus="PENDING_CONFIRMATION",
                        preservedFinalBoss="dynasty:zhenyuan_sovereign",
                        conflict="Existing final boss identity differs; candidate/pre-boss/hidden role unresolved. Do not replace or hook into ritual.")
            data["definitionStatus"] = "PENDING_CONFIRMATION"
        data["boss"] = boss
    elif category == "ARTIFACT":
        text = spec["sourceObtain"]
        mode = "BOSS" if number == 1 else "INTERACTION" if number in (8, 14, 15, 20, 21, 25) else "STRUCTURE"
        data["artifact"] = {"id": identity, "sourceType": mode, "dimension": dimension,
                            "sourceId": "dynasty:cod1/reward/" + IDS[category][number - 1],
                            "sourceStatus": "PROPOSED_PENDING_REWARD_HOOK", "sourceDescription": text,
                            "structureTags": [tagref("dynasty:cod1/artifact/" + IDS[category][number - 1])],
                            "firstTimeOnly": True, "repeatable": False, "rewardScope": "PER_PLAYER",
                            "prerequisites": [text], "sourceBossId": "dynasty:gongsun_wuwang" if number == 1 else None,
                            "ordinaryCraftRecipe": False, "jeiPolicy": "ITEM_AND_REAL_SOURCE_INFO_ONLY; NO_FAKE_RECIPE"}
        data["dropsReward"] = {"sourceText": "神器按对应来源获得；每玩家一次的建议策略待实现", "status": "PENDING_REWARD_HOOK"}
    else:
        artifact_number = PHANTOM_ARTIFACTS[number - 1]
        data["phantom"] = {"artifactId": "dynasty:" + IDS["ARTIFACT"][artifact_number - 1] if artifact_number else None,
                           "artifactBindingStatus": "PROPOSED_CATALOG_BINDING" if artifact_number else "PENDING_ARTIFACT_ID_NOT_DEFINED_IN_25",
                           "sourceArtifactName": spec["sourceArtifact"], "allowedDimensions": {"policy": "INHERIT_ARTIFACT_USE_POLICY", "excludedByPhantom": []},
                           "anchorType": ANCHORS[number - 1], "anchorSource": spec["sourceAnchor"],
                           "triggerSkill": PHANTOM_TRIGGERS[number - 1],
                           "duration": {"ticks": 60 if number == 5 else None, "status": "SPECIFIED" if number == 5 else "PENDING_ABILITY_TIMELINE"},
                           "renderDistance": {"blocks": 128 if number == 6 else 64, "status": "PROPOSED_PENDING_PERFORMANCE_TEST"},
                           "firstPersonRule": "HIDE_SELF_BODY_SAFE_ARMS_ONLY" if number == 2 else "WORLD_SPACE_WITH_NEAR_CAMERA_CULL",
                           "multiplayerVisibility": "WORLD_SPACE_FOR_OBSERVERS; OVERLAY_ONLY_FOR_LOCAL_CASTER",
                           "serverEntity": False, "cleanup": ["expiry", "cancel", "death", "dimension_change", "entity_unload"]}
        data["dropsReward"] = {"sourceText": None, "status": "NOT_APPLICABLE_VISUAL_ONLY"}
    return data


def scan_inventory() -> dict:
    java = sorted((ROOT / "src/main/java").rglob("*.java"))
    scans = {"entityRegistrySites": [], "entityRegistrySources": [], "itemRegistrySites": [], "itemRegistrySources": [], "renderers": [], "geoModels": [],
             "packets": [], "particleReferences": [], "soundReferences": []}
    for path in java:
        content = path.read_text(encoding="utf-8")
        if "DeferredRegister<EntityType<?>>" in content:
            scans["entityRegistrySources"].append({"path": rel(path), "sha256": digest(path)})
        if re.search(r"(?:DeferredRegister|RegistryObject)<Item>", content):
            scans["itemRegistrySources"].append({"path": rel(path), "sha256": digest(path)})
        for number, line in enumerate(content.splitlines(), 1):
            if 'ENTITIES.register("' in line and "DeferredRegister<EntityType<?>>" in content:
                scans["entityRegistrySites"].append({"path": rel(path), "line": number, "text": line.strip()})
            if "DeferredRegister<Item>" in content and (re.search(r'(?:register|basic|sword|item|food|trinket)\("', line)):
                scans["itemRegistrySites"].append({"path": rel(path), "line": number, "text": line.strip()})
        for key, needle in (("renderers", "Renderer"), ("geoModels", "extends GeoModel"), ("packets", "FriendlyByteBuf")):
            if needle in content:
                scans[key].append({"path": rel(path), "sha256": digest(path)})
        for key, pattern in (("particleReferences", r"ParticleTypes\.([A-Z_]+)"), ("soundReferences", r"SoundEvents\.([A-Z_]+)")):
            refs = sorted(set(re.findall(pattern, content)))
            if refs:
                scans[key].append({"path": rel(path), "symbols": refs})
    patterns = {"dimensions": "data/dynasty/dimension/*.json", "biomeTags": "data/dynasty/tags/worldgen/biome/*.json",
                "structureTags": "data/dynasty/tags/worldgen/structure/**/*.json", "structures": "data/dynasty/worldgen/structure/*.json",
                "geo": "assets/dynasty/geo/**/*.json", "animations": "assets/dynasty/animations/**/*.json",
                "itemModels": "assets/dynasty/models/item/*.json", "textures": "assets/dynasty/textures/**/*.png",
                "lootTables": "data/dynasty/loot_tables/**/*.json", "spawnConfigurations": "data/dynasty/forge/biome_modifier/spawn*.json",
                "particles": "assets/dynasty/particles/**/*.json", "sounds": "assets/dynasty/sounds/**/*", "soundDefinitions": "assets/dynasty/sounds.json"}
    resources = ROOT / "src/main/resources"
    for key, pattern in patterns.items():
        scans[key] = [{"path": rel(p), "sha256": digest(p)} for p in sorted(resources.glob(pattern)) if p.is_file()]
    entity_files = [ROOT / "src/main/java/com/dynasty/entity/DynastyEntities.java", ROOT / "src/main/java/com/dynasty/ritual/ZhenyuanBosses.java"]
    scans["legacyEntityIds"] = sorted("dynasty:" + name for path in entity_files for name in re.findall(r'ENTITIES\.register\("([^"]+)"', path.read_text()))
    return {"method": "STATIC_SOURCE_AND_RESOURCE_SCAN_NOT_RUNTIME_REGISTRY_DUMP", "warning": "Registration sites include helper calls; counts are not a claim of live item registry size. Resource hashes, not copies of dirty assets.",
            "counts": {key: len(value) for key, value in scans.items()}, "inventory": scans}


def make_catalog(source: Path) -> dict:
    old = {}
    existing = OUT / "content-definitions.json"
    if existing.is_file():
        old = {entry["id"]: entry for entry in json.loads(existing.read_text())["entries"]}
    entries = [definition(spec) for spec in read_spec(source)]
    for entry in entries:
        if entry["id"] in old:
            saved = old[entry["id"]]
            # An implementation agent owns these fields; refreshing evidence must
            # not turn an audited partial implementation back into NOT_STARTED.
            for key in ("implementationStatus", "verification", "implementationEvidence"):
                if key in saved:
                    entry[key] = saved[key]
            if saved["implementationStatus"] != "NOT_STARTED":
                for key in ("resources", "attributes", "spawn", "boss", "artifact", "phantom", "definitionStatus", "naturalSpawnActive", "acquisitionActive", "exactExistingId", "runtimeSkills", "dropsReward", "pendingWorldPlacement"):
                    if key in saved:
                        entry[key] = saved[key]
                for resource_list in entry["resources"].values():
                    for index, resource in enumerate(resource_list):
                        if isinstance(resource, dict) and resource.get("path"):
                            resource_list[index] = probe(resource["path"])
    return {"schemaVersion": 1, "source": {"path": str(source), "sha256": digest(source), "scope": "Gemini sections 1-5 plus appended engineering/location supplements only"},
            "statusSemantics": {"auditStatus": "Initial identity audit; similar legacy content is reference-only", "implementationStatus": "DONE requires actual assets and in-game evidence; stage0 is NOT_STARTED", "proposed": "No runtime registration, spawn, reward or quest hook is implied", "null": "Explicit unresolved requirement; not zero and not a completed definition"},
            "expectedCounts": COUNTS, "protectedFinalBoss": "dynasty:zhenyuan_sovereign", "entries": entries}


def game_test_evidence(test_log: Path, namespaces: tuple[str, ...] = ("dynasty",)) -> dict:
    """Match a complete successful run to current annotated dynasty test sources.

    No test totals are constants. Only explicitly supplied namespaces are counted;
    generated tests or changed annotation syntax fail closed.
    A current-source match is not a byte-for-byte archive of the executed build.
    """
    pattern = r'@GameTest\([^)]*\)\s*public static void (\w+)\('
    discovered, blueprint_tests = [], []
    for path in sorted((ROOT / "src/main/java").rglob("*.java")):
        text = path.read_text()
        holder = re.search(r'@GameTestHolder\(\s*(Dynasty.MODID|"[\w.-]+")\s*\)', text)
        namespace = "dynasty" if holder and holder[1] == "Dynasty.MODID" else holder[1].strip('"') if holder else None
        if namespace not in namespaces:
            continue
        assert "@GameTestGenerator" not in text, f"Generated tests require explicit discovery support: {path}"
        names = re.findall(pattern, text)
        assert len(names) == len(re.findall(r'@GameTest\s*\(', text)), f"Unsupported test annotation syntax: {path}"
        assert not re.search(r'@GameTest\([^)]*required\s*=\s*false', text), "Optional tests need separate log accounting"
        discovered.append(dict(probe(rel(path)), count=len(names), namespace=namespace))
        if path.parent == ROOT / "src/main/java/com/dynasty/blueprint":
            blueprint_tests.extend(names)
    assert blueprint_tests and len(blueprint_tests) == len(set(blueprint_tests)), "Missing/ambiguous blueprint tests"
    log = test_log.read_text()
    completed = re.findall(r'(\d+) GAME TESTS COMPLETE', log)
    passed = re.findall(r'All (\d+) required tests passed', log)
    failures = re.findall(r'\]: ([\w.:-]+) failed!', log)
    assert len(completed) == len(passed) == 1, "Need one complete successful GameTest run"
    total = int(completed[0])
    assert total == int(passed[0]) == sum(p["count"] for p in discovered), "Log total differs from current annotated dynasty tests"
    assert not failures and "BUILD SUCCESSFUL" in log, "Server test run was not wholly successful"
    assert "MissingPaletteEntryException" not in log, "Background chunk-light failure cannot count as a clean run"
    lines = log.splitlines()
    build_lines = [i + 1 for i, line in enumerate(lines) if re.fullmatch(r'> Task :build(?: UP-TO-DATE)?', line)]
    return {"suite": {"total": total, "passed": total, "failed": 0, "failures": []},
            "blueprintTests": {"count": len(blueprint_tests), "passed": len(blueprint_tests), "names": blueprint_tests,
                "basis": f"All {total} current annotated dynasty tests completed and passed; includes {len(blueprint_tests)} blueprint tests."},
            "sourceDiscovery": {"namespace": namespaces[0] if len(namespaces)==1 else list(namespaces), "method": "@GameTestHolder plus @GameTest annotations; count must match complete log", "files": discovered},
            "productionBuild": {"status": "PASS_LOGGED_BUILD_TASK" if build_lines else "NOT_RECORDED_IN_THIS_LOG",
                "buildTaskLines": build_lines,
                "artifactTasks": re.findall(r'^> Task :(jar|reobfJar|assemble|build)(?: UP-TO-DATE)?$', log, re.M)},
            "logLines": {"complete": next(i + 1 for i, line in enumerate(lines) if "GAME TESTS COMPLETE" in line),
                         "allPassed": next(i + 1 for i, line in enumerate(lines) if "required tests passed" in line),
                         "buildSuccessful": next(i + 1 for i, line in enumerate(lines) if "BUILD SUCCESSFUL" in line)}}


def structure_attempt_weights(definitions: str, spawn_source: str) -> dict:
    """Extract the narrow current helper contract, not just its display strings."""
    assert re.search(r'nextInt\(TemplateContentDefinitions.maximumWeight\(definition\)\)\s*'
                     r'>=TemplateContentDefinitions.effectiveWeight\(definition,!level.isDay\(\),light\)', spawn_source)
    maximum_part = definitions.split("static int maximumWeight", 1)[1].split("static int effectiveWeight", 1)[0]
    effective_part = definitions.split("static int effectiveWeight", 1)[1]
    maximum = {key: int(value) for key, value in re.findall(r'case "([^"]+)"->(\d+);', maximum_part)}
    effective = re.findall(r'case "([^"]+)"->(night(?:\|\|localLight<=\d+)?)\?(\d+):(\d+);', effective_part)
    assert len(effective) == len(re.findall(r'case "', effective_part)) == len(maximum)
    result = {}
    for key, condition, preferred, ordinary in effective:
        bound, preferred, ordinary = maximum[key], int(preferred), int(ordinary)
        assert 0 < ordinary <= preferred <= bound
        low_light = re.search(r'localLight<=(\d+)', condition)
        result[key] = {"maximumAttemptWeight": bound, "dayBrightWeight": ordinary, "nightWeight": preferred,
                       "lowLightAtMost": int(low_light[1]) if low_light else None,
                       "dayLowLightWeight": preferred if low_light else ordinary}
    return result


def client_stage_contract(army: bool = False) -> dict:
    """Read the current QA stage names; old 14-stage or death-only runs cannot pass."""
    qa_path = ROOT / "tools/blueprint/qa-src/com/dynasty/client/BlueprintClientQa.java"
    source = qa_path.read_text()
    match = re.search(r'String\[\] NAMES = (?:BATTLEFIELD \? new String\[\]\{[^}]*\}\s*:\s*)?ARMY \? new String\[\]\{(.*?)\}\s*:\s*new String\[\]\{(.*?)\};', source, re.S)
    if match:
        raw = match[1 if army else 2]
    else:
        match = re.search(r'String\[\] NAMES = \{(.*?)\};', source, re.S)
        raw = match[1] if match else ""
    assert match, "Cannot discover current client QA stages"
    names = re.findall(r'"([a-z0-9-]+)"', raw)
    assert len(names) == len(set(names)) == (23 if army else 22), "Client acceptance contract changed; review parser explicitly"
    if army:
        assert names[14] == "scout-knee"
        assert names[18:] == ["spear-death", "crossbow-death", "scout-death", "powder-death", "banner-death"]
    else:
        assert names[14:20] == ["sword-death-mid", "sword-death-planted", "priest-death-mid",
                              "priest-death-empty-robe", "shanxiao-death-mid", "shanxiao-death-curled-faded"]
        assert names[20:] == ["autonomous-wall-climb", "autonomous-summit-rock"]
    return {"stageNames": names, "stageCount": len(names), "currentQaSource": probe(rel(qa_path)),
            "sourceHashScope": "Current parser contract snapshot; not proof of which classes a past client loaded."}


def client_artifact_manifest(run_dir: Path, run: str, army: bool = False) -> dict:
    """Check the QA owner's frozen runClient classpath snapshot, not a packaged JAR."""
    path = run_dir / "artifact-manifest.json"
    if not path.is_file():
        return {"status": "PENDING_EXECUTED_CLASSPATH_SNAPSHOT", "expectedPath": rel(path),
                "limits": "Screenshot success alone does not identify the client's class/resource bytes."}
    manifest = json.loads(path.read_text())
    assert manifest["formatVersion"] == 1 and manifest["run"] == run, "Artifact snapshot run/schema mismatch"
    production_roots = ["build/classes/java/main", "build/resources/main"]
    allowed_roots = production_roots + ["build/classes/java/blueprintQa"]
    trees = manifest["trees"]
    assert [tree["root"] for tree in trees] == allowed_roots, "Unknown or incomplete classpath snapshot scope"
    checked = []
    detailed_resources = set()
    detailed_classes = set()
    for tree in trees:
        root = ROOT / tree["root"]
        files = sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix())
        hashes = {p.relative_to(root).as_posix(): digest(p) for p in files}
        # The frozen manifest owns ordering (older snapshots used Path-part order).
        # Verify complete file membership and every byte, not an incidental sorter.
        aggregate = hashlib.sha256("".join(entry["path"] + "\0" + hashes.get(entry["path"], "MISSING") + "\n"
                                           for entry in tree["entries"]).encode()).hexdigest()
        assert len(files) == tree["fileCount"] and sum(p.stat().st_size for p in files) == tree["bytes"], f"Classpath changed since snapshot: {tree['root']}"
        assert aggregate == tree["sha256"], f"Classpath hash changed since snapshot: {tree['root']}"
        seen = set()
        for entry in tree["entries"]:
            name = entry["path"]
            assert name not in seen and name in hashes, "Invalid/duplicate snapshot detail"
            seen.add(name)
            assert hashes[name] == entry["sha256"] and (root / name).stat().st_size == entry["bytes"], "Detailed snapshot hash mismatch"
            if tree["root"] == "build/resources/main":
                detailed_resources.add(name)
                if name not in ("META-INF/mods.toml", "pack.mcmeta"):
                    assert digest(ROOT / "src/main/resources" / name) == entry["sha256"], "Source asset differs from frozen runClient resource"
            if tree["root"] == "build/classes/java/main":
                detailed_classes.add(name)
        assert seen == set(hashes), "Snapshot must identify every supplied classpath file"
        checked.append({"root": tree["root"], "fileCount": len(files), "bytes": tree["bytes"],
                        "sha256": aggregate, "detailedEntryCount": len(seen)})
    assert {"com/dynasty/blueprint/TemplateMob.class", "com/dynasty/blueprint/combat/CenteredGroundNavigation.class"} <= detailed_classes
    ids = ("zuwu_daoshou", "ludun_jiashi", "fufa_jijiu", "shanjing_shanxiao")
    atlases = ("royal_guard", "imperial_soldier", "nian_beast")
    if army:
        ids = ("juma_changqiangbing", "liannu_zhenzu", "tiesuo_chihou", "kuijun_sishi", "zhenwang_zhangqiguan")
        atlases = ("archer", "rebel_soldier", "assassin", "royal_guard")
        assert {"com/dynasty/blueprint/ArmyBehaviors.class", "com/dynasty/blueprint/ArmyCaltrop.class"} <= detailed_classes
    required_resources = {f"assets/dynasty/geo/blueprint/{identity}.geo.json" for identity in ids}
    required_resources |= {f"assets/dynasty/animations/blueprint/{identity}.animation.json" for identity in ids}
    required_resources |= {f"assets/dynasty/textures/entity/{atlas}.png" for atlas in atlases}
    assert required_resources <= detailed_resources, "Missing blueprint/atlas snapshot details"
    production_hash = hashlib.sha256("".join(tree["root"] + "\0" + tree["sha256"] + "\n"
                                               for tree in trees if tree["root"] in production_roots).encode()).hexdigest()
    assert production_hash == manifest["productionSha256"], "Combined production snapshot hash mismatch"
    for source in manifest.get("expandedInputs", []):
        assert digest(ROOT / source["path"]) == source["sha256"], "Expanded resource input changed since run"
    return {"status": "FROZEN_RUNCLIENT_CLASSPATH_SNAPSHOT_MATCHES_CURRENT_OUTPUTS", "manifest": probe(rel(path)),
            "createdAt": manifest["createdAt"], "scope": manifest["scope"], "productionSha256": production_hash,
            "trees": checked, "sourceAssetDetailsMatch": True,
            "expandedResourceInputs": manifest.get("expandedInputs", "OLDER_SNAPSHOT_OUTPUT_BYTES_ONLY"),
            "limits": "Run-owner classpath snapshot and current output comparison; not per-class classloader instrumentation, not proof of loading the packaged release JAR, and not an archive of all production bytes."}


def client_lifecycle_evidence(run_dir: Path, run: str, players: int, ids: set[str]) -> dict:
    """Optional recorded lifecycle checks; absent evidence stays pending, never PASS."""
    roles = ("host",) if players == 1 else ("host", "peer")
    paths = [run_dir / role / "resource-reload.json" for role in roles]
    if not any(path.exists() for path in paths):
        return {"status": "PENDING", "resourceReload": "PENDING", "rejoin": "PENDING"}
    assert all(path.exists() for path in paths), "Incomplete resource-reload evidence"
    data = [json.loads(path.read_text()) for path in paths]
    for role, row in zip(roles, data):
        assert row["run"] == run and row["role"] == role and row["status"] == "PASS_ACTUAL_RESOURCE_RELOAD", "Mixed resource-reload run"
        assert len(row["mobs"]) == len(ids) and {m["id"] for m in row["mobs"]} == ids
        assert len({m["uuid"] for m in row["mobs"]}) == len(ids)
        for mob in row["mobs"]: uuid.UUID(mob["uuid"])
    rejoin = None
    if players == 2:
        before_path, after_path = (run_dir / "peer" / name for name in ("rejoin-before.json", "rejoin.json"))
        before, after = json.loads(before_path.read_text()), json.loads(after_path.read_text())
        assert data[0]["mobs"] == data[1]["mobs"] == before == after["mobs"], "Rejoin replaced existing tracked identities"
        assert after["run"] == run and after["role"] == "peer" and after["players"] == 2
        assert after["status"] == "PASS_REAL_TCP_DISCONNECT_RECONNECT" and after["clientTick"] > data[1]["clientTick"]
        rejoin = {"before":probe(rel(before_path)),"after":probe(rel(after_path)),"status":after["status"]}
        events_path = run_dir / "coord/peer-session-events.jsonl"
        if events_path.exists():
            events = [json.loads(line) for line in events_path.read_text().splitlines()]
            assert [e["event"] for e in events[:3]] == ["JOIN", "LEAVE", "JOIN"], "No real join/leave/join sequence"
            assert all(e["run"] == run for e in events) and len({e["uuid"] for e in events[:3]}) == 1
            assert events[0]["serverTick"] < events[1]["serverTick"] < events[2]["serverTick"]
            rejoin["serverEvents"] = probe(rel(events_path))
        else:
            rejoin["serverEvents"] = "OLDER_RUN_CLIENT_RECORDS_ONLY"
    return {"status":"PASS_RECORDED_LIFECYCLE_SCOPE", "resourceReload":[probe(rel(path)) for path in paths],
        "rejoin":rejoin if rejoin else "NOT_APPLICABLE_SOLO_NO_SERVER_RESTART", "scope":"Idle tracked fixtures retain identity; following action/death render stages pass. Not active-combat rejoin or server disk restart."}


def client_run_evidence(directory: Path, players: int, army: bool = False) -> dict:
    """Fail closed on incomplete, mixed-run, old-stage or single-client 'network' evidence.

    PASS is a harness result, not an art review. UUIDs are printed for action/death
    stages (7..19); the first seven static views only have exact-tracking assertions.
    """
    assert players in (1, 2)
    directory = directory.resolve()
    run_dir = directory.parent if directory.name == "host" else directory
    rel(run_dir)  # Evidence must be preserved in this repository, not an ephemeral external path.
    contract = client_stage_contract(army)
    names, stage_count = contract["stageNames"], contract["stageCount"]
    for role in (("host",) if players == 1 else ("host", "peer")):
        assert not (run_dir / role / "FAIL.txt").exists(), f"Failure report exists for {role}"
    coord = run_dir / "coord"
    state_path, complete_path = coord / "stage.json", coord / "complete.txt"
    state = json.loads(state_path.read_text())
    run = state["run"]
    assert run == run_dir.name and state["index"] == stage_count - 1 and state["phase"] == "ACTIVE", "Wrong/incomplete run identity"
    expected_complete = run + " all stages acknowledged by " + ("host only" if players == 1 else "both TCP clients")
    assert complete_path.read_text().strip() == expected_complete, "Missing matching completion acknowledgement"
    listening_path = coord / "listening.txt"
    assert listening_path.read_text().strip() == run + " loopback 127.0.0.1:25587", "Missing matching loopback session"
    ids = {"zuwu_daoshou", "ludun_jiashi", "fufa_jijiu", "shanjing_shanxiao"}
    action_owner = {7: ("zuwu_daoshou", 1, "attack"), 8: ("ludun_jiashi", 2, "attack"),
                    9: ("fufa_jijiu", 4, "buff"), 10: ("shanjing_shanxiao", 5, "skill"),
                    11: ("fufa_jijiu", 3, "attack"), 12: ("shanjing_shanxiao", 6, "rock"),
                    13: ("ludun_jiashi", 0, "death"), 14: ("zuwu_daoshou", 0, "death"),
                    15: ("zuwu_daoshou", 0, "death"), 16: ("fufa_jijiu", 0, "death"),
                    17: ("fufa_jijiu", 0, "death"), 18: ("shanjing_shanxiao", 0, "death"),
                    19: ("shanjing_shanxiao", 0, "death"),
                    20: ("shanjing_shanxiao", 0, "climb"), 21: ("shanjing_shanxiao", 6, "rock")}
    if army:
        ordered_ids = ["juma_changqiangbing", "liannu_zhenzu", "tiesuo_chihou", "kuijun_sishi", "zhenwang_zhangqiguan"]
        ids = set(ordered_ids)
        action_owner = {index: (ordered_ids[owner], skill, clip) for index, (owner, skill, clip) in enumerate([
            (0,10,"attack"),(0,11,"brace"),(1,12,"attack"),(1,13,"roll"),(2,14,"attack"),(2,15,"grapple"),(2,19,"knee"),
            (3,16,"attack"),(3,17,"detonate"),(4,18,"attack"),*( (i,0,"death") for i in range(5))], 8)}
    first_action = 8 if army else 7
    count_words = (str(len(ids)),) if army else ("four", "4")
    expected_pngs = {f"{index:02d}-{name}.png" for index, name in enumerate(names)}
    clients = {}
    for role in (("host",) if players == 1 else ("host", "peer")):
        output = run_dir / role
        assert not (output / "FAIL.txt").exists(), f"Failure report exists for {role}"
        report_path, observations_path = output / "PASS.txt", output / "observations.txt"
        report, observations = report_path.read_text(), observations_path.read_text()
        pass_lines = report.splitlines()
        assert pass_lines[:-1] == observations.splitlines(), f"PASS/observations differ for {role}"
        prefix = (f"PASS: isolated single-client {stage_count} stages, actual Gecko action/death clips, and screenshot harness."
                  if players == 1 else f"PASS: real loopback TCP clients acknowledged all {stage_count} stages")
        assert pass_lines[-1].startswith(prefix), f"Not a current full {stage_count}-stage {role} run"
        if players == 1:
            assert "NOT a multiplayer or visual-quality pass" in pass_lines[-1]
        else:
            assert "actual Gecko action/death clips" in pass_lines[-1] and "Screenshots still require visual review" in pass_lines[-1]
        captures = re.findall(r'^Captured ([a-z0-9-]+); (?:' + "|".join(count_words) + r') exact UUIDs tracked; players=(\d+); FPS=(\d+)$', observations, re.M)
        assert [c[0] for c in captures] == names and all(int(c[1]) == players for c in captures), f"Missing/out-of-order captures or wrong player count: {role}"
        pngs = sorted(output.glob("*.png"))
        assert {p.name for p in pngs} == expected_pngs, f"Missing/unexpected screenshots: {role}"
        screenshots = []
        for path in pngs:
            header = path.read_bytes()[:24]
            assert len(header) == 24 and header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR", f"Not PNG: {path}"
            width, height = struct.unpack(">II", header[16:24])
            assert width >= 600 and height >= 400, f"Undersized client capture: {path}"
            screenshots.append(dict(probe(rel(path)), width=width, height=height))
        acknowledgements = []
        for index, name in enumerate(names):
            for kind in ("ready", "captured"):
                path = coord / f"{kind}-{index}-{role}.txt"
                lines = path.read_text().splitlines()
                expected_data = [(f"All {word} exact entity UUIDs tracked; players={players}" if kind == "ready"
                                 else f"Captured {name}; {word} exact UUIDs tracked; players={players}; FPS={captures[index][2]}") for word in count_words]
                assert len(lines) == 2 and lines[0] == run and lines[1] in expected_data, f"Mismatched acknowledgement: {path}"
                acknowledgements.append(probe(rel(path)))
        states, last_key = {}, None
        for line in observations.splitlines():
            row = re.fullmatch(r'([a-z0-9-]+) entity=(\w+) uuid=([\da-f-]+) skill=(\d+) phase=(\w+) start=(-?\d+) clientTime=(\d+) actionAge=([\d.Ee+-]+)', line)
            if row:
                stage, identity, entity_uuid, skill, phase, start, client_time, age = row.groups()
                assert stage in names[first_action:] and identity in ids
                uuid.UUID(entity_uuid)
                key = (stage, identity)
                assert key not in states, f"Duplicate observed entity: {role}/{key}"
                states[key] = {"stage": stage, "id": identity, "uuid": entity_uuid, "skill": int(skill),
                               "phase": phase, "start": int(start), "clientTime": int(client_time), "actionAge": float(age)}
                last_key = key
            elif line.startswith("Rendered "):
                render = re.match(r'Rendered (\w+) requested=(\S+) queued=(\S+) controller=(\w+)(?: |$)', line)
                assert render and last_key and last_key[1] == render[1], f"Unpaired render observation: {role}"
                observed = states[last_key]
                assert "render" not in observed and render[4] in ("RUNNING", "PAUSED", "STOPPED", "TRANSITIONING"), f"Malformed Gecko state: {role}/{last_key}"
                observed["render"] = {"requested": render[2], "queued": render[3], "controller": render[4]}
        assert len(states) == (stage_count - first_action) * len(ids), f"Missing UUID/action states: {role}"
        for index in range(first_action, stage_count):
            owner, skill, clip = action_owner[index]
            stage_states = [states[(names[index], identity)] for identity in sorted(ids)]
            assert len({s["uuid"] for s in stage_states}) == len(ids), "Entity UUIDs are not distinct"
            for observed in stage_states:
                is_owner = observed["id"] == owner
                expected_clip = f"animation.{observed['id']}." + (clip if is_owner else "idle")
                assert observed["skill"] == (skill if is_owner else 0)
                assert (observed["start"] >= 0 if is_owner and (army or index != 20) else observed["start"] == -1)
                assert observed["phase"] in ({"WINDUP", "ACTIVE", "RECOVERY"} if is_owner and skill else {"IDLE"})
                assert observed.get("render", {}).get("requested") == expected_clip
                if is_owner:
                    assert observed["render"]["queued"] == expected_clip and observed["render"]["controller"] in ("RUNNING", "PAUSED"), f"Wrong Gecko clip: {role}/{observed}"
        final_mobs = {m["id"]: m for m in state["mobs"]}
        assert set(final_mobs) == ids
        for identity in ids:
            last = states[(names[-1], identity)]
            # Stage 21 retains the live stage-20 actors; its published metadata predates
            # the autonomous skill start. Compare action identity to server telemetry below.
            assert last["uuid"] == final_mobs[identity]["uuid"], "Final shared entity differs from client"
        encounters = {}
        if army:
            assert re.search(r'Real hook attachment target=\d+ expires=\d+', observations), "No actual hit hook synchronized"
        for index in (() if army else (20, 21)):
            event = json.loads((output / f"{index}-encounter.json").read_text())
            server = event["server"]
            assert event["run"] == server["run"] == run and event["role"] == role and event["stage"] == index
            assert event["uuid"] == server["uuid"] == states[(names[index], "shanjing_shanxiao")]["uuid"]
            assert not server["noAi"] and not server["noGravity"]
            assert abs(event["clientTick"] - event["serverTick"]) <= 3
            if index == 20:
                assert event["geometryValid"] and server["climbing"] and server["horizontalCollision"]
                assert event["rootAwayDot"] >= .9 and event["rootUpDot"] >= .9 and event["stanceContacts"] >= 2
                assert len(event["contacts"]) == 4
                assert all(-.04 <= c["planeDistance"] <= .16 and c["projectsOntoSolidWall"] for c in event["contacts"].values())
                assert event["clientClimbStart"] == server["climbStart"] and event["clientClimbFace"] == server["climbFace"]
            else:
                assert server["onGround"] and server["position"][1] >= server["initialY"] + 2
                assert server["skill"] == event["clientSkill"] == 6 and server["skillStart"] == event["clientStart"]
                assert event["visibleRockUuids"] and set(event["visibleRockUuids"]) & {r["uuid"] for r in server["rocks"]}
            encounters[index] = event
        if not army:
            assert encounters[20]["uuid"] == encounters[21]["uuid"], "Encounter actor replaced between climbing and throwing"
        clients[role] = {"players": players, "report": probe(rel(report_path)), "observations": probe(rel(observations_path)),
                         "screenshots": screenshots, "acknowledgements": acknowledgements,
                         "captures": [{"stage": c[0], "players": int(c[1]), "fps": int(c[2])} for c in captures],
                         "entityStates": list(states.values()), "encounters": encounters}
    cross_client = None
    if players == 2:
        host_states, peer_states = (clients[role]["entityStates"] for role in ("host", "peer"))
        host_map, peer_map = ({(s["stage"], s["id"]): s for s in states} for states in (host_states, peer_states))
        for key in host_map:
            assert all(host_map[key][field] == peer_map[key][field] for field in ("uuid", "skill", "start")), f"Cross-client entity/action identity mismatch: {key}"
        for index in (() if army else (20, 21)):
            host, peer = (clients[role]["encounters"][index] for role in ("host", "peer"))
            assert abs(host["serverTick"] - peer["serverTick"]) <= 3
            if index == 20:
                assert host["clientClimbStart"] == peer["clientClimbStart"] and host["clientClimbFace"] == peer["clientClimbFace"]
            else:
                assert set(host["visibleRockUuids"]) & set(peer["visibleRockUuids"]), "Clients saw different projectiles"
        cross_client = {"identityActionMatches": len(host_map), "printedUuidStageCount": stage_count - first_action,
                        "phaseDifferences": [{"stage": key[0], "id": key[1], "host": host_map[key]["phase"], "peer": peer_map[key]["phase"]}
                                             for key in host_map if host_map[key]["phase"] != peer_map[key]["phase"]],
                        "limits": "Phase is checked against each client's synchronized clock by the harness; phase-boundary samples need not be identical. First seven static stages have exact-tracking acknowledgements, not printed UUID tables."}
    return {"status": "HARNESS_PASS_QUALITY_PENDING", "run": run, "players": players, **contract,
            "artifactIdentity": client_artifact_manifest(run_dir, run, army),
            "lifecycle": client_lifecycle_evidence(run_dir, run, players, ids),
            "coordination": [probe(rel(p)) for p in (state_path, complete_path, listening_path)],
            "clients": clients, "crossClient": cross_client,
            "screenshots": [shot for client in clients.values() for shot in client["screenshots"]],
            "limits": "Actual Minecraft/Gecko state and screenshots; controlled NoAI/NoGravity action fixtures. Active/dead clips must run; off-camera inactive fixtures may stop. Optional lifecycle has its own limited scope; no full art, discovery, terrain, active-combat rejoin or server-restart acceptance."}


def refresh_templates(catalog: dict, test_log: Path, solo_dir: Path | None = None,
                      network_dir: Path | None = None, namespaces: tuple[str, ...] = ("dynasty",)) -> dict:
    """Extract the four actual prototypes without implying that runtime acceptance passed.

    This deliberately narrow Java-source extractor fails if the expected contracts
    change. Structure weights gate attempts inside fixed squads; only the shanxiao
    biome modifier uses a weighted natural-spawn pool.
    """
    base = "src/main/java/com/dynasty/blueprint/"
    source = lambda name: (ROOT / (base + name)).read_text()
    entities, definitions, skill_source = (source(p) for p in
        ("BlueprintEntities.java", "TemplateContentDefinitions.java", "TemplateSkills.java"))
    spawn_source = source("BlueprintSpawns.java")
    attempt_weights = structure_attempt_weights(definitions, spawn_source)
    number = lambda value: float(value.strip().removesuffix("F"))
    registrations = {m[1]: (m[0], m[2], number(m[3]), number(m[4])) for m in re.findall(
        r'(\w+) = mob\("([^"]+)", TemplateMob.Kind.(\w+), ([\d.F]+), ([\d.F]+)\)', entities)}
    stats = {m[0]: [number(x) for x in m[1].split(",")] for m in re.findall(
        r'event.put\((\w+).get\(\), attributes\(([^)]+)\)\)', entities)}
    spawn_rows = re.findall(
        r'new Spawn\("([^"]+)",Level.OVERWORLD,List.of\((.*?)\),List.of\((.*?)\),\s*'
        r'(-?\d+),(-?\d+),(\d+),(\d+),"([^"]+)","([^"]+)",(\d+),(\d+),(\d+),(\d+),"([^"]+)",\s*'
        r'"([^"]+)","([^"]+)"\)', definitions, re.S)
    registrations = {key: value for key, value in registrations.items() if value[1] in ("SWORD","SHIELD","PRIEST","BEAST")}
    spawn_rows = [row for row in spawn_rows if row[0] in registrations]
    assert len(registrations) == len(spawn_rows) == 4, "Template source format/count changed"
    skill_ids = dict(re.findall(r'(\w+) = (\d+)', skill_source))
    skills = {}
    for symbol, constant, key, args, contacts in re.findall(
            r'SkillDefinition (\w+) = new SkillDefinition\((\w+), "([^"]+)",\s*(.*?)List.of\(([^)]*)\)\);', skill_source, re.S):
        values = [v.strip() for v in args.rstrip().removesuffix(",").split(",")]
        assert len(values) == 11, f"Changed skill signature: {symbol}"
        names = "windupTicks activeTicks recoveryTicks cooldownTicks minRange maxRange angleDegrees definitionDamageMultiplier definitionKnockback interruptible requiresSight".split()
        # Eleven scalar fields after key; List.of contains the separate authored contacts.
        values = [v for v in values if v]
        assert len(values) == len(names)
        parsed = [v == "true" if v in ("true", "false") else number(v) for v in values]
        skill = dict(zip(names, parsed))
        for field_name in names[:4]: skill[field_name] = int(skill[field_name])
        skill.update(id=int(skill_ids[constant]), key=key,
                     impactTicks=[int(v.strip()) for v in contacts.split(",")],
                     totalTicks=sum(skill[n] for n in names[:3]), source=base + "TemplateSkills.java")
        skills[symbol] = skill
    assert len(skills) == 6, "Template skill count changed"
    assigned = {"SWORD": ["SWORD"], "SHIELD": ["SHIELD"], "PRIEST": ["TALISMAN", "BUFF"], "BEAST": ["LEAP", "ROCK"]}
    effects = {
        "SWORD": "Server melee contacts at both frames: 1.0x attack damage, knockback 0.2; shared legacy damage pipeline remains active.",
        "SHIELD": "First contact 0.6x damage/0.85 knockback and target handoff; second 1.3x/0.15. Front projectiles blocked, front melee multiplied by 0.2 before legacy reductions; corpse cover lasts 200 ticks.",
        "PRIEST": "Three talisman launches use 1.0x attack damage; possession activates at tick20 for160 ticks, movement/attack speed +30%, knockback resistance +1 (clamped). Possession accelerates complete skill timelines, including cooldown.",
        "BEAST": "Pounce tick14 launches, tick24 deals 1.15x within2.2 blocks and Wither45 ticks. Rock release tick18 uses1.1x, radius2.3 and knockback0.9. Projectiles expire after100 ticks."}
    loot = {entry["id"]: entry for entry in json.loads((OUT / "template-loot-status.json").read_text())["templates"]}
    tests = game_test_evidence(test_log, namespaces)
    total, test_count = tests["suite"]["total"], tests["blueprintTests"]["count"]
    build_passed = tests["productionBuild"]["status"] == "PASS_LOGGED_BUILD_TASK"
    solo = client_run_evidence(solo_dir, 1) if solo_dir else None
    network = client_run_evidence(network_dir, 2) if network_dir else None
    client_runs = [run for run in (solo, network) if run]
    snapshots = [run["artifactIdentity"] for run in client_runs]
    frozen = snapshots and all("productionSha256" in snapshot for snapshot in snapshots)
    if frozen:
        assert len({snapshot["productionSha256"] for snapshot in snapshots}) == 1, "Solo/network production classpath snapshots differ"
    artifact_identity = {"status": "MATCHING_FROZEN_CLASSPATH_SNAPSHOTS" if frozen else "PENDING_EXECUTED_CLASSPATH_SNAPSHOT",
        "runs": [run["run"] for run in client_runs], "productionSha256": snapshots[0]["productionSha256"] if frozen else None,
        "note": "Compared run-owned development classpath snapshots; not a loaded packaged-JAR claim. Full solo/network coverage also requires both harness runs."}
    evidence = {"status": "PARTIAL_SERVER_AND_CLIENT_HARNESS_PASS_QUALITY_MATRIX_PENDING" if solo and network else "PARTIAL_SERVER_TESTS_PASS_RUNTIME_ACCEPTANCE_PENDING", "log": str(test_log),
        "logSha256": digest(test_log), **tests,
        "modelReview": probe("docs/blueprint-cod1/models/REVIEW.txt"),
        "singleClientHarness": solo, "twoClientHarness": network,
        "twoPlayer": network["status"] if network else "PENDING_FINAL_NETWORK_ACCEPTANCE", "visualQuality": "PENDING_FINAL_MODEL_REVIEW",
        "clientArtifactIdentity": artifact_identity,
        "gradleTestInvocation": "BUILD_SUCCESSFUL",
        "productionArtifact": dict(probe("build/libs/dynasty-1.4.0.jar"),
            status="CURRENT_ARTIFACT_WITH_LOGGED_BUILD_PASS" if build_passed else "PRESENT_NOT_FINAL_BUILD_CERTIFICATION"),
        "limits": ["No complete single-player or two-player acceptance claimed by this evidence update.",
            "Model previews are not Minecraft screenshots.", "A logged :build success certifies that invocation, not later edits; the current JAR hash is a separate artifact snapshot.",
            "Current source/resource hashes are a fresh static scan, not a frozen byte-for-byte archive of the executed test build."]}
    model_atlas = {"SWORD": "royal_guard", "SHIELD": "royal_guard", "PRIEST": "imperial_soldier", "BEAST": "nian_beast"}
    modifier_path = "src/main/resources/data/dynasty/forge/biome_modifier/blueprint_shanxiao.json"
    modifier = json.loads((ROOT / modifier_path).read_text())
    model_inventory = []
    for identity in registrations:
        geo_path = f"src/main/resources/assets/dynasty/geo/blueprint/{identity}.geo.json"
        animation_path = f"src/main/resources/assets/dynasty/animations/blueprint/{identity}.animation.json"
        geometries = json.loads((ROOT / geo_path).read_text())["minecraft:geometry"]
        bones = [bone for geometry in geometries for bone in geometry["bones"]]
        clips = json.loads((ROOT / animation_path).read_text())["animations"]
        model_inventory.append({"id": "dynasty:" + identity, "bones": len(bones),
            "cuboids": sum(len(bone.get("cubes", [])) for bone in bones), "clips": len(clips),
            "geo": probe(geo_path), "animation": probe(animation_path)})
    evidence["modelInventory"] = {"status": "STATIC_RESOURCE_COUNTS_NOT_RUNTIME_ACCEPTANCE", "templates": model_inventory,
        "totals": {field: sum(model[field] for model in model_inventory) for field in ("bones", "cuboids", "clips")}}
    for row in spawn_rows:
        identity = "dynasty:" + row[0]
        entry = next(e for e in catalog["entries"] if e["id"] == identity)
        constant, kind, width, height = registrations[row[0]]
        health, damage, speed, armor, resistance = stats[constant]
        if entry["definitionStatus"] != "ACTIVE_RUNTIME": entry["pendingWorldPlacement"] = entry["spawn"]
        entry.update(implementationStatus="PARTIAL", exactExistingId=identity, definitionStatus="ACTIVE_RUNTIME",
                     naturalSpawnActive=kind == "BEAST", acquisitionActive=False)
        entry["attributes"].update(status="REGISTERED_BASE_ATTRIBUTES", MAX_HEALTH=health, ATTACK_DAMAGE=damage,
            MOVEMENT_SPEED=speed, ARMOR=armor, ARMOR_TOUGHNESS=0, FOLLOW_RANGE=28, KNOCKBACK_RESISTANCE=resistance,
            ATTACK_SPEED=1, ATTACK_KNOCKBACK=0, FLYING_SPEED=None, XP_REWARD=8 if kind == "SHIELD" else 5,
            entityDimensions={"width": width, "height": height, "source": base + "BlueprintEntities.java"},
            immunities={"fire": False, "water": False, "fall": "DISTANCE_MINUS_5_BEFORE_VANILLA_CALCULATION" if kind == "BEAST" else False},
            reason="Registered base values; vanilla armor/toughness and existing DynastyBalance event modifiers still affect final damage. FLYING_SPEED is not registered for these ground mobs.")
        entry["resources"] = {"implementationClass": [probe(base + p) for p in ("BlueprintEntities.java", "TemplateMob.java")],
            "skillClasses": [probe(base + p) for p in ("TemplateSkills.java", "TemplateProjectile.java", "TemplateSupportEffect.java", "combat/TimedAttack.java", "combat/CombatGeometry.java", "BlueprintVisualEvent.java")],
            "renderer": [probe(base + "client/" + p) for p in ("TemplateMobModel.java", "TemplateMobRenderer.java", "BlueprintVisuals.java")],
            "geo": [probe(f"src/main/resources/assets/dynasty/geo/blueprint/{row[0]}.geo.json")],
            "animation": [probe(f"src/main/resources/assets/dynasty/animations/blueprint/{row[0]}.animation.json")],
            "texture": [probe(f"src/main/resources/assets/dynasty/textures/entity/{model_atlas[kind]}.png")],
            "loot": [probe(f"src/main/resources/data/dynasty/loot_tables/entities/{row[0]}.json")],
            "navigation": [probe(base + "combat/CenteredGroundNavigation.java")] if kind == "SHIELD" else [],
            "spawn": [probe(base + p) for p in ("TemplateContentDefinitions.java", "BlueprintSpawns.java", "BlueprintSpawnState.java")]}
        tags = lambda raw, tag_kind: [dict(tagref(tag, tag_kind), status="ACTIVE_RUNTIME", activeForThisEntry=True,
            values=json.loads((ROOT / tagref(tag, tag_kind)["path"]).read_text())["values"])
            for tag in re.findall(r'tag\("([^"]+)"\)', raw)]
        spawn = {"status": "ACTIVE_RUNTIME", "dimension": "minecraft:overworld", "regionDescription": row[14],
            "biomeTags": tags(row[1], "biome"), "structureTags": tags(row[2], "structure"),
            "heightRange": {"min": int(row[3]), "max": int(row[4]), "status": "ACTIVE_RUNTIME"},
            "lightRange": [int(row[5]), int(row[6])], "timeWindow": row[7], "weatherCondition": row[8],
            "spawnWeight": {"active": int(row[9]), "definitionValue": int(row[9]),
                "status": "ACTIVE_BIOME_WEIGHT" if kind == "BEAST" else "ACTIVE_STRUCTURE_ATTEMPT_GATE"},
            "minGroup": int(row[10]), "maxGroup": int(row[11]), "localCap": int(row[12]),
            "spawnReason": row[13], "specialCondition": row[14], "despawnPolicy": row[15],
            "tagLogic": "BIOME_ANY_FOREST_OR_MOUNTAIN" if kind == "BEAST" else "PLAYER_INSIDE_REAL_TAGGED_STRUCTURE_START",
            "respawnRule": "VANILLA_NATURAL_ATTEMPTS_LOCAL_CAP" if kind == "BEAST" else
                "12000 ticks after latest member death/discard; full squad resets only when membership empty; unloaded members retained; nearby legacy BarHolder death clears marker",
            "runtimeSources": [base + "TemplateContentDefinitions.java", base + "BlueprintSpawns.java", base + "BlueprintSpawnState.java"]}
        if kind == "BEAST":
            assert modifier["spawners"]["type"] == identity
            assert modifier["spawners"]["weight"] == int(row[9])
            spawn.update(localCapScope="3 same-type loaded entities within24 blocks", daylightAcceptance=0.25,
                         spawnEggAndCommand="BYPASS_PLACEMENT_PREDICATE", biomeModifier=modifier_path)
            entry["resources"]["spawn"].append(probe(modifier_path))
        else:
            weights = attempt_weights.get(row[0], {"maximumAttemptWeight": int(row[9]),
                "dayBrightWeight": int(row[9]), "nightWeight": int(row[9]), "lowLightAtMost": None,
                "dayLowLightWeight": int(row[9])})
            spawn["spawnWeight"].update(weights, selectionPolicy="FIXED_SQUAD_WITH_PROBABILISTIC_ATTEMPT_ACCEPTANCE",
                acceptance={period: {"weight": weights[field], "outOf": weights["maximumAttemptWeight"],
                    "probability": weights[field] / weights["maximumAttemptWeight"]}
                    for period, field in (("dayBright", "dayBrightWeight"), ("night", "nightWeight"), ("dayLowLight", "dayLowLightWeight"))})
            spawn.update(localCapScope="PER_PERSISTENT_STRUCTURE_MARKER", squadComposition={
                "military_sites": {"ludun_jiashi": 1, "liannu_zhenzu": 2, "juma_changqiangbing": 1},
                "ritual_sites": {"fufa_jijiu": 1, "zuwu_daoshou": 2}},
                spawnBudget={"intervalTicks": int(re.search(r'getGameTime\(\)%(\d+)!=0', spawn_source)[1]),
                    "maximumAdditionsPerLevelPerInterval": int(re.search(r'int remaining=(\d+);', spawn_source)[1])},
                placement="Already-loaded positions inside structure; player-relative X/Z +-12 and Y -6..5; minimum player distance6; standing space and collision checks")
        entry["spawn"] = spawn
        entry["runtimeSkills"] = {"timingUnit": "SERVER_TICK_20_PER_SECOND", "baseTimeline": [skills[s] for s in assigned[kind]],
            "impactSemantics": effects[kind], "possessionSpeedMultiplier": 1.3,
            "source": base + "TemplateMob.java", "balanceStatus": "BASELINE_ONLY_GAMEPLAY_ACCEPTANCE_PENDING"}
        entry["dropsReward"].update(status=loot[identity]["status"], implemented=loot[identity]["implemented"], pending=loot[identity]["pending"])
        entry["verification"] = {"singlePlayer": solo["status"] if solo else "PENDING_MAIN_AGENT_ACCEPTANCE",
            "twoPlayer": network["status"] if network else "PENDING_MAIN_AGENT_ACCEPTANCE",
            "screenshots": [p["path"] for run in (solo, network) if run for p in run["screenshots"]],
            "serverGameTests": f"PASS_{test_count}_BLUEPRINT_TESTS",
            "modelResources": "STATIC_REVIEW_PASS_NOT_RUNTIME", "evidence": "docs/blueprint-cod1/template-verification.json",
            "note": f"PARTIAL：{test_count}项新GameTest通过；整套{total}/{total}；"
                + (f"真实单客户端{solo['stageCount']}阶段harness通过；" if solo else "未记录当前单机harness通过；")
                + (f"真实双客户端{network['stageCount']}阶段harness及实体身份核对通过；" if network else "未记录当前双端harness通过；")
                + "视觉质量、自然场景、活动战斗重连及服务器重启未据此完成；空闲重连/资源重载单独记录，不标DONE。"}
        entry["implementationEvidence"] = {"kind": kind, "texturePolicy": "REUSE_UNMODIFIED_EXISTING_OWN_ATLAS",
            "modelReview": "docs/blueprint-cod1/models/REVIEW.txt", "gameTestEvidence": "docs/blueprint-cod1/template-verification.json",
            "remaining": ([] if solo else ["Current single-client harness"])
                + ([] if network else ["Current real two-client harness"])
                + ([] if frozen else ["Frozen runClient classpath identity snapshot"])
                + ["Visual review: held gear, death floor contacts, empty robe/mask final pose, curled/faded shanxiao, particles and foot sliding",
                   "Natural-spawn/player-discovery and narrow-terrain matrix", "Active-combat two-player late tracking/rejoin and server disk restart"]
                + ([] if solo and network and all(r.get("lifecycle",{}).get("status","").startswith("PASS") for r in (solo,network))
                   else ["Actual resource reload and idle multiplayer rejoin"])
                + ([] if build_passed else ["Final production build"])
                + ["Pending decorative drops and original blueprint location/quest hooks"],
            "originalLocationPolicy": "pendingWorldPlacement retains proposed cod1 locations; those tags remain inactive and are not fabricated registrations."}
    return evidence


def world_tsv(catalog: dict) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(["name", "category", "id", "auditStatus", "implementationStatus", "definitionStatus", "dimension", "biomeStructure", "heightTimeWeather", "spawnSource", "weightGroupCap", "respawn", "prerequisites", "dropsReward", "questNode", "arenaSummon", "artifactSource", "phantomArtifactTriggerAnchorDimensions", "inGame"])
    compact = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    for entry in catalog["entries"]:
        location = entry.get("spawn", entry.get("boss", entry.get("artifact", entry.get("phantom", {}))))
        phantom = entry.get("phantom", {})
        writer.writerow([entry["name"], entry["category"], entry["id"], entry["auditStatus"], entry["implementationStatus"], entry["definitionStatus"],
                         location.get("dimension", "INHERIT_ARTIFACT_USE_POLICY"), compact({"biomeTags": location.get("biomeTags", []), "structureTags": location.get("structureTags", [])}),
                         compact({key: location.get(key) for key in ("heightRange", "timeWindow", "weatherCondition")}),
                         location.get("spawnReason", location.get("spawnMethod", location.get("sourceType", "TRIGGER_ONLY"))),
                         compact({key: location.get(key) for key in ("spawnWeight", "minGroup", "maxGroup", "localCap", "maxAlivePerStructure", "maxAlivePerArena")}),
                         location.get("respawnPolicy", location.get("respawnRule", "NO_NATURAL_SPAWN")),
                         compact(location.get("prerequisites", location.get("requiredProgress", location.get("specialCondition")))),
                         compact(entry["dropsReward"]), compact(entry["questNode"]), compact({key: location.get(key) for key in ("arena", "summonCondition")}),
                         location.get("sourceDescription", ""), compact(phantom) if phantom else "", entry["verification"]["note"]])
    return stream.getvalue()


def validate(catalog: dict, source: Path) -> dict:
    errors, pending = [], []
    if catalog["source"]["sha256"] != digest(source):
        errors.append("Blueprint source changed since catalog generation")
    specs = {(x["category"], x["number"]): x for x in read_spec(source)}
    entries = catalog["entries"]
    if collections.Counter(e["category"] for e in entries) != COUNTS:
        errors.append("Category counts differ from 30/15/12/25/12")
    if len({e["id"] for e in entries}) != 94:
        errors.append("IDs not unique")
    dimensions = {"minecraft:overworld", "minecraft:the_nether", "minecraft:the_end"} | {"dynasty:" + p.stem for p in (ROOT / "src/main/resources/data/dynasty/dimension").glob("*.json")}
    required = {
        "BASIC": ("spawn", "dimension biomeTags structureTags heightRange lightRange timeWindow weatherCondition spawnWeight minGroup maxGroup localCap spawnReason specialCondition despawnPolicy"),
        "ELITE": ("spawn", "dimension primaryLocation secondaryRareLocation spawnMethod respawnRule maxAlivePerStructure bossDependency"),
        "BOSS": ("boss", "dimension arena summonCondition requiredProgress arenaCenterSource firstKillReward repeatKillReward respawnPolicy worldStateKey"),
        "ARTIFACT": ("artifact", "id sourceType dimension sourceId firstTimeOnly repeatable prerequisites"),
        "PHANTOM": ("phantom", "artifactId allowedDimensions anchorType duration renderDistance firstPersonRule multiplayerVisibility"),
    }
    for entry in entries:
        spec = specs.get((entry["category"], entry["number"]))
        if not spec or entry["name"] != spec["name"]:
            errors.append(f"Exact source name mismatch: {entry['id']}")
        if spec and entry["source"]["sha256"] != spec["sourceBlockSha256"]:
            errors.append(f"Blueprint entry changed since audit: {entry['id']}")
        location = entry.get("spawn", entry.get("boss", entry.get("artifact", entry.get("phantom", {}))))
        section, keys = required[entry["category"]]
        missing = set(keys.split()) - set(entry.get(section, {}))
        if missing:
            errors.append(f"Missing definition fields for {entry['id']}: {sorted(missing)}")
        if "dimension" in location and location["dimension"] not in dimensions:
            errors.append(f"Nonexistent dimension: {entry['id']}")
        for tag in location.get("structureTags", []) + location.get("biomeTags", []):
            if tag.get("path") and tag["exists"] != (ROOT / tag["path"]).is_file():
                errors.append(f"Tag existence mismatch for {entry['id']}: {tag['id']}")
            if tag["status"] == "PROPOSED_PENDING" and tag["activeForThisEntry"]:
                errors.append(f"Proposed tag falsely marked active: {entry['id']}")
            if tag.get("activeForThisEntry") and not tag.get("exists"):
                errors.append(f"Active tag does not exist: {entry['id']}: {tag['id']}")
        if entry["category"] == "PHANTOM" and location["serverEntity"]:
            errors.append(f"Phantom registered as server entity: {entry['id']}")
        for resource_list in entry["resources"].values():
            for resource in resource_list:
                if isinstance(resource, dict) and "path" in resource:
                    actual = (ROOT / resource["path"]).is_file()
                    if actual != resource["exists"] or actual and resource.get("sha256") != digest(ROOT / resource["path"]):
                        pending.append({"id": entry["id"], "path": resource["path"], "recordedExists": resource["exists"], "actualExists": actual, "note": "Resource changed since scan; regenerate or update evidence"})
        if entry["implementationStatus"] == "DONE" and (entry["verification"]["singlePlayer"] != "PASS" or entry["verification"]["twoPlayer"] != "PASS"):
            errors.append(f"Unverified DONE: {entry['id']}")
        if entry["definitionStatus"] == "ACTIVE_RUNTIME":
            if entry.get("exactExistingId") != entry["id"] or entry["implementationStatus"] == "NOT_STARTED":
                errors.append(f"Active entry lacks implemented identity: {entry['id']}")
            for key in ("implementationClass", "geo", "animation", "texture", "loot", "spawn"):
                if not entry["resources"].get(key) or not all(p["exists"] for p in entry["resources"][key]):
                    errors.append(f"Missing active resource {key}: {entry['id']}")
    mixed = next(e for e in entries if e["id"] == "dynasty:hunyuan_zushou")
    if mixed["boss"].get("preservedFinalBoss") != "dynasty:zhenyuan_sovereign" or mixed["boss"].get("integrationStatus") != "PENDING_CONFIRMATION":
        errors.append("Final-boss conflict protection lost")
    return {"valid": not errors, "errors": errors, "resourceEvidenceChanges": pending,
            "counts": dict(collections.Counter(e["category"] for e in entries)),
            "implementationCounts": dict(collections.Counter(e["implementationStatus"] for e in entries)),
            "initialMissingExactIdentities": sum(e["auditStatus"] == "MISSING" for e in entries),
            "missingExactIdentities": sum(e.get("exactExistingId") is None for e in entries),
            "currentImplementedExactIdentities": sum(e.get("exactExistingId") == e["id"] for e in entries),
            "activeRuntimeDefinitions": sum(e["definitionStatus"] == "ACTIVE_RUNTIME" for e in entries),
            "pendingArtifactBindings": [e["id"] for e in entries if e.get("phantom", {}).get("artifactBindingStatus") == "PENDING_ARTIFACT_ID_NOT_DEFINED_IN_25"],
            "runtimeVerified": False, "note": "Static definition/resource validation only; runtime evidence is tracked per entry and complete acceptance is not implied by this report."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--generate", action="store_true", help="Mechanically regenerate reports; preserve implementation fields")
    parser.add_argument("--check", action="store_true", help="Read-only name/count/dimension/evidence validation")
    parser.add_argument("--baseline-log", type=Path, default=Path("/tmp/dynasty-cod1-baseline.log"))
    parser.add_argument("--refresh-inventory", action="store_true", help="Explicitly replace the static inventory after scanner changes; never replaces build evidence")
    parser.add_argument("--refresh-templates", action="store_true", help="With --generate, extract current four prototypes as PARTIAL with explicit server-test evidence")
    parser.add_argument("--template-test-log", type=Path, help="Explicit complete successful server test log; counts are read from annotations and the log")
    parser.add_argument("--solo-evidence", type=Path, help="Current complete 20-stage solo run directory (or its host directory); never implies visual-quality acceptance")
    parser.add_argument("--network-evidence", type=Path, help="Current complete 20-stage run root containing host, peer and coord; requires real two-player evidence")
    args = parser.parse_args()
    if args.refresh_templates and not args.generate:
        parser.error("--refresh-templates requires --generate")
    if args.refresh_templates and args.template_test_log is None:
        parser.error("--refresh-templates requires an explicit --template-test-log")
    if (args.solo_evidence or args.network_evidence) and not args.refresh_templates:
        parser.error("Client evidence options require --refresh-templates; use the parser API for a read-only check")
    if args.generate:
        OUT.mkdir(parents=True, exist_ok=True)
        catalog = make_catalog(args.source)
        if args.refresh_templates:
            evidence = refresh_templates(catalog, args.template_test_log,
                args.solo_evidence.resolve() if args.solo_evidence else None,
                args.network_evidence.resolve() if args.network_evidence else None)
            (OUT / "template-verification.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
        (OUT / "content-definitions.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
        (OUT / "world-placement.tsv").write_text(world_tsv(catalog))
        snapshot = OUT / "registry-snapshot.json"
        if not snapshot.exists() or args.refresh_inventory:
            snapshot.write_text(json.dumps(scan_inventory(), ensure_ascii=False, indent=2) + "\n")
        baseline = OUT / "baseline-build.json"
        if not baseline.exists():
            log = args.baseline_log.read_text()
            assert "BUILD SUCCESSFUL" in log, "Missing successful baseline build evidence"
            baseline.write_text(json.dumps({"command": "./gradlew build --offline", "exitStatus": "SUCCESS", "evidencePath": str(args.baseline_log),
                                           "evidenceSha256": digest(args.baseline_log), "result": "BUILD SUCCESSFUL in 3s", "testTask": "NO-SOURCE",
                                           "runtimeVerified": False, "note": "Baseline executed by main agent before implementation; source snapshot is an independent static scan, not a byte-for-byte archive of that build."}, ensure_ascii=False, indent=2) + "\n")
    else:
        catalog = json.loads((OUT / "content-definitions.json").read_text())
    report = validate(catalog, args.source)
    if args.generate:
        (OUT / "catalog-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
