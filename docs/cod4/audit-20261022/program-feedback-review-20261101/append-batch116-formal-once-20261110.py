"""Execute Main's exact116 single-use grant. Never retry/rebase after invocation.
Exclusive marker permanently consumes the attempt before the three formal writes.
No production, source-proof, old script/validator or ecological aggregation execution.
"""
from pathlib import Path
import json,hashlib,datetime,os
R=Path('/Users/a15356015027/Desktop/dynasty');B=R/'docs/cod4/audit-20261022';D=B/'program-feedback-review-20261101';F=B/'immune-feedback-research'
sha=lambda b:hashlib.sha256(b).hexdigest()
can=lambda o:sha(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def actual(p):return (R/Path(p)).resolve()
def load(p):return json.loads(Path(p).read_text())
def bind(p):
 p=actual(p);b=p.read_bytes();return dict(path=str(p.relative_to(R)) if p.is_relative_to(R) else str(p),sha256=sha(b),bytes=len(b))
def check(x):
 b=bind(x['path']);assert b['sha256']==x['sha256'] and b['bytes']==x['bytes'],x['path'];return b
def exclusive(p,o):
 with Path(p).open('x',encoding='utf-8') as w:
  json.dump(o,w,ensure_ascii=False,indent=2);w.write('\n');w.flush();os.fsync(w.fileno())
pp=D/'batch-116-formal-append-plan-20261110.json';rp=B/'coordinator-program116-append-plan-review-20261110.json'
assert bind(pp)['sha256']=='b4e5b07d4a06aa6e8987c4667f8ed41a0d58b8d89cb9ba835b15c66416f15577' and bind(pp)['bytes']==511978
assert bind(rp)['sha256']=='57bad8720566318b8708549c3d5c5476d4c338a3c0c95a11cdd87e24b6cefa9a' and bind(rp)['bytes']==79332
plan=load(pp);review=load(rp);e=plan['entry'];g=plan['dedup_group'];marker=actual(plan['one_time_start_marker']);proof=actual(plan['proof_path'])
assert Path(__file__).resolve()==D/'append-batch116-formal-once-20261110.py'
assert marker==D/'batch-116-formal-append-once-started-20261110.json' and proof==D/'batch-116-formal-ledger-delta-20261110.json'
assert not marker.exists() and not proof.exists(),'STOP: marker/proof already exists; no retry/rebase/replay.'
assert review['decision']=='EXACT_FROZEN_116_APPEND_PLAN_505_TO_506_REVIEWED_NOT_EXECUTED'
assert review['reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34' and review['plan']==bind(pp)
assert review['all169_current_input_bindings']==plan['all_current_input_bindings']
assert review['baseline']==plan['baseline'] and review['old505_fullobjects_order233groups_rawprefix_exact']
assert review['all39_individual_author_responses_actually_read'] and review['all_original24_16_Main22_17_and_complete_comparators_preserved']
assert review['current_count']==505 and review['conditional_next_count']==506 and review['conditional_next_gap']==494 and review['conditional_next_groups']==234
for k in ['planned_output_sha256','planned_output_byte_lengths','planned_entry_canonical_sha256','planned_group_canonical_sha256']:assert review[k]==plan[k]
assert plan['baseline_formal_count']==505 and plan['baseline_dedup_group_count']==233
assert plan['expected_after_formal_count']==506 and plan['expected_after_dedup_group_count']==234
assert plan['allowed_progress_changes']=={'reviewed_effective_semantic_dedup':[505,506],'remaining':[495,494]}
assert plan['gate_must_stay_false'] and plan['formal_paths_mutated']==[] and plan['allowed_formal_paths_now']==[]
allowed=[F/n for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert set(map(actual,plan['allowed_formal_paths_after_later_explicit_authorization']))==set(allowed)
inputs=plan['all_current_input_bindings'];assert len(inputs)==len({actual(x['path']) for x in inputs})==169
verified=[check(x) for x in inputs];reviewbinding=check(bind(rp));scriptbinding=bind(Path(__file__))
for x in plan['baseline'].values():check(x)
for k in ['Main_receipt','proposal','worker_validation_reused_not_rerun','actual_author_confirmation','current505_ecology50_context']:check(plan[k])
a=load(actual(plan['actual_author_confirmation']['path']));c=load(actual(plan['proposal']['path']));m=load(actual(plan['Main_receipt']['path']));ctx=load(actual(plan['current505_ecology50_context']['path']))
assert a['author_thread_id']=='01a16392-312e-72f2-a4dd-56e184f9cb02'
assert a['actual_author_ack_all22']==review['all22finding_responses']==e['actual_author_acknowledgment'] and len(a['actual_author_ack_all22'])==22
assert a['actual_author_ack_all17_limits']==review['all17limit_responses']==e['actual_author_limit_acknowledgment'] and len(a['actual_author_ack_all17_limits'])==17
assert [x['Main_finding_verbatim'] for x in a['actual_author_ack_all22']]==m['Main_findings']
assert [x['Main_limit_verbatim'] for x in a['actual_author_ack_all17_limits']]==m['Main_limits']
assert all(x['confirmed'] and x['actual_author_response'] for x in a['actual_author_ack_all22']+a['actual_author_ack_all17_limits'])
assert e['author_observations']==c['observations']==m['all_original24_observations_preserved']==a['original24_observations_verbatim'] and len(c['observations'])==24
assert e['author_limitations']==c['limitations']==m['all_original16_limits_preserved']==a['original16_limits_verbatim'] and len(c['limitations'])==16
assert e['main_independent_findings']==m['Main_findings']==a['Main22_findings_verbatim'] and len(m['Main_findings'])==22
assert e['main_preappend_limits_verbatim']==m['Main_limits']==a['Main17_limits_verbatim'] and len(m['Main_limits'])==17
assert e['full_chain_observation']==dict(author_verbatim=c['observations'],Main_verbatim=m['Main_findings'])
assert e['concrete_observation']=='\n'.join(['Author: '+x for x in c['observations']]+['Main: '+x for x in m['Main_findings']])
assert e['limitations']==['Author: '+x for x in c['limitations']]+['Main: '+x for x in m['Main_limits']]
assert e['source_refs']==c['source_refs']==m['actual_Main_all26_source_descriptors_read']
assert e['complete_prescreen']==c['dedup']['complete_prescreen']
for k in ['complete_five_formal_saved_judgments','complete_five_groups','complete_five_sweep_saved_judgments','complete_Brainiac_saved_whole','complete_additional_held_target_saved_judgment','complete_nine_additional_Main_fourfield_comparators','complete113_pending_boundary_reused0']:
 assert e[k]==m[k]==a[k]==ctx['complete_saved_owners_reused0'][k],k
ngk='complete_nine_additional_related_groups_actually_read'
assert len(e[ngk])==9 and e[ngk]==a[ngk]==ctx['complete_saved_owners_reused0'][ngk]==review['all_nine_complete_extra_group_objects_preserved']
assert g['retained_Main_findings']==m['Main_findings'] and g['retained_Main_limits']==m['Main_limits']
assert g['retained_original_author_observations']==c['observations'] and g['retained_original_author_limits']==c['limitations']
assert e['id']==e['semantic_dedup_key']==g['credited_chain']==m['whole_semantic_key']
assert e['research_credit']==1 and not e['native_acceptance'] and not e['global_uniqueness_claimed']
pending113=load(D/'immune-reference-batch-113.json');boundary=e['complete113_pending_boundary_reused0']
assert boundary['original25']==pending113['observations'] and boundary['original16']==pending113['limitations']
assert len(boundary['original25'])==25 and len(boundary['original16'])==16
protected=review['protected_files_unchanged_sha256'];assert protected==m['protected_files_unchanged']==ctx['protected_files_unchanged'] and len(protected)==8
for p,h in protected.items():assert bind(p)['sha256']==h,p
assert not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()
ecop=actual(ctx['current_ecology_master']['path']);check(ctx['current_ecology_master']);eco=load(ecop)
assert eco['independently_accepted']==len(eco['accepted'])==50 and eco['shortfall']==950 and not eco['gate_met']
assert {x['id']:can(x) for x in eco['accepted']}==ctx['all50_complete_accepted_master_object_canonical_hashes']
ecoreceipts=ctx['all50_actual_ecology_receipt_bindings'];assert len(ecoreceipts)==len({actual(x['path']) for x in ecoreceipts})==50
for x in ecoreceipts:check(x)
raw={p.name:p.read_bytes() for p in allowed};old=load(F/'reviewed.json');oldg=load(F/'semantic-dedup.json');oldp=load(F/'progress.json')
assert len(old)==505 and len(oldg['groups'])==233 and oldp['reviewed_effective_semantic_dedup']==505 and oldp['remaining']==495 and not oldp['formal_design_gate_satisfied']
assert {x['id']:can(x) for x in old}==plan['old505_complete_object_canonical_hashes']
assert [x['id'] for x in old]==plan['old505_complete_object_id_order']
assert [can(x) for x in oldg['groups']]==plan['old_dedup_group_canonical_hashes']
assert e['id'] not in {x['id'] for x in old}
tails={'reviewed.json':b'\n]\n','semantic-dedup.json':b'\n  ]\n}\n'};encoding=plan['exact_future_encoding']
for name,key in [('reviewed.json','old_ledger_prefix'),('semantic-dedup.json','old_dedup_prefix')]:
 assert raw[name].endswith(tails[name]);prefix=raw[name][:-len(tails[name])];assert sha(prefix)==encoding[key+'_sha256'] and len(prefix)==encoding[key+'_bytes']
def extend(name,obj,spaces):return raw[name][:-len(tails[name])]+b',\n'+b'\n'.join(b' '*spaces+x for x in json.dumps(obj,ensure_ascii=False,indent=2).encode().split(b'\n'))+tails[name]
outputs={'reviewed.json':extend('reviewed.json',e,2),'semantic-dedup.json':extend('semantic-dedup.json',g,4)};pb=raw['progress.json']
for before,after in [(b'"reviewed_effective_semantic_dedup": 505',b'"reviewed_effective_semantic_dedup": 506'),(b'"remaining": 495',b'"remaining": 494')]:assert pb.count(before)==1;pb=pb.replace(before,after)
outputs['progress.json']=pb
assert {k:sha(v) for k,v in outputs.items()}==plan['planned_output_sha256']
assert {k:len(v) for k,v in outputs.items()}==plan['planned_output_byte_lengths']
assert can(e)==plan['planned_entry_canonical_sha256'] and can(g)==plan['planned_group_canonical_sha256']
new=json.loads(outputs['reviewed.json']);newg=json.loads(outputs['semantic-dedup.json']);newp=json.loads(pb)
assert len(new)==506 and new[:-1]==old and new[-1]==e
assert len(newg['groups'])==234 and newg['groups'][:-1]==oldg['groups'] and newg['groups'][-1]==g
assert {k:v for k,v in newg.items() if k!='groups'}=={k:v for k,v in oldg.items() if k!='groups'}
assert {k:(oldp[k],newp[k]) for k in oldp if oldp[k]!=newp[k]}=={'reviewed_effective_semantic_dedup':(505,506),'remaining':(495,494)}
assert not newp['formal_design_gate_satisfied'] and newp['target']==1000
nonformal=[x for x in inputs if actual(x['path']) not in set(allowed)]+[reviewbinding];assert len(nonformal)==167
# Last full current-input guard before the permanently consumed marker.
for x in inputs:check(x)
check(reviewbinding);check(scriptbinding)
for x in ecoreceipts:check(x)
for p,h in protected.items():assert bind(p)['sha256']==h
assert not marker.exists() and not proof.exists()
exclusive(marker,dict(schema_version=1,started_utc=now(),batch=116,status='PERMANENTLY_CONSUMED_SINGLE116_ATTEMPT_NO_RETRY_EVEN_IF_LATER_FAILURE',author_thread_id='01a16392-312e-72f2-a4dd-56e184f9cb02',grant_source='Main explicit exact116 single-use execution delegation',plan=bind(pp),Main_plan_review=reviewbinding,script=scriptbinding,allowed_formal_paths=[str(x.relative_to(R)) for x in allowed],baseline=plan['baseline'],expected_output_sha256=plan['planned_output_sha256'],failure_policy='STOP_REPORT_NO_RETRY_REBASE_ROLLBACK_OR_OLD_SCRIPT_PROOF_REPLAY'))
markerbinding=bind(marker)
# Every failure after marker leaves the attempt permanently consumed.
for x in inputs:check(x)
check(reviewbinding);check(scriptbinding)
for p in allowed:
 assert p.read_bytes()==raw[p.name],str(p)
 with p.open('r+b') as w:w.seek(0);w.write(outputs[p.name]);w.truncate();w.flush();os.fsync(w.fileno())
assert all(p.read_bytes()==outputs[p.name] for p in allowed)
post=load(F/'reviewed.json');postg=load(F/'semantic-dedup.json');postp=load(F/'progress.json')
assert post[:-1]==old and post[-1]==e and len(post)==506
assert postg['groups'][:-1]==oldg['groups'] and postg['groups'][-1]==g and len(postg['groups'])==234
assert not postp['formal_design_gate_satisfied']
for x in nonformal:check(x)
for x in ecoreceipts:check(x)
for p,h in protected.items():assert bind(p)['sha256']==h
check(markerbinding);check(scriptbinding)
result=dict(schema_version=1,completed_utc=now(),batch=116,status='EXACT_SINGLE116_APPEND_COMPLETED_PENDING_MAIN_ACTUAL_DELTA_REVIEW',author_thread_id='01a16392-312e-72f2-a4dd-56e184f9cb02',explicit_Main_plan_grant_receipt=reviewbinding,plan=bind(pp),actual_author_confirmation=plan['actual_author_confirmation'],current505_ecology50_context=plan['current505_ecology50_context'],script=scriptbinding,permanently_consumed_marker=markerbinding,invocation='First and only script invocation; guards passed; no sourceproof/validator/oldappend/ecoaggregate execution.',all170_prewrite_current_input_bindings_verified=verified+[reviewbinding],nonformal_inputs_unchanged_after=nonformal,all50_actual_ecology_receipts_before_and_after=ecoreceipts,ecology_master_unchanged=bind(ecop),old505_complete_object_hashes_preserved=plan['old505_complete_object_canonical_hashes'],old505_id_order_preserved=plan['old505_complete_object_id_order'],old233_complete_group_hashes_preserved=plan['old_dedup_group_canonical_hashes'],old_raw_prefixes_preserved=encoding,old_complete_objects_equal_prefix=True,old_complete_groups_equal_prefix=True,exact_appended_entry=e,exact_appended_group=g,planned_entry_canonical_sha256=can(e),planned_group_canonical_sha256=can(g),formal_before=plan['baseline'],formal_after={p.name:bind(p) for p in allowed},exact_planned_sha256_matched=True,exact_planned_bytes_matched=True,formal_count_before_after=[505,506],remaining_before_after=[495,494],groups_before_after=[233,234],progress_only_two_fields_changed=plan['allowed_progress_changes'],protected8_before_after_sha256=protected,formal_paths_mutated=[str(p.relative_to(R)) for p in allowed],gate_met=False,native_acceptance=False,new_migration_credit=0,new_ecology_credit=0,source_proofs_rerun=False,old_append_scripts_executed=False,production_changes=0,game_starts=0,background_changes=0,Main_state_changes=0,checklist_deletions=0,network_requests=0,active_hours_claimed=None,all_tasks_complete=False)
exclusive(proof,result)
print(json.dumps(dict(script=scriptbinding,marker=markerbinding,proof=bind(proof),outputs=result['formal_after'],count=506,gap=494,groups=234,ecology=50,gate_met=False),ensure_ascii=False))
