"""First exact Main182 HOLD0 carry plus bounded fixed-local source-link evidence."""
import json,hashlib
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];PREV=P.parent/'research-20261104-smithy-183'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
mainpath=R/'docs/cod4/audit-20261022/coordinator-smithy182-F01-outdoor-coldwork-ground-boundary-whole-review-20261110.json';mb=bind(mainpath);assert mb['sha256']=='94bfee56a0d248567ad0644689b9f8addaab2f72c9d7099ce9651e1e8db2b95b' and mb['bytes']==57068;main=get(mainpath)
put('first-carry-182-independent-hold-zero.json',{'receipt':mb,'full_Main_judgment_preserved_exact':main,'actual_manual_reading':'完整全部字段分两段无截断实际读，包括10finding/7limits及完整061F02等已保存判词；不重开旧PNG/NBT/来源链，不把Main图片数当作者新看。','current_increment':0,'first_bound_batch':184})
root=get(P/'bounded-root-source-records.json');archive=root['archive'];texts={r['member']:r for r in root['records']};houses=texts['data/kaisyn/worldgen/template_pool/village/exclusives/nilotic/houses.json']['json'];loc='kaisyn:village/exclusives/nilotic/houses/nilotic_mason_1';typo='kaisyn:village/exclusives/nilotic/houses/nilotic_masons_1'
with ZipFile(archive['path']) as z:
 names=set(z.namelist());current='data/kaisyn/structures/village/exclusives/nilotic/houses/nilotic_mason_1.nbt';missing='data/kaisyn/structures/village/exclusives/nilotic/houses/nilotic_masons_1.nbt';exact=[]
 for n in sorted(names):
  if n.endswith(('.json','.json5','.toml','.mcmeta')) and loc.encode() in z.read(n):exact.append(n)
 for rec in root['records']:
  b=z.read(rec['member']);assert len(b)==rec['bytes'] and hashlib.sha256(b).hexdigest()==rec['sha256'] and b.decode()==rec['original_text']
 assert current in names and missing not in names and not exact
 selected=[e for e in houses['elements'] if e.get('element',{}).get('location')==typo];assert len(selected)==1
