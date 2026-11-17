"""Seal bounded selection evidence, not whole-building reference credit."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-168'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
s=get(P/'pre-render-history-screen.json')['rows'];raw=get(P/'preassessment-original-sources.json')['rows'];assert len(s)==3 and len(raw)==2 and not s[2]['eligible_for_new_source_study']
olds=[]
for batch,ident in [(68,'F02'),(90,'F01'),(108,'F01'),(113,'F01')]:
 f=R/f'docs/architecture/research-20261104-smithy-{batch:03d}/manual-review.json';j=get(f);c=next(c for c in j.get('cases',j.get('reviews',[])) if c['id']==ident);olds.append({'batch':batch,'binding':bind(f),'complete_saved_record_actually_read':c,'old_images_source_chains_not_reopened':True,'bounded_old108_113_not_reclassified_as_full_studies':True})
put('saved-family-reading.json',{'records':olds,'new_reference_credit':0})
ver=R/'docs/cod4/audit-20261022/coordinator-smithy165-first167-zero-carry-review-20261110.json';assert bind(ver)['sha256']=='342267b8163db6b141370f5258b82e6b304cd29e278c75fc38ce9c551faceed3' and bind(ver)['bytes']==6411
put('165-first167-carry-integrity-review-reuse.json',{'binding':bind(ver),'complete_saved_integrity_review_object_actually_read':get(ver),'new_source_or_visual_study':False,'reference_increment':0,'does_not_reaccept165':True})
f01={
 'id':'F01','status':'RAW_COMPLETE_WORKSHOP_ELIGIBILITY_PLAUSIBLE_RETAIN_FOR_NEXT_DEEP_REVIEW_NOT_REFERENCE_PROPOSAL',
 'layout':'南单格门颈两道相隔一格普通门接北横向共同冷作厅；smith2,1,2、箱6,1,3，石砖墙与完整原木阶状坡盖，无热区/住翼/床/梯。上下door均north/right/closed，地理南门不写北门。',
 'source_stats':'11×6×8/DV3465，528声明/279存=229非air50air/249省略；21palette、4完整BE、entities[]及6原始索引层实际读。源无熔炉/岩浆/水/砧，不因工具匠名补热工。',
 'circulation':'外门5,1/2,6→中间5,1/2,5air→内门5,1/2,4→北厅5,1/2,3air，门颈并非两间店。北厅仅单层commonhall，东两石阶是同高陈设不通屋顶。',
 'context_boundary':'只读houses精确selected权3/rigid/legacy/mountains-mossify，未读完整JSON、processor或metadata，不作自然生成/地形承托结论。两个向上decor/cat socket不是缺房翼或已生成NPC。入口finalstructure_void非air。',
 'preselection':'对完整旧090单入口共同炉箱室和068连续L冷室，需进一步核查两门门颈到横厅的整体关系是否足够，不能只因增门/换工位断新。保留下一批完整图/上下文审阅，尚非已完成建筑研究、未提出独立信用。',
 'formal_credit_added':0,'credit_proposal_maximum':0}
f02={
 'id':'F02','status':'BOUNDED_RAW_EXISTING_CONTINUOUS_L_COLD_ROOM_FAMILY_ZERO_NO_DEEP_VISUAL_STUDY',
 'layout':'9×7×12/DV3465声明756/382存=299非air83air/374省略；32palette/1BE/entities[]及7原始索引层实际读。西南x2,y2/3,z8/9双门入短横臂后向北长臂smith6,2,2，单层连续L冷室；完整阶坡盖但无床箱炉砧及内隔门。',
 'comparison':'与完整已读068F02同一西南双门入口臂→北长冷室→北smith的关键关系，113F01原有界记录也明确同族。warped替crimson/菌材、升floor1/use2、黑蓝染玻璃基及少一air格不产生新的工艺空间组织；不需为同家族再渲染PNG。113和108旧记录是有界筛查，未改称完整研究。',
 'source_limits':'原黑/蓝玻璃46/6是保存材，未读processor或进行转换，不能把图色或占位玻璃当水。两精确selected片段分别normal randomizer/zombie zombify权2，完整池和处理器尚未读。红石灯/plate0/打开trapdoor原态，不认机械或上楼。',
 'credit_proposal_maximum':0,'formal_credit_added':0}
f03={'id':'F03','status':'MACHINE_EXACT_ROLE_AND_OCCUPANCY_MATCH_ONLY_EXCLUDED_FROM_NEW_STUDY','member':s[2]['member'],'source_archive':s[2]['source_archive'],'matches':s[2]['historical_exact_matches'],'manual_original_NBT_study':False,'PNG_generated':0,'semantic_family_admission_claimed':False,'reason':'三指纹筛选中role与occupancy匹配既有cherry armorer_2，不能凭山地材质当新空间；未打开旧判词/图片或逐状态研究此F03，机器排除不计参考。','formal_credit_added':0}
put('manual-review.json',{'cases':[f01,f02,f03],'complete_whole_reference_studies':0,'complete_original_index_source_readings':2,'new_PNG_generated':0,'actual_current_images_viewed':0,'pending_maximum':0,'formal_credit_added':0,'all_tasks_complete':False})
put('sources.json',{'candidates':[{'id':x['id'],'source_archive':x['source_archive'],'member':x['member'],'source_preassessment_only':True,'formal_credit_added':0} for x in raw],'excluded_machine_match':f03,'not_whole_reference_credit':True})
put('actual-reading-boundary.json',{'F01':{'original_planes_read':6,'palette':21,'BE':4,'entities':[]},'F02':{'original_planes_read':7,'palette':32,'BE':1,'entities':[]},'F03_original_semantic_read':False,'all_PNG':0,'full_context_JSON':0,'only_three_precise_selected_pool_snippets_read':True,'metadata_read':0,'native_acceptance':False})
c=get(prev/'carried-forward-pending.json');assert [(x['batch'],x['id']) for x in c['carried_unresolved_whole_reference_proposals']]==[(157,'W01')];c['previous_batch_receipt']=bind(prev/'RECEIPT.json');c['current_batch_new_pending']=0;c['current_batch_pending_cases']=[]
put('carried-forward-pending.json',c);put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
for f in get(P/'protected-inputs.json')['files']:assert bind(f['path'])==f
assert not list(P.glob('*.png'))
put('verification.json',{'status':'PASS_BOUNDED_PRESELECTION_ONLY','fixed_archives_original_members_bound':True,'old_saved_records_bound_not_reaccepted':True,'protected_input_count':len(get(P/'protected-inputs.json')['files']),'new_reference_credit':0,'next_F01_not_pending_reference_proposal':True,'java_run':False})
sess={'batch':169,'status':'THREE_FIXED_SOURCE_PRESELECTIONS_ONE_RETAINED_FOR_DEEP_REVIEW','complete_whole_reference_studies':0,'original_index_sources_read':2,'machine_only_exclusions':1,'generated_png':0,'actual_images_viewed':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'170 deeply review169F01 complete mountains coldtool workshop, compare whole two-door neck/common hall;157 remains pending,1000 unmet no production.'}
put('session.json',sess);put('active-checkpoint.json',{**sess,'verification':bind(P/'verification.json'),'next_batch':170})
(P/'HANDOFF.md').write_text('169仅源预判：山地工具匠两门门颈→北横冷作厅有完整屋盖，留170深查，未提参考信用；warped工具匠原6/7层及palette/BE已读，连续L冷室同旧068/113组织，保守0不再出图；mountain甲匠2仅role/occupancy与旧cherry匹配机器排除，未语义研究。当前PNG0、完整研究0、三范围增量0。Main165首167 carry完整性0核查全文保存，本次不是新验收。157待核保留，无Java/制作/主清单。\n')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',{**sess,'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files)},ensure_ascii=False))
