"""Apply only frozen102 after Main's explicit single-use grant. NEVER retry after marker."""
from pathlib import Path
import json, hashlib, datetime, copy, os
ROOT=Path('/Users/a15356015027/Desktop/dynasty'); assert Path.cwd().resolve()==ROOT
BASE=Path('docs/cod4/audit-20261022'); OUT=BASE/'program-feedback-review-20261101'
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda o:json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
bind=lambda p:{'path':str(p),'sha256':sha(p.read_bytes())}
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
planpath=OUT/'batch-102-formal-append-plan-20261110.json'
reviewpath=BASE/'coordinator-program102-append-plan-review-20261110.json'
protected={str(planpath):'99f0c532f7b097e9ab8ae0212bf7256476fe2110e0a8c9ac9b7f72e3c0ce22f1',str(reviewpath):'af75480a31657f76fea7c70994ea626eb238de9d7a1567b339939e63de1d94b9'}
def freeze(binding):
 p=Path(binding['path']); raw=p.read_bytes(); assert sha(raw)==binding['sha256'], 'Input drift: STOP'
 if 'bytes' in binding:assert len(raw)==binding['bytes']
 protected[str(p)]=binding['sha256']
def recheck():
 for p,h in protected.items():assert sha(Path(p).read_bytes())==h, 'Immutable input drift: STOP'
