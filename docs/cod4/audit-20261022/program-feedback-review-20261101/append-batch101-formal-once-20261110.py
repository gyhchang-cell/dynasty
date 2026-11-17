"""Apply only Main-authorized frozen101 plan exactly once. Never retry after marker."""
from pathlib import Path
import json, hashlib, datetime, os, copy
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
assert Path.cwd().resolve()==ROOT
BASE=Path('docs/cod4/audit-20261022'); OUT=BASE/'program-feedback-review-20261101'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda o:json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
bind=lambda p:{'path':str(p),'sha256':sha(p.read_bytes())}
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
planpath=OUT/'batch-101-formal-append-plan-20261110.json'
reviewpath=BASE/'coordinator-program101-append-plan-review-20261110.json'
protected={str(planpath):'2556d740a188d61c30e3615ac2246f972e0d7efc4bd73ce1a3b690fe6949a709',str(reviewpath):'ddc37680a72e298dc8fe44c58e7838c0257a452330dc280d64a436b1edf84e3c'}
def freeze(binding):
 p=Path(binding['path']); assert sha(p.read_bytes())==binding['sha256']; protected[str(p)]=binding['sha256']
def recheck():
 for p,h in protected.items(): assert sha(Path(p).read_bytes())==h, 'Immutable input drift: STOP'
