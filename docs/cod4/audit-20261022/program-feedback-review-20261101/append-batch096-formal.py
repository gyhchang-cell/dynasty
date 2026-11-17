"""One-use Main-authorized research intake. Never rerun after the start marker exists."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path

B = Path(__file__).resolve().parent
PLAN = B / 'batch-096-formal-append-plan-20261109.json'
EXPECTED_PLAN = '69c8fa629ba9a3c2fd4fba3d629dfc47f31c5fa9063dbef24edabe8c36a8f2eb'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def reference(path):
    return {'path': str(path), 'sha256': sha(Path(path).read_bytes())}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


assert sha(PLAN.read_bytes()) == EXPECTED_PLAN
plan = json.loads(PLAN.read_text())
for key in ('Main_receipt', 'proposal', 'actual_author_confirmation'):
    assert reference(plan[key]['path']) == plan[key]
main = json.loads(Path(plan['Main_receipt']['path']).read_text())
proposal = json.loads(Path(plan['proposal']['path']).read_text())
confirmation = json.loads(Path(plan['actual_author_confirmation']['path']).read_text())
assert main['maximum_related_whole_credit'] == 1
assert main['formal_credit_applied_by_this_receipt'] == 0
assert confirmation['author_thread_id'] == main['author_thread_id']
entry = plan['entry']
assert entry['author_observations'] == proposal['observations'] == main['author_observations_all14_retained']
assert entry['author_limitations'] == proposal['limitations'] == main['author_limits_all6_retained']
assert entry['main_independent_findings'] == main['independent_findings'] == confirmation['Main_findings_all13_verbatim']
assert entry['main_preappend_limits_verbatim'] == main['mandatory_limits'] == confirmation['Main_limits_all6_verbatim']
paths = {name: Path(ref['path']) for name, ref in plan['baseline'].items()}
raw = {name: path.read_bytes() for name, path in paths.items()}
for name, data in raw.items():
    assert sha(data) == plan['baseline'][name]['sha256'], 'Baseline changed: leave pending; no append'
old = {name: json.loads(data) for name, data in raw.items()}
ledger, dedup, progress = (old[name] for name in ('reviewed.json', 'semantic-dedup.json', 'progress.json'))
assert len(ledger) == 495
assert progress['reviewed_effective_semantic_dedup'] == 495 and progress['remaining'] == 505
assert not progress['formal_design_gate_satisfied']
assert [{'id': obj['id'], 'sha256': canonical(obj)} for obj in ledger] == plan['old495_complete_object_canonical_hashes']
assert [canonical(group) for group in dedup['groups']] == plan['old_dedup_group_canonical_hashes']
key = entry['semantic_dedup_key']
assert entry['id'] == key and entry['research_credit'] == 1
assert all(obj.get('id') != key and obj.get('semantic_dedup_key') != key for obj in ledger)
assert not any(key in json.dumps(group, ensure_ascii=False) for group in dedup['groups'])
assert not Path(plan['proof_path']).exists()
assert not Path(plan['one_time_start_marker']).exists()

# Keep every old ledger/group byte before the enclosing closing bracket.
ledger_end = raw['reviewed.json'].rfind(b'\n]')
dedup_end = raw['semantic-dedup.json'].rfind(b'\n  ]')
assert ledger_end >= 0 and raw['reviewed.json'][ledger_end:] == b'\n]\n'
assert dedup_end >= 0 and raw['semantic-dedup.json'][dedup_end:] == b'\n  ]\n}\n'
entry_text = '\n'.join('  ' + line for line in json.dumps(entry, ensure_ascii=False, indent=2).splitlines()).encode()
group_text = '\n'.join('    ' + line for line in json.dumps(plan['dedup_group'], ensure_ascii=False, indent=2).splitlines()).encode()
new_raw = {
    'reviewed.json': raw['reviewed.json'][:ledger_end] + b',\n' + entry_text + b'\n]\n',
    'semantic-dedup.json': raw['semantic-dedup.json'][:dedup_end] + b',\n' + group_text + b'\n  ]\n}\n',
    'progress.json': raw['progress.json'].replace(b'"reviewed_effective_semantic_dedup": 495', b'"reviewed_effective_semantic_dedup": 496', 1).replace(b'"remaining": 505', b'"remaining": 504', 1),
}
expected = copy.deepcopy(old)
expected['reviewed.json'].append(entry)
expected['semantic-dedup.json']['groups'].append(plan['dedup_group'])
expected['progress.json']['reviewed_effective_semantic_dedup'] = 496
expected['progress.json']['remaining'] = 504
for name, data in new_raw.items():
    assert json.loads(data) == expected[name]
assert json.loads(new_raw['reviewed.json'])[:495] == ledger
assert json.loads(new_raw['semantic-dedup.json'])['groups'][:-1] == dedup['groups']
assert not expected['progress.json']['formal_design_gate_satisfied']

# A persistent exclusive marker makes this grant single-use. Any interruption
# requires Main review of actual disk state, never a blind retry of this script.
with Path(plan['one_time_start_marker']).open('x') as handle:
    json.dump({'created_utc': now(), 'plan': reference(PLAN), 'baseline': plan['baseline'], 'rerun_forbidden': True}, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
for name, path in paths.items():
    assert path.read_bytes() == raw[name], 'Baseline changed during intake; stop and review actual disk state'
    temp = B / ('batch-096-' + name + '.atomic-staging')
    with temp.open('xb') as handle:
        handle.write(new_raw[name])
        handle.flush()
        os.fsync(handle.fileno())
    assert path.read_bytes() == raw[name]
    os.replace(temp, path)
    assert path.read_bytes() == new_raw[name]

after = {name: json.loads(path.read_bytes()) for name, path in paths.items()}
assert after == expected
assert after['reviewed.json'][:495] == ledger
assert [{'id': obj['id'], 'sha256': canonical(obj)} for obj in after['reviewed.json'][:495]] == plan['old495_complete_object_canonical_hashes']
assert after['semantic-dedup.json']['groups'][:-1] == dedup['groups']
assert len(after['reviewed.json']) == 496
assert sum(obj.get('research_credit', 0) for obj in after['reviewed.json']) == sum(obj.get('research_credit', 0) for obj in ledger) + 1
proof = {
    'schema_version': 1,
    'created_utc': now(),
    'status': 'actual_original_author_one_time_guarded_formal_research_delta_applied_pending_Main_actual_delta_verification',
    'batch': 96,
    'plan': reference(PLAN),
    'Main_receipt': plan['Main_receipt'],
    'actual_author_confirmation': plan['actual_author_confirmation'],
    'source_proposal_unchanged': plan['proposal'],
    'formal_before': 495,
    'formal_after': 496,
    'remaining': 504,
    'formal_design_gate_satisfied': False,
    'appended_id': key,
    'appended_complete_object_sha256': canonical(entry),
    'old495_complete_objects_preserved': True,
    'old495_complete_object_canonical_hashes': plan['old495_complete_object_canonical_hashes'],
    'old_ledger_byte_prefix_preserved_sha256': sha(raw['reviewed.json'][:ledger_end]),
    'old_ledger_byte_prefix_length': ledger_end,
    'old_dedup_groups_preserved': True,
    'old_dedup_byte_prefix_preserved_sha256': sha(raw['semantic-dedup.json'][:dedup_end]),
    'old_dedup_byte_prefix_length': dedup_end,
    'progress_only_changed_fields': plan['allowed_progress_changes'],
    'before': plan['baseline'],
    'after': {name: reference(path) for name, path in paths.items()},
    'author14observations6limits_Main13findings6limits_preserved_verbatim': True,
    'new_formal_related_whole_research_credit': 1,
    'ecology_migration_main_master_production_changes': 0,
    'native_gameplay_acceptance': False,
    'native_execution': 0,
    'network_requests': 0,
    'hours_claimed': 0,
    'rerun_forbidden': True,
}
with Path(plan['proof_path']).open('x') as handle:
    json.dump(proof, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
assert json.loads(Path(plan['proof_path']).read_text()) == proof
print(json.dumps({'proof': reference(plan['proof_path']), 'after': proof['after'], 'formal': 496, 'remaining': 504, 'gate': False}, ensure_ascii=False))
