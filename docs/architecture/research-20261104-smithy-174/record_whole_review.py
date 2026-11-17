"""Record actual bounded whole-building study; independent semantic admission required."""
import json, hashlib
from pathlib import Path
from collections import Counter

P = Path(__file__).resolve().parent
R = P.parents[2]
PREV = P.parent / 'research-20261104-smithy-173'
assert not (P / 'RECEIPT.json').exists()

def get(p):
    return json.loads(Path(p).read_text())

def put(n, v):
    (P / n).write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')

def bind(p):
    p = Path(p)
    b = p.read_bytes()
    return {'path': str(p.resolve()), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}

source = get(P / 'sources.json')['candidates'][0]
raw = get(P / 'raw-source-audit.json')['candidates'][0]['nbt_decoded_original']
pal = raw['palette']
cells = {tuple(b['pos']): b for b in raw['blocks']}
def state(x, y, z):
    return pal[cells[(x, y, z)]['state']]

observations = {
 'layout': '东西桥口经z7横向通廊贯穿，北侧x6..8/z3..8窄长高炉厅向通廊开敞，南z9隔墙单门后为两床夹中间箱的寝室；公共交通横切工住之间，不是两作坊、四屋或四桥口环热台。高炉厅另有东侧低箱。',
 'proportion': '15×26×15/DV3120，5850原记录恰等声明体积；1068非air/4782显式air，无省略。y0..14主要石尖岛基；y16木地台、y17使用层，盖脊y24/25，不把26格画布、尖底或高屋盖当26层/上层工位。',
 'facade': '两边各一条横向桥前坪配云杉栏/灯、石英柱和花槽，房体为南北长窄墙，两侧z7开口连接公共通廊；后寝室唯一云杉门(7,17/18,9)south/right/open。窗与装饰活板不是额外出入口。',
 'roof': '南北长脊与横向桥口低翼交成十字坡盖，原pink_terracotta86、acacia_stairs84、acacia木脊及quartz柱，不可按分类灰图称全石瓦；(7,18..21,4)stone_brick_wall上接y22/23 polished_andesite及y24/25 bricks，属高炉上方烟道构形，运行排烟未验。无梯或可证上阁通路。',
 'materials': 'stone506为岛底主量；terracotta82/bricks49/stripped_acacia_log47/spruce_planks51/quartz_pillar60构屋。高炉(7,17,4)south/unlit/Items[]/BurnCookTotal0/RecipesUsed{}；寝室箱(7,17,11)north为sky_village_armorer seed8523599580502786033，工厅箱(8,17,8)north为normal_house seed-9200148453983457949。无砧/砂轮/锻造台/岩浆，不虚构完整锻打生产线。',
 'circulation': '西(0,16,7)west_up、东(14,16,7)east_up桥接头均final spruce_planks、同桥池；y17 z7全横列除村民接头外为显式air，接头finalair，原木/草地台在下。由中横廊北入高炉两侧留带，向南过单门到x7,z10床间通道及z11箱；实际栏/门/床/烟壁碰撞、NPC寻路与火险未验。',
 'terrain': '尖底浮岛、房体、横桥前坪同一完整NBT，独立房有基/墙/盖/内分区。两桥是村落交通接头，不能单凭接头说本屋缺失半栋，也不能说全村桥路已装配。两个村民接头finalair不等已生村民；原entities2均为石剑/铁剑item_frame，不是居民。不可把浮岛照搬为山脚地基成品。'
}
old65_path = P.parent / 'research-20261104-smithy-065/manual-review.json'
old95_path = P.parent / 'research-20261104-smithy-095/manual-review.json'
old65 = get(old65_path)['cases']
old95 = next(c for c in get(old95_path)['cases'] if c['id'] == 'F01')
main170 = get(PREV / 'first-carry-170-independent-zero.json')
comparison = {
 'status': 'PENDING_INDEPENDENT_RELEVANCE_AND_FAMILY_ADMISSION',
 'proposal_maximum': 1,
 'comparison': '相对065F01中央岩浆四向开放环流，本屋为侧桥横穿的窄厅与单门后寝室，北端高炉/烟道为壁边集中热位，不是换色环亭；相对065F02双门卧室+外东南L冷平台及内升阶，本屋仅一门后寝室，热位在北厅，东西公共桥通路夹在工住之间且无上阁梯。170为门颈接共用横厅无明确私寝；本屋的通廊/北热厅/单门后寝室有用途分界，但单高炉、剑框、armorer loot和浮岛本身都不能自动建立相关性或独立家族。095F01已示单高炉住宅可因相关性不足0，本屋同样须Main判断，保留0或最多1的可能，不自计。',
 'complete_saved_records_065_actual_read': old65,
 'complete_saved_record_095F01_actual_read': old95,
 'complete_Main170_judgment_reused_from173_not_reopened': main170['complete_Main_judgment_object'],
 'bindings': [bind(old65_path), bind(old95_path), bind(PREV / 'first-carry-170-independent-zero.json')],
 'old_images_or_NBT_context_reopened': False,
 'old_admission_increment': 0
}
put('saved-family-comparison.json', comparison)
images = [bind(p) for p in sorted(P.glob('*.png'))]
assert len(images) == 7
boundary = {
 'actual_images_viewed': images,
 'all_original_palette_entries_read': 57,
 'complete_BE_records_read': 11,
 'complete_entity_records_read': 2,
 'original_index_planes_actually_read': list(range(15,26)),
 'raw_indices_actually_read': 2475,
 'lower_0_to14_planes_only_machine_material_classification_read': True,
 'all_5850_original_states_semantically_read': False,
 'full_JSON_contexts_read': [c['member'] for c in get(P / 'source-context.json')['candidates'][0]['contexts']],
 'full_metadata_texts_read': [c['member'] for c in get(P / 'source-context.json')['metadata']],
 'runtime_generated_state_or_real_material_render': False,
 'scope': '7 actual class-color PNGs + full57palette/11BE/2entities + original y15..25 grids; lower15 layers classified only. No claim of complete cellwise semantic inspection.'
}
put('actual-reading-boundary.json', boundary)
case = {**source, 'observations': observations, 'images_actually_viewed': images,
 'whole_boundary': '完整同源浮岛基/房壳/屋盖/工住分区；桥socket不另算屋，未加载桥模板或全村；语义相关性及家族信用待独立判定。',
 'semantic_family_comparison': comparison, 'credit_proposal_maximum': 1,
 'status': 'COMPLETE_STUDY_PENDING_RELEVANCE_AND_FAMILY_NOT_SELF_ADMITTED',
 'native_acceptance': False}
