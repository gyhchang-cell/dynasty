"""Read-only verification of the delivered batch, without importing upstream code."""
from pathlib import Path
import hashlib
import json
from inspect_methods import end_method

ROOT = Path(__file__).resolve().parents[5]
DOCS = ROOT/'docs/cod4/audit-20261022/immune-feedback-research/helpers/halley-immune'
batch = json.loads((DOCS/'batch-001.json').read_text())
verification = json.loads((DOCS/'verification-001.json').read_text())
required = {'repo','revision','path','source_local','source_sha256','line','end_line',
            'excerpt','observation','application','limits','url'}
ids = set()
spans = 0
for row in batch['records']:
    assert required <= row.keys()
    assert row['id'] not in ids
    ids.add(row['id'])
    assert row['research_credit'] == row['suggested_credit'] == row['master_credit'] == 0
    for ref in row['source_refs']:
        assert required <= ref.keys()
        p = Path(ref['source_local'])
        data = p.read_bytes()
        lines = data.decode('utf-8').splitlines(keepends=True)
        assert hashlib.sha256(data).hexdigest() == ref['source_sha256'], p
        a,z = ref['line'], ref['end_line']
        assert 1 <= a <= z <= len(lines)
        assert ''.join(lines[a-1:z]) == ref['excerpt'], (p,a,z)
        if ref['unit'] == 'complete_method':
            assert end_method(lines,a) == z, (p,a,z)
        else:
            assert ref['unit'] == 'complete_file' and a == 1 and z == len(lines)
        if 'source_original_local' in ref:
            assert Path(ref['source_original_local']).read_bytes() == data
        spans += 1
assert spans == batch['evidence_span_count']
assert len(ids) == batch['total_family_record_count'] == 4
assert batch['audited_family_count'] == 3 and batch['partial_candidate_family_count'] == 1
assert batch['promotable_suggestion_count'] == batch['research_credit'] == batch['master_credit'] == 0
assert len(verification['files']) == verification['source_file_count']
archive = verification['archive']
assert hashlib.sha512(Path(archive['source_local']).read_bytes()).hexdigest() == archive['sha512']
print(f'PASS: {len(ids)} family records ({batch["partial_candidate_family_count"]} partial); '
      f'{spans} evidence ranges; {verification["source_file_count"]} source files; '
      'zero suggested/master credits; no upstream execution.')
