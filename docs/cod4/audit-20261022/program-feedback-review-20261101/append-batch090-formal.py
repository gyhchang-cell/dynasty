"""One expressly authorized 090 append; no production or old087 execution."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import tempfile

BASE = Path('/Users/a15356015027/Desktop/dynasty')
ROOT = BASE / 'docs/cod4/audit-20261022'
WORK = ROOT / 'program-feedback-review-20261101'
FORMAL = ROOT / 'immune-feedback-research'
sha = lambda value: hashlib.sha256(value).hexdigest()
canon = lambda value: sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
load = lambda path: json.loads(path.read_text())

def bind(path):
    return {'path': str(path.relative_to(BASE)), 'sha256': sha(path.read_bytes())}

def exclusive(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

proposal = WORK / 'immune-reference-batch-090.json'
review = FORMAL / 'coordinator-eclipsed-prior-status-custody-review-20261109.json'
receipt = WORK / 'batch-090-formal-ledger-delta-20261109.json'
plan = WORK / 'batch-090-formal-append-plan-20261109.json'
assert not receipt.exists() and not plan.exists(), 'Single-use append: inspect existing artifacts, never rerun.'
assert sha(proposal.read_bytes()) == 'c73f0eb83a9a2c72dc7de00122e40b66e41c071bdaee86e6621c599dd5088abe'
assert sha(review.read_bytes()) == '062c2f1199b2dafd395db110cc0b4e0043c538041f45345bd93698c9726fddd6'
assert len(review.read_bytes()) == 176641
p, m = load(proposal), load(review)
key = p['semantic_dedup_key']
assert m['semantic_dedup_key'] == key
assert m['accepted_whole_research_credit'] == 1 and m['formal_credit_applied_by_Main'] == 0
auth = m['original_author_append_authorization']
assert auth['maximum_new_records'] == 1 and auth['expected_formal_before'] == m['formal_before'] == 494
assert auth['expected_if_successful'] == 495
assert auth['preserve_every_old_complete_record'] and auth['check_proposal_and_source_hashes']
assert auth['no_duplicate_semantic_key'] and auth['record_Mains_independent_judgment_and_limits']
assert auth['applicable1000_gate_still_unmet'] and auth['actual_author_receipt_required']
assert m['author_proposal']['sha256'] == sha(proposal.read_bytes())
assert m['author_observations'] == p['observations'] and m['author_limitations'] == p['limitations']

lp, gp, pp = [FORMAL / name for name in ('reviewed.json', 'semantic-dedup.json', 'progress.json')]
oldbytes = {path: path.read_bytes() for path in (lp, gp, pp)}
old, groups, progress = [json.loads(oldbytes[path]) for path in (lp, gp, pp)]
assert len(old) == 494
assert sha(oldbytes[lp]) == m['canonical_old_ledger_sha256'] == '737b5c9d4416f659a805eb60dca8f0a4e99442daa7f432abf9fe8041c55e7379'
old_row_hashes = [canon(row) for row in old]
assert old_row_hashes == m['canonical_old_rows_sha256'], 'Every complete old494 object must match Main, in order.'
assert progress['reviewed_effective_semantic_dedup'] == 494 and progress['remaining'] == 506
assert not progress['formal_design_gate_satisfied']
assert key not in {row['id'] for row in old} and key not in {row['semantic_dedup_key'] for row in old}
assert all(key not in group.get('credited_chains', []) for group in groups['groups'])

# Current 090 bytes only; no rereading/verifying previously accepted087 source chains.
for binding in (p['manifest'], p['provenance']['tree'], m['fixed_manifest'], m['fixed_API_tree']):
    assert sha((BASE / binding['path']).read_bytes()) == binding['sha256']
manifest = load(BASE / p['manifest']['path'])
tree = load(BASE / p['provenance']['tree']['path'])
assert not tree['truncated'] and tree['sha'] == p['provenance']['commit']
inventory = {entry['path']: entry for entry in manifest['files']}
blobs = {entry['path']: entry['sha'] for entry in tree['tree'] if entry['type'] == 'blob'}
assert len(m['actual_source_checks']) == len(p['source_refs']) == 14
for ref, check in zip(p['source_refs'], m['actual_source_checks']):
    assert check['source'] == ref and check['actual_Main_read']
    raw = (BASE / ref['path']).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    lines = raw.decode().splitlines()
    excerpt = '\n'.join(lines[ref['start_line'] - 1:ref['end_line']])
    assert sha(raw) == ref['sha256'] == inventory[ref['upstream_path']]['sha256']
    assert blob == ref['git_blob'] == inventory[ref['upstream_path']]['git_blob_sha1'] == blobs[ref['upstream_path']]
    assert sha(excerpt.encode()) == ref['range_sha256'] and excerpt == check['normalized_excerpt']
for comparison in m['complete_current_comparators']:
    prior = next(row for row in old if row['id'] == comparison['id'])
    assert canon(prior) == comparison['canonical_complete_record_sha256']
    assert canon(prior) == p['dedup']['complete_immune_decision_canonical_sha256'][comparison['id']]
# Verify retained ownership objects, without re-reviewing their source or claiming new credit.
migration_rows = [json.loads(line) for line in (ROOT / 'legacy-migration-acceptance/reviewed.jsonl').read_text().splitlines() if line.strip()]
for owner in m['migration_whole_owners_reused_zero']:
    current = next(row for row in migration_rows if row.get('candidate_id') == owner['candidate_id'])
    assert {field: current[field] for field in owner} == owner
for prior in m['prior_uncredited_complete_judgments_preserved']:
    artifact = BASE / prior['artifact']['path']
    assert sha(artifact.read_bytes()) == prior['artifact']['sha256']
    value = load(artifact)
    for component in prior['json_pointer'].strip('/').split('/'):
        value = value[int(component)] if isinstance(value, list) else value[component]
    assert value == prior['complete_saved_judgment'] and canon(value) == prior['canonical_sha256']

stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
refs = [dict(ref, source_path=ref['upstream_path'], lines=[ref['start_line'], ref['end_line']], file_sha256=ref['sha256'], url=ref['source_url']) for ref in p['source_refs']]
row = {
    'id': key, 'status': 'reviewed_effective',
    'repo': p['provenance']['repo'], 'commit': p['provenance']['commit'],
    'category': 'native_prior_status_set_custody_with_temporary_global_applicability_veto_and_exit_replay_attempt',
    'semantic_dedup_key': key, 'count_unit': p['count_unit'], 'source_refs': refs,
    'full_chain_observation': '\n'.join(p['observations']),
    'concrete_observation': '\n'.join(m['Main_independent_findings']),
    'application_to_boss_immune': m['application'],
    'limitations': '\n'.join(p['limitations'] + m['limits'] + [
        'Main limits above are preserved verbatim from its preappend494 review. This author now applies the single authorized090 record to495, not native/gameplay acceptance. Applicable1000 remains unmet; no production changes.',
        'No actual duration pause, hidden-chain preservation or restored/lost statuses proved. Modern NeoForge native ordering/merge/cancellation remains unread; Main Forge47.4.10 poison-smoke timing is not transferred.',
        '087 including its empty PlayerAbility.onTakeDamage override remains exactly unchanged. No reappend or old087 source re-audit.'
    ]),
    'author_observations': p['observations'], 'author_limitations': p['limitations'],
    'main_independent_findings': m['Main_independent_findings'],
    'main_whole_mechanism_dedup_decision': m['whole_mechanism_dedup_decision'],
    'main_preappend_limits_verbatim': m['limits'],
    'whole_mechanism_comparisons': p['dedup']['semantic_comparisons'],
    'complete_prior_decision_canonical_sha256': p['dedup']['complete_immune_decision_canonical_sha256'],
    'prior_zero_judgments_preserved': p['dedup']['prior_zero_whole_judgments'],
    'existing_migration_owners_preserved_zero_new': m['migration_whole_owners_reused_zero'],
    'independent_review': dict(bind(review), reviewer_thread_id=m['reviewer_thread_id'], accepted_whole_research_credit=1, whole_mechanism_dedup_decision=m['whole_mechanism_dedup_decision'], limits=m['limits'], native_acceptance=False),
    'author_proposal': bind(proposal), 'research_credit': 1, 'reviewed_utc': stamp
}
raw = oldbytes[lp]
closing = raw.rfind(b']')
assert closing >= 0 and raw[closing + 1:].strip() == b''
cut = closing
while cut > 0 and raw[cut - 1:cut].isspace():
    cut -= 1
prefix = raw[:cut]
assert prefix.endswith(b'}')
newtext = '\n'.join('  ' + line for line in json.dumps(row, ensure_ascii=False, indent=2).splitlines()).encode()
newledger = prefix + b',\n' + newtext + b'\n' + raw[closing:]
assert json.loads(newledger) == old + [row]
newgroups = json.loads(oldbytes[gp])
newgroups['groups'].append({
    'family': 'mowzie-whole-prior-status-set-custody-global-veto-exit-replay-20261109',
    'credited_chains': [key],
    'rationale': '\n'.join(m['whole_mechanism_dedup_decision']),
    'limits': m['limits'], 'independent_review': bind(review)
})
assert newgroups['groups'][:-1] == groups['groups']
newprogress = oldbytes[pp]
for before, after in [(b'"reviewed_effective_semantic_dedup": 494', b'"reviewed_effective_semantic_dedup": 495'), (b'"remaining": 506', b'"remaining": 505')]:
    assert newprogress.count(before) == 1
    newprogress = newprogress.replace(before, after, 1)
assert {k: v for k, v in json.loads(newprogress).items() if k not in ('reviewed_effective_semantic_dedup', 'remaining')} == {k: v for k, v in progress.items() if k not in ('reviewed_effective_semantic_dedup', 'remaining')}
planned = {lp: newledger, gp: (json.dumps(newgroups, ensure_ascii=False, indent=2) + '\n').encode(), pp: newprogress}
exclusive(plan, {
    'created_utc': stamp, 'authorization_source_thread_id': '01a16364-cac0-7ca2-a042-a5312781ca34',
    'scope': 'Live explicit Main delegation: single090 494->495, exact old494 objects, checked090 source/proposal/review bindings, no duplicate key. Dedup one group and progress two counters only. No production/game/task deletion.',
    'author_confirmation': 'I am the original090 author; I accept and preserve all Main independent findings, whole-policy decision and limits in the appended record. Semantic count1 only, no native acceptance. These checks passed before the actual append.',
    'proposal': bind(proposal), 'independent_review': bind(review),
    'before_hashes': {str(path.relative_to(BASE)): sha(value) for path, value in oldbytes.items()},
    'planned_after_hashes': {str(path.relative_to(BASE)): sha(value) for path, value in planned.items()},
    'old494_complete_objects_canonical_sha256': canon(old), 'all494_per_row_canonical_sha256': old_row_hashes,
    'new_object_canonical_sha256': canon(row), 'guards_passed': True, 'native_acceptance': False
})
for path, value in oldbytes.items():
    assert path.read_bytes() == value, 'Concurrent edit before mutation: abort.'
for path, value in planned.items():
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.batch090-', delete=False) as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
        tmp = stream.name
    os.chmod(tmp, path.stat().st_mode & 0o777)
    assert path.read_bytes() == oldbytes[path], 'Concurrent edit before replacement: abort.'
    os.replace(tmp, path)

after, ag, ap = [load(path) for path in (lp, gp, pp)]
assert len(after) == 495 and after[:-1] == old and after[-1] == row
assert [canon(value) for value in after[:-1]] == old_row_hashes
assert lp.read_bytes().startswith(prefix + b',\n')
assert len({value['id'] for value in after}) == len({value['semantic_dedup_key'] for value in after}) == 495
assert ag == newgroups and ag['groups'][:-1] == groups['groups']
assert sum(group.get('credited_chains', []).count(key) for group in ag['groups']) == 1
assert ap['reviewed_effective_semantic_dedup'] == 495 and ap['remaining'] == 505
assert not ap['formal_design_gate_satisfied']
assert bind(proposal) == row['author_proposal'] and bind(review)['sha256'] == row['independent_review']['sha256']
exclusive(receipt, {
    'schema_version': 1, 'created_utc': stamp,
    'decision': 'AUTHOR_SINGLE_GUARDED_APPEND_ONE_INDEPENDENTLY_ACCEPTED090_PENDING_MAIN_ACTUAL_DELTA_VERIFICATION',
    'applying_thread_id': '01a16392-312e-72f2-a4dd-56e184f9cb02',
    'authorization_source_thread_id': '01a16364-cac0-7ca2-a042-a5312781ca34',
    'authorization_and_author_confirmation': bind(plan), 'proposal': bind(proposal), 'independent_review': bind(review),
    'semantic_key': key, 'before_count': 494, 'after_count': 495, 'remaining': 505, 'new_credit_applied': 1,
    'old494_complete_objects_unchanged': True,
    'old494_complete_objects_canonical_sha256': canon(old), 'after_prefix494_canonical_sha256': canon(after[:-1]),
    'all494_per_row_canonical_sha256': old_row_hashes,
    'new_complete_object_canonical_sha256': canon(row),
    'old_byte_prefix_through_last_old_object_preserved': True,
    'old_dedup_groups_deep_unchanged': True, 'new_key_exactly_once_in_ledger_and_dedup': True,
    'progress_only_two_counter_fields_changed': True,
    'before_hashes': {str(path.relative_to(BASE)): sha(value) for path, value in oldbytes.items()},
    'after_hashes': {str(path.relative_to(BASE)): sha(path.read_bytes()) for path in planned},
    'Main_findings_decision_limits_preserved_verbatim': True,
    'all090_source_bindings_current': True,
    'main_actual_delta_verified': False, 'native_acceptance': False, 'no_old087_source_or_append_rerun': True,
    'production_changes': 0, 'master_task_list_changes': 0, 'checklist_deletions': 0,
    'background_changes': 0, 'shared_jar_changes': 0, 'game_starts': 0, 'network_requests': 0,
    'runtime_tests': 0, 'hours_claimed': 0
})
print(json.dumps({'receipt': bind(receipt), 'plan': bind(plan), 'formal_ledger': bind(lp), 'count': 495, 'remaining': 505, 'old494_deep_unchanged': True, 'main_actual_delta_verified': False}, ensure_ascii=False))