recheck();plan=json.loads(planpath.read_bytes());review=json.loads(reviewpath.read_bytes())
assert review['decision']=='FROZEN_ONE_WHOLE_APPEND_PLAN_REVIEWED_498_TO_499_EXECUTION_NOT_PERFORMED'
assert review['reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34'
assert review['plan']['path']==str(planpath) and review['plan']['sha256']==protected[str(planpath)]
assert review['baseline']==plan['baseline'] and review['planned_output_sha256']==plan['planned_output_sha256']
assert [review[k] for k in ['formal_count_current','formal_count_planned','remaining_planned','dedup_groups_planned']]==[498,499,501,227]
assert review['formal_intake_applied_by_this_review']==0 and review['marker_and_proof_absent'] is True
for k in ['old498_complete_objects_order_and226groups_exact','old_raw_prefixes_exact','entry_group_full_canonical_exact','author16observations9limits_Main16findings10limits_all_verbatim','seven_complete_judgments_six_groups_seven_migration_judgments_and_current101_47_contexts_exact','progress_only_two_fields_gate_false']:assert review[k] is True
for k in ['Main_receipt','proposal','worker_validation_reused_not_rerun','actual_author_confirmation','current498_complete_handoff']:freeze(plan[k])
assert review['actual_original_author_confirmation']['path']==plan['actual_author_confirmation']['path']
assert review['actual_original_author_confirmation']['sha256']==plan['actual_author_confirmation']['sha256']=='612e5e514b415842cd14e58f1d78e0a1f68c63f168c0e6da4b5365811ae175a5'
assert review['Main_whole_review']==plan['Main_receipt']
paths={n:Path(v['path']) for n,v in plan['baseline'].items()}
assert set(paths)=={'reviewed.json','semantic-dedup.json','progress.json'}
assert {str(p) for p in paths.values()}==set(plan['allowed_formal_paths_after_later_explicit_authorization'])
assert all(p==BASE/'immune-feedback-research'/n and not p.is_symlink() for n,p in paths.items())
# Main's current validated bindings are distinct from explicitly historical cross-area references.
for binding in review['verified_file_bindings']:
 p=Path(binding['path']);raw0=p.read_bytes();assert sha(raw0)==binding['sha256'] and len(raw0)==binding['bytes']
 if p not in paths.values():freeze(binding)
for path,digest in review['protected_files_unchanged_sha256'].items():freeze({'path':path,'sha256':digest})
for name,digest in [('immune-reference-batch-103.json','4a53251c1970a8434e209720cd04e32294c4b275592dd6f8138d680a98c47720'),('batch-103-worker-validation-20261110.json','9ffbc56bc8b62f123f371a658bc0ab6f7538437503d4e7412fdcfafcbc6fd87f')]:freeze({'path':str(OUT/name),'sha256':digest})
author=json.loads(Path(plan['actual_author_confirmation']['path']).read_bytes())
main=json.loads(Path(plan['Main_receipt']['path']).read_bytes())
proposal=json.loads(Path(plan['proposal']['path']).read_bytes())
handoff=json.loads(Path(plan['current498_complete_handoff']['path']).read_bytes())
assert author['author_thread_id']==main['author_thread_id']=='01a16392-312e-72f2-a4dd-56e184f9cb02'
assert author['Main_thread_id']==main['reviewer_thread_id']==review['reviewer_thread_id']
assert author['baseline']==plan['baseline'] and author['formal_intake_applied_by_this_confirmation'] is False
entry=plan['entry'];group=plan['dedup_group']
assert entry['author_observations']==author['author_observations_all16_verbatim']==proposal['observations']==main['author_observations_all16_retained']==handoff['author_observations_all16_verbatim']
assert entry['author_limitations']==author['author_limits_all9_verbatim']==proposal['limitations']==main['author_limits_all9_retained']==handoff['author_limits_all9_verbatim']
assert entry['main_independent_findings']==author['Main_findings_all16_verbatim']==main['independent_findings']==group['retained_Main_findings']
assert entry['main_preappend_limits_verbatim']==author['Main_limits_all10_verbatim']==main['mandatory_limits']==group['retained_Main_limits']
assert [len(entry[k]) for k in ['author_observations','author_limitations','main_independent_findings','main_preappend_limits_verbatim']]==[16,9,16,10]
assert entry['whole_mechanism_comparisons']==main['seven_complete_selected_semantic_judgments_read']==author['complete_prior_semantic_judgments_verbatim']
assert entry['complete_group_rationales']==main['six_complete_group_rationales_read']==author['complete_group_rationales_verbatim']
assert entry['complete_migration_judgments']==main['seven_complete_saved_migration_judgments_read']==author['complete_migration_judgments_verbatim']
assert [len(entry[k]) for k in ['whole_mechanism_comparisons','complete_group_rationales','complete_migration_judgments']]==[7,6,7]
assert entry['cross_area_prescreen']==proposal['dedup'], 'Historical proposal context must stay verbatim'
assert entry['current101_delta_context']==plan['current101_delta_context']==author['current101_delta_context']
assert entry['current47_ecology_context']==plan['current47_ecology_context']==author['current47_ecology_context']
c101=plan['current101_delta_context'];c47=plan['current47_ecology_context']
assert c101['current101_complete_group']==main['current101_group']==handoff['new101_group']
assert c101['current101_complete_substantive_judgment_verbatim']==main['current101_Main_own_judgment_reused_without_source_reread']
assert c47['current47_master']==main['ecology_current47_identity_only']
assert c47['addedEA48_complete_saved_scope_verbatim']==main['ecology_addedEA48_Main_own_judgment_reused_no_chain_reread']
for binding in [c101['Main_actual_delta_closure'],c101['current498_complete_handoff'],c47['current47_master'],c47['addedEA48_complete_saved_scope_verbatim']['receipt']]:freeze(binding)
for binding in c47['all47_receipt_content_screen_bindings']:freeze(binding)
assert len(c47['all47_receipt_content_screen_bindings'])==47
assert sha(canonical(entry))==plan['planned_entry_canonical_sha256'] and sha(canonical(group))==plan['planned_group_canonical_sha256']
assert plan['baseline_formal_count']==498 and plan['baseline_dedup_group_count']==226
assert plan['expected_after_formal_count']==499 and plan['expected_after_dedup_group_count']==227
assert plan['allowed_progress_changes']=={'reviewed_effective_semantic_dedup':[498,499],'remaining':[502,501]} and plan['gate_must_stay_false'] is True
marker=Path(plan['one_time_start_marker']);proofpath=Path(plan['proof_path'])
assert marker==OUT/'batch-102-formal-append-once-started-20261110.json' and proofpath==OUT/'batch-102-formal-ledger-delta-20261110.json'
assert not marker.exists() and not proofpath.exists(), 'Consumed marker/proof: STOP, NEVER retry'
oldraw={n:p.read_bytes() for n,p in paths.items()}
assert {n:sha(v) for n,v in oldraw.items()}=={n:v['sha256'] for n,v in plan['baseline'].items()}, 'Baseline drift: STOP, never rebase'
oldrows,olddedup,oldprogress=[json.loads(oldraw[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert len(oldrows)==498 and len(olddedup['groups'])==226
assert oldprogress['reviewed_effective_semantic_dedup']==498 and oldprogress['remaining']==502 and oldprogress['formal_design_gate_satisfied'] is False
rowhashes={r['id']:sha(canonical(r)) for r in oldrows};roworder=[r['id'] for r in oldrows];grouphashes=[sha(canonical(g)) for g in olddedup['groups']]
assert len(rowhashes)==498 and rowhashes==plan['old498_complete_object_canonical_hashes']==author['old498_complete_object_canonical_hashes']
assert roworder==plan['old498_complete_object_id_order']==author['old498_complete_object_id_order']
assert grouphashes==plan['old_dedup_group_canonical_hashes']==author['old_dedup_group_canonical_hashes']
assert rowhashes[c101['current101_formal_id']]==c101['current101_full_object_canonical_sha256']
wrapper=c101['current101_complete_group'];assert wrapper['complete_group'] in olddedup['groups'] and sha(canonical(wrapper['complete_group']))==wrapper['full_object_canonical_sha256']
key=entry['id'];assert key==entry['semantic_dedup_key']==proposal['semantic_dedup_key']==main['semantic_dedup_key']==group['credited_chain']
assert not any(key in [r.get('id'),r.get('semantic_dedup_key')] for r in oldrows)
assert entry['research_credit']==1 and entry['native_acceptance'] is False and entry['global_uniqueness_claimed'] is False
indent=lambda o,n:'\n'.join(' '*n+l for l in json.dumps(o,ensure_ascii=False,indent=2).splitlines()).encode()
rtail=b'\n]\n';gtail=b'\n  ]\n}\n'
assert oldraw['reviewed.json'].endswith(rtail) and oldraw['semantic-dedup.json'].endswith(gtail)
rprefix=oldraw['reviewed.json'][:-len(rtail)];gprefix=oldraw['semantic-dedup.json'][:-len(gtail)]
encoding=plan['exact_future_encoding'];assert sha(rprefix)==encoding['old_ledger_prefix_sha256'] and len(rprefix)==encoding['old_ledger_prefix_bytes']
assert sha(gprefix)==encoding['old_dedup_prefix_sha256'] and len(gprefix)==encoding['old_dedup_prefix_bytes']
newraw={'reviewed.json':rprefix+b',\n'+indent(entry,2)+rtail,'semantic-dedup.json':gprefix+b',\n'+indent(group,4)+gtail,'progress.json':oldraw['progress.json']}
for old,new in [(b'"reviewed_effective_semantic_dedup": 498',b'"reviewed_effective_semantic_dedup": 499'),(b'"remaining": 502',b'"remaining": 501')]:
 assert newraw['progress.json'].count(old)==1;newraw['progress.json']=newraw['progress.json'].replace(old,new)
assert {n:sha(v) for n,v in newraw.items()}==plan['planned_output_sha256']==review['planned_output_sha256']
assert {n:len(v) for n,v in newraw.items()}==plan['planned_output_byte_lengths']
nr,nd,np=[json.loads(newraw[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert len(nr)==499 and nr[:-1]==oldrows and nr[-1]==entry
assert len(nd['groups'])==227 and nd['groups'][:-1]==olddedup['groups'] and nd['groups'][-1]==group
reverse=copy.deepcopy(nd);reverse['groups'].pop();assert reverse==olddedup
reverse=copy.deepcopy(np);reverse.update(reviewed_effective_semantic_dedup=498,remaining=502);assert reverse==oldprogress and np['formal_design_gate_satisfied'] is False
assert newraw['reviewed.json'][:len(rprefix)]+rtail==oldraw['reviewed.json']
assert newraw['semantic-dedup.json'][:len(gprefix)]+gtail==oldraw['semantic-dedup.json']
script=Path(__file__);freeze(bind(script));recheck()
for n,p in paths.items():assert p.read_bytes()==oldraw[n]
assert not marker.exists() and not proofpath.exists()
markerdata={'schema_version':1,'created_utc':now(),'batch':102,'status':'exclusive_one_time_start_never_retry_after_marker','plan':bind(planpath),'Main_plan_review':bind(reviewpath),'script':bind(script),'explicit_authorization':'Main exactly once original frozen99f0c532 plan498to499/gap501/227groups; three writes only. Drift or interruption stops for audit; no rebase/retry/rollback/oldscript replay.','before':plan['baseline'],'expected_after':plan['planned_output_sha256']}
with marker.open('x') as f:
 json.dump(markerdata,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
# Exactly one write per authorized formal path; any interruption leaves marker permanently consumed.
written=[]
for n,p in paths.items():
 recheck()
 for n0,p0 in paths.items():assert p0.read_bytes()==(newraw[n0] if n0 in written else oldraw[n0])
 with p.open('wb') as f:
  assert f.write(newraw[n])==len(newraw[n]);f.flush();os.fsync(f.fileno())
 written.append(n);assert p.read_bytes()==newraw[n]
actual={n:p.read_bytes() for n,p in paths.items()};assert actual==newraw
ar,ad,ap=[json.loads(actual[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert ar[:-1]==oldrows and ad['groups'][:-1]==olddedup['groups']
assert {r['id']:sha(canonical(r)) for r in ar[:-1]}==rowhashes and [r['id'] for r in ar[:-1]]==roworder
assert [sha(canonical(g)) for g in ad['groups'][:-1]]==grouphashes
recheck()
proof={'schema_version':1,'created_utc':now(),'status':'actual_original_author_one_time_formal499_append_applied_exact_frozen_plan','batch':102,'plan':bind(planpath),'Main_plan_review':bind(reviewpath),'Main_receipt':plan['Main_receipt'],'actual_author_confirmation':plan['actual_author_confirmation'],'source_proposal_unchanged':plan['proposal'],'script':bind(script),'one_time_start_marker':bind(marker),'formal_before':498,'formal_after':499,'remaining':501,'formal_design_gate_satisfied':False,'appended_id':key,'appended_complete_object_sha256':sha(canonical(ar[-1])),'appended_group_canonical_sha256':sha(canonical(ad['groups'][-1])),'old498_complete_objects_preserved':True,'old498_complete_object_canonical_hashes':rowhashes,'old498_complete_object_id_order':roworder,'old_ledger_byte_prefix_preserved_sha256':sha(rprefix),'old_ledger_byte_prefix_length':len(rprefix),'old_ledger_reconstructed_exact_baseline_sha256':sha(actual['reviewed.json'][:len(rprefix)]+rtail),'old_dedup_groups_before':226,'dedup_groups_after':227,'old226_complete_groups_preserved':True,'old_dedup_group_canonical_hashes':grouphashes,'old_dedup_byte_prefix_preserved_sha256':sha(gprefix),'old_dedup_byte_prefix_length':len(gprefix),'old_dedup_reconstructed_exact_baseline_sha256':sha(actual['semantic-dedup.json'][:len(gprefix)]+gtail),'progress_only_changed_fields':plan['allowed_progress_changes'],'before':plan['baseline'],'after':{n:bind(p) for n,p in paths.items()},'all_three_actual_hashes_exact_frozen_plan':True,'author16observations9limits_Main16findings10limits_preserved_verbatim':True,'seven_prior_judgments_six_groups_seven_migration_judgments_current101_and47_contexts_exact':True,'current101_delta_context_immutable_reuse':c101,'current47_ecology_context_immutable_reuse':c47,'historical_cross_area_prescreen_unchanged_not_treated_as_current_baseline':True,'immutable_inputs_verified_sha256':protected,'new_formal_related_whole_research_credit':1,'new_native_gameplay_credit':0,'103_remains_candidate_zero_credit_unchanged':True,'formal_paths_written_once':written,'other_ledgers_Main_session_active_pending_tasks_production_art_sharedJar_runtime_changes':0,'native_gameplay_acceptance':False,'old_source_proofs_validators_append_scripts_replayed':False,'network_requests':0,'hours_claimed':0,'rerun_forbidden':True,'prewrite_failure_this_execution':None,'inspection_output_recovery':'First receipt display oversized; selected all substantive review scalars and explicit historical-only references recovered bounded; bindings verified by hashes, not claimed as fresh source reading.'}
with proofpath.open('x') as f:
 json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert json.loads(proofpath.read_bytes())==proof
print(json.dumps({'proof':bind(proofpath),'proof_bytes':proofpath.stat().st_size,'script':bind(script),'marker':bind(marker),'formal_after':499,'remaining':501,'groups':227,'gate':False,'after':proof['after'],'103_formal_credit_added':0},ensure_ascii=False))
