"""Verify only the new055 fixed-source evidence bindings, once on success."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty')
H=Path(__file__).resolve().parent
out=H/'batch-055-integrity.json'
assert not out.exists(), 'sealed receipt exists; do not rerun'
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):
    return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def check(r):
    assert sha((R/r['path']).read_bytes())==r['sha256'],r['path']
path=H/'immune-reference-batch-055.json'
assert ref(path)['sha256']=='5475031c51142ec85215fba0ee330516657956920ef9947a469e37bc22f26dc3'
d=json.loads(path.read_text())
assert d['research_credit']==0 and d['maximum_proposed_credit']==1
assert d['status']=='ONE_WHOLE_AREA_TICK_LIST_CAPTURE_RELEASE_POLICY_PENDING_INDEPENDENT_REVIEW'
sources={}
provenance_bindings=[]
for v in d['provenances']:
    mp=R/v['manifest_path']; cp=R/v['commit_metadata_path'];tp=R/v['tree_metadata_path']
    assert sha(mp.read_bytes())==v['manifest_sha256']
    assert sha(cp.read_bytes())==v['commit_metadata_sha256']
    assert sha(tp.read_bytes())==v['tree_metadata_sha256']
    m=next(x for x in json.loads(mp.read_text()) if x['repo']==v['repo'])
    c=json.loads(cp.read_text());t=json.loads(tp.read_text())
    assert c['sha']==m['commit']==v['commit']
    assert c['tree']['sha']==t['sha']==v['git_tree'] and not t.get('truncated',False)
    sources[v['repo']]=({e['path']:e for e in m['files']},{e['path']:e for e in t['tree']},v['commit'])
    provenance_bindings.append({'repo':v['repo'],'manifest':ref(mp),'commit_metadata':ref(cp),'tree_metadata':ref(tp)})
covered={}
for x in d['source_refs']:
    es,tree,commit=sources[x['repo']]
    assert x['commit']==commit
    e=es[x['upstream_path']];b=(R/x['path']).read_bytes();lines=b.decode().splitlines()
    assert e['source']==x['path']
    assert sha(b)==e['sourceSha256']==x['file_sha256']
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['source_blob']==x['git_blob_sha1']==tree[x['upstream_path']]['sha']
    a,z=x['lines'];assert 1<=a<=z<=len(lines)
    assert sha('\n'.join(lines[a-1:z]).encode())==x['range_text_sha256']
    old=covered.setdefault(x['path'],set());new=set(range(a,z+1));assert not old.intersection(new);old.update(new)
assert len(d['source_refs'])==d['source_ranges']==53
assert len(covered)==d['unique_files']==46
assert sum(map(len,covered.values()))==d['cited_lines']==4279
assert sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items())==d['full_files']==39
for binding in d['prior_read_reuse']['evidence']:
    check(binding)
for overlap in d['existing_work_overlap']:
    check(overlap['evidence'])
# Inspect only the four quoted decisions; do not run an accepted ledger validation suite.
ledger=R/d['dedup_snapshot']['path'];rows=json.loads(ledger.read_text());index={r['id']:r for r in rows}
for x in d['dedup_snapshot']['comparisons']:
    assert all(index[x['accepted_id']][k]==val for k,val in x['complete_semantic_decision_read'].items())
assert len(d['dedup_snapshot']['comparisons'])==4
assert not any(d[k] for k in ['production_changes','runtime_executed','network_requests','master_changes','checklist_deletions','hours_claimed'])
receipt={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS_ONCE_NEW055_BINDINGS_ONLY',
    'evidence':ref(path),'builder':ref(H/'build-batch-055.py'),'verifier':ref(Path(__file__)),
    'provenance_bindings':provenance_bindings,'source_ranges':53,'unique_files':46,'full_files':39,'cited_lines':4279,
    'complete_saved_immune_decisions':4,'complete_existing_migration_owner':0,
    'research_credit':0,'maximum_pending_credit':1,'baseline_count':d['baseline']['formal_count_observed'],
    'ledger_binding_at_check':ref(ledger),'old_verifier_or_ledger_validator_executed':False,
    'upstream_execution':False,'runtime_execution':False,'production_changes':False,
    'scope':'New055 source/tree/hash and exact quoted-decision integrity only. Does not accept novelty, installed data, gameplay, transport, visuals or original task completion.'}
with out.open('x') as f:
    json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'receipt':ref(out),'status':receipt['status'],'research_credit':0,'maximum_pending':1}))
