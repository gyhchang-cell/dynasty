"""Verify only new048 fixed bindings; do not run any old verifier or ledger command."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
p = H / 'immune-reference-batch-048.json'
raw = p.read_bytes()
assert sha(raw) == 'b1dec92f9b924ee5ebcbb40becffbf2c2e89eaccaa04edfad2d219abd2044efd'
d = json.loads(raw)
v = d['provenances'][0]
mraw = (R / v['manifest_path']).read_bytes()
assert sha(mraw) == v['manifest_sha256']
m = next(x for x in json.loads(mraw) if x['repo'] == d['repo'])
craw = (R / v['commit_metadata_path']).read_bytes()
traw = (R / v['tree_metadata_path']).read_bytes()
assert sha(craw) == m['commit_metadata_sha256']
assert sha(traw) == m['tree_metadata_sha256']
c, t = json.loads(craw), json.loads(traw)
assert c['sha'] == d['commit'] == m['commit'] == v['commit']
assert c['tree']['sha'] == t['sha'] == m['git_tree'] == v['git_tree']
assert not t['truncated']
tree = {x['path']: x['sha'] for x in t['tree'] if x['type'] == 'blob'}
manifest = {x['path']: x for x in m['files']}
covered = {}
for s in d['source_refs']:
    b = (R / s['path']).read_bytes()
    e = manifest[s['upstream_path']]
    assert e['source'] == s['path']
    assert sha(b) == s['file_sha256'] == e['sourceSha256']
    blob = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
    assert blob == s['git_blob_sha1'] == e['source_blob'] == tree[s['upstream_path']]
    lines = b.decode().splitlines()
    a, z = s['lines']
    assert 1 <= a <= z <= len(lines)
    assert sha('\n'.join(lines[a-1:z]).encode()) == s['range_text_sha256']
    previous = covered.setdefault(s['path'], set())
    new = set(range(a, z+1))
    assert not previous.intersection(new)
    previous.update(new)
assert len(covered) == d['unique_files']
assert sum(map(len, covered.values())) == d['cited_lines']
assert sum(len(v) == len((R/k).read_text().splitlines()) for k, v in covered.items()) == d['full_files']
for field, is_jsonl, id_key in [('dedup_snapshot', False, 'id'), ('migration_overlap_screen', True, 'candidate_id')]:
    snapshot = d[field]
    b = (R / snapshot['path']).read_bytes()
    assert sha(b) == snapshot['sha256']
    rows = list(map(json.loads, b.decode().splitlines())) if is_jsonl else json.loads(b)
    lookup = {x[id_key]: x for x in rows}
    for comparison in snapshot['comparisons']:
        live = lookup[comparison['accepted_id']]
        assert all(live[k] == value for k, value in comparison['complete_semantic_decision_read'].items())
for field in ['accepted045_receipt', 'accepted045_review', 'accepted046_receipt', 'accepted046_review', 'accepted047_receipt', 'accepted047_review']:
    b = d['baseline'][field]
    assert sha((R / b['path']).read_bytes()) == b['sha256']
assert d['research_credit'] == 0 and d['maximum_proposed_credit'] == 1
receipt = {
    'created_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS', 'runs': 1,
    'evidence_sha256': sha(raw), 'source_ranges': len(d['source_refs']),
    'unique_files': d['unique_files'], 'full_files': d['full_files'], 'cited_lines': d['cited_lines'],
    'whole_immune_judgments': len(d['dedup_snapshot']['comparisons']),
    'whole_migration_judgments': len(d['migration_overlap_screen']['comparisons']),
    'scope': 'Only new048 provenance/ranges/saved-decision equality; no semantic approval, runtime acceptance or old ledger/verifier rerun.',
    'accepted_credit': 0, 'game_starts': 0, 'production_changes': False,
}
with (H / 'batch-048-integrity.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps(receipt, ensure_ascii=False))
