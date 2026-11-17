"""New060 integrity only, one successful run; no old ledger validators."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def check(x):assert sha((R/x['path']).read_bytes())==x['sha256'],x['path']
out=H/'batch-060-integrity.json';assert not out.exists(),'sealed receipt exists; do not rerun'
p=H/'immune-reference-batch-060-screen.json'
assert sha(p.read_bytes())=='ae2b936159da0e49dee5a7f48675ca0737552c3df7057efe91ae50d54a3c17af'
d=json.loads(p.read_text());assert d['research_credit']==d['maximum_proposed_credit']==0
v=d['provenance']
for k in ['manifest','commit_metadata','tree_metadata']:check(v[k])
m=next(x for x in json.loads((R/v['manifest']['path']).read_text()) if x['repo']==d['repo'])
c=json.loads((R/v['commit_metadata']['path']).read_text());t=json.loads((R/v['tree_metadata']['path']).read_text())
assert c['sha']==m['commit']==d['commit'] and c['tree']['sha']==t['sha']==v['git_tree'] and not t.get('truncated')
es={x['path']:x for x in m['files']};ts={x['path']:x for x in t['tree']};covered={}
for x in d['source_refs']:
    e=es[x['upstream_path']];b=(R/x['path']).read_bytes();ls=b.decode().splitlines()
    assert e['source']==x['path'] and x['commit']==d['commit']
    assert sha(b)==e['sourceSha256']==x['file_sha256']
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['source_blob']==x['git_blob_sha1']==ts[x['upstream_path']]['sha']
    a,z=x['lines'];assert 1<=a<=z<=len(ls)
    assert sha('\n'.join(ls[a-1:z]).encode())==x['range_text_sha256']
    s=covered.setdefault(x['path'],set());new=set(range(a,z+1));assert not s.intersection(new);s.update(new)
assert len(d['source_refs'])==d['source_ranges']==18
assert len(covered)==d['unique_files']==16
assert sum(map(len,covered.values()))==d['cited_lines']==1024
assert sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items())==d['full_files']==9
lp=R/d['dedup_snapshot']['path'];idx={x['id']:x for x in json.loads(lp.read_text())}
for x in d['dedup_snapshot']['comparisons']:
    assert all(idx[x['accepted_id']][k]==v for k,v in x['complete_semantic_decision_read'].items())
    if 'reused_evidence' in x:
        check(x['reused_evidence']);old=json.loads((R/x['reused_evidence']['path']).read_text())
        quoted=next(z['complete_semantic_decision_read'] for z in old['dedup_snapshot']['comparisons'] if z['accepted_id']==x['accepted_id'])
        assert quoted==x['complete_semantic_decision_read']
assert len(d['dedup_snapshot']['comparisons'])==3
assert not any(d[k] for k in ['production_changes','runtime_executed','network_requests','master_changes','checklist_deletions','hours_claimed'])
receipt={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS_ONCE_NEW060_BINDINGS_ONLY',
 'evidence':ref(p),'builder':ref(H/'build-batch-060.py'),'verifier':ref(Path(__file__)),
 'source_ranges':18,'unique_files':16,'full_files':9,'cited_lines':1024,
 'whole_comparisons':3,'new_whole_decisions_read':2,'exact_prior_decision_reused':1,
 'research_credit':0,'maximum_pending_credit':0,'ledger_observed':ref(lp),
 'old_verifier_or_ledger_validator_executed':False,'production_changes':False,'runtime_executed':False,
 'scope':'Only new060 fixed source/tree/blob/range and exact quoted judgments. Not semantic acceptance, natural acquisition, installed lifecycle, successful protection or rendered target feedback.'}
with out.open('x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'receipt':ref(out),'status':receipt['status'],'credit':0}))
