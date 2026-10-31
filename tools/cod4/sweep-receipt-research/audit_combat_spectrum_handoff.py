"""Main-owned integrity audit; judgments remain explicit in reviews/batch-097/098.

Checking context hashes is not human semantic review and awards no credit.
Never modifies helper-owned files.
"""
from pathlib import Path
import json, hashlib, datetime, collections

R = Path(__file__).resolve().parents[3]
O = R / 'docs/cod4/audit-20261022/sweep-receipt-research'
H = O / 'helpers/combat-spectrum'
sha = lambda b: hashlib.sha256(b).hexdigest()
batch = json.loads((H / 'batch-001.json').read_text())['records']
contexts = json.loads((H / 'evidence-contexts.json').read_text())['evidence']
errors = []
sources = {}
for label, r in [(str(i), r) for i, r in enumerate(batch)] + list(contexts.items()):
    raw = (R / r['source_local']).read_bytes()
    text = '\n'.join(raw.decode().splitlines()[r['line']-1:r['end_line']])
    if sha(raw) != r['source_sha256']:
        errors.append([label, 'source_sha256'])
    if sha(r['excerpt'].encode()) != r['snippet_sha256']:
        errors.append([label, 'snippet_sha256'])
    if text.strip() != r['excerpt'].strip():
        errors.append([label, 'range_excerpt'])
    sources[r['source_local']] = r['source_sha256']
for i, r in enumerate(batch):
    for key in r['support_evidence']:
        if key not in contexts:
            errors.append([i, 'missing_support', key])
rows = [json.loads(line) for line in (O / 'reviewed.jsonl').read_text().splitlines()]
merged = [r for r in rows if r.get('helper_provenance', {}).get('batch', '').endswith('combat-spectrum/batch-001.json')]
assert len(merged) == len(batch) == 29
assert not errors, errors
report = {
    'generated_at': datetime.datetime.now().astimezone().isoformat(),
    'helper_files_modified': False,
    'input_hashes': {name: sha((H/name).read_bytes()) for name in ('HANDOFF.md', 'batch-001.json', 'evidence-contexts.json', 'source-manifest.json')},
    'proposed_records': len(batch), 'source_files_integrity_checked': len(sources),
    'support_contexts_integrity_checked': len(contexts), 'integrity_errors': errors,
    'integrity_check_awards_credit': 0,
    'all_291_contexts_human_reviewed': False,
    'human_review_boundary': '主方法29条全文独立复核；按实际链阅读相关支持方法。291段只对字节/全文行范围统一检查，未声称291段均人工语义研究，也不计291信用。',
    'main_decisions': dict(collections.Counter(r['decision'] for r in merged)),
    'main_authored_reviews': ['reviews/batch-097.json', 'reviews/batch-098.json'],
    'accepted_methods_source_pin_evidence': 'accepted.jsonl: pin_verification; remote-pins.json',
    'decisions': [{k:r[k] for k in ('candidate_index', 'candidate_id', 'repo', 'revision', 'path', 'line', 'end_line', 'source_sha256', 'decision', 'observation', 'credit')} for r in merged],
    'dedup_boundary': 'BetterCombat两端合为7369一链；普通比较器、观察者式检测、离线补产、裂纹传送门、Idol普通冷却、箭矢模板、浮动方块模板不新增信用。',
    'production_changed': False, 'external_runtime_tested': False,
}
out = O / 'combat-spectrum-main-review.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('proposed_records', 'source_files_integrity_checked', 'support_contexts_integrity_checked', 'main_decisions', 'integrity_errors')}, ensure_ascii=False))
