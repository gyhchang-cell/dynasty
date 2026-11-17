"""Verify new057 fixed-cache and quoted-decision bindings once; no credit."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def check(x):assert sha((R/x['path']).read_bytes())==x['sha256'],x['path']
out=H/'batch-057-integrity.json';assert not out.exists(),'sealed receipt exists; do not rerun'
p=H/'immune-reference-batch-057-screen.json'
assert sha(p.read_bytes())=='dbfea42a14bdd1eda9350b1c702515112dd6417c6e5e0f3d051cafaec9275e54'
d=json.loads(p.read_text());assert d['research_credit']==d['maximum_proposed_credit']==0
prov=d['provenance'];check(prov['source_manifest']);check(prov['cached_tree'])
mp=R/prov['source_manifest']['path'];meta=json.loads(mp.read_text());tree=json.loads((R/prov['cached_tree']['path']).read_text())
assert meta['commit']==d['commit']==prov['commit_label']==tree['sha']==prov['tree_response_sha']
assert tree['url']==prov['cached_tree_url'] and not tree.get('truncated')
mf={x['path']:x for x in meta['files']};tf={x['path']:x for x in tree['tree']}
covered={}
for x in d['source_refs']:
    sp=R/x['path'];b=sp.read_bytes();ls=b.decode().splitlines();e=mf[x['upstream_path']]
    assert sp==mp.parent/x['upstream_path']
    assert x['repo']==meta['repo'] and x['commit']==meta['commit']
    assert sha(b)==x['file_sha256']==e['sha256']
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['git_blob_sha1']==e['git_blob_sha1']==tf[x['upstream_path']]['sha']
    a,z=x['lines'];assert 1<=a<=z<=len(ls)
    assert sha('\n'.join(ls[a-1:z]).encode())==x['range_text_sha256']
    s=covered.setdefault(x['path'],set());new=set(range(a,z+1));assert not s.intersection(new);s.update(new)
assert len(d['source_refs'])==d['source_ranges']==8
assert len(covered)==d['unique_files']==6
assert sum(map(len,covered.values()))==d['cited_lines']==754
assert sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items())==d['full_files']==4
check(d['prior_read_reuse']['evidence'])
old=json.loads((R/d['prior_read_reuse']['evidence']['path']).read_text());r=d['prior_read_reuse']['range']
x=next(x for x in old['discovery_only'] if x['path']==r['path'])
assert x['sha256']==r['file_sha256'] and x['actual_lines_read']==r['lines']
ledger=R/d['dedup_snapshot']['path'];index={x['id']:x for x in json.loads(ledger.read_text())}
for x in d['dedup_snapshot']['comparisons']:
    assert all(index[x['accepted_id']][k]==v for k,v in x['complete_semantic_decision_read'].items())
assert len(d['dedup_snapshot']['comparisons'])==2
assert not any(d[k] for k in ['production_changes','runtime_executed','network_requests','master_changes','checklist_deletions','hours_claimed'])
receipt={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS_ONCE_NEW057_BINDINGS_ONLY',
 'evidence':ref(p),'builder':ref(H/'build-batch-057.py'),'verifier':ref(Path(__file__)),
 'source_ranges':8,'unique_files':6,'full_files':4,'cited_lines':754,'new_ranges':7,'reused_ranges':1,
 'complete_saved_comparison_decisions':2,'research_credit':0,'maximum_pending_credit':0,
 'ledger_binding_at_check':ref(ledger),'old_verifier_or_ledger_validator_executed':False,
 'runtime_executed':False,'production_changes':False,
 'scope':'New057 local manifest/cached-tree/blob/range bindings and exact two quoted decisions only. No new remote commit-object authentication, semantic novelty, native/full activation/transport/visual acceptance or task completion.'}
with out.open('x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'receipt':ref(out),'status':receipt['status'],'credit':0}))
