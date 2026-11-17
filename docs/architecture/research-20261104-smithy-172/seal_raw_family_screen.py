"""Bounded original-state family screen before needless visual duplication."""
import json,hashlib
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-171'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get(P/'pre-render-history-screen.json')['rows'][0];raw=get(P/'preassessment-original-sources.json')['rows'][0];d=raw['original'];pal=d['palette'];cell={tuple(x['pos']):x for x in d['blocks']}
assert r['eligible_for_new_source_study'] and bind(r['source_archive'])==r['fixed_archive']
with ZipFile(r['source_archive']) as z:assert hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256']
assert d['size']==[9,9,11] and d['DataVersion']==3465 and len(d['blocks'])==len(cell)==560 and len(pal)==37 and d['entities']==[]
assert len([x for x in d['blocks'] if pal[x['state']]['Name']=='minecraft:air'])==110 and len([x for x in d['blocks'] if 'nbt' in x])==4
critical=[([2,2,1],'minecraft:grindstone'),([6,2,1],'minecraft:lava'),([6,2,2],'minecraft:lava'),([4,3,3],'minecraft:furnace'),([4,4,3],'minecraft:furnace'),([6,2,4],'minecraft:chest'),([2,2,6],'minecraft:crimson_door'),([2,3,6],'minecraft:crimson_door'),([0,1,3],'minecraft:jigsaw'),([5,2,5],'minecraft:air'),([5,2,6],'minecraft:air'),([5,2,7],'minecraft:crimson_fence'),([5,3,7],'minecraft:crimson_pressure_plate')]
for pos,name in critical:assert pal[cell[tuple(pos)]['state']]['Name']==name
assert not list(P.glob('*.png'))
oldp=R/'docs/architecture/research-20261104-smithy-067/manual-review.json';old=get(oldp);classicp=R/'docs/architecture/research-20261104-smithy-168/whole-family-comparison.json';classic=get(classicp)
put('saved-family-comparison.json',{'old067_binding':bind(oldp),'old067_two_complete_records_actually_read':old['cases'],'classic057_previous_actual_reading_reused_binding':bind(classicp),'classic057_full_saved_record_preserved':classic['old_complete_record_actually_read'],'classic057_complete_original_comparison_preserved':classic['old_entire_original_semantic_comparison_actually_read'],'old_images_sources_and_nested_chains_not_reopened':True,'current_comparison':'当前北开放磨/双层炉与东北熔槽热棚，南封闭共同室并向东北伸箱凹位，单门分内外。相对057经典前低热棚/后封室及067F02外作业凹位/内长冷室/箱区，本案变化仍是既有棚—室—储凹位及设备/材料摆放，未有新工住分层或独立作业动线；保守原格筛查0，不凭叠双炉、升基一格、红木/熔岩数量增加完整相关建筑信用。并非声称字节相同或证明原始作者复制。','credit_proposal_maximum':0})
obs={
 'layout':'北部开放工作棚含西磨、中央两竖叠炉及东北双格熔槽，南部闭共同室以一门接棚；北东侧箱凹位与共同室连通，源只单层使用，不分成热棚/储室/住翼多栋。与经典前棚后室/工作凹位配冷室/储区家族保守归有界0。',
 'proportion':'9×9×11/DV3465声明891/存560=450非air110air，331省略不是air。37palette、9完整索引层、4BE、entities[]实际读，未渲染PNG/未做完整视觉研究。主要floor1/use2，炉位y3/4是竖叠设备而非二层经营；高屋面到y8非9层。',
 'facade_roof_materials':'blackstone159、crimsonplanks68/hyphae38、crimsonstairs62、obsidian17为原保存材；北低盖与南坡盖由原层分布识别但无图立面观察。黑红玻璃69/4只记保存基材，未读randomizer不得称完成柱替换/熔岩下承托。无床、内梯或楼层板，原门2,2/3,6south/right/closed为一扇上下两态。',
 'functional_states':'grind2,2,1floor/east，6,2,z1/2 lava level0，4,3/4,3两west unlit普通炉均Items[]/计时0/RecipesUsed{}；箱6,2,4south原crimson_weaponsmithloot/seed8571126717758176822。无砧/锻台/已产物证据，3redtorch/压力板poweredfalse为静态不冒机关。',
 'circulation':'西入口0,1,3west_up通实际crimson/streets，finaleast bottomblackstonestairs，不是empty。南门进南共同室；东箱凹位沿x5,y2,z4..6为air，但x5,2,7fence/3,7pressureplate保留，不把所有格写成无障碍动线。双炉正面、门槛与熔槽安全未原生验。',
 'context_and_limits':'只读两个精确selected片段normal/zombie均weight2 rigid legacy而processor分别randomizer/zombify，未读完整池、处理器、metadata、街路或loot上下文；机器解析/指纹/索引实际阅读不当完整研究或独立Main接纳。为避免重复既有组织未进一步生成PNG；未修改旧判断。'
}
put('sources.json',{'candidates':[{'id':'F01','source_archive':r['source_archive'],'member':r['member'],'nbt_sha256':r['nbt_sha256'],'raw_only_family_screen':True,'formal_credit_added':0}]})
put('manual-review.json',{'cases':[{'id':'F01','screening_observations':obs,'status':'BOUNDED_RAW_EXISTING_FRONT_WORK_SHED_REAR_COMMON_ROOM_STORAGE_RECESS_FAMILY_ZERO','credit_proposal_maximum':0,'formal_credit_added':0,'actual_full_reference_study_complete':False,'native_acceptance':False}],'complete_whole_reference_studies':0,'raw_original_sources_screened':1,'actual_current_images_viewed':0,'pending_maximum':0,'formal_credit_added':0})
put('actual-reading-boundary.json',{'original_index_planes_actually_read':list(range(9)),'palette_states_actually_read':37,'full_block_entities_actually_read':4,'entities':[],'selected_pool_snippets_read':2,'full_context_JSON_or_metadata_read':0,'actual_PNG_generated_or_viewed':0,'old067two_full_written_records_read':True,'old057saved_whole_record_exact_reuse_from168':True,'full_visual_study_or_native_acceptance':False})
c=get(prev/'carried-forward-pending.json');assert [(x['batch'],x['id']) for x in c['carried_unresolved_whole_reference_proposals']]==[(157,'W01'),(170,'F01')];c['previous_batch_receipt']=bind(prev/'RECEIPT.json');c['current_batch_new_pending']=0;c['current_batch_pending_cases']=[]
put('carried-forward-pending.json',c);put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
for f in get(P/'protected-inputs.json')['files']:assert bind(f['path'])==f
put('verification.json',{'status':'PASS_RAW_SOURCE_FAMILY_SCREEN_ONLY','original_member_and_fixed_archive_bound':True,'unique_source_positions':560,'critical_original_state_assertions':len(critical),'assertions_are_not_reference_count':True,'protected_input_count':len(get(P/'protected-inputs.json')['files']),'no_PNG_or_native_study':True,'java_run':False})
s={'batch':172,'status':'RAW_CRIMSON_WEAPONSMITH_EXISTING_FRONT_WORK_SHED_REAR_ROOM_FAMILY_ZERO','complete_whole_reference_studies':0,'raw_original_sources_screened':1,'generated_png':0,'actual_images_viewed':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'173 continue fixed-local genuinely different complete related work/living designs;157 and170 pending,1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':173})
(P/'HANDOFF.md').write_text('172原格有界家族筛查0：crimson weaponsmith北开放磨/竖叠双炉/熔槽棚→南封共同室及侧箱凹位，保守仍经典前棚后室/凹作业区配冷室储区组织，不以红木、叠炉、抬基增加参考。实际9原索引层/37palette/4BE/空实体/2精确selected片段；完整JSON/metadata/PNG0，未称完整研究。067双完整旧七观察及原比较本轮读，057从168已实际读的完整记录精确复用，旧图源链不重跑。157及170待核，无Java/游戏/生产/清单删除。\n')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',{**s,'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files)},ensure_ascii=False))