put('manual-review.json', {'cases': [case], 'actual_current_images_viewed': 7,
 'manual_observations': 7, 'formal_credit_added': 0, 'no_independent_self_admission': True})

checks = []
def check(name, result):
    assert result, name
    checks.append(name)
check('size_DV', raw['size'] == [15,26,15] and raw['DataVersion'] == 3120)
check('dense_5850_distinct_no_omitted', len(raw['blocks']) == len(cells) == 5850)
check('57palette_11BE_2entities', len(pal)==57 and sum('nbt' in b for b in raw['blocks'])==11 and len(raw['entities'])==2)
check('air4782_nonair1068', sum(state(*p)['Name']=='minecraft:air' for p in cells)==4782)
check('blast_south_empty_unlit', state(7,17,4)=={'Name':'minecraft:blast_furnace','Properties':{'lit':'false','facing':'south'}} and cells[(7,17,4)]['nbt']=={'CookTime':0,'BurnTime':0,'Items':[],'id':'minecraft:blast_furnace','CookTimeTotal':0,'RecipesUsed':{}})
check('chimney_wall_four_levels', all(state(7,y,4)['Name']=='minecraft:stone_brick_wall' for y in range(18,22)))
check('chimney_cap_exact', all(state(7,y,4)['Name']=='minecraft:polished_andesite' for y in (22,23)) and all(state(7,y,4)['Name']=='minecraft:bricks' for y in (24,25)))
check('single_south_open_door_two_halves', [cells[(7,y,9)]['state'] for y in (17,18)]==[23,30])
check('two_complete_bed_pairs', [cells[(x,17,z)]['state'] for x in (6,8) for z in (10,11)]==[52,53,52,53])
for x,seed,table in [(7,8523599580502786033,'armorer'),(8,-9200148453983457949,'normal_house')]:
    z=11 if x==7 else 8
    check('chest_'+table, cells[(x,17,z)]['nbt']=={'LootTable':'skyvillages:chests/sky_village_'+table,'id':'minecraft:chest','LootTableSeed':seed} and state(x,17,z)['Properties']['facing']=='north')
