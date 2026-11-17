import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent/'research-20261104-smithy-192';R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
def rd(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=p.resolve();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
mp=R/'docs/cod4/audit-20261022/coordinator-smithy190-F01-vertical-work-life-whole-review-20261110.json';mb=bind(mp);assert mb['sha256']=='4eda68b15d539850bc87c80e5ebc1734223cad5616fbb174c7cbef71583de40e' and mb['bytes']==122728;main=rd(mp)
ad=rd(O/'latest-independent-admissions.json');ca=rd(O/'carried-forward-pending.json');assert 'newly_notified_NPC01_admission_190_F01'not in ad;assert '190F01_NPC01_resolved_accept1_first193'not in ca
assert main['accepted_research_unit']==1 and main['formal_author_carry_applied']==0 and main['COD4_increment']==0 and main['NPC05_increment']==0
assert len(main['Main_seven_dimensions'])==7 and len(main['Main_limits'])==14
first={'Main_binding':mb,'full_Main_judgment_preserved_exact':main,'first_author_binding_batch':193,'accepted_reference_scope':'COD3 NPC01完整相关工作/居住空间','increment_once':1,'current_batch_formal_credit_added':1,'subsequent_carry_increment':0,'COD4_increment':0,'NPC05_increment':0,'NPC01_cumulative_not_inferred':True,'actual_reading':'本批完整实际读Main全部新判词、七维、家族结论、14限制及064保存判词；附原173palette/42BE/5entity/20层RLE/4JSON2metadata与190实际完整读内容逐对象相同，复用不重复声称新读/新看图。','large_payload_reuse_checks':rd(P/'Main190-original-payload-reuse.json'),'not_production_or_game_acceptance':True}
put('first-carry-190-independent-admission.json',first);ad['newly_notified_NPC01_admission_190_F01']=first;ad['current_batch_formal_credit_added']=1;put('latest-independent-admissions.json',ad)
oldpending=[x for x in ca['carried_unresolved_whole_reference_proposals']if x['batch']==190 and x['id']=='F01'];assert len(oldpending)==1
ca['carried_unresolved_whole_reference_proposals']=[x for x in ca['carried_unresolved_whole_reference_proposals']if not(x['batch']==190 and x['id']=='F01')];ca['190F01_NPC01_resolved_accept1_first193']={**first,'prior_pending_preserved_as_resolved_history':oldpending[0]};ca['previous_batch_receipt']=bind(O/'RECEIPT.json');put('carried-forward-pending.json',ca)
put('previous-checkpoint.json',{'receipt':bind(O/'RECEIPT.json'),'190_immutable_receipt':bind(P.parent/'research-20261104-smithy-190/RECEIPT.json')})
put('protected-inputs.json',rd(O/'protected-inputs.json'))
put('manual-review.json',{'new_original_semantic_source_studies':0,'new_PNG_actually_viewed':0,'new_qualifying_whole_reference_proposals':0,'accepted_prior190_first_carry':{'Main_binding':mb,'Main_seven_dimensions_preserved_exact':main['Main_seven_dimensions'],'Main_all14_limits_preserved_exact':main['Main_limits'],'family_decision_preserved_exact':main['family_decision'],'increment_once':1,'future_carry_increment':0},'machine_discovery_not_credit':True,'not_received_only_for190':True,'192_received0_not_independent_Main_7PNG_replay':True})
put('actual-reading-boundary.json',{'Main190_new_judgment_and_seven_dimensions_all14limits':'actually read complete bounded output','Main064_saved_complete_judgment':'complete saved object actually read; no original064NBT/PNG replay, no retroacceptance','Main190_large_original_payloads':'exact equality to190 actual previous full read, reused only','new_reference_original_NBT_semantic_read':0,'new_PNG_generated_or_viewed':0,'new_source_reading_credit':0,'prior190_independent_admission_firstcarry':1,'future190_increment':0,'unsealed_tool_error':'empty-selection history script initially referenced inventory_path declared only in candidate loop. Corrected before seal by declaring inventory_path before loop; rerun succeeded. No source verdict affected.'})
disc=rd(P/'unread-production-living-machine-discovery.json');assert not disc['errors']
ss={'batch':193,'status':'FIRST_EXACT_ONCE_MAIN190_NPC01_ACCEPT1_CARRY_AND_BOUNDED_MACHINE_DISCOVERY','formal_credit_added':1,'formal_credit_origin':'190F01 first author carry193 only','all_other_prior_admissions_current_increment':0,'190_first193_increment':1,'190_after193_carry_increment':0,'186first187_later_carry_increment':0,'actual_new_original_semantic_source_studies':0,'complete_new_qualifying_whole_reference_studies':0,'current_PNG':0,'COD4_accepted_baseline':153,'COD4_gap':847,'COD4_increment':0,'NPC05_increment':0,'NPC01_cumulative_not_inferred':True,'java_run':False,'game_run':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'194从本批机器共存候选选择真实完整相关工居例逐源实际研究，先比完整旧实例，不把机器扫描/组件/亭/职业换色充数。157W01仍待审，182HOLD/064历史pending不转接受，190以后carry0。'}
put('session.json',ss);checks=[]
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
ck('Main190_binding_exact',bind(mp)==mb)
ck('first_record_Main_object_exact',rd(P/'first-carry-190-independent-admission.json')['full_Main_judgment_preserved_exact']==main)
ck('admission_Main_object_exact',rd(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_190_F01']['full_Main_judgment_preserved_exact']==main)
ck('carry_Main_object_exact',rd(P/'carried-forward-pending.json')['190F01_NPC01_resolved_accept1_first193']['full_Main_judgment_preserved_exact']==main)
ck('all_payload_reuse_exact',all(rd(P/'Main190-original-payload-reuse.json')['checks'].values()))
ck('190_removed_only_from_active_pending',not any(x['batch']==190 for x in ca['carried_unresolved_whole_reference_proposals']))
ck('157_pending_exact',ca['carried_unresolved_whole_reference_proposals']==[x for x in rd(O/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals']if x['batch']!=190])
for k in ['182F01_NPC01_resolved_initial_review_HOLD0_first184','174F01_NPC01_resolved_accept1_first177','186F04_NPC01_resolved_accept1_first187']:ck('old_carry_exact:'+k,ca[k]==rd(O/'carried-forward-pending.json')[k])
for f in rd(P/'protected-inputs.json')['files']:ck('protected:'+f['path'],bind(Path(f['path']))==f)
for f in rd(P.parent/'research-20261104-smithy-190/RECEIPT.json')['files']:ck('sealed190_immutable:'+f['path'],bind(Path(f['path']))==f)
ck('noPNG',not list(P.glob('*.png')));ck('machine_discovery0',disc['formal_credit_added']==0 and not any(x['actual_manual_semantic_read']for x in disc['scanned']))
v={'status':'PASS'if all(c['passed']for c in checks)else'FAIL','checks':checks,'check_count':len(checks),'machine_assertions_not_semantic_credit':True};put('verification.json',v);put('active-checkpoint.json',{**ss,'verification':v['status']})
(P/'HANDOFF.md').write_text('193首次准确承接Main190接纳：NPC01完整相关参考+1仅一次；完整Main判词对象/7维/14限制存于first/admissions/carry三处，之后190 carry0。190封存29文件未改；COD4仍153/847、NPC05+0、NPC01累计不推断，064不变接受、182HOLD与157待审保留。当前新原源语义研究0/新PNG0，后续机器设备床共存发现仅候选不加分，不等完整工居；不修改主清单/共享Jar或启动Java/游戏。\n')
if v['status']!='PASS':print([c for c in checks if not c['passed']]);raise SystemExit('NOT SEALED')
put('RECEIPT.json',{**ss,'files':[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(rd(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))
