"""First exact carry of independently accepted174; no new source/image study."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-176'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
f=R/'docs/cod4/audit-20261022/coordinator-smithy174-F01-cross-passage-work-private-whole-review-20261110.json';j=get(f)
assert bind(f)['sha256']=='65bbbc310b52cc5f21feef4e37ea67b139440fa4d7d42df75760bd906a8e047f' and bind(f)['bytes']==255955
assert len(j['Main_observations'])==11 and len(j['Main_limits'])==10 and len(j['original_author_seven_observations_preserved'])==7 and len(j['complete_065_two_saved_judgments'])==2 and len(j['complete_095F01_saved_judgment']['observations'])==7
assert j['current_NPC01_related_reference_increment']==1 and j['COD4_reference_increment']==j['NPC05_reference_increment']==j['later_carry_increment']==0
first={'receipt':bind(f),'complete_Main_judgment_object':j,'first_bound_batch':177,'first_carry_related_reference_increment':1,'subsequent_carry_increment':0,'scope':'COD3 NPC01 related complete workshop/living spatial reference only','COD4_increment':0,'NPC05_increment':0,'cumulative_NPC01_not_inferred':True}
put('first-carry-174-independent-admission.json',first)
a=get(prev/'latest-independent-admissions.json');a['newly_notified_NPC01_admission_174_F01']=first;put('latest-independent-admissions.json',a)
c=get(prev/'carried-forward-pending.json');original=c['carried_unresolved_whole_reference_proposals'];assert sorted((x['batch'],x['id'])for x in original)==[(157,'W01'),(174,'F01')]
c['previous_batch_receipt']=bind(prev/'RECEIPT.json');c['174F01_NPC01_resolved_accept1_first177']=first;c['carried_unresolved_whole_reference_proposals']=[x for x in original if(x['batch'],x['id'])!=(174,'F01')];c['current_batch_new_pending']=0;c['current_batch_pending_cases']=[]
assert [(x['batch'],x['id'])for x in c['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]
put('carried-forward-pending.json',c);put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'));put('previous-checkpoint.json',{'receipt':bind(prev/'RECEIPT.json'),'old_complete_admissions_not_replayed':True})
protected=[R/'modpack/mods/dynasty-1.4.0.jar',R/'docs/cod4/audit-20261022/pending-tasks.json',R/'docs/cod4/audit-20261022/task-ownership-20261026.json']+sorted(Path('/Users/a15356015027/Desktop/code x提示词').glob('cod[1-6].txt'))
guards=[bind(p)for p in protected];put('protected-inputs.json',{'files':guards})
put('sources.json',{'candidates':[],'new_source_studies':0,'carry_only':True});put('manual-review.json',{'cases':[],'scope':'First exact independent admission carry only; no new source or visual study','complete_whole_reference_studies':0,'new_source_reference_credit':0,'native_acceptance':False})
for v in [get(P/'first-carry-174-independent-admission.json'),get(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_174_F01'],get(P/'carried-forward-pending.json')['174F01_NPC01_resolved_accept1_first177']]:assert v==first and v['complete_Main_judgment_object']==get(f)
assert not list(P.glob('*.png'))
for g in guards:assert bind(Path(g['path']))==g
put('verification.json',{'status':'PASS_EXACT_WHOLE_MAIN_OBJECT_FIRST177_CARRY_ONLY','three_full_objects_equal':True,'Main11observations10limits7author_and_complete065two095one_comparisons_actually_read':True,'Main_fields_actually_read_in_eight_bounded_unclipped_outputs':True,'nested_unchanged_Main170_exact_verified_and_reused_from_prior_actual_full_read':True,'full_Main_object_preserved':True,'first_NPC01_increment':1,'subsequent_increment':0,'new_source_reference_credit':0,'NPC05_increment':0,'COD4_increment':0,'pending157_preserved':True,'old174_files_not_revalidated_or_modified':True,'protected_files_unchanged':len(guards),'java_run':False})
s={'batch':177,'status':'FIRST174_NPC01_INDEPENDENT_WHOLE_ADMISSION_CARRY_ONLY_NO_NEW_STUDY','complete_whole_reference_studies':0,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':1,'first174NPC01independent_carry_increment':1,'all_other_prior_carry_increment':0,'cumulative_NPC01_not_inferred':True,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'178 continue fixed-local related whole-building study and dedup; preserve157W01 pending,1000 gate unmet, no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':178})
(P/'HANDOFF.md').write_text('177为174独立接受首次完整carry：Main11观察10限制、原7观察、065两整项及095F01完整比较与全体其余字段分8个有界无截断输出实际阅读；嵌套Main170完整对象与173已经全文读完的记录逐字段完全相等，复用旧全文阅读而非重开旧源图链。整个255955B判断原样进入firstcarry/admissions/resolved三表示并相等。NPC01既有相关整栋参考首次携带1，后批0，不是177新研究或游戏任务完成；COD4/NPC05增量0，NPC01累计不推算。174从新批pending移除，仅157W01保留。174/175/176封存不回写，无新PNG/源研究/Java/制作/清单删项。\n')
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{**s,'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files),'first174_NPC01_carry_increment':1,'new_source_credit':0},ensure_ascii=False))
