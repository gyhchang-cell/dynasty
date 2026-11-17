"""Independent integrity checks for one snapshot; never credits semantic review."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/cod4/audit-20261022/guard-ownership-research'
raw = (BASE / 'references.json').read_bytes()
rows = json.loads(raw)
sha = lambda b: hashlib.sha256(b).hexdigest()
errors = []
files = {}
for i, row in enumerate(rows):
    path = Path(row['source'])
    data = files.setdefault(str(path), path.read_bytes())
    if sha(data) != row['sourceSha256']:
        errors.append([i, 'source_hash'])
    if sha(row['text'].encode()) != row['excerptSha256']:
        errors.append([i, 'excerpt_hash'])
    snippet = '\n'.join(data.decode().splitlines()[row['start']-1:row['end']])
    if snippet.strip() != '\n'.join(row['text'].splitlines()).strip():
        errors.append([i, 'source_range'])
    normalized = re.sub(r'/\*.*?\*/|//[^\n]*', '', row['text'], flags=re.S)
    normalized = re.sub(r'\s+', '', normalized)
    if sha(normalized.encode()) != row['normalizedSha256']:
        errors.append([i, 'normalized_hash'])
    expected_url = f"https://github.com/{row['repo']}/blob/{row['commit']}/{row['path']}#L{row['start']}-L{row['end']}"
    if row['url'] != expected_url:
        errors.append([i, 'source_url'])
    if not re.fullmatch('[0-9a-f]{40}', row['commit']):
        errors.append([i, 'unpinned_commit'])
    if any(len(row.get(key, '')) < 16 for key in ('observation', 'application', 'limits')):
        errors.append([i, 'missing_observation'])
duplicate_fields = {}
for key in ('id', 'normalizedSha256'):
    duplicate_fields[key] = [value for value, count in Counter(r[key] for r in rows).items() if count > 1]
assert not errors, errors
assert not any(duplicate_fields.values()), duplicate_fields
report = {
    'date': datetime.datetime.now().astimezone().isoformat(),
    'snapshot_rows': len(rows), 'snapshot_sha256': sha(raw),
    'source_files': len(files), 'repositories': len({r['repo'] for r in rows}),
    'integrity_errors': errors, 'exact_or_normalized_duplicates': duplicate_fields,
    'semantic_review_credit_added_by_this_check': 0,
    'all_semantics_re_reviewed_by_coordinator': False,
    'gate_satisfied_by_hash_check_alone': False,
    'production_changed': False, 'game_started': False,
}
out = BASE / f"coordinator-integrity-{len(rows)}.json"
if out.exists():
    if json.loads(out.read_text())['snapshot_sha256'] != sha(raw):
        out = BASE / f"coordinator-integrity-{len(rows)}-{sha(raw)[:12]}.json"
if out.exists():
    assert json.loads(out.read_text())['snapshot_sha256'] == sha(raw), 'Do not replace another snapshot'
else:
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False))