put('source-link-boundary.json',{'source_archive':archive,'original_182_member':current,'original_182_location':loc,'original_182_NBT_reopened':False,'house_pool_read_complete':True,'house_pool_selected_literal_element':selected[0],'exact_182_location_in_scanned_archive_text_members':exact,'pool_literal_target_member':missing,'pool_literal_target_member_exists':False,'actual_singular_member_exists':True,'source_link_conclusion':'同一固定Jar houses池引用nilotic_masons_1而实际为nilotic_mason_1；不能把相似拼写静默修正为实际装配关系。已找到对应风格根配置，但未确立它装配182的原始路径。','minimum_ground_conclusion':'base_plate pool仅terrain_matching+legacy_single+jigsaw_replacement，structure WORLD_SURFACE_WG/start_height-1/beard_thin；这5份JSON原文不是实际y-1地面。原rootNBT已由061历史研究，不重开也不重新计数。完整承托仍未闭环，不制作假地板。','house_processor':'两random规则packed_mud .4→mud_bricks、mangrove_wood .4→mangrove_roots；不填下层、不运行概率。','not_read_or_verified':['baseplate NBT未重新打开；复用Main061已保存描述','jigsaw_replacement处理器实现本次未读','别的Jar/运行时重映射及注入代码未查，不称所有来源都无别名','世界实际地形承托/装配/寻路/原生外观未验'],'new_whole_reference_credit':0})
put('actual-reading-boundary.json',{'full_Main182_object_actually_read':mb,'Main_findings_count':10,'Main_limits_count':7,'complete_061F02_comparator_preserved_in_Main':main['complete_saved_comparators_read']['061F02'],'complete_new_original_JSON_texts_actually_read':[{'member':x['member'],'sha256':x['sha256'],'bytes':x['bytes']} for x in root['records']],'manual_new_context_JSON_count':5,'new_original_NBT_semantic_reading':0,'new_images_generated_or_viewed':0,'new_whole_building_studies':0,'formal_credit_added':0})
put('previous-checkpoint.json',{'receipt':bind(PREV/'RECEIPT.json'),'historical_sealed_inputs_not_rewritten':True})
protected=[R/'modpack/mods/dynasty-1.4.0.jar',R/'docs/cod4/audit-20261022/pending-tasks.json',R/'docs/cod4/audit-20261022/task-ownership-20261026.json']+sorted(Path('/Users/a15356015027/Desktop/code x提示词').glob('cod[1-6].txt'));put('protected-inputs.json',{'files':[bind(p) for p in protected]})
admissions=get(PREV/'latest-independent-admissions.json');admissions['newly_notified_NPC01_hold_zero_182_F01']={'receipt':mb,'first_bound_batch':184,'current_increment':0,'full_Main_judgment_preserved_exact':main};put('latest-independent-admissions.json',admissions)
carry=get(PREV/'carried-forward-pending.json');assert [(x['batch'],x['id']) for x in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01'),(182,'F01')];carry['carried_unresolved_whole_reference_proposals']=[x for x in carry['carried_unresolved_whole_reference_proposals'] if x['batch']!=182];carry['182F01_NPC01_resolved_initial_review_HOLD0_first184']={'receipt':mb,'first_bound_batch':184,'current_increment':0,'full_Main_judgment_preserved_exact':main,'held_evidence_not_cancelled_or_reset':True,'ground_boundary_still_unresolved':True};carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[];put('carried-forward-pending.json',carry);put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('main10findings7limits',len(main['Main_findings'])==10 and len(main['Main_limits'])==7)
ck('MainHOLD0notaccepted',main['decision']=='HOLD_ZERO_UNRESOLVED_GROUND_ASSEMBLY_CONSISTENT_WITH_PRIOR061F02' and main['cod3_npc01_credit_added']==0)
ck('exactMain3representations',get(P/'first-carry-182-independent-hold-zero.json')['full_Main_judgment_preserved_exact']==get(P/'latest-independent-admissions.json')['newly_notified_NPC01_hold_zero_182_F01']['full_Main_judgment_preserved_exact']==get(P/'carried-forward-pending.json')['182F01_NPC01_resolved_initial_review_HOLD0_first184']['full_Main_judgment_preserved_exact']==main)
ck('061F02complete_comparator_retained',get(P/'actual-reading-boundary.json')['complete_061F02_comparator_preserved_in_Main']==main['complete_saved_comparators_read']['061F02'])
ck('5completeJSONtextbindings',len(root['records'])==5)
ck('housepool12entries_literalplural_weight1',len(houses['elements'])==12 and selected[0]['weight']==1)
ck('sourcearchiveunchanged',bind(archive['path'])==archive)
ck('only157pending_preserved',[(x['batch'],x['id']) for x in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')])
for batch in (182,183):
 rp=P.parent/f'research-20261104-smithy-{batch}/RECEIPT.json'
 for f in get(rp)['files']:ck(f'sealed{batch}_'+Path(f['path']).name,bind(f['path'])==f)
for g in get(P/'protected-inputs.json')['files']:ck('protected_unchanged_'+g['path'],bind(g['path'])==g)
put('verification.json',{'status':'PASS_EXACT_FIRST_MAIN182_HOLD0_CARRY_AND_BOUNDED_SOURCE_LINK','checks':checks,'check_count':len(checks),'machine_assertions_not_semantic_credit':True})
s={'batch':184,'status':'FIRST_MAIN182_HOLD0_EXACT_CARRY_PLUS_LITERAL_SOURCE_LINK_GAP','formal_credit_added':0,'prior_admissions_current_increment':0,'new_context_JSON_actual_read':5,'new_NBT_semantic_read':0,'new_PNG':0,'new_whole_building_studies':0,'COD4_accepted_baseline':153,'COD4_gap':847,'NPC01_cumulative_not_inferred':True,'NPC05_increment':0,'java_run':False,'game_run':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'185继续未读完整相关建筑；182HOLD证据保留，plural池对singular源不自动改名，157W01待审。'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json')});(P/'HANDOFF.md').write_text('184首携Main182完整57068B判词，10finding/7limits/完整061F02原样三表示保留，HOLD0初审已收、承托仍未解，不清零旧研究。最小本地来源增量实际全文读5JSON：风格根/housepool/processor/structure/biometag；pool引用nilotic_masons_1但Jar只有nilotic_mason_1，无自动纠正或填假地板。完整实际承托仍未证实，0信用；不重看旧PNG/NBT，不改sealed182/183。183报告露场0收据已验证；157pending保留，历史174carry0。未Java/游戏/产品/清单。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(get(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))
