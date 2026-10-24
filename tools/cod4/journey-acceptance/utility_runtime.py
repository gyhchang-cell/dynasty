"""Bind current, complete native utility receipts to the full equipment denominator."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NATIVE = HERE / 'evidence/old-equipment-utility/native-20261023-utility'
SCHOOL = ('zhanma_dao', 'yuchang_dagger', 'qinggang_sword', 'yitian_sword', 'gilded_mace', 'sea_trident')
IMPERIAL = ('qilin_war_axe', 'baihu_glaive', 'thunder_spear', 'ziwei_saber')
CASES = {**{'school_' + item: [item] for item in SCHOOL},
         **{'faction_' + item: [item] for item in ('qinggang_sword', 'yitian_sword')},
         **{'imperial_' + item: [item] for item in IMPERIAL},
         'siege': ['siege_crossbow'], 'tether': ['rope_dart', 'flying_claw'],
         'hammer': ['meteor_hammer'], 'paired_axes': ['mandarin_duck_axe'],
         'longyin': ['longyin_zhanma_duanyue_dao'], 'zhanlu': ['zhanlu_rendao_bamian_jian']}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return str(path.relative_to(ROOT))


def describe(case):
    if case.startswith('school_'):
        return ('EXISTING_SCHOOL_LINK_AND_KILL_GROWTH',
            '原守御两件（贞观镜、虎贲护腕）与剑术两件（连城穗、踏云佩）分别使实际 Player.attack 扣血增加，卸下恢复基线；十次实际击杀敌对僵尸后该旧武器等级2、守御熟练等级1。',
            '守御夹具基础护甲韧性10；Curios未加载，走原物品栏兼容路径，未注入activeIds/成长XP/NBT。验证已有系列联动，不声称该旧武器伤害超过毕业装备。',
            [('DynastySchoolProgression.java', 'Other swords are viable'), ('DynastyWeaponProgression.java', 'class DynastyWeaponProgression')])
    if case.startswith('faction_'):
        source, target = ('eunuch_mastermind', 'royal_guard') if 'qinggang' in case else ('rebel_general', 'rebel_soldier')
        return ('EXISTING_FACTION_ADVANTAGE', '原首杀条件下，对应阵营实际伤害提高15%；对无关僵尸没有这项增益。',
            '测试设置原首杀标记dynasty_firstkill_' + source + '，实际伤害目标dynasty:' + target + '；此条件夹具不证明首杀/掉落自然获取。',
            [('expansion/EquipmentBehaviors.java', 'revengeBonus')])
    if case.startswith('imperial_'):
        return ('EXISTING_IMPERIAL_PAIR_LINK', '副手持另一件帝兵太乙剑时，当前旧武器实际攻击扣血增加；副手同ID复制品不加成。',
            '主副手两件不同ID的原帝兵组合；输入来自原注册物品，不新增配方或装配门槛。',
            [('expansion/EquipmentBehaviors.java', 'twinBonus')])
    return {
        'siege': ('EXISTING_PIERCING_SCENARIO', '原生右键装填消耗一发重弩矢，发射穿透等级2的真实弹体并实际伤害两个共线敌人，只扣一次耐久；撞墙后的穿透清零遵循原版。',
            '敌人位于4格和8格，射线末端实体石墙；自然弹道，不调用onHit或手动扣血。', [('expansion/ExpansionWeapons.java', 'class BurstCrossbow')]),
        'tether': ('EXISTING_CONTROL_OR_TRAVERSAL_SCENARIO', '绳镖/飞爪实际右键牵引敌人并施加踉跄；飞爪命中方块使玩家产生受碰撞限制的移动速度；冷却重复输入和空命中不会重复支付。',
            '12格内可见非Boss目标，或飞爪实方块锚点；只证明原生速度/碰撞标志，没有把它当完整跨地形探索。', [('expansion/WeaponCueNativeGameTests.java', 'void actualNativeRopeAndClawContact')]),
        'hammer': ('EXISTING_AREA_DAMAGE_SCENARIO', '流星锤真实蓄力/释放造成原范围伤害并一次扣3耐久；短蓄力不扣血、不扣耐久。',
            '完整24tick与不足10tick对照；原0.6攻击伤害+110附加伤害和80tick冷却，沿用原方法断言。', [('expansion/WeaponCueNativeGameTests.java', 'void actualNativeHammerCharge')]),
        'paired_axes': ('EXISTING_FRONT_GUARD_SCENARIO', '双鸳鸯斧实际举持抵挡正面攻击，正面伤害为背面35%，清除踉跄，下一次实际攻击消耗一次反击。',
            '主副手同为鸳鸯斧，在已有完美格挡帧内，无套装门槛；包含背面伤害对照。', [('expansion/PerfectBlockNativeGameTests.java', 'void actualFrontBlockedDamage')]),
        'longyin': ('EXISTING_SURROUNDED_PARRY_SCENARIO', '原生挥击后正面来袭被弹反；三个可见敌人包围时正面物理伤害减25%且拒绝踉跄，背面攻击不减免。',
            '普通难度、三个原注册敌人、正面/背面对照；原方法断言实际7.5/10扣血及一次弹反，非函数返回值替代伤害。', [('blueprint/artifact/ArtifactGameTests.java', 'void nativeFrontClashThenSurround')]),
        'zhanlu': ('EXISTING_DISARM_HEAL_SCENARIO', '实际右键保持地面姿态，20tick准备后真实收走敌人双手装备、减速70%且阻止其攻击；80tick场域结束恢复装备和移速，回复30%最大生命。',
            '原半径5格、站定、持同一把剑、期间没有击杀；19tick未成场为负对照。单一有序移动/tick夹具保持原落地条件。', [('blueprint/artifact/ZhanluAbility.java', 'void tickUse'), ('blueprint/artifact/ZhanluField.java', 'class ZhanluField')]),
    }[case]


def bind(rows, tracked):
    if not (NATIVE / 'run-receipt.json').exists():
        return None
    receipt = json.loads((NATIVE / 'run-receipt.json').read_text())
    records = json.loads((NATIVE / 'native-results.json').read_text())
    manifest = json.loads((NATIVE / 'source-hashes.json').read_text())
    assert receipt['exit_code'] == 0 and receipt['selected_cases'] == 'ALL'
    assert receipt['qa_unchanged_during_run'] and receipt['init_unchanged_during_run']
    assert sha(NATIVE / 'native.log') == receipt['log_sha256']
    assert sha(NATIVE / 'source-hashes.json') == receipt['source_manifest_sha256']
    assert sha(NATIVE / 'JourneyUtilityGameTests.java') == receipt['qa_sha256']
    assert sha(NATIVE / 'utility.init.gradle') == receipt['init_sha256']
    assert sha(ROOT / 'build.gradle') == receipt['build_gradle_sha256'], 'Runtime dependency configuration changed'
    history_path = NATIVE.parent / 'runtime-attempts.json'
    history = json.loads(history_path.read_text())
    final_attempt = next(a for a in history['attempts'] if a['run'] == receipt['run'])
    assert all(sha(ROOT / path) == digest for path, digest in final_attempt['files'].items())
    tracked.update((history_path, NATIVE.parent / 'phase-17-pending/report.json', ROOT / 'build.gradle'))
    log = (NATIVE / 'native.log').read_text()
    assert 'All 18 required tests passed' in log and 'BUILD SUCCESSFUL' in log
    assert len(records) == len(CASES) == 18 and {r['case'] for r in records} == CASES.keys()
    assert all(r['pass'] for r in records)
    current_paths = {str(p.relative_to(ROOT)) for folder in ('src/main/java', 'src/main/resources/data') for p in (ROOT / folder).rglob('*') if p.is_file()}
    bound_paths = {p for p in manifest if p.startswith(('src/main/java/', 'src/main/resources/data/'))}
    assert current_paths == bound_paths, 'Production implementation/data file set changed; re-evaluate utility coverage'
    assert all(sha(ROOT / p) == manifest[p] for p in bound_paths), 'Production Java/data drift requires review before re-certification'
    tracked.update(NATIVE.iterdir())
    covered = set()
    for index, record in enumerate(records):
        case = record['case']
        assert set(record['items']) == {'dynasty:' + item for item in CASES[case]}
        kind, observed, conditions, implementations = describe(case)
        sources = []
        for name, token in implementations:
            path = ROOT / 'src/main/java/com/dynasty' / name
            raw = path.read_text(); position = raw.index(token)
            sources.append({'path': rel(path), 'sha256': sha(path), 'line': raw.count('\n', 0, position) + 1})
            tracked.add(path)
        evidence = {'status': 'CURRENT_NATIVE_PASS_SOURCE_BOUND', 'kind': kind, 'observed': observed,
            'conditions_and_limits': conditions, 'record': {'file': rel(NATIVE / 'native-results.json'),
                'json_pointer': '/' + str(index), 'case': case, 'native_test': record['native_test'], 'pass': True},
            'measurements': record['measurements'], 'curios_loaded': record['curios_loaded'],
            'implementation_sources': sources, 'qa_source': rel(NATIVE / 'JourneyUtilityGameTests.java'),
            'qa_sha256': receipt['qa_sha256'], 'run_receipt': rel(NATIVE / 'run-receipt.json')}
        for item in record['items']:
            assert item in rows and not rows[item]['material_uses']
            assert rows[item]['classification'] != 'TERMINAL_ENDPOINT_EXCLUDED'
            row = rows[item]; row['runtime_scenario_evidence'].append(evidence)
            row.pop('gap', None)
            row['utility_status'] = 'VERIFIED_EXISTING_RUNTIME_UTILITY'
            if row['classification'] == 'EARLIER_TIER_REVIEW_REQUIRED':
                row['classification'] = 'EARLIER_TIER_WITH_RUNTIME_UTILITY'
            elif row['classification'] == 'SPECIALIZED_REPLACEMENT_OR_RUNTIME_REVIEW_REQUIRED':
                row['classification'] = 'SPECIALIZED_WITH_RUNTIME_UTILITY'
            covered.add(item)
    assert len(covered) == 17
    return {'receipt': rel(NATIVE / 'run-receipt.json'), 'log': rel(NATIVE / 'native.log'),
        'record': rel(NATIVE / 'native-results.json'), 'native_tests': 18, 'passed': 18,
        'unique_equipment_covered': 17, 'covered_items': sorted(covered),
        'all_current_java_and_data_match_run_snapshot': True, 'curios_loaded': False,
        'scope': '有控制条件的真实专用服务端伤害、击杀、输入、扣料与场景效果；不等于完整整合包客户端或六阶段生存。',
        'failure_history': 'tools/cod4/journey-acceptance/evidence/old-equipment-utility/runtime-attempts.json'}
