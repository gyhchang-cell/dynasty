"""First exact carry of Main170 complete but insufficient-relevance zero decision."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-172'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
f=R/'docs/cod4/audit-20261022/coordinator-smithy170-F01-common-cold-workshop-family-whole-review-20261110.json';j=get(f)
assert bind(f)['sha256']=='3338f28d498d90223363f69bb506d11b50a1d04e66c17119c4a23e0e0ba0edb6' and bind(f)['bytes']==107891
assert len(j['Main_observations'])==10 and len(j['Main_limits'])==9 and len(j['original_author_seven_observations_preserved'])==7 and len(j['complete_two_old_saved_whole_comparisons']['complete_saved_records'])==2
assert j['current_NPC01_related_reference_increment']==j['COD4_reference_increment']==j['NPC05_reference_increment']==j['later_carry_increment']==0
first={'receipt':bind(f),'complete_Main_judgment_object':j,'first_bound_batch':173,'first_carry_related_reference_increment':0,'subsequent_carry_increment':0,'scope':'170 complete related cold workshop studied; common work/storage family distinction insufficient, not unread or nonwhole','COD4_increment':0,'NPC05_increment':0,'cumulative_NPC01_not_inferred':True}
put('first-carry-170-independent-zero.json',first)
a=get(prev/'latest-independent-admissions.json');a['newly_notified_NPC01_zero_170_F01']=first;put('latest-independent-admissions.json',a)
c=get(prev/'carried-forward-pending.json');old=c['carried_unresolved_whole_reference_proposals'];assert sorted((x['batch'],x['id']) for x in old)==[(157,'W01'),(170,'F01')]
c['previous_batch_receipt']=bind(prev/'RECEIPT.json');c['170F01_NPC01_resolved_family0_first173']=first;c['carried_unresolved_whole_reference_proposals']=[x for x in old if (x['batch'],x['id'])!=(170,'F01')];c['current_batch_new_pending']=0;c['current_batch_pending_cases']=[]
put('carried-forward-pending.json',c);put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'));put('previous-checkpoint.json',{'receipt':bind(prev/'RECEIPT.json'),'old_complete_admissions_not_replayed':True})
guards=[bind(p) for p in [R/'modpack/mods/dynasty-1.4.0.jar',R/'docs/cod4/audit-20261022/pending-tasks.json',R/'docs/cod4/audit-20261022/task-ownership-20261026.json']+sorted(Path('/Users/a15356015027/Desktop/code x提示词').glob('cod[1-6].txt'))];put('protected-inputs.json',{'files':guards})
put('sources.json',{'candidates':[],'new_source_studies':0,'carry_only':True});put('manual-review.json',{'cases':[],'scope':'First complete independent relevance-zero judgment carry; no new source/visual study','complete_whole_reference_studies':0,'formal_credit_added':0,'native_acceptance':False})
for v in [get(P/'first-carry-170-independent-zero.json'),get(P/'latest-independent-admissions.json')['newly_notified_NPC01_zero_170_F01'],get(P/'carried-forward-pending.json')['170F01_NPC01_resolved_family0_first173']]:assert v==first and v['complete_Main_judgment_object']==get(f)
assert [(x['batch'],x['id']) for x in c['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]
for g in guards:assert bind(g['path'])==g
assert not list(P.glob('*.png'))
put('verification.json',{'status':'PASS_EXACT_WHOLE_MAIN_ZERO_OBJECT_FIRST173','three_full_objects_equal':True,'Main10observations9limits7author2comparisons_actually_read':True,'all_remaining_fields_read_in_bounded_outputs':True,'all_fields_actual_read_in_six_bounded_unclipped_outputs':True,'no_old170_source_or_images_reopened':True,'first_and_later_increment':0,'all_three_reference_scopes_increment':0,'pending157_preserved':True,'protected_files_unchanged':len(guards),'java_run':False})
s={'batch':173,'status':'FIRST170_COMPLETE_RELATED_COLD_WORKSHOP_FAMILY_ZERO_CARRY_ONLY','complete_whole_reference_studies':0,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'first170independent_zero_bound':True,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'174 continue truly related fixed-local workshop/forge whole designs, preserve157W01 pending;1000 unmet means no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':174})
(P/'HANDOFF.md').write_text('173首次原样carry Main170完整判词：完整相关冷作铺但共用工储厅家族差异不足，三范围增量0；不是未读、非完整或强判旧家族重复。10观察9限制及全对象进入三个表示并完全相等，170 pending在新批移除，157W01保留。旧169/170封存不修改；无源/图重读、新PNG、Java、制作或清单删除。\n')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',{**s,'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files)},ensure_ascii=False))
