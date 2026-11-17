"""First exact carry of independently accepted158; no new source/image study."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-163'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
f=R/'docs/cod4/audit-20261022/coordinator-smithy158-F01-upper-entry-cold-prep-whole-review-20261110.json';j=get(f)
assert bind(f)['sha256']=='3e82acd9c536ff62d1c16c76290e2812d25765a45bf4af91c20d8364d2085821' and bind(f)['bytes']==82887
assert len(j['Main_observations'])==len(j['Main_limits'])==10 and len(j['original_author_seven_observations_preserved'])==7 and len(j['complete_four_old_saved_comparisons'])==4
assert j['current_NPC01_related_reference_increment']==1 and j['COD4_reference_increment']==j['NPC05_reference_increment']==j['later_carry_increment']==0
first={'receipt':bind(f),'complete_Main_judgment_object':j,'first_bound_batch':164,'first_carry_related_reference_increment':1,'subsequent_carry_increment':0,'scope':'COD3 NPC01 related complete workshop/living spatial reference only','COD4_increment':0,'NPC05_increment':0,'cumulative_NPC01_not_inferred':True}
put('first-carry-158-independent-admission.json',first)
a=get(prev/'latest-independent-admissions.json');a['newly_notified_NPC01_admission_158_F01']=first;put('latest-independent-admissions.json',a)
c=get(prev/'carried-forward-pending.json');original=c['carried_unresolved_whole_reference_proposals'];assert sorted((x['batch'],x['id'])for x in original)==[(157,'W01'),(158,'F01')]
c['previous_batch_receipt']=bind(prev/'RECEIPT.json');c['158F01_NPC01_resolved_accept1_first164']=first;c['carried_unresolved_whole_reference_proposals']=[x for x in original if(x['batch'],x['id'])!=(158,'F01')];c['current_batch_new_pending']=0;c['current_batch_pending_cases']=[]
assert [(x['batch'],x['id'])for x in c['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]
put('carried-forward-pending.json',c);put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'));put('previous-checkpoint.json',{'receipt':bind(prev/'RECEIPT.json'),'old_complete_admissions_not_replayed':True})
protected=[R/'modpack/mods/dynasty-1.4.0.jar',R/'docs/cod4/audit-20261022/pending-tasks.json',R/'docs/cod4/audit-20261022/task-ownership-20261026.json']+sorted(Path('/Users/a15356015027/Desktop/code x提示词').glob('cod[1-6].txt'))
guards=[bind(p)for p in protected];put('protected-inputs.json',{'files':guards})
put('sources.json',{'candidates':[],'new_source_studies':0,'carry_only':True});put('manual-review.json',{'cases':[],'scope':'First exact independent admission carry only; no new source or visual study','complete_whole_reference_studies':0,'new_source_reference_credit':0,'native_acceptance':False})
for v in [get(P/'first-carry-158-independent-admission.json'),get(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_158_F01'],get(P/'carried-forward-pending.json')['158F01_NPC01_resolved_accept1_first164']]:assert v==first and v['complete_Main_judgment_object']==get(f)
assert not list(P.glob('*.png'))
for g in guards:assert bind(Path(g['path']))==g
put('verification.json',{'status':'PASS_EXACT_WHOLE_MAIN_OBJECT_FIRST164_CARRY_ONLY','three_full_objects_equal':True,'Main10observations10limits7authorobservations4oldcomparisons_actually_read':True,'remaining_Main_fields_actually_read_in_second_bounded_output':True,'full_Main_object_preserved':True,'first_NPC01_increment':1,'subsequent_increment':0,'new_source_reference_credit':0,'NPC05_increment':0,'COD4_increment':0,'pending157_preserved':True,'old158_files_not_revalidated_or_modified':True,'protected_files_unchanged':len(guards),'java_run':False})
s={'batch':164,'status':'FIRST158_NPC01_INDEPENDENT_WHOLE_ADMISSION_CARRY_ONLY_NO_NEW_STUDY','complete_whole_reference_studies':0,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':1,'first158NPC01independent_carry_increment':1,'all_other_prior_carry_increment':0,'cumulative_NPC01_not_inferred':True,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'165 continue fixed-local related whole-building study and dedup; preserve157W01 pending,1000 gate unmet, no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':165})
(P/'HANDOFF.md').write_text('164为158独立验收首次完整carry：Main全文10观察10限制、原七观察/四旧比较及其余全部字段分两次实际读完，整个判断原样进入firstcarry/admissions/resolved三个表示并逐对象相等。仅COD3 NPC01既有相关整屋接受1首次携带，后批0；不是164新研究信用，也非游戏任务完成。158研究pending移除，157W01 NPC05待审保留；153/156旧接纳仅carry0，COD4仍153/gap847。无源重读/新PNG/Java/游戏/生产/清单修改。\n')
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{**s,'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files),'first158_NPC01_carry_increment':1,'new_source_credit':0},ensure_ascii=False))
