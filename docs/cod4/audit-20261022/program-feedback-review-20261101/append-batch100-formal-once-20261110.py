"""Authorized one-time application of frozen batch100 plan; never rerun after marker."""
from pathlib import Path
import json, hashlib, datetime, os, copy
ROOT = Path('/Users/a15356015027/Desktop/dynasty')
assert Path.cwd().resolve() == ROOT
BASE = Path('docs/cod4/audit-20261022')
OUT = BASE / 'program-feedback-review-20261101'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
canonical = lambda obj: json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
bind = lambda p: {'path': str(p), 'sha256': sha(p.read_bytes())}
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
planpath = OUT / 'batch-100-formal-append-plan-20261110.json'
reviewpath = BASE / 'coordinator-program100-append-plan-review-20261110.json'
assert sha(planpath.read_bytes()) == '52fe8382098965fbf83dce2ddb9ae8573cf15555c828aa69eb906a3f2b7744b0'
assert sha(reviewpath.read_bytes()) == 'e49b6a6c03f5e0712729e7765f47e842385be6a0e25bbdd9d7ca7457834ccb7b'
plan = json.loads(planpath.read_bytes())
review = json.loads(reviewpath.read_bytes())
assert review['decision'] == 'EXACT_ONE_ROW_PLAN_REVIEWED_READY_FOR_ORIGINAL_AUTHOR_ONE_TIME_APPEND'
assert review['plan']['path'] == str(planpath) and review['plan']['sha256'] == bind(planpath)['sha256']
assert review['baseline'] == plan['baseline']
assert review['planned_output_sha256'] == plan['planned_output_sha256']
assert review['old_complete_rows_preserved_in_memory'] == 496 and review['old_complete_groups_preserved_in_memory'] == 224
assert review['expected_after'] == 497 and review['expected_gap'] == 503
assert review['reviewer_thread_id'] == '01a16364-cac0-7ca2-a042-a5312781ca34'
assert plan['baseline_formal_count'] == 496 and plan['baseline_dedup_group_count'] == 224
assert plan['allowed_progress_changes'] == {'reviewed_effective_semantic_dedup': [496, 497], 'remaining': [504, 503]}
protected = {str(planpath): bind(planpath)['sha256'], str(reviewpath): bind(reviewpath)['sha256']}
for name in ['Main_receipt', 'proposal', 'worker_validation_reused_not_rerun', 'actual_author_confirmation']:
    binding = plan[name]
    path = Path(binding['path'])
    assert sha(path.read_bytes()) == binding['sha256']
    protected[str(path)] = binding['sha256']