recheck()
plan=json.loads(planpath.read_bytes()); review=json.loads(reviewpath.read_bytes())
assert review['decision']=='EXACT_ONE_ROW101_PLAN_REVIEWED_READY_FOR_ORIGINAL_AUTHOR_ONE_TIME_APPEND'
assert review['reviewer_thread_id']=='01a16364-cac0-7ca2-a042-a5312781ca34'
assert review['plan']['sha256']==protected[str(planpath)] and review['plan']['path']==str(planpath)
assert review['baseline']==plan['baseline'] and review['planned_output_sha256']==plan['planned_output_sha256']
assert [review[k] for k in ['old_complete_rows_preserved_in_memory','old_complete_groups_preserved_in_memory','new_rows','new_groups','expected_after','expected_gap']]==[497,225,1,1,498,502]
for k in ['Main_receipt','proposal','worker_validation_reused_not_rerun','actual_author_confirmation','current497_complete_handoff']:freeze(plan[k])
context=plan['current100_delta_context']
for k in ['Main_actual_delta_closure','actual_original_author_delta']:freeze(context[k])
assert review['actual_author_confirmation']['sha256']==plan['actual_author_confirmation']['sha256']=='63b2c7e0acf7e6802ffd5a25852600bdfbdd2d6e00938ab5d5919f8c2c0397a1'
assert review['Main_whole_review']==plan['Main_receipt']
author=json.loads(Path(plan['actual_author_confirmation']['path']).read_bytes())
main=json.loads(Path(plan['Main_receipt']['path']).read_bytes())
proposal=json.loads(Path(plan['proposal']['path']).read_bytes())
assert author['author_thread_id']==main['author_thread_id']=='01a16392-312e-72f2-a4dd-56e184f9cb02'
assert author['Main_thread_id']==main['reviewer_thread_id']==review['reviewer_thread_id']
assert author['baseline']==plan['baseline'] and author['formal_intake_applied_by_this_confirmation'] is False
entry=plan['entry']; group=plan['dedup_group']
assert entry['author_observations']==author['author_observations_all16_verbatim']==proposal['observations']==main['author_observations_all16_retained']
assert entry['author_limitations']==author['author_limits_all9_verbatim']==proposal['limitations']==main['author_limits_all9_retained']
assert entry['main_independent_findings']==author['Main_findings_all16_verbatim']==main['independent_findings']==group['retained_Main_findings']
assert entry['main_preappend_limits_verbatim']==author['Main_limits_all9_verbatim']==main['mandatory_limits']==group['retained_Main_limits']
assert [len(entry[k]) for k in ['author_observations','author_limitations','main_independent_findings','main_preappend_limits_verbatim']]==[16,9,16,9]
assert entry['current100_delta_context']==author['current100_delta_context']==context
assert sha(canon(entry))==plan['planned_entry_canonical_sha256'] and sha(canon(group))==plan['planned_group_canonical_sha256']
assert plan['baseline_formal_count']==497 and plan['baseline_dedup_group_count']==225
assert plan['expected_after_formal_count']==498 and plan['expected_after_dedup_group_count']==226
assert plan['allowed_progress_changes']=={'reviewed_effective_semantic_dedup':[497,498],'remaining':[503,502]}
marker=Path(plan['one_time_start_marker']); proofpath=Path(plan['proof_path'])
assert marker==OUT/'batch-101-formal-append-once-started-20261110.json'
assert proofpath==OUT/'batch-101-formal-ledger-delta-20261110.json'
assert not marker.exists() and not proofpath.exists(), 'Consumed marker/proof: NEVER RERUN'
paths={n:Path(b['path']) for n,b in plan['baseline'].items()}
assert set(paths)=={'reviewed.json','semantic-dedup.json','progress.json'}
assert {str(p) for p in paths.values()}==set(plan['allowed_formal_paths_after_later_explicit_authorization'])
for n,p in paths.items():assert p==BASE/'immune-feedback-research'/n and not p.is_symlink()
oldraw={n:p.read_bytes() for n,p in paths.items()}
assert {n:sha(b) for n,b in oldraw.items()}=={n:b['sha256'] for n,b in plan['baseline'].items()}, 'Baseline drift: STOP, no rebase'
oldrows,olddedup,oldprogress=[json.loads(oldraw[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert len(oldrows)==497 and len(olddedup['groups'])==225
assert oldprogress['reviewed_effective_semantic_dedup']==497 and oldprogress['remaining']==503 and oldprogress['formal_design_gate_satisfied'] is False
rowhashes={r['id']:sha(canon(r)) for r in oldrows}; grouphashes=[sha(canon(g)) for g in olddedup['groups']]
assert rowhashes==plan['old497_complete_object_canonical_hashes']==author['old497_complete_object_canonical_hashes']
assert grouphashes==plan['old_dedup_group_canonical_hashes']==author['old_dedup_group_canonical_hashes']
assert rowhashes[context['current100_formal_id']]==context['current100_full_object_canonical_sha256']
key=entry['id']; assert key==entry['semantic_dedup_key']==proposal['semantic_dedup_key']==main['semantic_dedup_key']==group['credited_chain']
assert not any(key in [r.get('id'),r.get('semantic_dedup_key')] for r in oldrows)
assert entry['research_credit']==1 and entry['native_acceptance'] is False and entry['global_uniqueness_claimed'] is False
indent=lambda o,n:'\n'.join(' '*n+l for l in json.dumps(o,ensure_ascii=False,indent=2).splitlines()).encode()
rtail=b'\n]\n'; gtail=b'\n  ]\n}\n'
assert oldraw['reviewed.json'].endswith(rtail) and oldraw['semantic-dedup.json'].endswith(gtail)
rprefix=oldraw['reviewed.json'][:-len(rtail)]; gprefix=oldraw['semantic-dedup.json'][:-len(gtail)]
newraw={'reviewed.json':rprefix+b',\n'+indent(entry,2)+rtail,'semantic-dedup.json':gprefix+b',\n'+indent(group,4)+gtail,'progress.json':oldraw['progress.json']}
for before,after in [(b'"reviewed_effective_semantic_dedup": 497',b'"reviewed_effective_semantic_dedup": 498'),(b'"remaining": 503',b'"remaining": 502')]:
 assert newraw['progress.json'].count(before)==1; newraw['progress.json']=newraw['progress.json'].replace(before,after)
assert {n:sha(b) for n,b in newraw.items()}==plan['planned_output_sha256']
assert {n:len(b) for n,b in newraw.items()}==plan['planned_output_byte_lengths']
rows,dedup,progress=[json.loads(newraw[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert len(rows)==498 and rows[:-1]==oldrows and rows[-1]==entry
assert len(dedup['groups'])==226 and dedup['groups'][:-1]==olddedup['groups'] and dedup['groups'][-1]==group
rev=copy.deepcopy(dedup); rev['groups'].pop(); assert rev==olddedup
rev=copy.deepcopy(progress);rev.update(reviewed_effective_semantic_dedup=497,remaining=503);assert rev==oldprogress
assert progress['formal_design_gate_satisfied'] is False
assert newraw['reviewed.json'][:len(rprefix)]+rtail==oldraw['reviewed.json']
assert newraw['semantic-dedup.json'][:len(gprefix)]+gtail==oldraw['semantic-dedup.json']
recheck()
for n,p in paths.items():assert p.read_bytes()==oldraw[n]
script=Path(__file__); protected[str(script)]=sha(script.read_bytes())
markerdata={'schema_version':1,'created_utc':now(),'batch':101,'status':'exclusive_one_time_start_never_blind_rerun','plan':bind(planpath),'Main_plan_review':bind(reviewpath),'script':bind(script),'explicit_authorization':'Main exact frozen2556d740 one-time grant:497to498/225to226/gap503to502; no rebase or old script replay.','before':plan['baseline'],'expected_after':plan['planned_output_sha256']}
with marker.open('x') as f:
 json.dump(markerdata,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
written=[]
for n,p in paths.items():
 recheck()
 for n0,p0 in paths.items():assert p0.read_bytes()==(newraw[n0] if n0 in written else oldraw[n0])
 with p.open('wb') as f:
  assert f.write(newraw[n])==len(newraw[n]);f.flush();os.fsync(f.fileno())
 written.append(n);assert p.read_bytes()==newraw[n]
actual={n:p.read_bytes() for n,p in paths.items()}; assert actual==newraw
ar,ad,ap=[json.loads(actual[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert ar[:-1]==oldrows and ad['groups'][:-1]==olddedup['groups']
assert {r['id']:sha(canon(r)) for r in ar[:-1]}==rowhashes and [sha(canon(g)) for g in ad['groups'][:-1]]==grouphashes
recheck()
proof={'schema_version':1,'created_utc':now(),'status':'actual_original_author_one_time_formal498_append_applied_exact_frozen_plan','batch':101,'plan':bind(planpath),'Main_plan_review':bind(reviewpath),'Main_receipt':plan['Main_receipt'],'actual_author_confirmation':plan['actual_author_confirmation'],'source_proposal_unchanged':plan['proposal'],'script':bind(script),'one_time_start_marker':bind(marker),'formal_before':497,'formal_after':498,'remaining':502,'formal_design_gate_satisfied':False,'appended_id':key,'appended_complete_object_sha256':sha(canon(ar[-1])),'appended_group_canonical_sha256':sha(canon(ad['groups'][-1])),'old497_complete_objects_preserved':True,'old497_complete_object_canonical_hashes':rowhashes,'old_ledger_byte_prefix_preserved_sha256':sha(rprefix),'old_ledger_byte_prefix_length':len(rprefix),'old_ledger_reconstructed_exact_baseline_sha256':sha(actual['reviewed.json'][:len(rprefix)]+rtail),'old_dedup_groups_before':225,'dedup_groups_after':226,'old225_complete_groups_preserved':True,'old_dedup_group_canonical_hashes':grouphashes,'old_dedup_byte_prefix_preserved_sha256':sha(gprefix),'old_dedup_byte_prefix_length':len(gprefix),'old_dedup_reconstructed_exact_baseline_sha256':sha(actual['semantic-dedup.json'][:len(gprefix)]+gtail),'progress_only_changed_fields':plan['allowed_progress_changes'],'before':plan['baseline'],'after':{n:bind(p) for n,p in paths.items()},'all_three_actual_hashes_exact_frozen_plan':True,'author16observations9limits_Main16findings9limits_preserved_verbatim':True,'eight_prior_judgments_eight_group_rationales_four_migration_and_current100_context_preserved_in_frozen_entry':True,'current100_delta_context_immutable_reuse':context,'new_formal_related_whole_research_credit':1,'new_native_gameplay_credit':0,'formal_paths_written_once':written,'other_ledgers_Main_session_active_pending_tasks_production_art_Jar_runtime_changes':0,'native_gameplay_acceptance':False,'network_requests':0,'hours_claimed':0,'rerun_forbidden':True,'prewrite_failure_this_execution':None}
with proofpath.open('x') as f:
 json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert json.loads(proofpath.read_bytes())==proof
print(json.dumps({'proof':bind(proofpath),'script':bind(script),'marker':bind(marker),'formal_after':498,'remaining':502,'gate':False,'after':proof['after']},ensure_ascii=False))
