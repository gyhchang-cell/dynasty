"""Exact authorized 087 append; immutable receipts, old complete rows/groups retained."""
import json,hashlib,datetime,os,tempfile
from pathlib import Path
BASE=Path('/Users/a15356015027/Desktop/dynasty')
ROOT=BASE/'docs/cod4/audit-20261022';WORK=ROOT/'program-feedback-review-20261101';FORMAL=ROOT/'immune-feedback-research'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def load(path):return json.loads(path.read_text())
def exclusive(path,obj):
 with path.open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
proposal=WORK/'immune-reference-batch-087.json';review=WORK/'coordinator-batch087-independent-review-20261109.json';receipt=WORK/'batch-087-formal-ledger-delta-20261109.json'
assert not receipt.exists(),'Never append twice; inspect existing receipt instead.'
assert sha(proposal.read_bytes())=='99dc92ff070d0a402ab9f872f4ee0b4bb5fa32114938126bc1125ae6c8ad058e'
assert sha(review.read_bytes())=='475c514dd3ffa7260c2bd72ddfa95e0fad14ddd4eb3bfcd4ea06fc5131b52cb9'
p=load(proposal);m=load(review);key=p['semantic_dedup_key'];assert m['semantic_dedup_key']==key and m['accepted_research_credit']==1 and m['formal_before']==493 and m['formal_after_required_if_author_exact_append']==494
lp=FORMAL/'reviewed.json';gp=FORMAL/'semantic-dedup.json';pp=FORMAL/'progress.json'
oldbytes={str(x):x.read_bytes() for x in [lp,gp,pp]};old=load(lp);groups=load(gp);progress=load(pp)
assert len(old)==493 and sha(oldbytes[str(lp)])=='b0cd33fd166ca61e7e00c3dbf74ec65cbd60ddbd9a629c98441d9122f15d0dbd'
assert progress['reviewed_effective_semantic_dedup']==493 and progress['remaining']==507 and not progress['formal_design_gate_satisfied']
assert key not in {x['id'] for x in old} and key not in {x['semantic_dedup_key'] for x in old}
assert all(key not in x.get('credited_chains',[]) for x in groups['groups'])
assert m['source_refs']==p['source_refs']
for c in m['complete_comparisons']:
 x=next(x for x in old if x['id']==c['id']);assert canon(x)==c['complete_record_sha256']==p['dedup']['complete_immune_decision_canonical_sha256'][c['id']]
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
refs=[dict(x,source_path=x['upstream_path'],lines=[x['start_line'],x['end_line']],file_sha256=x['sha256'],url=x['source_url']) for x in p['source_refs']]
correction='PlayerAbility.onTakeDamage is an empty override; the common handler dynamic-dispatches to that empty method for this player. Parent Ability damage-interruption behavior is NOT attributed to this player chain. Context support0 only.'
row={'id':key,'status':'reviewed_effective','repo':p['manifest']['repo'],'commit':p['manifest']['commit'],'category':'native_mixed_source_damage_reconciliation_and_result_qualified_secondary_control_feedback','semantic_dedup_key':key,'count_unit':p['count_unit'],'source_refs':refs,'full_chain_observation':'\n'.join(p['observations']),'concrete_observation':'\n'.join(m['source_findings']),'application_to_boss_immune':p['application'],'limitations':'\n'.join(p['limitations']+[correction,m['provenance_limit']]),'author_observations':p['observations'],'author_limitations':p['limitations'],'main_source_findings':m['source_findings'],'review_correction':correction,'whole_mechanism_comparisons':p['dedup']['semantic_comparisons'],'complete_prior_decision_canonical_sha256':p['dedup']['complete_immune_decision_canonical_sha256'],'prior_uncredited_decisions_retained_zero':[{'path':x['path'],'sha256':x['sha256'],'location':x['location'],'decision_canonical_sha256':x['decision_canonical_sha256'],'comparison':x['comparison']} for x in p['dedup']['prior_uncredited_decisions']],'independent_review':{'path':str(review.relative_to(BASE)),'sha256':sha(review.read_bytes()),'reviewer_thread':m['reviewer_thread'],'decision':m['decision'],'accepted_research_credit':1,'complete_comparisons':m['complete_comparisons'],'native_acceptance':False},'author_proposal':{'path':str(proposal.relative_to(BASE)),'sha256':sha(proposal.read_bytes()),'complete_dedup_records_location':'dedup.complete_immune_decisions and dedup.prior_uncredited_decisions; immutable original records retained in linked proposal, not new credits.'},'research_credit':1,'reviewed_utc':stamp}
# Same exact-prefix append discipline recorded in earlier author delta receipts.
raw=oldbytes[str(lp)];closing=raw.rfind(b']');assert closing>=0 and raw[closing+1:].strip()==b''
cut=closing
while cut>0 and raw[cut-1:cut].isspace():cut-=1
prefix=raw[:cut];assert prefix.endswith(b'}')
rowtext=json.dumps(row,ensure_ascii=False,indent=2);indented='\n'.join('  '+line for line in rowtext.splitlines()).encode()
newledger=prefix+b',\n'+indented+b'\n'+raw[closing:]
assert json.loads(newledger)==old+[row]
newgroups=json.loads(oldbytes[str(gp)]);newgroups['groups'].append({'family':'mowzie-whole-mixed-source-reconciliation-and-secondary-result-control-20261109','credited_chains':[key],'rationale':m['decision']+' Raw Pair and inferred registration are different; both damage components/callers/packets/phase constants0 extra. '+correction,'independent_review':{'path':str(review.relative_to(BASE)),'sha256':sha(review.read_bytes())}})
assert newgroups['groups'][:-1]==groups['groups']
newprogress=oldbytes[str(pp)]
for a,b in [(b'"reviewed_effective_semantic_dedup": 493',b'"reviewed_effective_semantic_dedup": 494'),(b'"remaining": 507',b'"remaining": 506')]:
 assert newprogress.count(a)==1;newprogress=newprogress.replace(a,b,1)