check('two_bridge_finalplanks_actualpool', all(cells[(x,16,7)]['nbt']['pool']=='skyvillages:skyvillage_bridges' and cells[(x,16,7)]['nbt']['final_state']=='minecraft:spruce_planks' for x in (0,14)))
check('public_aisle_original_air_or_finalair', all(state(x,17,7)['Name']=='minecraft:air' or cells[(x,17,7)].get('nbt',{}).get('final_state')=='minecraft:air' for x in range(15)))
check('no_ladder_anvil_smith_grind_lava', not any(any(k in p['Name'] for k in ['ladder','anvil','smithing_table','grindstone','lava']) for p in pal))
check('entities_itemframes_not_people', all(e['nbt']['id']=='minecraft:item_frame' for e in raw['entities']))
check('selected_pool_weight50_rigid', get(P/'preassessment-original-sources.json')['rows'][0]['selected_pool_snippets'][0]['selected_element_only']['weight']==50)
check('six_context_two_metadata', len(boundary['full_JSON_contexts_read'])==6 and len(boundary['full_metadata_texts_read'])==2)
check('saved_old_records_complete', len(old65)==2 and all(len(c['observations'])==7 for c in old65) and len(old95['observations'])==7)
guards = get(P/'protected-inputs.json')['files']
for g in guards:
    check('protected_unchanged_'+g['path'], bind(g['path'])==g)

admissions=get(PREV/'latest-independent-admissions.json')
put('latest-independent-admissions.json', admissions)
carry=get(PREV/'carried-forward-pending.json')
assert [(c['batch'],c['id']) for c in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]
carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json')
carry['current_batch_new_pending']=1
carry['current_batch_pending_cases']=[{'batch':174,'id':'F01','scope':'COD3 NPC01','maximum':1,'status':'pending independent relevance/family judgment'}]
carry['carried_unresolved_whole_reference_proposals'].append({'batch':174,'id':'F01','scope':'COD3 NPC01','maximum':1,'status':'pending independent relevance/family judgment','manual_review':bind(P/'manual-review.json')})
put('carried-forward-pending.json', carry)
put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('verification.json', {'status':'PASS_BOUNDED_OFFLINE_SOURCE_AND_RECEIPT_CHECKS',
 'checks':checks,'check_count':len(checks),'machine_assertions_not_reference_credit':True,
 'independent_admission':False,'native_acceptance':False,'java_run':False})
session={'batch':174,'status':'SKYVILLAGES_HOUSE1_WHOLE_STUDY_PENDING_RELEVANCE_FAMILY',
 'complete_whole_reference_studies':1,'actual_images_viewed':7,'generated_png':7,
 'pending_maximum':1,'formal_credit_added':0,'prior_admissions_current_increment':0,
 'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'native_acceptance':False,
 'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,
 'actual_active_work_hours':None,
 'next':'175 continue fixed-local genuinely distinct complete related candidates;157W01 and174F01 pending.1000 unmet, no production.'}
put('session.json',session)
put('active-checkpoint.json',{**session,'verification':bind(P/'verification.json'),'next_batch':175})
(P/'HANDOFF.md').write_text('174 SkyVillages house_1完整工住屋研究，东西桥横向公共通廊→北高炉厅/单门南双床房；7PNG实际查看、57pal/11BE/2itemframes全读，y15..25原索引2475格实际阅读，y0..14仅机器层材质分类。6完整JSON/2metadata全文已读，Minecraft代理loot/桥fallback/实际桥模板、村民模板和运行结果未读未验。与065两例及095F01完整既存判词实际比较，170复用173已读完整判词。相关性和语义家族待Main独立审核，最多1，正式0。保留157W01；旧170在173已判0不再pending。COD4仍153/gap847，不推算NPC累计。不制作、不Java、不清单删项。173脚本注释残留relevance-zero：以其完整Main170对象及family-zero状态为准，此处不回写旧收据。\n')
put('RECEIPT.json',{**session,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'checks':len(checks),'files':len(get(P/'RECEIPT.json')['files'])},ensure_ascii=False))
