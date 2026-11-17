"""Accept one independently read complete policy family; no production edits."""
from datetime import datetime, timezone
import hashlib
import json
import subprocess
from ledger import O, R, verify


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def git(repo, *args):
    return subprocess.check_output(['git', '--git-dir', str(repo), *args])


def main():
    proposal_path = R / 'docs/cod4/audit-20261022/program-feedback-review-20261101/immune-reference-batch-022.json'
    review_path = O / 'coordinator-weedwood-ignition-review-20261103.json'
    acceptance_path = O / 'coordinator-weedwood-ignition-acceptance-20261103.json'
    assert not review_path.exists() and not acceptance_path.exists()
    raw = proposal_path.read_bytes()
    assert sha(raw) == 'ce24be5b5799e65c12bafaa28357bbcd6b79adfc6b2206fdf9871ab088dcaff5'
    p = json.loads(raw)
    assert p['status'] == 'pending_independent_semantic_review'
    assert type(p['research_credit']) is int and p['research_credit'] == 0
    assert type(p['maximum_proposed_credit']) is int and p['maximum_proposed_credit'] == 1
    ledger_path, dedup_path = O / 'reviewed.json', O / 'semantic-dedup.json'
    before, dedup_before = ledger_path.read_bytes(), dedup_path.read_bytes()
    assert sha(before) == 'cdb188292332fa85a10fd3630b1d6db2c96b78b582f05c2a7a497032387e38f1'
    rows, dedup = json.loads(before), json.loads(dedup_before)
    assert len(rows) == 462
    key = p['semantic_family']
    assert key not in {r['semantic_dedup_key'] for r in rows}
    provenance = p['provenance']
    manifest_raw = (R / provenance['manifest_path']).read_bytes()
    assert sha(manifest_raw) == provenance['manifest_sha256']
    meta = next(m for m in json.loads(manifest_raw) if m['repo'] == p['repo'])
    repo = R / provenance['bare_git_path']
    commit = p['commit']
    assert git(repo, 'rev-parse', commit + '^{commit}').decode().strip() == commit == meta['commit']
    tree = git(repo, 'rev-parse', commit + '^{tree}').decode().strip()
    assert tree == meta['git_tree'] == provenance['git_tree']
    files = {f['path']: f for f in meta['files']}
    refs, checks = [], []
    for r in p['source_refs']:
        local = R / r['path']
        data = local.read_bytes()
        rel = r['upstream_path']
        m = files[rel]
        assert local == R / m['source']
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert sha(data) == r['file_sha256'] == m['sourceSha256']
        assert blob == r['git_blob_sha1'] == m['source_blob']
        assert git(repo, 'show', commit + ':' + rel) == data
        lo, hi = r['lines']
        lines = data.splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        url = f'https://github.com/{p["repo"]}/blob/{commit}/{rel}#L{lo}-L{hi}'
        refs.append({'path': r['path'], 'source_path': rel, 'lines': [lo, hi],
                     'file_sha256': sha(data), 'url': url})
        checks.append({**r, 'excerpt_sha256': sha(b''.join(lines[lo-1:hi])),
                       'coordinator_actual_range_read': True, 'fixed_commit_blob_verified': True,
                       'binding_credit': 0})
    assert len(refs) == 29
    by = {r['id']: r for r in rows}
    comparisons = []
    fields = ['id', 'category', 'semantic_dedup_key', 'full_chain_observation',
              'concrete_observation', 'limitations']
    for c in p['dedup_snapshot']['comparisons']:
        current = by[c['accepted_id']]
        assert all(current.get(f) == c['full_semantic_decision_read'].get(f) for f in fields)
        comparisons.append({'id': current['id'], 'full_record_sha256': sha(json.dumps(current, ensure_ascii=False, sort_keys=True).encode()),
                            'substantive_decision_fields_actually_read': True, 'old_source_chain_reread': False,
                            'distinction': c['distinction']})
    extra = {
        'mowzie-native-crane-teleport-qualified-invulnerability-versus-ignition':
            'Teleport ability owns entity damage/ignition rejection, not stack burning new-use refusal and passive durability erosion.',
        'betweenlands-native-collision-derived-phasing-suffocation-refusal-and-equipment-time-budget-exit-request':
            'Collision-derived player eligibility, separate energy/time budget and return request are distinct from burning own shield and conditional break-path salvage.',
        'betweenlands-native-refused-hit-refractory-window-suppresses-damage-wakeup-with-independent-environment-activation':
            'Dormant entity damage-wake refractory eligibility is not shield activation refusal or carried/dropped stack destruction.'
    }
    for k, distinction in extra.items():
        current = by[k]
        comparisons.append({'id': k, 'full_record_sha256': sha(json.dumps(current, ensure_ascii=False, sort_keys=True).encode()),
                            'substantive_decision_fields_actually_read': True, 'old_source_chain_reread': False,
                            'distinction': distinction})
    assert len(comparisons) == 10
    clarifications = [
        'Ignition refuses NEW right-click activation only. Inherited current-use admission does not read burningTicks, but native use reevaluation, durability callbacks and the earlier ordinary disable branch remain unexpanded; continued successful blocking is not proven.',
        'Timer assignment is not max/extend: an80 assignment can shorten120. Ignition uses trueSource and the attacker ACTIVE stack, not arbitrary fire damage, immediate projectile identity or mainhand alone.',
        'Carried and dropped erosion have different native calls and cleanup. Neither shown path invokes the subclass salvage callback explicitly. Native destruction hooks, creative/enchantment handling and callback order were not expanded.',
        'Exact zero permits explicit break-path mask placement; negative timer is not burning but still fails exact-zero salvage. Parent clears current active-hand slot while subclass fills the passed hand; no reproduced inventory loss or guaranteed salvage outcome.',
        'Spit capability, cooldown, current-hand packet, renderer and registrations are support0. Capability does not implement ISerializableCapability; full native disk/copy lifecycle is not established. Status30 and overlay are not block, destruction, projectile-add or hit acknowledgments.',
        'Coordinator actually read all29 cited ranges in bounded outputs: full mod-owned core classes and specified registration/entry contexts. Registry/proxy contexts are partial; ClientProxy.postInit method was complete. MessageEntity/Base are shared supporting transport, no second credit.',
        'Seven proposal decision snapshots were actually read then checked equal to current462 ledger substantive fields; three additional current decision records were actually read. The four newest unrelated large records had a clipped combined output and are not claimed as complete additional comparisons. No old source chain was reread for dedup.'
    ]
    limits = p['critical_boundaries'] + clarifications + [
        'Fixed1.12 source is comparative research, not drop-in compatibility or native1.20 verification. Whole policy family earns at most1;29 ranges, classes, inherited ordinary shield logic, native calls, graphics and integrity checks earn0 separately.',
        'No Java/Gradle/game/network execution, audio/pixel acceptance, specialist asset work, production patch, sharedJar/world/checklist modification or duration claim.'
    ]
    observations = [x['stage'] + ': ' + x['observation'] for x in p['full_chain']] + clarifications
    now = datetime.now(timezone.utc).isoformat()
    review = {
        'recorded_utc': now, 'reviewer_thread_id': '01a16364-cac0-7ca2-a042-a5312781ca34',
        'proposal_author_thread_id': '01a16392-312e-72f2-a4dd-56e184f9cb02',
        'proposal_path': str(proposal_path.relative_to(R)), 'proposal_sha256': sha(raw),
        'decision': 'ACCEPT_ONE_COMPLETE_STACK_IGNITION_ACTIVATION_EROSION_SALVAGE_POLICY',
        'recommended_credit': 1, 'review_alone_ledger_credit': 0, 'semantic_key': key,
        'ledger_sha256_at_review': sha(before), 'provenance': provenance,
        'actual_source_checks': checks, 'semantic_comparisons': comparisons,
        'complete_chain_observations': observations, 'limitations': limits,
        'game_starts': 0, 'production_changes': 0, 'checklist_deletions': 0,
        'active_hours_claimed': 0
    }
    review_raw = encode(review)
    row = {
        'id': key, 'status': 'reviewed_effective', 'repo': p['repo'], 'commit': commit,
        'category': 'native_stack_ignition_new_activation_refusal_with_passive_erosion_and_conditional_break_salvage',
        'semantic_dedup_key': key,
        'count_unit': 'one complete semantically distinct policy lifecycle; inherited shield and all helper/feedback variants support0',
        'source_refs': refs, 'full_chain_observation': '\n'.join(observations),
        'concrete_observation': 'Per-stack burning NBT refuses new activation while current inherited block qualification remains unchanged in this class. Separate carried/dropped native erosion paths and exact-zero explicit salvage form one ownership lifecycle, distinct from timed parry, finite-hit disarm, paid rearm or shared-wearer charge admission.',
        'application_to_boss_immune': p['application'], 'limitations': '\n'.join(limits),
        'research_credit': 1, 'reviewed_utc': now,
        'independent_review': {'path': str(review_path.relative_to(R)), 'sha256': sha(review_raw), 'accepted_credit': 1}
    }
    rows.append(row)
    dedup['groups'].append({'family': 'stack-ignition-new-use-refusal-and-passive-erosion-20261103',
                            'credited_chains': [key], 'rationale': row['concrete_observation']})
    assert ledger_path.read_bytes() == before and dedup_path.read_bytes() == dedup_before
    with review_path.open('xb') as f:
        f.write(review_raw)
    ledger_path.write_bytes(encode(rows))
    dedup_path.write_bytes(encode(dedup))
    verify()
    assert json.loads(ledger_path.read_bytes())[:-1] == json.loads(before)
    acceptance = {
        'recorded_utc': now, 'decision': review['decision'], 'new_effective_credit': 1,
        'prior_total': 462, 'accepted_total': 463, 'remaining': 537,
        'prior_ledger_sha256': sha(before), 'current_ledger_sha256': sha(ledger_path.read_bytes()),
        'proposal': {'path': str(proposal_path.relative_to(R)), 'sha256': sha(raw), 'unchanged': True},
        'review': row['independent_review'], 'old462_records_identical': True,
        'formal_design_gate_satisfied': False, 'production_changes': 0, 'game_starts': 0,
        'checklist_deletions': 0, 'active_hours_claimed': 0
    }
    with acceptance_path.open('xb') as f:
        f.write(encode(acceptance))
    print(json.dumps({'acceptance': str(acceptance_path.relative_to(R)),
                      'sha256': sha(acceptance_path.read_bytes()), 'accepted_total': 463,
                      'remaining': 537, 'ledger_sha256': acceptance['current_ledger_sha256']}))


if __name__ == '__main__':
    main()
