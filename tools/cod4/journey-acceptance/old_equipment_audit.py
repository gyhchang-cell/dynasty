#!/usr/bin/env python3
"""Read actual saved Forge registry + original recipes/native receipts; never change gameplay."""
import collections
import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / 'evidence/20261023'
OUT = HERE / 'evidence/old-equipment-utility'
sys.path.insert(0, str(ROOT / 'tools/art'))
from quest_snbt import list_compounds, object_id
from utility_runtime import bind as bind_runtime


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return str(path.relative_to(ROOT))


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def read_nbt(path):
    """Read the existing native server's level.dat without editing or starting that world."""
    stream = io.BytesIO(gzip.decompress(path.read_bytes()))

    def number(fmt):
        return struct.unpack('>' + fmt, stream.read(struct.calcsize('>' + fmt)))[0]

    def string():
        return stream.read(number('H')).decode('utf-8')

    def payload(kind):
        if 1 <= kind <= 6:
            return number({1: 'b', 2: 'h', 3: 'i', 4: 'q', 5: 'f', 6: 'd'}[kind])
        if kind == 7:
            return stream.read(number('i'))
        if kind == 8:
            return string()
        if kind == 9:
            child, length = number('B'), number('i')
            return [payload(child) for _ in range(length)]
        if kind == 10:
            result = {}
            while (child := number('B')):
                name = string()
                result[name] = payload(child)
            return result
        if kind in (11, 12):
            return [number('i' if kind == 11 else 'q') for _ in range(number('i'))]
        raise ValueError(kind)

    kind = number('B')
    string()
    return payload(kind)


def source(path, line=1):
    return {'path': rel(path), 'line': line, 'sha256': sha(path)}


def equipment_inventory():
    rows = {}
    for name in ('DynastyGear.java', 'DynastyWeapons.java', 'expansion/ExpansionContent.java'):
        path = ROOT / 'src/main/java/com/dynasty' / name
        raw = path.read_text()
        pattern = r'RegistryObject<Item>\s+\w+\s*=\s*(?:ITEMS.register|sword|pickaxe|armor)\("([^"]+)"'
        for match in re.finditer(pattern, raw):
            item = match[1]
            category = ('armor' if item.endswith(('_helmet', '_chestplate', '_leggings', '_boots'))
                        else 'tool' if item.startswith('pickaxe_') else 'weapon')
            rows['dynasty:' + item] = {'item': 'dynasty:' + item, 'category': category,
                'registration': source(path, raw.count('\n', 0, match.start()) + 1)}
    path = ROOT / 'src/main/java/com/dynasty/DynastyGear.java'
    raw = path.read_text()
    for match in re.finditer(r'\{"([^"]+)", DynastyArmorMaterials\.', raw):
        for slot in ('helmet', 'chestplate', 'leggings', 'boots'):
            item = 'dynasty:' + match[1] + '_' + slot
            rows[item] = {'item': item, 'category': 'armor', 'registration': {
                **source(path, raw.count('\n', 0, match.start()) + 1),
                'expansion': 'registerExtraSets:143-146; all four actual registered slots'}}
    path = ROOT / 'src/main/java/com/dynasty/blueprint/artifact/ArtifactContent.java'
    raw = path.read_text()
    for match in re.finditer(r'RegistryObject<Item>\s+\w+\s*=ITEMS.register\((\w+),', raw):
        item = re.search(r'String ' + match[1] + r'="([^"]+)"', raw)[1]
        rows['dynasty:' + item] = {'item': 'dynasty:' + item, 'category': 'weapon',
            'registration': source(path, raw.count('\n', 0, match.start()) + 1)}
    assert len(rows) == 180, 'Registry class inventory changed; review denominator, do not silently omit items'
    rows['minecraft:crossbow'] = {'item': 'minecraft:crossbow', 'category': 'weapon',
        'registration': {'source': 'vanilla 1.20.1; actual saved Forge minecraft:item registry',
                         'inclusion': 'Direct original predecessor of dynasty:repeating_crossbow'}}
    return rows


