"""One coordinator review of a different chat's bounded semantic proposal.

One-shot evidence writer, not a production change or a candidate auto-promoter.
"""
from datetime import datetime, timezone
import hashlib
import json
from ledger import B, O, R, verify


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def main():
    proposal_path = O / 'reviewer-vallumraptor-hide-lease-proposal-20261102.json'
    review_path = O / 'independent-vallumraptor-hide-lease-review-20261102.json'
    acceptance_path = O / 'coordinator-vallumraptor-hide-lease-acceptance-20261102.json'
    assert not review_path.exists() and not acceptance_path.exists()
    proposal_raw = proposal_path.read_bytes()
    assert sha(proposal_raw) == '28bd287375d307340e6bf5d2f048382ff130909b89bac8b30e06e123398d18e1'
    p = json.loads(proposal_raw)
    ledger_path, dedup_path = O / 'reviewed.json', O / 'semantic-dedup.json'
    before, dedup_before = ledger_path.read_bytes(), dedup_path.read_bytes()
    assert sha(before) == p['ledger_sha256_at_proposal'] == '865dbbdaba8dea66a29d9d27f95841865b6e6328c0a91d9e3150a413e58a9f90'
    rows, dedup = json.loads(before), json.loads(dedup_before)
    assert len(rows) == 460 and p['ledger_count_at_proposal'] == 460
    assert p['accepted_credit'] == p['research_credit'] == 0
    assert p['proposed_maximum_credit'] == 1
    assert p['author_thread_id'] != p['review_owner_thread_id'] == '01a16364-cac0-7ca2-a042-a5312781ca34'
    assert p['semantic_key'] not in {r['semantic_dedup_key'] for r in rows}
    source = B / 'sources/AlexModGuy__AlexsCaves'
    manifest_raw, tree_raw = [(source / name).read_bytes() for name in ['source.json', 'tree.json']]
    assert sha(manifest_raw) == p['source_manifest_sha256']
    assert sha(tree_raw) == p['source_tree_sha256']
    meta, tree = json.loads(manifest_raw), json.loads(tree_raw)
    assert meta['commit'] == tree['sha'] == p['commit'] and not tree['truncated']
    manifest = {f['path']: f for f in meta['files']}
    blobs = {f['path']: f['sha'] for f in tree['tree'] if f['type'] == 'blob'}
    refs, checks = [], []
    for r in p['actual_source_ranges']:
        path = R / r['path']
        raw = path.read_bytes()
        rel, (lo, hi) = r['source_path'], r['lines']
        lines = raw.splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines) and path == source / rel
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert sha(raw) == r['file_sha256'] == manifest[rel]['sha256']
        assert blob == r['git_blob_sha1'] == manifest[rel]['git_blob_sha1'] == blobs[rel]
        assert sha(b''.join(lines[lo - 1:hi])) == r['excerpt_sha256']
        refs.append({k: r[k] for k in ['path', 'source_path', 'lines', 'file_sha256', 'url']})
        checks.append({**r, 'coordinator_actually_read': True, 'binding_matches': True,
                       'research_credit': 0})
    assert len(refs) == 14 and len({r['path'] for r in refs}) == 9
    comparisons = []
    for c in p['semantic_comparisons']:
        row = next(r for r in rows if r['id'] == c['key'])
        assert sha(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()) == c['full_record_sha256']
        comparisons.append({**c, 'coordinator_substantive_decision_fields_actually_read': True,
                            'coordinator_old_source_chain_reread': False, 'decision': 'distinct_complete_lifecycle'})
    assert len(comparisons) == 6
    clarifications = [
        'Numeric hideFor is the AI-target refusal gate. Local interpolated hideProgress is a separate graphic lifetime; '
        'progress updates before numeric decrement, so fading or translucent body does not establish current protection.',
        'Low-health trigger requires tame, retained live noncreative threat and nonpositive timer. Recovery requests occur '
        'earlier and may change eligibility; renewal is conditional, not guaranteed or a forever-safe state.',
        'Flee origin/timer are shared with chest theft and the separate wild-prey escape branch. afterSteal can replace '
        'them with a different origin and longer timer, so fleeing and hiding cannot be treated as one inseparable lease.',
        'Only the entry-selected threat receives revenge/last-hurt clear requests. The registered recurring Mob sweep '
        'clears only current target. The protected entity own melee predicate has no hide gate, but MOVE priority matters.',
        'Complete own subclass has no hide-specific hurt override. Bounded Dinosaur base identity/initialization reading '
        'does not prove absence of inherited or other listener protections. No universal damage or control immunity claimed.',
        'Coordinator reread every proposed source range, complete entity/renderer/melee and complete two target listeners; '
        'large registry/proxy ranges are limited binding declarations. Only alpha declaration and complete setter/render '
        'methods of model were read, not whole model/art. Six prior substantive decision records read, not six source chains.'
    ]
    observations = p['full_chain_observation'] + clarifications
    limits = p['limitations'] + [
        'All statements are bounded source analysis. Hashes, 14 ranges, 9 files, model alpha, held-item layer, HP threshold '
        'and different species provide zero separate credit. No actual sound, PNG, game, TCP, loaded registry or performance acceptance.',
        'Hidden graphic body is nominally10percent alpha, not full invisibility. Held item path has no same alpha parameter. '
        'Server guards differ across branches; neither event arbitration nor client/server convergence was exercised.'
    ]
    now = datetime.now(timezone.utc).isoformat()
    review = {
        'recorded_utc': now, 'reviewer_thread_id': p['review_owner_thread_id'],
        'proposal_author_thread_id': p['author_thread_id'],
        'proposal_path': str(proposal_path.relative_to(R)), 'proposal_sha256': sha(proposal_raw),
        'decision': 'ACCEPT_AT_MOST_ONE_COMPLETE_RENEWABLE_TARGET_REFUSAL_LEASE_FAMILY',
        'recommended_credit': 1, 'ledger_credit_written_by_this_review': 0,
        'semantic_key': p['semantic_key'], 'ledger_sha256_at_review': sha(before),
        'source_manifest_sha256': sha(manifest_raw), 'source_tree_sha256': sha(tree_raw),
        'source_commit': p['commit'], 'provenance_checks': checks,
        'complete_chain_observations': observations, 'semantic_comparisons': comparisons,
        'limitations': limits, 'production_changes': 0, 'art_changes': 0,
        'game_starts': 0, 'checklist_deletions': 0, 'duration_hours_claimed': 0
    }
    review_raw = encoded(review)
    row = {
        'id': p['semantic_key'], 'status': 'reviewed_effective', 'repo': p['repo'], 'commit': p['commit'],
        'category': 'native_health_qualified_renewable_target_refusal_lease_with_independent_flee_and_graphic_lifetimes',
        'semantic_dedup_key': p['semantic_key'],
        'count_unit': 'one semantically distinct complete implementation lifecycle; helpers/constants/graphics/bindings support0',
        'source_refs': refs, 'full_chain_observation': '\n'.join(observations),
        'concrete_observation': p['distinctness_argument'] + '\n' + '\n'.join(clarifications),
        'application_to_boss_immune': p['application_to_boss_immune'], 'limitations': '\n'.join(limits),
        'research_credit': 1, 'reviewed_utc': now,
        'independent_review': {'path': str(review_path.relative_to(R)), 'sha256': sha(review_raw), 'accepted_credit': 1}
    }
    rows.append(row)
    dedup['groups'].append({
        'family': 'health-qualified-renewable-native-target-refusal-lease-versus-body-fade-20261102',
        'credited_chains': [p['semantic_key']],
        'rationale': p['distinctness_argument'] + ' Timer, flee, recovery and graphic consumers count together as one family.'
    })
    assert ledger_path.read_bytes() == before and dedup_path.read_bytes() == dedup_before
    with review_path.open('xb') as stream:
        stream.write(review_raw)
    ledger_path.write_bytes(encoded(rows))
    dedup_path.write_bytes(encoded(dedup))
    verify()
    acceptance = {
        'recorded_utc': now, 'decision': review['decision'], 'new_effective_credit': 1,
        'prior_total': 460, 'accepted_total': 461, 'remaining': 539,
        'key': p['semantic_key'], 'prior_ledger_sha256': sha(before),
        'current_ledger_sha256': sha(ledger_path.read_bytes()),
        'proposal': {'path': str(proposal_path.relative_to(R)), 'sha256': sha(proposal_raw), 'immutable_history_retained': True},
        'independent_review': row['independent_review'], 'semantic_comparisons': comparisons,
        'clarifications': clarifications, 'production_changes': 0, 'art_changes': 0,
        'game_starts': 0, 'checklist_deletions': 0, 'duration_hours_claimed': 0,
        'formal_design_gate_satisfied': False
    }
    with acceptance_path.open('xb') as stream:
        stream.write(encoded(acceptance))
    print(json.dumps({'acceptance': str(acceptance_path.relative_to(R)),
                      'sha256': sha(acceptance_path.read_bytes()),
                      'review_sha256': sha(review_raw), 'current_ledger_sha256': sha(ledger_path.read_bytes()),
                      'accepted_total': 461, 'remaining': 539}))


if __name__ == '__main__':
    main()
