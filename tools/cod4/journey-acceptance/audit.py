#!/usr/bin/env python3
"""Publish reproducible, scoped evidence; never mark survival/client acceptance complete."""
import argparse
import collections
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = HERE / '.work'
sys.path.insert(0, str(ROOT / 'tools/art'))
from quest_snbt import list_compounds, object_id


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return str(path.relative_to(ROOT))


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def primary_mapping_refresh(map_path):
    path = ROOT / 'docs/cod4/audit-20261022/task-location-refresh.json'
    if not path.exists():
        return None
    refresh = json.loads(path.read_text())
    current_sha = sha(map_path)
    return {'evidence': rel(path), 'evidence_sha256': sha(path),
            'before_sha256': refresh['before_sha256'], 'after_sha256': refresh['after_sha256'],
            'current_map_sha256': current_sha,
            'current_matches_refresh_after': current_sha == refresh['after_sha256'],
            'changed_rows': refresh['changed_rows'],
            'corrected_chapter_references': refresh['corrected_chapter_references'],
            'all_live_quest_ids': refresh['all_live_quest_ids'],
            'changed_columns': ['CURRENT_TASK', 'TASK_STAGE', 'NOTES'],
            'preserved_columns': refresh['preserved_columns'],
            'task_id_or_game_file_changes': refresh['task_id_or_game_file_changes'],
            'interpretation': '主代理的修复记录；旧审计186条仅统计已不存在的章节名，317处为主代理章节及stage引用校准，统计口径不同。是否仍匹配修复后版本以本次current_matches_refresh_after为准。'}


def input_items(value):
    if isinstance(value, dict):
        if 'item' in value:
            yield value['item']
        if 'tag' in value:
            yield '#' + value['tag']
        for key, child in value.items():
            if key not in ('result', 'item', 'tag'):
                yield from input_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from input_items(child)