def registration_closure(native_sources, tracked):
    roots = {'SwordItem', 'AxeItem', 'PickaxeItem', 'ShovelItem', 'HoeItem', 'TieredItem', 'DiggerItem',
             'BowItem', 'CrossbowItem', 'ProjectileWeaponItem', 'ArmorItem', 'ShieldItem', 'TridentItem',
             'ShearsItem', 'FishingRodItem'}
    declarations, registrars = [], []
    for path in sorted((ROOT / 'src/main/java').rglob('*.java')):
        raw = path.read_text()
        for match in re.finditer(r'\bclass\s+(\w+)\s+extends\s+([\w.]+)', raw):
            declarations.append({'class': match[1], 'base': match[2].split('.')[-1],
                                 'source': source(path, raw.count('\n', 0, match.start()) + 1)})
        if re.search(r'DeferredRegister\s*<\s*Item\s*>|\bITEMS\.register\(', raw):
            registrars.append(path)
    classes = set(roots)
    while (added := {d['class'] for d in declarations if d['base'] in classes} - classes):
        classes.update(added)
    equipment_types = [d for d in declarations if d['class'] in classes]
    sources = set(registrars) | {ROOT / d['source']['path'] for d in equipment_types}
    assert all(sha(p) == native_sources.get(rel(p)) for p in sources), 'Registry/type drift: native saved inventory may be stale'
    factories = [rel(p) for p in registrars if any(re.search(r'\b' + re.escape(c) + r'\s*(?:\(|::new)', p.read_text()) for c in classes)]
    assert set(factories) == {'src/main/java/com/dynasty/DynastyGear.java',
        'src/main/java/com/dynasty/DynastyWeapons.java', 'src/main/java/com/dynasty/expansion/ExpansionContent.java',
        'src/main/java/com/dynasty/blueprint/artifact/ArtifactContent.java'}, 'Additional equipment registrar must join inventory'
    tracked.update(sources)
    dump(OUT / 'registration-closure.json', {'base_classes': sorted(roots),
        'equipment_subclass_declarations': equipment_types,
        'all_item_registration_sources': [source(p) for p in registrars],
        'equipment_factory_sources': factories, 'all_sources_match_native_snapshot': True,
        'method': 'Read all production Java class declarations to a fixed point; inspect every Item deferred/register source. Enumerate all literals and all 21 table-driven armor sets from the four resulting equipment factories; cross-check each with the actual saved native registry. Fail if factory/source set changes.'})


