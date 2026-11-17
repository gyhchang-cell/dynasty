#!/usr/bin/env python3
"""Record an owner semantic re-review of existing proposals, without production writes."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def evidence(p):
    return dict(path=str(p), sha256=sha(p))

def load(p):
    return json.loads(p.read_text())

def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

SCOPES = {
    'DUN03-MEDIUM-GROUND-GARRISON': dict(
        title='DUN03地面中型驻防堡／营院完整布局',
        definition='地面单组驻防建筑，约29–36格平面、17–30格保存高度，含守备主体及其围合地脚／院带，学习防护边界、驻所与高低守望空间的组织。作者完整遗址按现存遗址一次计；不是残墙组件。',
        exclusions=['大型中心瓮城或整片古战场', '双高塔大型前哨', '16格低四棚小院', '孤立民居、房间、未拼装外围地块'],
        ids=['010-F01', '010-F02', '010-F03', '010-F05']),
    'DUN03-SINGLE-WATCHPOST': dict(
        title='DUN03小占地独立守望塔完整布局',
        definition='一座独立竖向守望建筑及自带地脚／低围栏，约15–27格平面，主要驻守空间沿单塔竖轴叠置，保存高度25–53格。以室层、平台及竖向收放比较；旗杆和屋帽高度不折算楼层。不同层数仍服务同类小占地守望岗位。',
        exclusions=['长厅连接端塔', '双高塔堡', '角塔与L厅组合', '大营院、城墙组件、实体接口及地形底座'],
        ids=['011-F01', '011-F02', '012-F01', '012-F02', '013-F01', '015-F01']),
    'DUN03-HALL-WITH-LOOKOUT': dict(
        title='DUN03长厅连接偏置守望楼完整布局',
        definition='约24–29格长轴、15–17格短轴的地面守备厅与偏置高守望段，共用连续厅房且有横向门廊；观察水平驻所和垂直瞭望空间的联结。不能借独立单塔或普通教堂增加例数。',
        exclusions=['独立单塔', '普通民居或教堂', '仅替换端塔屋顶、材质或等比缩放的变体', '大型营院'],
        ids=['011-F03']),
}

# These are substantive layout comparisons, not deductions from Jaccard scores.
DECISIONS = {
    '010-F01': ('ACCEPT', '作者现存石堡遗址有围院、角部高低残墙、地面开口和内部树；接口仅实体，不缺待接建筑。本次不复原坍塌前形态。',
                '相较009-F03连续退台方壳、007-F08封闭分室小院，主体是断墙围成的开放院及高角残段；相较010-F02的竖向层叠台，空间主序是水平围合，不是换材／旋转。'),
    '010-F02': ('ACCEPT', '粗角柱、下部围室和层叠守备平台及宽屋盖均在同一模板内，俘虏接口是单实体，不是缺失牢房。',
                '与002-F09集中覆顶殿阁相比，有下层笼室及开放守备层台；与003-F09低四棚露院相比，中部连续叠层且高台集中，不是四角低棚加高屋顶。'),
    '010-F03': ('ACCEPT', '高木围栅、中央低长营厅和两者间院带共同构成完整驻防组。',
                '005-F01为L形乡间小屋配花园地脚，无近圆高围栅营院；010-F05是低栅院中高窄长厅加偏低翼，此处外围高栅／中央低厅及环院关系不同。'),
    '010-F05': ('ACCEPT', '低栅不规则院、高长厅和侧低翼已整体保存，外接仅实体。',
                '003-F05为单角方高塔连接L形较低厅；此处主高体沿厅纵轴拉长，侧低翼与低院周界相连，未形成单角竖塔。与010-F03亦有高低主次和围合拓扑差异。'),
    '011-F01': ('ACCEPT', '细颈塔身承较宽多向上室，完整四向外挑与地脚同属一塔。',
                '比013-F01偏心多小室石塔，此处上室明显展宽而下颈收窄；比015-F01连续方墙筒，承托／围室关系不同。015-F02细身宽顶近似族继续HOLD，不额外记第二例。'),
    '011-F02': ('ACCEPT', '低多边栏场、中央收分平台塔和上段小室本体完整；缺猫池定义不等于缺建筑翼，但生成依赖仍未验。',
                '012-F04风车状建筑有四斜叶和主体房，岗位与机构用途未明，不借它计数；010-F02为粗角柱近等宽台堡，此处中央多级收分单轴高塔，差异在承托、室层足印和周边地脚。'),
    '011-F03': ('ACCEPT', '连续横向长厅、侧门廊和偏置高低竖段完整；全组算一例。',
                'W007为集中叠坡大室、中央小上室；W008是单端塔顺接单厅。此处长厅受两处不等高竖段穿入，侧门廊形成横向分支，厅与竖段的相交组织不同，不以双尖帽造型本身计数。'),
    '011-F04': ('HOLD_FAMILY', '整体建筑本体完整，但完整性不能代替设计族独立性。',
                '013-F02、014-F01/F02及015-F03均有中心柱附近升降、紧凑叠室与上部帽顶。已见层板和足印差别，尚未证明超出尺度、屋顶和材料变体；不认作重复定论，也不正式加数。'),
    '012-F01': ('ACCEPT', '作者完整废塔原貌包含错位残台、外伸长阶及侧小帽，接口仅实体；不补想缺失屋盖。',
                '与002-F02厚实体方堡连侧门堡不同，此处两个错位高低残台与外伸低阶主导路线和轮廓；与010-F01横向院式遗址不同，此处为狭长竖向守望岗位。'),
    '012-F02': ('ACCEPT', '偏移小室、收腰塔体和小阳台自成一个完整高窄守望建筑。',
                '013-F02为紧凑近同轴叠室塔，此处多个房层足印逐层偏移、腰部明显缩窄并设外挑小台。011-F02为同轴逐级收分平台，此处收放非单调；不是以蘑菇柄换白石材料就加例。'),
    '012-F03': ('HOLD_FAMILY', '端高塔、扶壁长厅和低门廊完整；可以学习，暂不计独立设计信用。',
                '与W008同为单端高塔顺接双坡长厅，两侧分节外扶撑。尺寸、平顶／坡帽和材料变化已确认，但不足以排除同类原型变体；与011-F03的差异不能自动证明相对W008的新设计。'),
    '013-F01': ('ACCEPT', '多小室石塔、上部露台、偏高有帽房和低棚为同一完整建筑，俘虏接口不是额外房。',
                '004-F03为低双层破屋带外阶；本例分室向上延续、上部露台与偏高小楼相邻。011-F01细颈宽顶、015-F01连续单筒不具这种多室围合和偏心双高程上缘。'),
    '015-F01': ('ACCEPT', '连续方墙筒、内叠层板和露天木顶台自成完整塔体；外接terrain_small只是未拼装地形，不计第二建筑。',
                '011-F04与014-F02均为中心柱附近叠室并覆大帽顶；此处墙筒持续围室、换侧梯连接内层板，顶层是完整敞天大台。与011-F01细颈托宽顶房不同；差异包含围护、层板和顶台关系，不单是泥材或无坡帽。'),
}

COMPARATORS = [
    'continuation-20261022/references/whole-candidates/W008.png',
    'research-20261101-dungeons-003/F01-whole.png',
    'research-20261101-dungeons-003/F05-whole.png',
    'research-20261101-dungeons-003/F09-whole.png',
    'research-20261101-dungeons-015/F03-whole.png',
    'research-20261101-dungeons-013/F02-whole.png',
    'research-20261101-dungeons-014/F01-whole.png',
    'research-20261101-dungeons-002/F02-whole.png',
    'research-20261101-dungeons-002/F09-whole.png',
    'research-20261101-dungeons-005/F01-whole.png',
    'research-20261101-dungeons-004/F03-whole.png',
    'research-20261101-dungeons-009/F03-whole.png',
    'research-20261101-dungeons-014/F02-whole.png',
    'research-20261101-dungeons-012/F04-whole.png',
    'continuation-20261022/references/whole-candidates/W007.png',
    'research-20261101-dungeons-007/F08-whole.png',
]

UNCHANGED = {
    'continuation-20261022/references/full-buildings.json': '9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408',
    'research-20261101-scoped-outpost-ledger/outpost-scope-register.json': '2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267',
    'research-20261101-scoped-urban-lodging-ledger/urban-lodging-scope-register.json': '38a1bcaf7c032e024a18dcf5f66c00467b34771e1974299e4dad4da98b64a330',
}

def main():
    src = load(OUT / 'sources.json')
    dedup = load(OUT / 'dedup-evidence.json')
    assert dedup['prior_self_identities'] == 13
    assert not dedup['within_batch_exact_duplicate_pairs']
    assert all(not e['other_historical_exact_matches'] for e in dedup['entries'])
    for e in src['inputs']:
        assert sha(Path(e['path'])) == e['sha256']
    for p, expected in UNCHANGED.items():
        assert sha(BASE / p) == expected
    entries = []
    for c in src['candidates']:
        folder = BASE / f"research-20261101-dungeons-{c['original_batch']:03d}"
        original = next(e for e in load(folder / 'manual-review.json')['entries'] if e['id'] == c['original_id'])
        decision, complete, independent = DECISIONS[c['id']]
        scope = next((s for s, v in SCOPES.items() if c['id'] in v['ids']), None)
        assert (decision == 'ACCEPT') == (scope is not None)
        entries.append(dict(id=c['id'], decision=decision, scope_id=scope, credit=int(scope is not None),
                            completeness=complete, semantic_independence=independent,
                            source=c, observations=original['observations'],
                            seven_aspect_record=evidence(folder / 'manual-review.json'),
                            original_state_record=evidence(folder / 'vertical-original-states.json'),
                            interface_record=evidence(folder / 'interface-audit.json'),
                            actual_images_reviewed_again=c['actual_images_from_original_study'],
                            acceptance_kind='WHOLE_BUILDING_LAYOUT_RESEARCH_ONLY', native_acceptance=False))
    accepted = [e for e in entries if e['credit']]
    held = [e for e in entries if not e['credit']]
    assert len(entries) == 13 and len(accepted) == 11 and len(held) == 2
    dump('semantic-review.json', dict(
        reviewer='建筑专岗同一执行者的逐例语义复核；不是新增独立人类／协调者审核。',
        task_anchor=evidence(BASE / 'research-20261101-task-map/architecture-task-map.json'),
        task_application='DUN03万骨枯寂·血海古战场的驻防附属营院、守望岗位布局学习；不等同于15m夯土瓮城、全战场、国风建筑或地牢资产完成。',
        entries=entries, historical_comparison_images_reviewed_again=[evidence(BASE / p) for p in COMPARATORS],
        source_images_reviewed_again=52, historical_comparison_images_reviewed_again_count=16,
        new_source_templates=0, new_images=0,
        geometric_screening='188个历史archive/member身份含13个本次原身份；每例排除自身后比较187个。175是排除全部13身份的其余索引量，均不是建筑信用数。',
        limitations=['本次实际重看52幅候选图及16幅历史比较图，未声称重看全部188身份。',
                     '原图为原始NBT全方格近似和分类色，不认证原生碰撞、贴图、光照、世界地形或全路径。',
                     '未借哈希无重复推导所有语义原型皆独立；两项仍保留设计族疑问。',
                     '缺猫池及terrain_small拼装／终止证据不被本体布局参考验收覆盖。']))
    scopes = []
    for key, spec in SCOPES.items():
        rows = [e for e in accepted if e['scope_id'] == key]
        scopes.append(dict(scope_id=key, title=spec['title'], scope_definition=spec['definition'],
                           exclusions=spec['exclusions'], target=1000, accepted_references=len(rows),
                           remaining=1000-len(rows), construction_allowed=False, accepted_ids=[e['id'] for e in rows]))
    dump('scoped-reference-register.json', dict(
        status='ELEVEN_EXISTING_PROPOSALS_ACCEPTED_FOR_BOUNDED_LAYOUT_RESEARCH',
        scopes=scopes, accepted=accepted, held=held, formal_reference_acceptance_events=11,
        new_source_discoveries=0, new_production_tasks_completed=0, checklist_deletions=0,
        count_unit='每个完整相关设计一次；不按NBT片段、接口、房、附翼、平台、屋顶、截图或旋转增加例数。',
        no_combined_threshold='4、6、1分属不同岗位／规模范围，不汇总成任何建筑任务的11/1000，也不转借旧148或既有其他范围信用。',
        preserved_registries=[dict(path=str(BASE/p),sha256=h) for p,h in UNCHANGED.items()],
        semantic_review=evidence(OUT / 'semantic-review.json'), dedup_evidence=evidence(OUT / 'dedup-evidence.json'),
        remaining_original_batch_holds=12, original_batch_templates=23,
        boundary='010–015原13待验现11限定参考接纳、2设计族保留；加上原10HOLD，23模板中尚12项不计信用。所有生产与任务／指南针同步仍未完成。'))
    print('Recorded 13 owner decisions: 11 scoped layout references, 2 family holds; no production threshold reached.')

if __name__ == '__main__':
    main()
