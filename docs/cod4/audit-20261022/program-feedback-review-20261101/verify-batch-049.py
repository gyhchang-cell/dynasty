"""One new evidence binding check. Does not execute upstream code or award credit."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
out = H/'batch-049-integrity.json'
assert not out.exists(), 'sealed receipt exists; do not rerun'
sha = lambda b: hashlib.sha256(b).hexdigest()
def binding(p):
    return {'path': str(p.relative_to(R)), 'sha256': sha(p.read_bytes())}
def check_ref(r):
    assert sha((R/r['path']).read_bytes()) == r['sha256'], r['path']

path = H/'immune-reference-batch-049-screen.json'
assert binding(path)['sha256'] == '2ce4636625f906db1fd80535f7f4cc6e1b9478acf1e4afb801a81590adb291e4'
d = json.loads(path.read_text())
assert d['research_credit'] == d['maximum_proposed_credit'] == 0
assert d['status'] == 'STORM_CLOUD_WHOLE_POLICY_OVERLAP_HOLD_ZERO'
v = d['provenances'][0]
manifest = R/v['manifest_path']
assert sha(manifest.read_bytes()) == v['manifest_sha256']
m = next(x for x in json.loads(manifest.read_text()) if x['repo'] == v['repo'])
assert m['commit'] == d['commit'] == v['commit']
cpath, tpath = R/v['commit_metadata_path'], R/v['tree_metadata_path']
c, t = json.loads(cpath.read_text()), json.loads(tpath.read_text())
assert c['sha'] == v['commit']
assert c['tree']['sha'] == t['sha'] == v['git_tree']
assert not t.get('truncated', False)
tree = {x['path']: x for x in t['tree']}
entries = {x['path']: x for x in m['files']}
covered = {}
for x in d['source_refs']:
    e = entries[x['upstream_path']]
    b = (R/x['path']).read_bytes()
    lines = b.decode().splitlines()
    assert e['source'] == x['path']
    assert sha(b) == x['file_sha256'] == e['sourceSha256']
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == x['git_blob_sha1'] == e['source_blob'] == tree[x['upstream_path']]['sha']
    a, z = x['lines']
    assert 1 <= a <= z <= len(lines)
    assert sha('\n'.join(lines[a-1:z]).encode()) == x['range_text_sha256']
    previous = covered.setdefault(x['path'], set())
    new = set(range(a, z+1))
    assert not previous.intersection(new)
    previous.update(new)
assert len(d['source_refs']) == d['source_ranges'] == 40
assert len(covered) == d['unique_files'] == 33
assert sum(map(len, covered.values())) == d['cited_lines'] == 3665
assert sum(len(s) == len((R/p).read_text().splitlines()) for p,s in covered.items()) == d['full_files'] == 26
new = [x for x in d['source_refs'] if x['reading_context'] == 'actual_read049']
assert len(new) == d['prior_read_reuse']['new_ranges'] == 6
assert sum(x['lines'][1]-x['lines'][0]+1 for x in new) == 541
check_ref(d['prior_read_reuse']['evidence'])
for r in d['prior_read_reuse']['other_reuse_evidence']:
    check_ref(r)
check_ref(d['pending_overlap']['evidence'])

# Check the five quoted decisions only. Do not rerun the accepted ledger validator.
current = json.loads((R/d['dedup_snapshot']['path']).read_text())
index = {x['id']: x for x in current}
for comparison in d['dedup_snapshot']['comparisons']:
    actual = index[comparison['accepted_id']]
    assert all(actual[k] == value for k,value in comparison['complete_semantic_decision_read'].items())
mig = d['migration_overlap_screen']
mi = {x['candidate_id']: x for x in map(json.loads, (R/mig['path']).read_text().splitlines())}
for comparison in mig['comparisons']:
    actual = mi[comparison['accepted_id']]
    assert all(actual[k] == value for k,value in comparison['complete_semantic_decision_read'].items())
assert not any(d[k] for k in ['production_changes','runtime_executed','network_requests','master_changes','checklist_deletions','hours_claimed'])
receipt = {'created_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'PASS_ONCE_NEW049_FIXED_BINDINGS_ONLY', 'evidence': binding(path),
    'builder': binding(H/'build-batch-049.py'), 'verifier': binding(Path(__file__)),
    'commit_metadata': binding(cpath), 'tree_metadata': binding(tpath),
    'source_ranges':40, 'unique_files':33, 'full_files':26, 'cited_lines':3665,
    'new_read_ranges':6, 'new_read_lines':541, 'complete_saved_immune_judgments':5,
    'unchanged_migration_judgments':2, 'research_credit':0, 'maximum_pending_credit':0,
    'formal_count_at_evidence':d['baseline']['formal_count_observed'],
    'current_ledger_sha256_observed':sha((R/d['dedup_snapshot']['path']).read_bytes()),
    'old_verifier_or_ledger_validator_executed':False, 'upstream_or_runtime_executed':False,
    'pre_seal_attempt':'First new049 check stopped before receipt creation at metadata shape (cached Git commit endpoint has top-level tree). Corrected only unsealed verifier; no old passed checks rerun.',
    'scope':'Integrity of new049 evidence only. Hashes, tree membership and quoted decisions do not establish novelty or gameplay acceptance.'}
with out.open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'receipt':binding(out),'status':receipt['status'],'credit':0}))