main = json.loads(Path(plan['Main_receipt']['path']).read_bytes())
author = json.loads(Path(plan['actual_author_confirmation']['path']).read_bytes())
proposal = json.loads(Path(plan['proposal']['path']).read_bytes())
entry, group = plan['entry'], plan['dedup_group']
assert author['author_thread_id'] == '01a16392-312e-72f2-a4dd-56e184f9cb02'
assert author['Main_thread_id'] == main['reviewer_thread_id'] == review['reviewer_thread_id']
assert author['baseline'] == plan['baseline']
assert author['formal_intake_applied_by_this_confirmation'] is False
assert entry['author_observations'] == author['author_observations_all16_verbatim'] == proposal['observations'] == main['author_observations_all16_retained']
assert entry['author_limitations'] == author['author_limits_all8_verbatim'] == proposal['limitations'] == main['author_limits_all8_retained']
assert entry['main_independent_findings'] == author['Main_findings_all16_verbatim'] == main['independent_findings'] == group['retained_Main_findings']
assert entry['main_preappend_limits_verbatim'] == author['Main_limits_all8_verbatim'] == main['mandatory_limits'] == group['retained_Main_limits']
assert [len(entry[k]) for k in ['author_observations','author_limitations','main_independent_findings','main_preappend_limits_verbatim']] == [16,8,16,8]
assert sha(canonical(entry)) == plan['planned_entry_canonical_sha256'] and sha(canonical(group)) == plan['planned_group_canonical_sha256']
marker = Path(plan['one_time_start_marker'])
proofpath = Path(plan['proof_path'])
assert marker.parent == proofpath.parent == OUT
assert not marker.exists() and not proofpath.exists(), 'One-time marker/proof already exists: STOP; do not rerun.'
paths = {name: Path(v['path']) for name, v in plan['baseline'].items()}
assert set(paths) == {'reviewed.json','semantic-dedup.json','progress.json'}
assert {str(p) for p in paths.values()} == set(plan['allowed_formal_paths_after_later_explicit_authorization'])
for name,p in paths.items(): assert p == BASE / 'immune-feedback-research' / name and not p.is_symlink()
oldraw = {name: path.read_bytes() for name,path in paths.items()}
for name,raw in oldraw.items(): assert sha(raw) == plan['baseline'][name]['sha256'], 'Baseline drift: STOP; never rebase.'
oldrows, olddedup, oldprogress = [json.loads(oldraw[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert len(oldrows) == 496 and len(olddedup['groups']) == 224
assert oldprogress['reviewed_effective_semantic_dedup'] == 496 and oldprogress['remaining'] == 504 and oldprogress['formal_design_gate_satisfied'] is False
oldrowhashes = {r['id']: sha(canonical(r)) for r in oldrows}
oldgrouphashes = [sha(canonical(g)) for g in olddedup['groups']]
assert oldrowhashes == plan['old496_complete_object_canonical_hashes'] == author['old496_complete_object_canonical_hashes']
assert oldgrouphashes == plan['old_dedup_group_canonical_hashes'] == author['old_dedup_group_canonical_hashes']
key = entry['id']
assert key == entry['semantic_dedup_key'] == proposal['semantic_dedup_key'] == main['semantic_dedup_key'] == group['credited_chain']
assert not any(key in [r.get('id'), r.get('semantic_dedup_key')] for r in oldrows)
assert entry['research_credit'] == 1 and entry['native_acceptance'] is False and entry['global_uniqueness_claimed'] is False
indent = lambda obj,n: '\n'.join(' '*n+line for line in json.dumps(obj,ensure_ascii=False,indent=2).splitlines()).encode()
rtail, gtail = b'\n]\n', b'\n  ]\n}\n'
assert oldraw['reviewed.json'].endswith(rtail) and oldraw['semantic-dedup.json'].endswith(gtail)
rprefix = oldraw['reviewed.json'][:-len(rtail)]
gprefix = oldraw['semantic-dedup.json'][:-len(gtail)]
newraw = {'reviewed.json': rprefix+b',\n'+indent(entry,2)+rtail, 'semantic-dedup.json': gprefix+b',\n'+indent(group,4)+gtail, 'progress.json': oldraw['progress.json']}
for old,new in [(b'"reviewed_effective_semantic_dedup": 496', b'"reviewed_effective_semantic_dedup": 497'),(b'"remaining": 504',b'"remaining": 503')]:
    assert newraw['progress.json'].count(old) == 1
    newraw['progress.json'] = newraw['progress.json'].replace(old,new)
assert {n:sha(raw) for n,raw in newraw.items()} == plan['planned_output_sha256']
assert {n:len(raw) for n,raw in newraw.items()} == plan['planned_output_byte_lengths']
newrows, newdedup, newprogress = [json.loads(newraw[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert len(newrows) == 497 and newrows[:-1] == oldrows and newrows[-1] == entry
assert len(newdedup['groups']) == 225 and newdedup['groups'][:-1] == olddedup['groups'] and newdedup['groups'][-1] == group
reversegroups = copy.deepcopy(newdedup); reversegroups['groups'].pop(); assert reversegroups == olddedup
reverseprogress = copy.deepcopy(newprogress); reverseprogress.update(reviewed_effective_semantic_dedup=496,remaining=504); assert reverseprogress == oldprogress
assert newprogress['formal_design_gate_satisfied'] is False
assert newraw['reviewed.json'][:len(rprefix)]+rtail == oldraw['reviewed.json']
assert newraw['semantic-dedup.json'][:len(gprefix)]+gtail == oldraw['semantic-dedup.json']
# Recheck all immutable inputs and formal baselines immediately before the exclusive start marker.
for path,digest in protected.items(): assert sha(Path(path).read_bytes()) == digest
for name,path in paths.items(): assert path.read_bytes() == oldraw[name]
script = Path(__file__)
markerdata = {'schema_version':1,'created_utc':now(),'batch':100,'status':'exclusive_one_time_start_never_blind_rerun','plan':bind(planpath),'Main_plan_review':bind(reviewpath),'script':bind(script),'explicit_authorization':'Main delegated exactly once frozen52fe8382 plan,496to497/224to225/gap504to503, three exact output hashes, no rebase or blind rerun, save actual delta.','before':plan['baseline'],'expected_after':plan['planned_output_sha256']}
with marker.open('x') as f:
    json.dump(markerdata,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
# Exactly one formal write per path. An interruption leaves the exclusive marker for audit, never automated retry/rollback.
written = []
for name,path in paths.items():
    for path0,digest in protected.items(): assert sha(Path(path0).read_bytes()) == digest
    for n,p0 in paths.items(): assert p0.read_bytes() == (newraw[n] if n in written else oldraw[n])
    with path.open('wb') as f:
        assert f.write(newraw[name]) == len(newraw[name]); f.flush(); os.fsync(f.fileno())
    written.append(name)
    assert path.read_bytes() == newraw[name]
actual = {n:p.read_bytes() for n,p in paths.items()}
assert actual == newraw
actualrows,actualdedup,actualprogress = [json.loads(actual[n]) for n in ['reviewed.json','semantic-dedup.json','progress.json']]
assert actualrows[:-1] == oldrows and actualdedup['groups'][:-1] == olddedup['groups']
assert {r['id']:sha(canonical(r)) for r in actualrows[:-1]} == oldrowhashes
assert [sha(canonical(g)) for g in actualdedup['groups'][:-1]] == oldgrouphashes
for path,digest in protected.items(): assert sha(Path(path).read_bytes()) == digest
proof = {'schema_version':1,'created_utc':now(),'status':'actual_original_author_one_time_formal497_append_applied_exact_frozen_plan','batch':100,'plan':bind(planpath),'Main_receipt':plan['Main_receipt'],'Main_plan_review':bind(reviewpath),'actual_author_confirmation':plan['actual_author_confirmation'],'source_proposal_unchanged':plan['proposal'],'script':bind(script),'one_time_start_marker':bind(marker),'formal_before':496,'formal_after':497,'remaining':503,'formal_design_gate_satisfied':False,'appended_id':key,'appended_complete_object_sha256':sha(canonical(actualrows[-1])),'appended_group_canonical_sha256':sha(canonical(actualdedup['groups'][-1])),'old496_complete_objects_preserved':True,'old496_complete_object_canonical_hashes':oldrowhashes,'old_ledger_byte_prefix_preserved_sha256':sha(rprefix),'old_ledger_byte_prefix_length':len(rprefix),'old_ledger_reconstructed_exact_baseline_sha256':sha(actual['reviewed.json'][:len(rprefix)]+rtail),'old_dedup_groups_before':224,'dedup_groups_after':225,'old224_complete_groups_preserved':True,'old_dedup_group_canonical_hashes':oldgrouphashes,'old_dedup_byte_prefix_preserved_sha256':sha(gprefix),'old_dedup_byte_prefix_length':len(gprefix),'old_dedup_reconstructed_exact_baseline_sha256':sha(actual['semantic-dedup.json'][:len(gprefix)]+gtail),'progress_only_changed_fields':plan['allowed_progress_changes'],'before':plan['baseline'],'after':{n:bind(p) for n,p in paths.items()},'all_three_actual_hashes_exact_frozen_plan':True,'author16observations8limits_Main16findings8limits_preserved_verbatim':True,'new_formal_related_whole_research_credit':1,'new_native_gameplay_credit':0,'formal_paths_written_once':written,'ecology_migration_Main_master_production_changes':0,'native_gameplay_acceptance':False,'native_execution':0,'network_requests':0,'hours_claimed':0,'rerun_forbidden':True}
with proofpath.open('x') as f:
    json.dump(proof,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
assert json.loads(proofpath.read_bytes()) == proof
print(json.dumps({'proof':bind(proofpath),'script':bind(script),'marker':bind(marker),'formal_after':497,'remaining':503,'gate':False,'after':proof['after']},ensure_ascii=False))