def loot_items(value):
    if isinstance(value, dict):
        if value.get('type') == 'minecraft:item':
            yield value['name']
        for child in value.values():
            yield from loot_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from loot_items(child)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='server-20261023-contract')
    parser.add_argument('--log', default='native-20261023-contract.log')
    args = parser.parse_args()
    native_path = WORK / args.run / 'native-results.json'
    log_path = WORK / args.log
    native = json.loads(native_path.read_text())
    log = log_path.read_text()
    assert 'Game test server shutting down' in log, 'Do not publish an incomplete run'
    assert 'BUILD SUCCESSFUL' in log and all(x['pass'] for x in native), 'Acceptance requires an actually passing final run'
    evidence = HERE / 'evidence/20261023'
    evidence.mkdir(parents=True, exist_ok=True)
    for source, name in [(native_path, 'native-results.json'), (log_path, 'native.log'),
                         (WORK / 'source-hashes.json', 'source-hashes.json')]:
        shutil.copy2(source, evidence / name)
    # Preserve failed runs with an explicit invalid-contract classification, not as product failures.
    history = []
    for source_run, source_log, label in [('server-final', 'native-final.log', '20261022'),
                                         ('server-20261023', 'native-20261023.log', '20261023-before-contract-correction')]:
        target = HERE / 'evidence' / label
        target.mkdir(parents=True, exist_ok=True)
        for source, name in [(WORK / source_run / 'native-results.json', 'native-results.json'),
                             (WORK / source_log, 'native.log')]:
            if source.exists() and not (target / name).exists():
                shutil.copy2(source, target / name)
        history.append({'path': rel(target), 'status': 'SUPERSEDED_INVALID_TEST_CONTRACT',
                        'reason': '三项普通合成 NBT 继承断言由本验收自行添加；原需求不支持，不能列为生产缺陷。'})
    fixture_history = HERE / 'evidence/20261022-fixture-error'
    fixture_history.mkdir(parents=True, exist_ok=True)
    for source, name in [(WORK / 'server-baseline/native-results.json', 'native-results.json'),
                         (WORK / 'native-baseline.log', 'native.log')]:
        if source.exists() and not (fixture_history / name).exists():
            shutil.copy2(source, fixture_history / name)
    history.append({'path': rel(fixture_history), 'status': 'SUPERSEDED_TEST_FIXTURE_ERROR',
                    'reason': '首轮544个工作台结果为空是私有CraftingMenu使用ContainerLevelAccess.NULL导致；原生RecipeManager已选中正确配方。补实际世界上下文后通过，未改生产配方。'})

    frozen = WORK / 'frozen'
    data = frozen / 'src/main/resources/data/dynasty'
    recipes, outputs, uses, loot = {}, collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
    passed = {(x['id'], x['check']) for x in native if x['pass']}
    for path in sorted((data / 'recipes').rglob('*.json')):
        definition = json.loads(path.read_text())
        rid = 'dynasty:' + str(path.relative_to(data / 'recipes').with_suffix(''))
        result = definition['result']
        output = result['item'] if isinstance(result, dict) else result
        # Shaped costs count repeated symbols, not just distinct keys.
        if definition['type'] == 'minecraft:crafting_shaped':
            inputs = [item for row in definition['pattern'] for symbol in row if symbol != ' '
                      for item in input_items(definition['key'][symbol])]
        else:
            inputs = list(input_items(definition))
        check = {'minecraft:crafting_shaped': 'native_crafting_payment',
                 'minecraft:crafting_shapeless': 'native_crafting_payment',
                 'minecraft:smithing_transform': 'native_smithing_payment_and_nbt',
                 'minecraft:smelting': 'native_furnace_payment'}[definition['type']]
        recipes[rid] = {'path': str(path.relative_to(frozen)), 'sha256': sha(path), 'type': definition['type'],
                        'result': output, 'result_count': result.get('count', 1) if isinstance(result, dict) else 1,
                        'inputs': dict(collections.Counter(inputs)), 'native_check': check,
                        'native_pass': (rid, check) in passed}
        outputs[output].append(rid)
        for item in set(inputs):
            uses[item].append(rid)
    assert len(recipes) == 595 and all(x['native_pass'] for x in recipes.values())
    for path in sorted((data / 'loot_tables').rglob('*.json')):
        for item in set(loot_items(json.loads(path.read_text()))):
            loot[item].append(str(path.relative_to(frozen)))
    dump(evidence / 'recipe-index.json', recipes)

    source_manifest = json.loads((WORK / 'source-hashes.json').read_text())
    drift = [p for p, digest in source_manifest.items() if not (ROOT / p).exists() or sha(ROOT / p) != digest]
    references_path = ROOT / 'docs/cod4/audit-20261022/quest-reference-1000.json'
    references = json.loads(references_path.read_text())
    reference_files, mismatches = {}, []
    for site in references['sites']:
        path = Path(site['file'])
        reference_files.setdefault(str(path), sha(path) if path.exists() else None)
        if reference_files[str(path)] != site['file_sha256']:
            mismatches.append(site['quest'])
    assert len(references['sites']) == len({s['semantic_sha256'] for s in references['sites']}) == 1000
    assert not mismatches

    chapters = ROOT / 'modpack/config/ftbquests/quests/chapters'
    nodes, links, chapter_hashes = {}, collections.defaultdict(list), {}
    for path in sorted(chapters.glob('*.snbt')):
        raw = path.read_text(); chapter_hashes[rel(path)] = sha(path)
        for block in list_compounds(raw, 'quests'):
            identity = object_id(block)
            inner = '\n'.join(line[2:] if line.startswith('\t\t') else line for line in block.splitlines())
            deps = re.search(r'^\tdependencies:\s*\[([^\]]*)\]', inner, re.M)
            node = {'chapter': path.stem, 'quest': identity, 'path': rel(path),
                    'line': raw.count('\n', 0, raw.index(block)) + 1,
                    'dependencies': re.findall(r'"([0-9A-Fa-f]{16})"', deps[1]) if deps else []}
            nodes[identity] = node
            for task in list_compounds(inner, 'tasks'):
                items = set(re.findall(r'\b(?:id|entity):\s*"dynasty:([^"]+)"', task))
                adv = re.search(r'\badvancement:\s*"dynasty:cod4_(?:obtain_)?([^"]+)"', task)
                if adv:
                    items.add(adv[1])
                for item in items:
                    if node not in links[item]:
                        links[item].append(node)
    map_path = ROOT / 'docs/cod4/content-task-map.tsv'
    rows = list(csv.DictReader(map_path.open(), delimiter='\t'))
    names = {p.stem for p in chapters.glob('*.snbt')}
    stale_locations, unresolved_ids = [], []
    for row in rows:
        for chapter in row['CURRENT_TASK'].split(';'):
            if chapter != 'NO_CURRENT_TASK_LINK' and chapter not in names:
                stale_locations.append({'content': row['CONTENT_ID'], 'mapped_chapter': chapter,
                                        'actual_links': links.get(row['CONTENT_ID'], [])})
        for node_id in re.findall(r':([0-9a-fA-F]{16})', row['TASK_STAGE']):
            if node_id not in nodes:
                unresolved_ids.append({'content': row['CONTENT_ID'], 'quest': node_id})
    # Preserve the original pre-refresh snapshot; bind subsequent audits to their actual input.
    map_sha = sha(map_path)
    mapping_evidence = evidence / f'task-location-audit-{map_sha}.json'
    dump(mapping_evidence, {'input_sha256': map_sha, 'chapter_hashes': chapter_hashes,
         'stale_locations': stale_locations, 'unresolved_ids': unresolved_ids, 'actual_links': dict(links)})

    java_sources = {
        'dragon_emperor_seal': ['src/main/java/com/dynasty/DynastyBossDrops.java:38'],
        'emperor_bone': ['src/main/java/com/dynasty/DynastyBossDrops.java:43'],
        'dragon_spear': ['src/main/java/com/dynasty/DynastyBossDrops.java:45'],
        'rebel_head': ['src/main/java/com/dynasty/DynastyBossDrops.java:48'],
        'eunuch_token': ['src/main/java/com/dynasty/DynastyBossDrops.java:53'],
        'sky_token': ['src/main/java/com/dynasty/DynastyBossDrops.java:63'],
        'sea_token': ['src/main/java/com/dynasty/DynastyBossDrops.java:68'],
        'sunbow': ['src/main/java/com/dynasty/DynastyWeaponGifts.java:63'],
        'silver_ingot': ['src/main/java/com/dynasty/DynastyBossDrops.java:54',
                         'src/main/java/com/dynasty/cod3/DynastyNpcEntity.java:78'],
        'jade_crown': ['src/main/java/com/dynasty/expansion/ContentProgress.java'],
    }

    def source(item):
        full = item if ':' in item else 'dynasty:' + item
        return {'item': full, 'recipes': outputs.get(full, []), 'loot_tables': loot.get(full, []),
                'java_sources': java_sources.get(full.split(':', 1)[1], []),
                'source_status': 'STATIC_INDEX; presence alone does not prove natural world availability'}

    material_mobs = {'qimen_cable': 'clockwork_rat', 'qimen_gear': 'wooden_magpie', 'fox_pelt': 'red_fox',
                     'wolf_fang': 'gray_wolf', 'python_gall': 'giant_python', 'crab_shell': 'crab_soldier',
                     'kappa_scale': 'river_imp', 'sprite_jade': 'stone_sprite', 'lantern_oil': 'lantern_ghost',
                     'locust_dust': 'locust_swarm'}
    materials = []
    for material, mob in material_mobs.items():
        materials.append({**source(material), 'native_death_source': mob,
            'native_death_pass': (material, 'native_player_death_source') in passed,
            'original_recipe_uses': uses.get('dynasty:' + material, []), 'actual_task_nodes': links.get(material, []),
            'biome_modifier': 'src/main/resources/data/dynasty/forge/biome_modifier/secondary_' + mob + '.json',
            'natural_habitat_check': 'src/main/java/com/dynasty/expansion/SecondarySpawnHooks.java',
            'natural_encounter_acceptance': 'PENDING'})

    stage_specs = [
        ('开局', ['mu_mao', 'cloth_chestplate', 'bamboo_chestplate', 'pickaxe_jade'], ['raw_silk', 'silk', 'jade'],
         '木矛和布衣进入原后续配方；玉矿熔炼已验，矿脉发现和2–3小时节奏未验。'),
        ('早期', ['tong_dao', 'tie_jian', 'bronze_chestplate', 'sword_silver'], ['bronze_ingot', 'silver_ingot', 'refined_steel', 'cinnabar'],
         '铜/铁/青铜原配方可执行；银锭的原宝箱、刺客/Boss掉落和世界变化后商店已定位，未做自然寻路验收。'),
        ('中期', ['sword_jade', 'jade_chestplate', 'silk_pouch', 'jade_crown'], ['jade', 'blueprint', 'silver_ingot'],
         '官银剑可作玉剑材料；冠的官阶赠予是原Java入口，本批未完成科举到赠冠实玩。'),
        ('中后期', ['zhenyue_blade', 'liuyun_sword', 'zhuxing_bow', 'chiling_brush', 'pojun_ring', 'siege_crossbow'],
         ['qimen_gear', 'qimen_cable', 'refined_steel', 'dragon_crystal'],
         '学院兵器、流派饰品和奇门原配方已验；实际掉落→材料交易→原奇门商店链已验，官阶3是测试前提。'),
        ('后期', ['sword_dragon_crystal', 'tianzi_sword', 'qinglong_dao', 'xuanwu_blade', 'zhuque_fan', 'dragon_spear', 'sunbow'],
         ['dragon_crystal', 'dragon_scale', 'sea_token', 'sky_token', 'emperor_bone', 'dragon_emperor_seal'],
         '原升级配方已验；令牌、龙枪与射日弓的原掉落/授武入口已定位，本批未用自然Boss战取得全部材料。'),
        ('终盘', ['xuantian_chestplate', 'beidou_chestplate', 'hongmeng_chestplate', 'houyi_bow', 'bawang_spear'],
         ['xuantian_jade', 'dragon_crystal', 'emperor_bone', 'dragon_emperor_seal'],
         '终盘原配方已验；玄天/鸿蒙是终点套装，保留原套装效果；镇渊前置、真实成本和替代时机仍待生存验收。'),
    ]
    stages = []
    for name, targets, raw, note in stage_specs:
        stages.append({'stage': name, 'status': 'NATIVE_RECIPE_AND_STATIC_SOURCE_PARTIAL; survival pending',
            'targets': [{**source(item), 'task_nodes': links.get(item, []),
                         'old_item_recipe_uses': uses.get('dynasty:' + item, [])} for item in targets],
            'materials': [source(item) for item in raw], 'assessment': note})

    old_armor = []
    for row in rows:
        if row['TYPE'] != 'armor':
            continue
        pieces = {}
        for slot in ('helmet', 'chestplate', 'leggings', 'boots'):
            item = row['CONTENT_ID'] + '_' + slot
            pieces[item] = {'production_recipes': outputs.get('dynasty:' + item, []),
                            'later_recipe_uses': uses.get('dynasty:' + item, [])}
        old_armor.append({'set': row['CONTENT_ID'], 'pieces': pieces,
            'continuing_value': 'original_recipe_material' if any(p['later_recipe_uses'] for p in pieces.values())
                                else 'terminal_set_behavior; EquipmentBehaviors.java (static, not new runtime acceptance)',
            'nbt_transfer': 'Ordinary crafting is not promised to copy old NBT; native smithing is checked separately.'})
    interactions = [{'id': row['CONTENT_ID'], 'actual_task_nodes': links.get(row['CONTENT_ID'], []),
                     'implementation': 'src/main/java/com/dynasty/expansion/SmallInteractions.java',
                     'acceptance': 'NOT_RETESTED_HERE; source index only, no natural placement/timing/secret completion claim'}
                    for row in rows if row['TYPE'] == 'interaction']
    counts = collections.Counter(x['check'] for x in native)
    report = {
        'schema_version': 1, 'date': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'scope': ['COD4-7', 'COD4-11', 'COD4-14'],
        'input_path_resolution': '请求的audit-20261022/content-task-map.tsv不存在；读取实际docs/cod4/content-task-map.tsv。',
        'status': 'SCOPED_NATIVE_CHECKS_PASSED; full survival journey NOT certified',
        'production_changes': [],
        'fixes': ['修复私有测试脚手架的CraftingMenu缺失世界上下文。',
                  '撤销普通合成必须继承全部NBT的自行添加断言，改验原需求中的旧装备材料用途。'],
        'confirmed_production_breaks': [],
        'requirement_correction': {
            'retracted_claim': '银剑→玉剑、连弩→重弩、布衣→竹甲的NBT清空是既定缺陷。',
            'finding': '三次原生NBT变化确实发生，但不构成已确认需求违反；原规格明确区分普通合成与锻造进化。',
            'evidence': ['docs/cod4/audit-20261022/cod4-before.txt:175', 'docs/cod4/request.txt:392',
                         'tools/art/quest_growth.py:69',
                         'modpack/config/ftbquests/quests/chapters/dynasty_build_sword.snbt:271',
                         'modpack/config/ftbquests/quests/chapters/dynasty_build_archer.snbt:336',
                         'src/main/java/com/dynasty/DynastyWeaponProgression.java:14'],
            'existing_supported_interface': '47 existing minecraft:smithing_transform recipes, executed through native SmithingMenu',
            'java_coordination_needed': False, 'general_crafting_nbt_policy': 'No new product policy introduced',
            'historical_runs': history,
        },
        'research': {'record': rel(references_path), 'sha256': sha(references_path), 'reused_count': 1000,
            'unique_semantic_count': 1000, 'verified_source_files': len(reference_files), 'source_hash_mismatches': mismatches,
            'applicability': 'Same existing quest objective/material/predecessor/reward chain audit. No new mechanic or production change.',
            'limits': '既有机器辅助结构研究的复用及源文件核验；不是新做1000次实玩，也不能推出所有合成都应继承NBT。'},
        'native': {'game_tests': 6, 'failed_game_tests': 0, 'transaction_or_source_records': len(native),
            'records_by_check': dict(counts), 'unique_materials_from_native_death': 10,
            'recipe_coverage': {'total': len(recipes), 'crafting': 544, 'smithing': 47, 'smelting': 4},
            'evidence': rel(evidence), 'native_results_sha256': sha(evidence / 'native-results.json'),
            'log_sha256': sha(evidence / 'native.log'), 'source_manifest_sha256': sha(evidence / 'source-hashes.json'),
            'snapshot_current_drift': drift,
            'snapshot_current_java_or_data_drift': [p for p in drift if '/java/' in p or '/data/' in p],
            'asset_drift_note': '其他聊天的资产变更独立列出；本轮仅验服务器配方/来源，未写资产也未验客户端显示。',
            'limitations': ['无创造取出成品；配方底料/旧装备NBT为测试夹具，不能证明原料自然获取。',
                           '每条配方使用其原生Ingredient列出的第一个可用原料；未穷举同标签所有木种等替代输入。',
                           '掉落来自实际玩家伤害死亡，但实体由测试放置、生命降到1且随机种子固定；不证明自然生成率或战斗难度。',
                           '商店使用原入口和MerchantMenu实际扣料；NPC位置和既有官阶3解锁为测试夹具。',
                           '未加载完整整合包、FTB或Curios；不是客户端/双人验收。']},
        'recipe_index': rel(evidence / 'recipe-index.json'),
        'task_mapping': {'input': rel(map_path), 'status': 'CURRENT_AT_REPORT_GENERATION',
            'sha256': map_sha, 'rows': len(rows), 'live_quests': len(nodes),
            'stale_chapter_location_references': len(stale_locations), 'unresolved_node_references': len(unresolved_ids),
            'details': rel(mapping_evidence), 'primary_refresh': primary_mapping_refresh(map_path),
            'historical_pre_refresh_details': rel(evidence / 'task-location-audit.json'),
            'interpretation': '章节位置映射陈旧与任务ID丢失分别记录；未修改映射或任务书，不据此宣称玩法断链。'},
        'materials': materials, 'six_stages': stages, 'old_armor': old_armor, 'interactions': interactions,
        'remaining_acceptance': ['六阶段真实生存连续流程、自然材料/NPC/Boss发现与实际制作成本。',
            '开局2–3小时、Build替代时机和终盘实战价值。', '15个互动自然放置、实际时长、秘密联动和多人隔离。',
            '完整整合包FTB/JEI导航、真实旧档重启与双客户端。',
            '除已列原生来源外，晚期Boss材料和条件授武只完成来源定位，未在本批自然取得。'],
    }
    target = ROOT / 'docs/cod4/audit-20261022/journey-acceptance.json'
    dump(target, report)
    print(json.dumps({'report': rel(target), 'native_records': len(native), 'recipe_count': len(recipes),
                      'stale_map_locations': len(stale_locations), 'unresolved_map_ids': len(unresolved_ids),
                      'source_drift_count': len(drift),
                      'java_or_data_drift': [p for p in drift if '/java/' in p or '/data/' in p]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