def quest_acquisition(rows, tracked):
    nodes, links = {}, collections.defaultdict(list)
    for path in sorted((ROOT / 'modpack/config/ftbquests/quests/chapters').glob('*.snbt')):
        tracked.add(path)
        raw = path.read_text()
        for block in list_compounds(raw, 'quests'):
            inner = '\n'.join(line[2:] if line.startswith('\t\t') else line for line in block.splitlines())
            identity = object_id(block).lower()
            dependency = re.search(r'^\tdependencies:\s*\[([^\]]*)\]', inner, re.M)
            title = re.search(r'^\ttitle:\s*"([^"\n]*)"', inner, re.M)
            objectives = set()
            rewards = set()
            for field, found in (('tasks', objectives), ('rewards', rewards)):
                for entry in list_compounds(inner, field):
                    kind = re.search(r'\btype:\s*"([^"]+)"', entry)
                    if not kind:
                        continue
                    if kind[1] == 'item':
                        item = re.search(r'\bitem:\s*\{\s*id:\s*"([^"]+)"', entry)
                        if item:
                            found.add(item[1])
                    elif field == 'tasks' and kind[1] == 'advancement':
                        adv = re.search(r'\badvancement:\s*"dynasty:([^"]+)"', entry)
                        if not adv:
                            continue
                        ap = ROOT / 'src/main/resources/data/dynasty/advancements' / (adv[1] + '.json')
                        if not ap.exists():
                            continue
                        tracked.add(ap)
                        for criterion in json.loads(ap.read_text()).get('criteria', {}).values():
                            if criterion.get('trigger') == 'minecraft:inventory_changed':
                                for predicate in criterion.get('conditions', {}).get('items', []):
                                    found.update(predicate.get('items', []))
            nodes[identity] = {'quest': identity, 'chapter': path.stem, 'path': rel(path),
                'line': raw.count('\n', 0, raw.index(block)) + 1, 'title': title[1] if title else '',
                'dependencies': [v.lower() for v in re.findall(r'"([0-9a-fA-F]{16})"', dependency[1])] if dependency else [],
                'equipment_objectives': sorted(objectives & rows.keys()),
                'equipment_rewards': sorted(rewards & rows.keys())}
            for item in (objectives | rewards) & rows.keys():
                links[item].append(identity)
    assert len(nodes) == 1259, 'Published task graph changed; review audit assumptions'
    assert all(dep in nodes for n in nodes.values() for dep in n['dependencies'])

    def ancestors(node):
        visited, queue = set(), list(nodes[node]['dependencies'])
        while queue:
            current = queue.pop()
            if current in visited:
                continue
            visited.add(current)
            queue.extend(nodes[current]['dependencies'])
        return visited

    for item, row in rows.items():
        row['acquisition_tasks'] = [nodes[n] for n in links[item]]
        row['earlier_equipment_objectives'] = sorted({gear for n in links[item] for prior in ancestors(n)
            for gear in nodes[prior]['equipment_objectives'] if gear != item})
    dump(OUT / 'quest-acquisition-graph.json', {'nodes': nodes,
        'interpretation': 'Only actual item objectives/rewards and inventory_changed predicates; icons/descriptions excluded. Quest prerequisites establish availability/order hints, not actual play time or automatic replacement.'})


TERMINAL = {
    'bawang_spear': ('src/main/java/com/dynasty/DynastyWeapons.java', 384, '龙枪→霸王枪的长柄配方终点；无后继，同类雷霆枪并非其升级。'),
    'houyi_bow': ('tools/art/gen_growth_book.py', 15, '射术三次锻造进化终点，注册源明确毕业弓。'),
    'leiting_hammer': ('tools/art/weapon_evolution_paths.py', 10, '破军→巨灵→雷霆的重兵器分支终点。'),
    'xuanwu_blade': ('tools/art/gen_growth_book.py', 13, '镇岳→巨阙→青龙→玄武的守御进化终点。'),
    'hunyuan_staff': ('tools/art/gen_growth_book.py', 16, '符术主线和朱雀扇分支共同终点。'),
    'zhuque_bow': ('tools/art/weapon_evolution_paths.py', 20, '神臂→落雁→天狼→朱雀的弓分支终点。'),
    'pickaxe_dragon_crystal': ('src/main/java/com/dynasty/DynastyGear.java', 57, '实际只注册玉镐和龙晶镐，原配方由前者升级到后者，工具终点。'),
}
for _set, _line, _note in (('xuantian', 85, '原玄天终盘甲路径终点'), ('hongmeng', 132, '原两条终盘甲线合流终点')):
    for _slot in ('helmet', 'chestplate', 'leggings', 'boots'):
        TERMINAL[_set + '_' + _slot] = ('src/main/java/com/dynasty/DynastyGear.java', _line, _note + '；逐件确认没有后继，不要求再造配方。')

