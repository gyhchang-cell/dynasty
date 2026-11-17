"""Check only new056 evidence bindings, once; no semantic credit or old QA."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty')
H=Path(__file__).resolve().parent
out=H/'batch-056-integrity.json'
assert not out.exists(), 'sealed receipt exists; do not rerun'
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):
    return {'path':str(p.relative_to(R)), 'sha256':sha(p.read_bytes())}
def check(x):
    assert sha((R/x['path']).read_bytes())==x['sha256'], x['path']

p=H/'immune-reference-batch-056-screen.json'
assert sha(p.read_bytes())=='9640d5819a2267465d9816eba75383a50580ecf39bd7b58c9143edd1a6ce8783'
d=json.loads(p.read_text())
assert d['research_credit']==d['maximum_proposed_credit']==0
assert d['status']=='HELD_ZERO_EXISTING_DAMAGE_INDEPENDENT_MOTION_AND_PARTIAL_RESOURCE_POLICY'
sources={}
for v in d['provenances']:
    mp=R/v['manifest_path'];cp=R/v['commit_metadata_path'];tp=R/v['tree_metadata_path']
    assert sha(mp.read_bytes())==v['manifest_sha256']
    assert sha(cp.read_bytes())==v['commit_metadata_sha256']
    assert sha(tp.read_bytes())==v['tree_metadata_sha256']
    m=next(x for x in json.loads(mp.read_text()) if x['repo']==v['repo'])
    c=json.loads(cp.read_text());t=json.loads(tp.read_text())
    assert c['sha']==m['commit']==v['commit']
    assert c['tree']['sha']==t['sha']==v['git_tree'] and not t.get('truncated',False)
    sources[v['repo']]=({e['path']:e for e in m['files']},{e['path']:e for e in t['tree']},v['commit'])
covered={}
for x in d['source_refs']:
    es,tree,commit=sources[x['repo']];e=es[x['upstream_path']]
    b=(R/x['path']).read_bytes(); lines=b.decode().splitlines()
    assert x['commit']==commit and e['source']==x['path']
    assert sha(b)==e['sourceSha256']==x['file_sha256']
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['source_blob']==x['git_blob_sha1']==tree[x['upstream_path']]['sha']
    a,z=x['lines']; assert 1<=a<=z<=len(lines)
    assert sha('\n'.join(lines[a-1:z]).encode())==x['range_text_sha256']
    old=covered.setdefault(x['path'],set());new=set(range(a,z+1));assert not old.intersection(new);old.update(new)
assert len(d['source_refs'])==d['source_ranges']==10
assert len(covered)==d['unique_files']==10
assert sum(map(len,covered.values()))==d['cited_lines']==1525
assert sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items())==d['full_files']==8
check(d['prior_read_reuse']['evidence'])
prior=json.loads((R/d['prior_read_reuse']['evidence']['path']).read_text())
reused=[x for x in d['source_refs'] if x['reading_context'].startswith('exact037')]
assert len(reused)==d['prior_read_reuse']['reused_ranges']==1
for x in reused:
    y=next(y for y in prior['source_refs'] if y['path']==x['path'] and y['lines']==x['lines'])
    assert all(x[k]==y[k] for k in ['repo','commit','path','upstream_path','lines','file_sha256','git_blob_sha1'])
ledger=R/d['dedup_snapshot']['path'];index={r['id']:r for r in json.loads(ledger.read_text())}
for x in d['dedup_snapshot']['comparisons']:
    assert all(index[x['accepted_id']][k]==v for k,v in x['complete_semantic_decision_read'].items())
assert len(d['dedup_snapshot']['comparisons'])==3
for x in d['discovery_only']:
    check(x)
    assert x['credit']==0 and not x['fixed_commit_provenance_claimed_in_this_screen']
    assert x['actual_lines_read']==[1,len((R/x['path']).read_text().splitlines())]
assert not any(d[k] for k in ['production_changes','runtime_executed','network_requests','master_changes','checklist_deletions','hours_claimed'])
receipt={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS_ONCE_NEW056_BINDINGS_ONLY',
         'evidence':ref(p),'builder':ref(H/'build-batch-056.py'),'verifier':ref(Path(__file__)),
         'source_ranges':10,'unique_files':10,'full_files':8,'cited_lines':1525,
         'new_ranges':9,'reused_ranges':1,'complete_saved_comparison_decisions':3,
         'discovery_only_reads_outside_bound_totals':2,'research_credit':0,'maximum_pending_credit':0,
         'ledger_binding_at_check':ref(ledger),'old_verifier_or_ledger_validator_executed':False,
         'upstream_execution':False,'runtime_execution':False,'production_changes':False,
         'scope':'New056 file/tree/blob/range bindings, exact reused range, three quoted judgments and two explicitly unclosed class-read hashes only. No semantic acceptance, runtime/transport/visual validation or original-task completion.'}
with out.open('x') as f:
    json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'receipt':ref(out),'status':receipt['status'],'credit':0}))