assert {k:v for k,v in json.loads(newprogress).items() if k not in ['reviewed_effective_semantic_dedup','remaining']}=={k:v for k,v in progress.items() if k not in ['reviewed_effective_semantic_dedup','remaining']}
newgroupbytes=(json.dumps(newgroups,ensure_ascii=False,indent=2)+'\n').encode()
planned={str(lp):newledger,str(gp):newgroupbytes,str(pp):newprogress}
exclusive(WORK/'batch-087-formal-append-plan-20261109.json',{'created_utc':stamp,'authorization_source_thread':'01a16364-cac0-7ca2-a042-a5312781ca34','independent_review':row['independent_review'],'scope':'Exactly 493->494 one reviewed whole087, dedup group and progress; no production/master/task/native scope.','before':{k:sha(v) for k,v in oldbytes.items()},'planned_after':{k:sha(v) for k,v in planned.items()},'old493_canonical_sha256':canon(old),'new_row_canonical_sha256':canon(row)})
# Compare all three exact byte baselines immediately before any authorized replacement.
for path,rawbefore in oldbytes.items():assert Path(path).read_bytes()==rawbefore,'Concurrent modification: abort before mutations'
for path,rawafter in planned.items():
 with tempfile.NamedTemporaryFile(dir=Path(path).parent,prefix='.batch087-',delete=False) as temp:
  temp.write(rawafter);temp.flush();os.fsync(temp.fileno());tmp=temp.name
 assert Path(path).read_bytes()==oldbytes[path],'Concurrent modification before this replacement'
 os.replace(tmp,path)
after=load(lp);ag=load(gp);ap=load(pp)
assert len(after)==494 and after[:-1]==old and canon(after[:-1])==canon(old)
assert lp.read_bytes().startswith(prefix+b',\n')
assert after[-1]==row and len({x['id'] for x in after})==494 and len({x['semantic_dedup_key'] for x in after})==494
assert ag==newgroups and ag['groups'][:-1]==groups['groups']
assert sum(g.get('credited_chains',[]).count(key) for g in ag['groups'])==1
assert ap['reviewed_effective_semantic_dedup']==494 and ap['remaining']==506 and not ap['formal_design_gate_satisfied']
assert sha(proposal.read_bytes())==row['author_proposal']['sha256'] and sha(review.read_bytes())==row['independent_review']['sha256']
exclusive(receipt,{'schema_version':1,'created_utc':stamp,'decision':'AUTHOR_EXACT_APPEND_ONE_INDEPENDENTLY_ACCEPTED087_PENDING_MAIN_ACTUAL_DELTA_VERIFICATION','applying_thread_id':'01a16392-312e-72f2-a4dd-56e184f9cb02','authorization_source_thread':'01a16364-cac0-7ca2-a042-a5312781ca34','authorization':'Live explicit Main delegation: exact493->494, old493 deep unchanged, dedup/progress consistent, supplement empty PlayerAbility.onTakeDamage override; no duplicate append.','proposal':row['author_proposal'],'independent_review':row['independent_review'],'semantic_key':key,'before_count':493,'after_count':494,'remaining':506,'new_credit_applied':1,'old493_complete_objects_unchanged':True,'old493_complete_objects_canonical_sha256':canon(old),'after_prefix493_canonical_sha256':canon(after[:-1]),'all493_per_row_canonical_sha256':{x['id']:canon(x) for x in old},'new_complete_object_canonical_sha256':canon(row),'old_byte_prefix_through_last_old_object_preserved':True,'old_dedup_groups_deep_unchanged':True,'new_key_exactly_once_in_ledger_and_dedup':True,'progress_only_two_counter_fields_changed':True,'before_hashes':{k:sha(v) for k,v in oldbytes.items()},'after_hashes':{k:sha(Path(k).read_bytes()) for k in planned},'main_actual_delta_verified':False,'no_old_source_verifier_rerun':True,'production_changes':0,'master_task_list_changes':0,'checklist_deletions':0,'background_changes':0,'shared_jar_changes':0,'game_starts':0,'network_requests':0,'runtime_tests':0,'hours_claimed':0})
print(json.dumps({'receipt':str(receipt.relative_to(BASE)),'receipt_sha256':sha(receipt.read_bytes()),'formal_ledger_sha256':sha(lp.read_bytes()),'applied_count':494,'remaining':506,'old493_deep_equal':True,'new_group_once':True,'main_actual_delta_verified':False},ensure_ascii=False))
