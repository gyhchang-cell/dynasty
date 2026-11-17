"""Consume the separately authorized, frozen batch105 plan exactly once.

No source proof execution, rebase, retries, rollback, or production operations.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

ROOT = Path('/Users/a15356015027/Desktop/dynasty')
BASE = ROOT / 'docs/cod4/audit-20261022/program-feedback-review-20261101'
PLAN = BASE / 'batch-105-formal-append-plan-20261110.json'
REVIEW = ROOT / 'docs/cod4/audit-20261022/coordinator-program105-append-plan-review-20261110.json'
PLAN_SHA = '7fc4a680a57aa5743c213bd05ac6ad0104a628eb17f3def02effb39dafe70f92'
REVIEW_SHA = '8a7cd8ea4b14a1fe3f7ed5356c363b3a93d46b9c0532cff1bde05ac722dde103'
CONFIRM_SHA = '9a0f57d6842617a713b2c1db4d298f2c28dc439feaa5d5e8638357fbd669b8f2'


def require(condition, message):
    if not condition:
        raise RuntimeError('STOP: ' + message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode())


def absolute(name):
    p = Path(name)
    return p if p.is_absolute() else ROOT / p


def binding(p):
    raw = p.read_bytes()
    return {'path': str(p), 'sha256': digest(raw), 'bytes': len(raw)}


def exclusive_json(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def indented(value, spaces):
    return '\n'.join(' ' * spaces + line for line in
                     json.dumps(value, ensure_ascii=False, indent=2).splitlines()).encode()


require(digest(PLAN.read_bytes()) == PLAN_SHA, 'frozen plan drift')
require(digest(REVIEW.read_bytes()) == REVIEW_SHA, 'Main plan review drift')
plan = json.loads(PLAN.read_bytes())
review = json.loads(REVIEW.read_bytes())
require(review['plan']['sha256'] == PLAN_SHA, 'review plan binding')
require(review['actual_original_author_confirmation']['sha256'] == CONFIRM_SHA,
        'review author binding')
require(plan['actual_author_confirmation']['sha256'] == CONFIRM_SHA,
        'plan author binding')
require(review['planned_output_sha256'] == plan['planned_output_sha256'],
        'review output hashes')
require(review['baseline'] == plan['baseline'], 'review baseline')
def normalized_bindings(items):
    return [(str(absolute(v['path']).resolve()), v['sha256'], v['bytes']) for v in items]


require(normalized_bindings(review['verified_current_bindings']) ==
        normalized_bindings(plan['all_current_input_bindings']), 'review current inputs')
require(len(plan['all_current_input_bindings']) == 88, 'input count')

marker = absolute(plan['one_time_start_marker'])
proof = absolute(plan['proof_path'])
require(not marker.exists() and not proof.exists(), 'once marker/proof already exists')
names = ['reviewed.json', 'semantic-dedup.json', 'progress.json']
paths = {name: absolute(plan['baseline'][name]['path']) for name in names}
require(set(str(p.relative_to(ROOT)) for p in paths.values()) ==
        set(plan['allowed_formal_paths_after_later_explicit_authorization']),
        'exact three-path allowlist')


def verify_current_inputs():
    require(digest(PLAN.read_bytes()) == PLAN_SHA, 'plan drift before write')
    require(digest(REVIEW.read_bytes()) == REVIEW_SHA, 'Main receipt drift before write')
    actual = []
    for expected in plan['all_current_input_bindings']:
        raw = absolute(expected['path']).read_bytes()
        require(digest(raw) == expected['sha256'], 'input drift: ' + expected['path'])
        require(len(raw) == expected['bytes'], 'input length drift: ' + expected['path'])
        actual.append(expected)
    return actual


verified = verify_current_inputs()
before = {name: p.read_bytes() for name, p in paths.items()}
old_rows = json.loads(before['reviewed.json'])
old_dedup = json.loads(before['semantic-dedup.json'])
old_progress = json.loads(before['progress.json'])
require(len(old_rows) == 500 and len(old_dedup['groups']) == 228, '500/228 baseline')
require([row['id'] for row in old_rows] == plan['old500_complete_object_id_order'],
        'all old object order')
require({row['id']: canonical(row) for row in old_rows} ==
        plan['old500_complete_object_canonical_hashes'], 'all old complete objects')
require([canonical(group) for group in old_dedup['groups']] ==
        plan['old_dedup_group_canonical_hashes'], 'all old complete groups')
require(old_progress['reviewed_effective_semantic_dedup'] == 500 and
        old_progress['remaining'] == 500 and
        old_progress['formal_design_gate_satisfied'] is False, 'progress baseline')
require(canonical(plan['entry']) == plan['planned_entry_canonical_sha256'], 'entry')
require(canonical(plan['dedup_group']) == plan['planned_group_canonical_sha256'], 'group')
require(plan['entry']['id'] not in {row['id'] for row in old_rows}, 'duplicate entry')
encoding = plan['exact_future_encoding']
tail_rows = encoding['reviewed_tail_utf8'].encode()
tail_groups = encoding['dedup_tail_utf8'].encode()
require(before['reviewed.json'].endswith(tail_rows), 'ledger tail')
require(before['semantic-dedup.json'].endswith(tail_groups), 'dedup tail')
row_prefix = before['reviewed.json'][:-len(tail_rows)]
group_prefix = before['semantic-dedup.json'][:-len(tail_groups)]
require(digest(row_prefix) == encoding['old_ledger_prefix_sha256'] and
        len(row_prefix) == encoding['old_ledger_prefix_bytes'], 'ledger prefix')
require(digest(group_prefix) == encoding['old_dedup_prefix_sha256'] and
        len(group_prefix) == encoding['old_dedup_prefix_bytes'], 'dedup prefix')
after = {
    'reviewed.json': row_prefix + b',\n' + indented(plan['entry'], 2) + tail_rows,
    'semantic-dedup.json': group_prefix + b',\n' + indented(plan['dedup_group'], 4) + tail_groups,
}
progress_raw = before['progress.json']
for key, (old, new) in plan['allowed_progress_changes'].items():
    literal = ('"' + key + '": ' + str(old)).encode()
    require(progress_raw.count(literal) == 1, 'single literal: ' + key)
    progress_raw = progress_raw.replace(literal, ('"' + key + '": ' + str(new)).encode())
after['progress.json'] = progress_raw
new_rows = json.loads(after['reviewed.json'])
new_dedup = json.loads(after['semantic-dedup.json'])
new_progress = json.loads(after['progress.json'])
require(new_rows == old_rows + [plan['entry']], 'exact single row append')
require(new_dedup == {**old_dedup, 'groups': old_dedup['groups'] + [plan['dedup_group']]},
        'exact single group append')
require(new_progress == {**old_progress, 'reviewed_effective_semantic_dedup': 501,
                         'remaining': 499}, 'exact two-field progress change')
for name in names:
    require(digest(after[name]) == plan['planned_output_sha256'][name], 'planned SHA: ' + name)
    require(len(after[name]) == plan['planned_output_byte_lengths'][name], 'planned bytes: ' + name)

# Nothing above executes an old source validator or writes a formal file.
verified = verify_current_inputs()
require(not marker.exists() and not proof.exists(), 'once artifacts appeared')
script_binding = binding(Path(__file__).resolve())
marker_record = {
    'date': '2026-11-10', 'started_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'ONE_TIME_AUTHORIZATION_CONSUMED_DO_NOT_RERUN',
    'author_thread_id': '01a16392-312e-72f2-a4dd-56e184f9cb02',
    'Main_thread_id': '01a16364-cac0-7ca2-a042-a5312781ca34',
    'explicit_grant': 'Main delegated explicit once-only execution of frozen105 plan after independent plan review; 500 to501/remaining499/groups229/gatefalse only.',
    'plan': binding(PLAN), 'Main_plan_review': binding(REVIEW), 'script': script_binding,
    'verified_current_input_count': len(verified), 'formal_paths': [str(paths[n]) for n in names],
    'expected_outputs': plan['planned_output_sha256'], 'source_proofs_rerun': False,
    'retry_or_rebase_authorized': False,
    'pre_marker_guard_correction': 'Initial invocation stopped before marker or formal writes because literal Main relative paths differed from three plan absolute paths. Read-only follow-up verified all88 actual inputs unchanged; comparison now resolves paths while retaining exact order, SHA and bytes. No append had executed and no source proof reran.',
}
exclusive_json(marker, marker_record)
# An exception after marker creation permanently consumes this execution.
verify_current_inputs()
for name in names:
    with paths[name].open('r+b') as f:
        require(f.read() == before[name], 'formal file changed immediately before its write: ' + name)
        f.seek(0)
        f.write(after[name])
        f.truncate()
        f.flush()
        os.fsync(f.fileno())
    require(paths[name].read_bytes() == after[name], 'actual output differs: ' + name)

unchanged_inputs = []
formal_set = set(paths.values())
for expected in verified:
    p = absolute(expected['path'])
    if p not in formal_set:
        require(digest(p.read_bytes()) == expected['sha256'], 'postwrite nonformal drift: ' + str(p))
        unchanged_inputs.append(expected)
require(digest(PLAN.read_bytes()) == PLAN_SHA and digest(REVIEW.read_bytes()) == REVIEW_SHA,
        'postwrite plan/Main drift')
delta = {
    'date': '2026-11-10', 'completed_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'EXACT_FROZEN_ONE_WHOLE_APPEND_EXECUTED_PENDING_MAIN_READ_ONLY_ACCEPTANCE',
    'batch': 105, 'plan': binding(PLAN), 'Main_plan_review': binding(REVIEW),
    'actual_author_confirmation': plan['actual_author_confirmation'],
    'script': script_binding, 'consumed_once_marker': binding(marker),
    'all88_prewrite_current_input_bindings_verified': verified,
    'nonformal_inputs_unchanged_after': unchanged_inputs,
    'before': plan['baseline'], 'actual_after': {n: binding(paths[n]) for n in names},
    'actual_count_before': 500, 'actual_count_after': 501,
    'actual_remaining_after': 499, 'actual_groups_before': 228, 'actual_groups_after': 229,
    'old500_complete_object_hashes_preserved': plan['old500_complete_object_canonical_hashes'],
    'old500_complete_object_id_order_preserved': plan['old500_complete_object_id_order'],
    'old228_complete_group_hashes_preserved': plan['old_dedup_group_canonical_hashes'],
    'raw_prefixes_preserved': encoding, 'exact_appended_entry': plan['entry'],
    'exact_appended_group': plan['dedup_group'],
    'only_progress_field_changes': plan['allowed_progress_changes'],
    'formal_design_gate_satisfied': False, 'research_credit_appended': 1,
    'other_batches_107_106_104_credit': 0, 'source_proofs_rerun': False,
    'native_acceptance': False, 'production_changes': 0, 'game_starts': 0,
    'checklist_deletions': 0, 'Main_session_active_edits': 0, 'active_hours_claimed': None,
    'formal_mutated_paths': [str(paths[n]) for n in names],
    'script_and_marker_permanently_consumed': True,
    'pre_marker_guard_correction': marker_record['pre_marker_guard_correction'],
}
exclusive_json(proof, delta)
print(json.dumps({'proof': binding(proof), 'script': script_binding,
                  'marker': binding(marker), 'actual_after': delta['actual_after'],
                  'count': 501, 'remaining': 499, 'groups': 229, 'gate': False},
                 ensure_ascii=False, indent=2))
