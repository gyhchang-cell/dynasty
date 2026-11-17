"""Close a bounded exclusion screen. Does not admit references or edit product files."""
import collections
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
assert not (OUT / 'RECEIPT.json').exists()

def put(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def bind(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}

previous = ROOT / 'docs/architecture/research-20261104-smithy-271'
old_path = ROOT / 'docs/architecture/research-20261104-smithy-165/manual-review.json'
old = json.loads(old_path.read_text())['cases'][0]
assert len(old['screening_observations']) == 7
put('saved-165-own-seven-observations.json', {
    'binding': bind(old_path), 'member': old['member'],
    'own_seven_observations_actually_read': old['screening_observations'],
    'original_status': old['status'], 'original_native_acceptance': old['native_acceptance'],
    'nested_saved_comparisons_not_claimed_fully_reread_this_batch': True,
    'old_images_reopened': 0, 'old_reference_new_credit': 0,
})

diff = json.loads((OUT / 'F02-targeted-165-semantic-duplicate-check.json').read_text())
counts = collections.Counter()
exceptions = []
natural = {'minecraft:grass_block', 'minecraft:grass', 'minecraft:tall_grass',
           'minecraft:poppy', 'minecraft:dandelion'}
for row in diff['nonair_nonjigsaw_differences']:
    a, b = row['current'], row['old165']
    names = {v['state']['Name'] for v in (a, b) if v}
    if names <= natural:
        kind = 'ground_grass_or_plant_presence'
    elif row['pos'][1] == 0 and names == {'minecraft:deepslate', 'minecraft:grass_block'}:
        kind = 'ground_base_deepslate_vs_grass'
    elif names == {'minecraft:torch'}:
        kind = 'old_ground_torch_removed'
    elif names in ({'minecraft:redstone_lamp'}, {'minecraft:daylight_detector'}):
        kind = 'saved_redstone_state'
        exceptions.append(row)
    else:
        raise AssertionError(('Unexpected architectural difference', row))
    counts[kind] += 1
assert dict(counts) == {'ground_grass_or_plant_presence': 182,
                       'ground_base_deepslate_vs_grass': 18,
                       'old_ground_torch_removed': 3, 'saved_redstone_state': 2}
assert diff['same_entities'] is True
put('semantic-screen-decision.json', {
    'F02': {
        'decision': 'AUTHOR_DUPLICATE_DESIGN_EXCLUSION_ZERO',
        'comparison': bind(OUT / 'F02-targeted-165-semantic-duplicate-check.json'),
        'raw_files_identical': False,
        'nonair_nonjigsaw_difference_categories': dict(counts),
        'saved_state_differences': exceptions,
        'human_design_judgment': '旧165已读完整七维观察与当前原坐标对照：地层家务制作厅、北柱双次折转阶、中层书写厅与东侧门台、顶层西三完整床、双坡主盖保持同一组织。声明高度40对19、地表裙边、花草、三炬和灯/检测器保存状态不足新建筑。不是所有原状态/稀疏空气完全相同，也不把机器比较称整屋新研究。',
        'sparse_air_limit': '全部存储差异242；显式air与省略的区别保留，未据此保证碰撞/净空一致。',
        'old_source_targeted_reopen': '仅为新候选近族判定重读旧165固定NBT；旧PNG未重开，新增旧参考信用0。',
        'new_whole_reference_study': False, 'proposed_credit': 0, 'formal_credit': 0,
    },
    'F01': {
        'decision': 'BOUNDED_SOURCE_RELEVANCE_UNPROVEN_DEFERRED_ZERO',
        'reason': '大体量蜂巢住宅仅材料/BE有界筛查；尚无符合原任务具体用途的充分证据。不能凭文件大小或蜂巢数量计相关完整建筑。未全读状态、逐层或渲染。',
        'new_whole_reference_study': False, 'proposed_credit': 0, 'formal_credit': 0,
    },
    'F03': {
        'decision': 'BOUNDED_SOURCE_ASSEMBLY_AND_RELEVANCE_UNPROVEN_DEFERRED_ZERO',
        'reason': '起始池直接选住宅，续接池含住宅/桥两项各权1，不能仅因jigsaw认定不完整，也不能未经研究认定完整独立；未读桥NBT或实际装配。五床块不是五张床，普通草原住宅不自动满足NPC12茶馆或DUN05徽派民宅。',
        'context_output_limit': '七JSON保存完整原文，但首次工具输出截断。只有后续完整显示的两池、根结构及biome标签四JSON认作人工完整读取；三loot表不声称本轮完整人工阅读。',
        'new_whole_reference_study': False, 'proposed_credit': 0, 'formal_credit': 0,
    },
    'original_task_filter': {
        'COD3_NPC12': '原文茶馆/驿道随机、日占卜夜收摊雨避；不是任意有床民宅或酒瓶即算茶馆。',
        'DUN05': '原文黑瓦白墙徽派民宅、沿街商铺/客栈及屋顶-石巷立体通行；不得把西式住宅风格当满足原任务。',
        'COD3_NPC13': '原文大雪山木屋、日猎夜烤火雨避；本批无新的对应整屋证据。',
    },
    'complete_new_related_whole_studies': 0, 'formal_credit_added': 0,
    'production_changes': 0, 'tasks_deleted': 0, 'native_acceptance': False,
})

protected = []
for row in json.loads((previous / 'protected-inputs-current.json').read_text())['files']:
    prior = row['current271']; now = bind(prior['path'])
    protected.append({'previous271': prior, 'current272': now, 'unchanged': prior == now,
                      'this_chat_wrote_file': False})
put('protected-inputs-current.json', {'files': protected, 'cod5_missing_not_invented': True,
    'this_chat_product_writes': 0})
session = json.loads((previous / 'session.json').read_text())
session.update({'batch': 272, 'previous271_receipt': bind(previous / 'RECEIPT.json'),
    'formal_credit_added': 0, 'first_carry_added': 0, 'old260_carry_added': 0,
    'next': 'Continue purpose-and-scale related complete building selection; F02 duplicates165, F01/F03 bounded deferred not accepted or complete. 266/269/270 remain pendingMain.',
    'current_batch_new_whole_studies': 0, 'current_batch_proposal': 0,
    'java_run': False, 'game_run': False, 'network_used': False,
    'production': False, 'masterlists_edited': False, 'all_tasks_complete': False,
    'actual_active_work_hours': None})
session.setdefault('research_holds', []).append('272F02_SAME_165_DESIGN_ZERO')
put('session.json', session)
put('active-checkpoint.json', {'batch': 272, 'status': 'BOUNDED_SCREEN_COMPLETE_NO_WHOLE_ADMISSION',
    'COD4_accepted': 153, 'COD4_gap': 847, 'NPC_totals': None,
    'new_whole_studies': 0, 'formal_credit_added': 0, 'task_deletions': 0,
    'native_acceptance': False, 'java_run': False, 'all_tasks_complete': False,
    'session': bind(OUT / 'session.json')})
checks = {
    'three_prefilter_rows': len(json.loads((OUT / 'pre-render-history-screen.json').read_text())['rows']) == 3,
    'F02_nonair_diff205': len(diff['nonair_nonjigsaw_differences']) == 205,
    'F02_all_stored_diff242': diff['all_stored_differences_count'] == 242,
    'difference_categories_exhaustive': sum(counts.values()) == 205,
    'same_source_entities': diff['same_entities'],
    'old_seven_observations_saved': len(old['screening_observations']) == 7,
    'no_new_images': not list(OUT.glob('*.png')),
    'no_tasks_deleted': True,
    'protected8_unchanged': len(protected) == 8 and all(r['unchanged'] for r in protected),
}
assert all(checks.values()), checks
put('verification.json', {'checks': checks, 'passed': True,
    'independent_Main_admission': False, 'native_acceptance': False})
files = [bind(f) for f in sorted(OUT.iterdir()) if f.is_file() and f.name != 'RECEIPT.json']
put('RECEIPT.json', {'batch': 272, 'status': 'SEALED_BOUNDED_SCREEN_ZERO_NOT_TASK_COMPLETION',
    'files': files, 'checks': checks, 'complete_new_whole_studies': 0,
    'proposal_maximum': 0, 'formal_credit_added': 0, 'native_acceptance': False,
    'tasks_deleted': 0, 'production_changes': 0, 'all_tasks_complete': False})
print(json.dumps({'receipt': bind(OUT / 'RECEIPT.json'), 'files': len(files), 'checks': len(checks)}, ensure_ascii=False))
