"""First exact carry of Main165 complete but insufficient-relevance zero decision."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-166'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
f=R/'docs/cod4/audit-20261022/coordinator-smithy165-F01-domestic-relevance-whole-review-20261110.json';j=get(f)
assert bind(f)['sha256']=='f2638546ace8f9143325a5836ad28ce165ca4e5d33ba554a9ad240b0cc53c329' and bind(f)['bytes']==109213
assert len(j['Main_observations'])==11 and len(j['Main_limits'])==10 and len(j['original_author_seven_observations_preserved'])==7 and len(j['complete_four_old_saved_comparisons'])==4
assert j['current_NPC01_related_reference_increment']==j['COD4_reference_increment']==j['NPC05_reference_increment']==j['later_carry_increment']==0
first={'receipt':bind(f),'complete_Main_judgment_object':j,'first_bound_batch':167,'first_carry_related_reference_increment':0,'subsequent_carry_increment':0,'scope':'165 complete domestic design studied; related smithy applicability insufficient, not unread or nonwhole','COD4_increment':0,'NPC05_increment':0,'cumulative_NPC01_not_inferred':True}
put('first-carry-165-independent-zero.json',first)
a=get(prev/'latest-independent-admissions.json');a['newly_notified_NPC01_zero_165_F01']=first;put('latest-independent-admissions.json',a)
c=get(prev/'carried-forward-pending.json');old=c['carried_unresolved_whole_reference_proposals'];assert sorted((x['batch'],x['id']) for x in old)==[(157,'W01'),(165,'F01')]
c['previous_batch_receipt']=bind(prev/'RECEIPT.json');c['165F01_NPC01_resolved_relevance0_first167']=first;c['carried_unresolved_whole_reference_proposals']=[x for x in old if (x['batch'],x['id'])!=(165,'F01')];c['current_batch_new_pending']=0;c['current_batch_pending_cases']=[]
put('carried-forward-pending.json',c);put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'));put('previous-checkpoint.json',{'receipt':bind(prev/'RECEIPT.json'),'old_complete_admissions_not_replayed':True})
guards=[bind(p) for p in [R/'modpack/mods/dynasty-1.4.0.jar',R/'docs/cod4/audit-20261022/pending-tasks.json',R/'docs/cod4/audit-20261022/task-ownership-20261026.json']+sorted(Path('/Users/a15356015027/Desktop/code x提示词').glob('cod[1-6].txt'))];put('protected-inputs.json',{'files':guards})
put('sources.json',{'candidates':[],'new_source_studies':0,'carry_only':True});put('manual-review.json',{'cases':[],'scope':'First complete independent relevance-zero judgment carry; no new source/visual study','complete_whole_reference_studies':0,'formal_credit_added':0,'native_acceptance':False})
for v in [get(P/'first-carry-165-independent-zero.json'),get(P/'latest-independent-admissions.json')['newly_notified_NPC01_zero_165_F01'],get(P/'carried-forward-pending.json')['165F01_NPC01_resolved_relevance0_first167']]:assert v==first and v['complete_Main_judgment_object']==get(f)
assert [(x['batch'],x['id']) for x in c['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]
for g in guards:assert bind(g['path'])==g
assert not list(P.glob('*.png'))
put('verification.json',{'status':'PASS_EXACT_WHOLE_MAIN_ZERO_OBJECT_FIRST167','three_full_objects_equal':True,'Main11observations10limits7author4comparisons_actually_read':True,'all_remaining_fields_read_in_bounded_outputs':True,'earlier_clipped_remainder_recovered_palette_tail_BE_matrices_context_metadata':True,'no_old165_source_or_images_reopened':True,'first_and_later_increment':0,'all_three_reference_scopes_increment':0,'pending157_preserved':True,'protected_files_unchanged':len(guards),'java_run':False})
s={'batch':167,'status':'FIRST165_COMPLETE_DOMESTIC_STUDY_RELEVANCE_ZERO_CARRY_ONLY','complete_whole_reference_studies':0,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'first165independent_zero_bound':True,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'168 continue truly related fixed-local workshop/forge whole designs, preserve157W01 pending;1000 unmet means no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':168})
(P/'HANDOFF.md').write_text('167首次原样carry Main165完整判词：完整住宅研究但铁匠热/冷作业组织相关性不足，三范围增量0；不是未读、非完整或强判旧家族重复。11观察10限制及全对象进入三个表示并完全相等，165 pending在新批移除，157W01保留。旧165/166封存不修改；无源/图重读、新PNG、Java、制作或清单删除。\n')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',{**s,'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files)},ensure_ascii=False))