EARLIER = {
    'zhanma_dao': '官银阶普通刀，原环首刀+精钢配方与任务节点确立过渡用途；无后续材料配方，也未找到专属优势的运行断言。',
    'yuchang_dagger': '青铜阶刺客掉落剑；快攻速是静态属性，尚无相对后期武器的场景实测，不能据此直接通过。',
    'qinggang_sword': '玉阶宦官首脑掉落剑；revengeBonus有对应阵营15%分支，但现有该组测试没有执行青釭分支。',
    'yitian_sword': '玉阶叛将掉落剑；revengeBonus有对应阵营15%分支，但现有该组测试没有执行倚天分支。',
    'gilded_mace': '官阶12授武，官阶17另授尚方；普通玉阶武器，未找到后续材料或专属场景的运行证据。',
}


def historical_scenarios(rows, tracked):
    meta = ROOT / 'docs/maintenance/validation/night-20261009-batch35.json'
    log = meta.parent / 'night-20261009-batch35-full-native-special-weapon-cues.log.gz'
    tracked.update((meta, log))
    manifest = json.loads(meta.read_text())
    text = gzip.decompress(log.read_bytes()).decode()
    assert sha(log) == manifest['logs']['gametest-batch35-full-native-special-weapon-cues.log']['sha256']
    assert 'All 632 required tests passed' in text and 'BUILD SUCCESSFUL' in text
    scenarios = {
        'siege_crossbow': ('cod4_native_siege_cue', 'expansion/WeaponCueNativeGameTests.java', 'actualSiegeNativeChargeFireKeepsOnePiercingProjectileAndFiniteOwnerRecoil', '原生装填/发射实际一发、穿透2和扣弹/耐久。'),
        'rope_dart': ('cod4_native_tether_cue', 'expansion/WeaponCueNativeGameTests.java', 'actualNativeRopeAndClawContactKeepOnePullWallCollisionCooldownAndNoMissCue', '真实右键命中牵引与踉跄，支付耐久、冷却和墙体碰撞。'),
        'flying_claw': ('cod4_native_tether_cue', 'expansion/WeaponCueNativeGameTests.java', 'actualNativeRopeAndClawContactKeepOnePullWallCollisionCooldownAndNoMissCue', '真实右键拉敌及方块牵引，墙体碰撞、耐久和冷却。'),
        'meteor_hammer': ('cod4_native_hammer_cue', 'expansion/WeaponCueNativeGameTests.java', 'actualNativeHammerChargeAndReleasePreserveOriginalAreaDamageAndSingleDurabilityPayment', '真实蓄力释放后AOE扣血，短蓄不扣料，完整蓄力仅一次耐久支付。'),
        'baihu_glaive': ('cod4_symbol_mechanics', 'SchoolLinkageGameTests.java', 'matchingSymbolsAddActualBlockBurnBreakAndFiniteDragonWave', '白虎装备联动施加真实破甲状态；该部分直接调用服务端命中处理器。'),
        'thunder_spear': ('cod4_real_combo', 'SchoolLinkageGameTests.java', 'fiveRealPlayerAttacksReturnQiAfterVanillaResetsAttackCooldown', '五次实际Player.attack命中，伤害、攻击冷却与第五次回气检查。'),
    }
    for item, (batch, name, method, observation) in scenarios.items():
        lines = [{'line': i + 1, 'text': line} for i, line in enumerate(text.splitlines()) if f"'{batch}:1'" in line]
        assert lines, batch
        path = ROOT / 'src/main/java/com/dynasty' / name
        tracked.add(path)
        raw = path.read_text()
        assert method in raw
        rows['dynasty:' + item]['runtime_scenario_evidence'].append({
            'status': 'HISTORICAL_ACTUAL_RUNTIME_NOT_CURRENT_SOURCE_BOUND', 'log': rel(log),
            'log_sha256': sha(log), 'manifest': rel(meta), 'batch_lines': lines,
            'current_test_source': source(path, raw.count('\n', 0, raw.index('void ' + method)) + 1),
            'method': method, 'observed': observation,
            'limitation': '历史632通过日志可定位此批实际运行；其清单没有这次运行的逐源哈希，不能把当前测试源码哈希冒充历史输入哈希。本报告不据此计入当前版本通过数。'})


