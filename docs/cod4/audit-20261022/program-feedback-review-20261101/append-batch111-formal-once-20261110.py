"""Main's explicit111 single-use grant only. Marker permanently consumes execution.
No retries, rebases, rollback, old append/proof/validator execution or production work.
"""
from pathlib import Path
import json,hashlib,datetime,os
R=Path('/Users/a15356015027/Desktop/dynasty');B=R/'docs/cod4/audit-20261022';D=B/'program-feedback-review-20261101';F=B/'immune-feedback-research'
sha=lambda x:hashlib.sha256(x).hexdigest()
can=lambda x:sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(p):return json.loads(Path(p).read_text())
def actualpath(p):return (R/Path(p)).resolve()
def bind(p):
 p=actualpath(p);b=p.read_bytes();return {'path':str(p.relative_to(R)) if p.is_relative_to(R) else str(p),'sha256':sha(b),'bytes':len(b)}
def check(x):
 b=bind(x['path']);assert b['sha256']==x['sha256'] and b['bytes']==x['bytes'],x['path'];return b
def exclusive(p,o):
 with Path(p).open('x',encoding='utf-8') as w:
  json.dump(o,w,ensure_ascii=False,indent=2);w.write('\n');w.flush();os.fsync(w.fileno())
planpath=D/'batch-111-formal-append-plan-20261110.json';mrpath=B/'coordinator-program111-append-plan-review-20261110.json'
assert bind(planpath)['sha256']=='d5cd410ceea2b42f2d13943465270d8ad937498f24c2cf767a2d78bea00bd732'
assert bind(planpath)['bytes']==639765
assert bind(mrpath)['sha256']=='265c81d5fc2c31a5a6a1282ab452361963b98023426eb40b6e9f57536bb3796b' and bind(mrpath)['bytes']==57827
plan=load(planpath);mr=load(mrpath);entry=plan['entry'];group=plan['dedup_group'];marker=actualpath(plan['one_time_start_marker']);proof=actualpath(plan['proof_path'])
assert marker==D/'batch-111-formal-append-once-started-20261110.json' and proof==D/'batch-111-formal-ledger-delta-20261110.json'
assert not marker.exists() and not proof.exists(),'Marker/proof exists; permanently STOP. Do not rerun or rebase.'
assert mr['decision']=='EXACT_FROZEN_111_APPEND_PLAN_504_TO_505_REVIEWED_NOT_EXECUTED'
assert mr['reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34'
assert mr['plan']==bind(planpath) and mr['all142_current_input_bindings']==plan['all_current_input_bindings']
for k in ['planned_output_sha256','planned_output_byte_lengths','planned_entry_canonical_sha256','planned_group_canonical_sha256']:assert mr[k]==plan[k]
assert mr['all31_individual_author_responses_actually_read'] and mr['old504_fullobjects_order232groups_rawprefix_exact']
assert plan['baseline_formal_count']==504 and plan['baseline_dedup_group_count']==232
assert plan['expected_after_formal_count']==505 and plan['expected_after_dedup_group_count']==233
assert plan['allowed_progress_changes']=={'reviewed_effective_semantic_dedup':[504,505],'remaining':[496,495]}
assert plan['gate_must_stay_false'] and plan['allowed_formal_paths_now']==[] and plan['formal_paths_mutated']==[]
allowed=[F/n for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert set(map(actualpath,plan['allowed_formal_paths_after_later_explicit_authorization']))==set(allowed)
inputs=plan['all_current_input_bindings'];assert len(inputs)==len({actualpath(x['path']) for x in inputs})==142
verified=[check(x) for x in inputs];reviewbinding=check(bind(mrpath));scriptbinding=bind(Path(__file__))
context=load(actualpath(plan['current504_ecology50_context']['path']));author=load(actualpath(plan['actual_author_confirmation']['path']));candidate=load(actualpath(plan['proposal']['path']));whole=load(actualpath(plan['Main_receipt']['path']))
assert author['author_thread_id']=='01a16392-312e-72f2-a4dd-56e184f9cb02'
assert author['actual_author_ack_all19']==mr['all19finding_responses']==entry['actual_author_acknowledgment']
assert author['actual_author_ack_all12_limits']==mr['all12limit_responses']==entry['actual_author_limit_acknowledgment']
assert len(author['actual_author_ack_all19'])==19 and len(author['actual_author_ack_all12_limits'])==12
assert entry['author_observations']==candidate['observations']==whole['all_original22_observations_preserved'] and len(entry['author_observations'])==22
assert entry['author_limitations']==candidate['limitations']==whole['all_original14_limits_preserved'] and len(entry['author_limitations'])==14
assert entry['main_independent_findings']==whole['Main_findings'] and len(whole['Main_findings'])==19
assert entry['main_preappend_limits_verbatim']==whole['Main_limits'] and len(whole['Main_limits'])==12
assert entry['concrete_observation']=='\n'.join(['Author: '+x for x in candidate['observations']]+['Main: '+x for x in whole['Main_findings']])
assert entry['limitations']==['Author: '+x for x in candidate['limitations']]+['Main: '+x for x in whole['Main_limits']]
assert entry['source_refs']==candidate['source_refs']==whole['actual_Main_all22_source_descriptors_read']
assert entry['full_chain_observation']=={'author_verbatim':candidate['observations'],'Main_verbatim':whole['Main_findings']}
for k in ['complete_three_formal_judgments','complete_three_groups','complete_two_goat_migration_saved_judgments','complete_Main_goat_horn_whole_owner_correction','Guardian_prior_saved_judgment_reused0','Milk_Main22_findings_reused0','Milk_Main11_limits_reused0','Axolotl_Main21_12_saved_judgment_reused0','Sonic_author20_12_saved_judgment_reused0']:assert entry[k]==whole[k]==author[k]==context['complete_saved_comparisons_reused0'][k],k
assert entry['complete_prescreen']==candidate['dedup']['complete_prescreen']
assert group['retained_Main_findings']==whole['Main_findings'] and group['retained_Main_limits']==whole['Main_limits']
assert group['retained_original_author_observations']==candidate['observations'] and group['retained_original_author_limits']==candidate['limitations']
assert entry['research_credit']==1 and entry['id']==entry['semantic_dedup_key']==group['credited_chain']==whole['whole_semantic_key']
assert not entry['native_acceptance'] and not entry['global_uniqueness_claimed']
protected=mr['protected_files_unchanged_sha256'];assert protected==whole['protected_files_unchanged'] and len(protected)==8
for p,h in protected.items():assert bind(p)['sha256']==h,p
assert not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()
ecop=actualpath(context['current_ecology_master']['path']);check(context['current_ecology_master']);eco=load(ecop)
assert eco['independently_accepted']==len(eco['accepted'])==50 and eco['shortfall']==950 and not eco['gate_met']
assert {x['id']:can(x) for x in eco['accepted']}==context['all50_complete_accepted_master_object_canonical_hashes']
ecoreceipts=context['all50_actual_receipt_bindings'];assert len(ecoreceipts)==len({actualpath(x['path']) for x in ecoreceipts})==50
for x in ecoreceipts:check(x)
raw={p.name:p.read_bytes() for p in allowed};old=load(F/'reviewed.json');oldg=load(F/'semantic-dedup.json');oldp=load(F/'progress.json')
assert len(old)==504 and len(oldg['groups'])==232 and oldp['reviewed_effective_semantic_dedup']==504 and oldp['remaining']==496 and not oldp['formal_design_gate_satisfied']
assert {x['id']:can(x) for x in old}==plan['old504_complete_object_canonical_hashes']
assert [x['id'] for x in old]==plan['old504_complete_object_id_order']
assert [can(x) for x in oldg['groups']]==plan['old_dedup_group_canonical_hashes']
assert entry['id'] not in {x['id'] for x in old}
tails={'reviewed.json':b'\n]\n','semantic-dedup.json':b'\n  ]\n}\n'}
encoding=plan['exact_future_encoding']
for name,key in [('reviewed.json','old_ledger_prefix'),('semantic-dedup.json','old_dedup_prefix')]:
 assert raw[name].endswith(tails[name]);prefix=raw[name][:-len(tails[name])];assert sha(prefix)==encoding[key+'_sha256'] and len(prefix)==encoding[key+'_bytes']
def extend(name,obj,spaces):return raw[name][:-len(tails[name])]+b',\n'+b'\n'.join(b' '*spaces+x for x in json.dumps(obj,ensure_ascii=False,indent=2).encode().split(b'\n'))+tails[name]
outputs={'reviewed.json':extend('reviewed.json',entry,2),'semantic-dedup.json':extend('semantic-dedup.json',group,4)};pb=raw['progress.json']
for before,after in [(b'"reviewed_effective_semantic_dedup": 504',b'"reviewed_effective_semantic_dedup": 505'),(b'"remaining": 496',b'"remaining": 495')]:assert pb.count(before)==1;pb=pb.replace(before,after)
outputs['progress.json']=pb
assert {k:sha(v) for k,v in outputs.items()}==plan['planned_output_sha256']
assert {k:len(v) for k,v in outputs.items()}==plan['planned_output_byte_lengths']
assert can(entry)==plan['planned_entry_canonical_sha256'] and can(group)==plan['planned_group_canonical_sha256']
new=json.loads(outputs['reviewed.json']);newg=json.loads(outputs['semantic-dedup.json']);newp=json.loads(pb)
assert len(new)==505 and new[:-1]==old and new[-1]==entry
assert len(newg['groups'])==233 and newg['groups'][:-1]==oldg['groups'] and newg['groups'][-1]==group
assert {k:v for k,v in newg.items() if k!='groups'}=={k:v for k,v in oldg.items() if k!='groups'}
assert {k:(oldp[k],newp[k]) for k in oldp if oldp[k]!=newp[k]}=={'reviewed_effective_semantic_dedup':(504,505),'remaining':(496,495)}
assert not newp['formal_design_gate_satisfied'] and newp['target']==1000
formalpaths=set(allowed);nonformal=[x for x in inputs if actualpath(x['path']) not in formalpaths]+[reviewbinding]
assert len(nonformal)==140
# Last complete fresh guard before permanently consuming the new111 marker.
for x in inputs:check(x)
check(reviewbinding);check(scriptbinding)
for x in ecoreceipts:check(x)
for p,h in protected.items():assert bind(p)['sha256']==h
assert not marker.exists() and not proof.exists()
exclusive(marker,dict(schema_version=1,started_utc=now(),batch=111,status='PERMANENTLY_CONSUMED_SINGLE111_ATTEMPT_NO_RETRY_EVEN_ON_LATER_FAILURE',author_thread_id='01a16392-312e-72f2-a4dd-56e184f9cb02',grant_source='Main explicit delegation of111 frozenplan once only',plan=bind(planpath),Main_plan_review=reviewbinding,script=scriptbinding,allowed_formal_paths=[str(x.relative_to(R)) for x in allowed],baseline=plan['baseline'],expected_output_sha256=plan['planned_output_sha256'],failure_policy='STOP_AND_REPORT_NO_RETRY_REBASE_ROLLBACK_OR_OLD_SCRIPT_REPLAY'))
markerbinding=bind(marker)
# Any failure from this point leaves marker consumed forever, even if no file changed.
for x in inputs:check(x)
check(reviewbinding);check(scriptbinding)
for p in allowed:
 assert p.read_bytes()==raw[p.name],str(p)
 with p.open('r+b') as w:w.seek(0);w.write(outputs[p.name]);w.truncate();w.flush();os.fsync(w.fileno())
assert all(p.read_bytes()==outputs[p.name] for p in allowed)
post=load(F/'reviewed.json');postg=load(F/'semantic-dedup.json');postp=load(F/'progress.json')
assert post[:-1]==old and post[-1]==entry and len(post)==505
assert postg['groups'][:-1]==oldg['groups'] and postg['groups'][-1]==group and len(postg['groups'])==233
assert not postp['formal_design_gate_satisfied']
for x in nonformal:check(x)
for x in ecoreceipts:check(x)
for p,h in protected.items():assert bind(p)['sha256']==h
check(markerbinding);check(scriptbinding)
result=dict(schema_version=1,completed_utc=now(),batch=111,status='SINGLE111_APPEND_COMPLETED_EXACTLY_AS_FROZEN_PENDING_MAIN_DELTA_REVIEW',author_thread_id='01a16392-312e-72f2-a4dd-56e184f9cb02',explicit_Main_plan_grant_receipt=reviewbinding,plan=bind(planpath),actual_author_confirmation=plan['actual_author_confirmation'],current504_ecology50_context=plan['current504_ecology50_context'],script=scriptbinding,permanently_consumed_marker=markerbinding,invocation='First and only script invocation; all guards passed. No source proof/validator/old append/eco aggregation executed.',all143_prewrite_current_input_bindings_verified=verified+[reviewbinding],nonformal_inputs_unchanged_after=nonformal,all50_actual_ecology_receipts_before_and_after=ecoreceipts,ecology_master_unchanged=bind(ecop),old504_complete_object_hashes_preserved=plan['old504_complete_object_canonical_hashes'],old504_id_order_preserved=plan['old504_complete_object_id_order'],old232_complete_group_hashes_preserved=plan['old_dedup_group_canonical_hashes'],old_raw_prefixes_preserved=encoding,old_complete_objects_equal_prefix=True,old_complete_groups_equal_prefix=True,exact_appended_entry=entry,exact_appended_group=group,planned_entry_canonical_sha256=can(entry),planned_group_canonical_sha256=can(group),formal_before=plan['baseline'],formal_after={p.name:bind(p) for p in allowed},exact_planned_sha256_matched=True,exact_planned_bytes_matched=True,formal_count_before_after=[504,505],remaining_before_after=[496,495],groups_before_after=[232,233],progress_only_two_fields_changed=plan['allowed_progress_changes'],protected8_before_after_sha256=protected,formal_paths_mutated=[str(p.relative_to(R)) for p in allowed],gate_met=False,native_acceptance=False,new_migration_credit=0,new_ecology_credit=0,source_proofs_rerun=False,old_append_scripts_executed=False,production_changes=0,game_starts=0,background_changes=0,Main_state_changes=0,checklist_deletions=0,network_requests=0,active_hours_claimed=None,all_tasks_complete=False)
exclusive(proof,result)
print(json.dumps(dict(script=scriptbinding,marker=markerbinding,proof=bind(proof),outputs=result['formal_after'],count=505,gap=495,groups=233,ecology=50,gate_met=False),ensure_ascii=False))
