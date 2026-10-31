"""Read-only source/excerpt checks; writes helper receipts, never runs game code."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[5]
DOC = ROOT/'docs/cod4/audit-20261022/immune-feedback-research/helpers/herschel-immune'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

from reference_evidence import reader
summaries = []
for batch in [60]:
    path = DOC/f'batch-{batch:03}.json'
    data = json.loads(path.read_text())
    receipt = json.loads((DOC/f'receipt-{batch:03}.json').read_text())
    files = json.loads((DOC/f'source-manifest-{batch:03}.json').read_text())['files']
    errors = []
    def check(value, message):
        if not value:
            errors.append(message)
    check(sha(path.read_bytes()) == receipt['batch_sha256'], 'batch receipt hash')
    check(data['research_credit'] == data['suggested_credit'] == data['effective_promoted'] == 0, 'no helper credit')
    method_refs = 0
    support_refs = 0
    focus_refs = 0
    for key, record in files.items():
        local = ROOT/record['local']
        raw = local.read_bytes()
        check(sha(raw) == record['sha256'], 'source SHA '+key)
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        check(blob == record['git_blob_sha1'], 'source blob '+key)
        base = ROOT/'tools/cod4/immune-feedback-research/helpers/herschel-immune'/f'sources-batch{batch:03}'/key.split('/')[0]
        if record.get('fixed_tree_verified'):
            tree = json.loads((base/'tree.json').read_text())
            check(tree['sha'] == record['commit'], 'tree pin '+key)
            entries = [x for x in tree['tree'] if x['path'] == record['path']]
            check(len(entries) == 1 and entries[0]['sha'] == blob, 'fixed tree blob '+key)
        else:
            metadata = json.loads((base/'source.json').read_text())
            entries = [x for x in metadata['files'] if x['path'] == record['path']]
            check(len(entries)==1 and entries[0]['sha256']==sha(raw), 'archive inventory SHA '+key)
            check(metadata['commit']==record['commit'] and metadata['archive_sha256']==record['archive_sha256'], 'archive fixed provenance '+key)
    for row in data['rows']:
        check(row['research_credit'] == row['suggested_credit'] == 0, 'row credit '+row['id'])
        for ref in row['source_refs']:
            raw = (ROOT/files[ref['source_key']]['local']).read_bytes()
            lines = raw.decode().splitlines(keepends=True)
            a,b = ref['lines']
            excerpt = ''.join(lines[a-1:b])
            check(excerpt == ref['excerpt'], 'source range '+row['id'])
            check(sha(excerpt.encode()) == ref['excerpt_sha256'], 'excerpt hash '+row['id'])
            check(sha(re.sub(r'\s+', '', excerpt).encode()) == ref['normalized_excerpt_sha256'], 'normalized excerpt '+row['id'])
            check(files[ref['source_key']]['commit'] in ref['url'] and ref['url'].endswith(f'#L{a}-L{b}'), 'fixed URL '+row['id'])
            check(sha(raw) == ref['file_sha256'], 'ref file hash '+row['id'])
            if 'decision_focus' in ref:
                focus_refs += 1
                f = ref['decision_focus']; x,y = f['lines']
                check(a <= x <= y <= b, 'focus range '+row['id'])
                focus = ''.join(lines[x-1:y])
                check(focus == f['excerpt'] and sha(focus.encode()) == f['excerpt_sha256'], 'focus hash '+row['id'])
            if ref['unit'] == 'complete_method':
                method_refs += 1
                check(reader['end_method'](lines,a) == b, 'lexical complete method '+row['id'])
                check('{' in excerpt and excerpt.rstrip().endswith('}'), 'method boundaries '+row['id'])
            else:
                support_refs += 1
    summary = dict(batch=batch, evidence_integrity_pass=not errors, errors=errors,
        batch_sha256=sha(path.read_bytes()), source_files=len(files),
        complete_method_references=method_refs, support_resource_references=support_refs,
        fixed_decision_focus_references=focus_refs,
        research_credit=0, semantic_review='Russell required; byte checks confer no credit',
        runtime_validation=False, upstream_code_executed=False)
    (DOC/f'integrity-{batch:03}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    summaries.append(summary)
print(json.dumps(summaries,ensure_ascii=False,indent=2))
if any(s['errors'] for s in summaries):
    raise SystemExit(1)