def main():
    tracked = {Path(__file__), ROOT / 'docs/cod4/audit-20261022/cod4-before.txt',
        ROOT / 'docs/cod4/audit-20261022/quest-reference-1000.json'}
    before_protected = {p: sha(p) for p in (ROOT / 'docs/cod4/content-task-map.tsv',
        ROOT / 'docs/cod4/audit-20261022/cod4-remaining.txt')}
    rows = equipment_inventory()
    for row in rows.values():
        if 'path' in row['registration']:
            tracked.add(ROOT / row['registration']['path'])
    level = HERE / '.work/server-20261023-contract/world/level.dat'
    saved = OUT / 'native-level.dat'
    OUT.mkdir(parents=True, exist_ok=True)
    if not saved.exists():
        saved.write_bytes(level.read_bytes())
    registry = {entry['K']: entry['V'] for entry in read_nbt(saved)['fml']['Registries']['minecraft:item']['ids']}
    assert all(item in registry for item in rows)
    for item, row in rows.items():
        row['native_registry_id'] = registry[item]
    dump(OUT / 'native-item-registry.json', {'source': rel(saved), 'sha256': sha(saved),
        'nbt_path': 'fml/Registries/minecraft:item/ids', 'dynasty_items': {k: v for k, v in registry.items() if k.startswith('dynasty:')},
        'external_equipment_predecessors': {'minecraft:crossbow': registry['minecraft:crossbow']}})
    tracked.add(saved)
    recipes_path, native_path = EVIDENCE / 'recipe-index.json', EVIDENCE / 'native-results.json'
    tracked.update((recipes_path, native_path, EVIDENCE / 'native.log', EVIDENCE / 'source-hashes.json'))
    recipes, native = json.loads(recipes_path.read_text()), json.loads(native_path.read_text())
    current_recipe_paths = {rel(p) for p in (ROOT / 'src/main/resources/data/dynasty/recipes').rglob('*.json')}
    assert current_recipe_paths == {r['path'] for r in recipes.values()}, 'Recipe set changed; native595 cannot silently cover new/deleted recipes'
    assert all(sha(ROOT / recipe['path']) == recipe['sha256'] for recipe in recipes.values()), 'Recipe drift requires new native evidence'
    native_checks = {(row['id'], row['check']): (index, row) for index, row in enumerate(native)}
    native_sources = json.loads((EVIDENCE / 'source-hashes.json').read_text())
    registration_closure(native_sources, tracked)
    assert len(recipes) == 595 and len(native) == 621 and all(r['pass'] for r in native)
    for row in rows.values():
        registration = row['registration'].get('path')
        if registration:
            assert row['registration']['sha256'] == native_sources[registration]
        row['material_uses'], row['runtime_scenario_evidence'] = [], []
        row['produced_by'] = [rid for rid, recipe in recipes.items() if recipe['result'] == row['item']]
        for rid, recipe in recipes.items():
            if row['item'] not in recipe['inputs']:
                continue
            path = ROOT / recipe['path']
            tracked.add(path)
            assert sha(path) == recipe['sha256']
            index, check = native_checks[rid, recipe['native_check']]
            definition = json.loads(path.read_text())
            if definition['type'] == 'minecraft:smithing_transform':
                ingredients = [definition[k] for k in ('template', 'base', 'addition')]
            elif definition['type'] == 'minecraft:crafting_shaped':
                ingredients = [definition['key'][c] for line in definition['pattern'] for c in line if c != ' ']
            else:
                ingredients = definition['ingredients']
            # Original tests executed the first Ingredient alternative. Only exact singleton item predicates qualify.
            actual_count = sum(value == {'item': row['item']} for value in ingredients)
            assert actual_count == recipe['inputs'][row['item']] and check['pass']
            row['material_uses'].append({'recipe': rid, 'result': recipe['result'], 'input_count': actual_count,
                'recipe_path': recipe['path'], 'recipe_sha256': recipe['sha256'], 'matches_current': True,
                'ingredient_proof': 'Exact singleton item predicate, no untested tag/alternative substitution',
                'native_record': {'file': rel(native_path), 'json_pointer': '/' + str(index),
                    'id': check['id'], 'check': check['check'], 'pass': check['pass']}})
        short = row['item'].split(':')[1]
        if row['material_uses']:
            row['classification'], row['utility_status'] = 'CONFIRMED_RECIPE_PREDECESSOR', 'VERIFIED_MATERIAL_PAYMENT'
        elif short in TERMINAL:
            path, line, reason = TERMINAL[short]
            tracked.add(ROOT / path)
            row.update(classification='TERMINAL_ENDPOINT_EXCLUDED', utility_status='NOT_REQUIRED_AS_REPLACED_GEAR',
                exception={'reason': reason, 'source': source(ROOT / path, line),
                           'basis': 'Reviewed actual incoming/outgoing recipes plus original branch endpoint; not every graph leaf is treated as terminal.'})
        else:
            row.update(classification='EARLIER_TIER_REVIEW_REQUIRED' if short in EARLIER else 'SPECIALIZED_REPLACEMENT_OR_RUNTIME_REVIEW_REQUIRED',
                utility_status='NOT_CERTIFIED', gap=EARLIER.get(short, '无后续材料配方；独立场景/系列分支不能仅凭说明判通过，也不能仅凭低于另一武器的数值判已被淘汰。替代关系及当前运行证据独立留待核实。'))
            if short in EARLIER:
                path = ROOT / 'src/main/java/com/dynasty/DynastyWeapons.java'
                raw = path.read_text()
                match = re.search(r'sword\("' + short + r'", DynastyTiers\.(\w+), (\d+), (-?[\d.]+)F\)', raw)
                assert match
                row['replacement_context'] = {'registered_tier': match[1], 'damage_parameter': int(match[2]),
                    'speed_modifier': float(match[3]), 'source': source(path, raw.count('\n', 0, match.start()) + 1),
                    'interpretation': '较早注册材质/授武顺序使其必须接受过渡装备审查；这不是生存实机替换记录。不得用无后继配方把它自动排除为毕业装备。'}
    quest_acquisition(rows, tracked)
    historical_scenarios(rows, tracked)
    reference = json.loads((ROOT / 'docs/cod4/audit-20261022/quest-reference-1000.json').read_text())
    reference_files = {site['file']: site['file_sha256'] for site in reference['sites']}
    assert len(reference['sites']) == len({site['semantic_sha256'] for site in reference['sites']}) == 1000
    assert all(Path(path).exists() and sha(Path(path)) == digest for path, digest in reference_files.items())
    counts = collections.Counter(row['classification'] for row in rows.values())
    assert counts == {'CONFIRMED_RECIPE_PREDECESSOR': 149, 'TERMINAL_ENDPOINT_EXCLUDED': 15,
                      'EARLIER_TIER_REVIEW_REQUIRED': 5, 'SPECIALIZED_REPLACEMENT_OR_RUNTIME_REVIEW_REQUIRED': 12}
    runtime = bind_runtime(rows, tracked)
    tracked.add(HERE / 'utility_runtime.py')
    if runtime:
        counts = collections.Counter(row['classification'] for row in rows.values())
        assert counts == {'CONFIRMED_RECIPE_PREDECESSOR': 149, 'TERMINAL_ENDPOINT_EXCLUDED': 15,
            'EARLIER_TIER_WITH_RUNTIME_UTILITY': 5, 'SPECIALIZED_WITH_RUNTIME_UTILITY': 12}
    # These extra read-only sources explain candidate order/behavior; declarations alone never certify utility.
    for name in ('DynastyTiers.java', 'DynastyBalance.java', 'DynastyWeaponGifts.java', 'DynastyBossDrops.java',
                 'expansion/EquipmentBehaviors.java', 'expansion/EquipmentGuardGameTests.java', 'DynastyContent.java'):
        tracked.add(ROOT / 'src/main/java/com/dynasty' / name)
    for path, before in before_protected.items():
        assert sha(path) == before, 'Shared task map/TODO changed during audit; no writes performed by this tool'
    hashes = {rel(path): sha(path) for path in sorted(tracked)}
    dump(OUT / 'input-sha256.json', hashes)
    report = {'schema_version': 2, 'updated_at': datetime.datetime.now().astimezone().isoformat(),
        'status': 'FULL_INVENTORY_PARTIAL_UTILITY_EVIDENCE_DO_NOT_REMOVE_TODO',
        'requirement': 'COD4-14 对被替代的旧装备逐项确认仍有升级/锻造材料、系列联动或特定场景优势',
        'production_changes': [], 'new_native_run': False, 'nbt_contract_added': False,
        'coverage': {'scope': 'All Dynasty SwordItem/BowItem/CrossbowItem/PickaxeItem/ArmorItem subclasses and literal/table registrations; plus vanilla crossbow, the only external equipment predecessor consumed by the 595 recipes.',
            'dynasty_equipment_inventory': 180, 'vanilla_direct_equipment_predecessors': 1,
            'inventory_denominator': len(rows), 'categories': dict(collections.Counter(row['category'] for row in rows.values())),
            'confirmed_recipe_predecessors': counts['CONFIRMED_RECIPE_PREDECESSOR'],
            'verified_material_payment': 149, 'unique_consuming_recipes': len({u['recipe'] for row in rows.values() for u in row['material_uses']}),
            'terminal_exclusions': 15, 'conservative_review_denominator': 166,
            'unresolved_earlier_tier_candidates': 5, 'unresolved_specialized_candidates': 12,
            'classification_counts': dict(counts),
            'definition': '完整清点181件；其中实际配方前驱149件是确认可被后继消耗的旧装备集合。剔除15件有原链终点依据的例外后，保守审查分母166。其余17件是待判定/待运行证明的候选，不声称全都已实际被替代，更不声称完全无用；不能把它们隐入终盘例外来得出100%。',
            'boundary': '食品/消耗性符箓/弹药/材料/Curios饰品/方块/手册与非装备功能道具不计武器工具盔甲分母。普通工具指注册Pickaxe/Digger/Tiered装备；毛笔、罗盘、虎符及六件可用宝物另有功能，不是镐进化线的被替代装备。'},
        'registry_evidence': rel(OUT / 'native-item-registry.json'),
        'registry_classification_closure': rel(OUT / 'registration-closure.json'),
        'quest_order_evidence': rel(OUT / 'quest-acquisition-graph.json'),
        'native_reuse': {'record': rel(native_path), 'sha256': sha(native_path), 'log': rel(EVIDENCE / 'native.log'),
            'log_sha256': sha(EVIDENCE / 'native.log'), 'recipe_count': 595, 'record_count': 621,
            'registration_sources_match_native_snapshot': True, 'all_595_recipes_match_native_snapshot': True,
            'interpretation': '原生ResultSlot/SmithingMenu已真实扣除输入并产出后继；每件链接确切配方和原记录JSON pointer。此次只读关联，不声称新跑测试或自然取得原料。'},
        'research': {'record': 'docs/cod4/audit-20261022/quest-reference-1000.json', 'reused_semantic_records': 1000,
            'source_files_hash_verified': len(reference_files), 'applicability': '同一既有任务来源/前驱/材料用途核查；不是1000次实机，不支持新增NBT契约。'},
        'actual_recipe_predecessor_set': sorted(item for item, row in rows.items() if row['material_uses']),
        'no_material_uses': sorted(item for item, row in rows.items() if not row['material_uses']),
        'earlier_tier_no_material_review': sorted('dynasty:' + item for item in EARLIER),
        'terminal_exceptions': sorted('dynasty:' + item for item in TERMINAL),
        'unresolved_specialized_candidates': sorted(item for item, row in rows.items() if row['classification'] == 'SPECIALIZED_REPLACEMENT_OR_RUNTIME_REVIEW_REQUIRED'),
        'confirmed_no_use_items': [], 'confirmed_no_use_note': '没有材料去向不等于没有任何用途；本审计不以缺证据冒充已经证实完全无用。',
        'can_remove_this_todo': False,
        'closure_gap': '5件较早材质/授武候选缺逐项后续材料或当前运行证明；12件独立场景候选还需界定是否被替代及补齐当前版本运行证据。历史场景日志已关联，但未将无输入哈希绑定的旧运行当作当前已过。',
        'limitations': ['任务获取目标、前置和配方不能证明真实获取时间或被玩家实际替换；没有以图标/描述文本冒充任务检测。',
            '此次不增加配方、不修改生产Java或原主表/TODO；普通合成NBT继承不属于验收契约。',
            '六阶段完整生存、自然寻物和真人实机仍未验收；确认材料用途不替代这些验收。'],
        'input_hashes': rel(OUT / 'input-sha256.json'), 'protected_read_only_sha256': {rel(p): h for p, h in before_protected.items()},
        'items': [rows[item] for item in sorted(rows)]}
    if runtime:
        report.update(schema_version=3, status='FULL_DENOMINATOR_UTILITY_VERIFIED_WITH_NATIVE_SCOPE',
            new_native_run=True, current_runtime=runtime, can_remove_this_todo=True, closure_gap=None,
            closure_scope='仅支持主协调移除COD4-14“对被替代的旧装备逐项确认仍有升级/锻造材料、系列联动或特定场景优势”这一条；本工具没有删除待办。',
            phase_report='tools/cod4/journey-acceptance/evidence/old-equipment-utility/phase-17-pending/report.json',
            earlier_tier_runtime_verified=sorted('dynasty:' + item for item in EARLIER),
            verified_runtime_utility_items=runtime['covered_items'],
            confirmed_no_use_note='32件无后续材料配方之中，17件已有当前原生运行证明的系列/场景用途，其余15件是原链终点例外；未证实无真实用途的产品缺口。')
        report['coverage'].update(verified_runtime_utility=17, verified_review_items=166,
            unresolved_earlier_tier_candidates=0, unresolved_specialized_candidates=0,
            definition='清点181件=149件有实扣后继配方+17件有现有系列/场景原生用途+15件有原链终点依据的例外。保守审查分母166/166有用途证据，未扩大terminal集合。149是确认配方前驱集合；17件仍保留较早装备/独立分支来源语义，不声称它们全都在生存中被替换，也无需依赖这种推断才能证明它们有用途。')
        report['native_reuse']['interpretation'] = '原595配方/621细分记录仅只读复用；每件材料用途均指向原生结果槽实扣记录。本次新增的18项场景测试单列于current_runtime，不合并冒称613配方或1000实机。'
        report['limitations'].extend([
            '流派实测未加载Curios，实际使用原物品栏兼容分支；Curios槽位集成、完整客户端与双人仍需各自验收。普通旧武器的既有系列联动不等于其数值优于毕业装备。',
            '测试使用原注册装备、配饰、敌人和条件夹具，守御韧性10、首杀标记等前提明确列出；无自然取得装备/配饰/首杀或任务时长主张。',
            '独立QA Java只调用现有原生路径并记录结果；早期失败及夹具修正详见runtime-attempts.json，没有据失败改变正式玩法。'])
    dump(HERE / 'old-equipment-utility.json', report)
    dump(ROOT / 'docs/cod4/audit-20261022/old-equipment-utility.json', report)
    print(json.dumps({'report': rel(HERE / 'old-equipment-utility.json'), 'coverage': report['coverage'],
                      'can_remove_this_todo': report['can_remove_this_todo']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
