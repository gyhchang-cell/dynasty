"""Publish the coordinator's independently read whole recovery-policy decision."""
from datetime import datetime, timezone
import hashlib
import json
from accept_weedwood_20261103 import sha, encode, git
from ledger import O, R, verify


def main():
    proposal = R / 'docs/cod4/audit-20261022/program-feedback-review-20261101/immune-reference-batch-027.json'
    review_path = O / 'coordinator-cooperative-recovery-review-20261103.json'
    acceptance_path = O / 'coordinator-cooperative-recovery-acceptance-20261103.json'
    assert not review_path.exists() and not acceptance_path.exists()
    raw = proposal.read_bytes()
    assert sha(raw) == '318a028369d54067db99665cd3b92fa52ef4ba0358c9171dc98ecc18551a4218'
    p = json.loads(raw)
    assert p['status'] == 'candidate_whole_cooperative_downed_release_chain_pending_independent_review'
    assert type(p['research_credit']) is int and p['research_credit'] == 0
    assert type(p['maximum_proposed_credit']) is int and p['maximum_proposed_credit'] == 1
    lp, dp = O / 'reviewed.json', O / 'semantic-dedup.json'
    before, dbefore = lp.read_bytes(), dp.read_bytes()
    assert sha(before) == 'e5a17c70ca5de74e24a7684fd50044c5959edd25bfbdf387da832fb2486e00fb'
    rows, dedup = json.loads(before), json.loads(dbefore)
    assert len(rows) == 466
    key = p['semantic_family']
    assert key not in {r['semantic_dedup_key'] for r in rows}
    prov = p['provenance']
    manifest_raw = (R / prov['manifest_path']).read_bytes()
    assert sha(manifest_raw) == prov['manifest_sha256']
    meta = next(x for x in json.loads(manifest_raw) if x['repo'] == p['repo'])
    repo, commit = R / prov['bare_git_path'], p['commit']
    assert git(repo, 'rev-parse', commit + '^{commit}').decode().strip() == commit == meta['commit']
    assert git(repo, 'rev-parse', commit + '^{tree}').decode().strip() == prov['git_tree'] == meta['git_tree']
    files = {x['path']: x for x in meta['files']}
    checks, refs = [], []
    for ref in p['source_refs']:
        rel = ref['upstream_path']
        entry = files[rel]
        assert R / ref['path'] == R / entry['source']
        data = (R / ref['path']).read_bytes()
        assert sha(data) == ref['file_sha256'] == entry['sourceSha256']
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == ref['git_blob_sha1'] == entry['source_blob']
        assert git(repo, 'show', commit + ':' + rel) == data
        lo, hi = ref['lines']
        lines = data.splitlines(keepends=True)
        assert lo == 1 and hi == len(lines)
        checks.append({**ref, 'excerpt_sha256': sha(b''.join(lines)),
                       'coordinator_actual_complete_file_read': True,
                       'fixed_commit_blob_verified': True, 'support_credit': 0})
        refs.append({'path': ref['path'], 'source_path': rel, 'lines': [lo, hi],
                     'file_sha256': sha(data),
                     'url': f'https://github.com/{p["repo"]}/blob/{commit}/{rel}#L{lo}-L{hi}'})
    assert len(checks) == 22
    assert sum(x['lines'][1] for x in checks) == 1469
    by = {r['id']: r for r in rows}
    comparisons = []
    for item in p['dedup_snapshot']['comparisons']:
        current = by[item['accepted_id']]
        assert all(current.get(k) == v for k, v in item['full_semantic_decision_read'].items())
        comparisons.append({'id': current['id'],
                            'full_current_record_sha256': sha(json.dumps(current, ensure_ascii=False, sort_keys=True).encode()),
                            'substantive_decision_fields_actually_read': True,
                            'old_source_chain_reread': False,
                            'distinction': item['distinction']})
    assert len(comparisons) == 10
    screen = p['migration_overlap_screen']
    migration_path = R / screen['path']
    migration_before = migration_path.read_bytes()
    assert sha(migration_before) == screen['sha256']
    migration = [json.loads(line) for line in migration_before.splitlines() if line.strip()]
    assert len(migration) == screen['rows']
    migration_by = {r['candidate_id']: r for r in migration}
    for item in screen['comparisons']:
        current = migration_by[item['accepted_id']]
        assert all(current.get(k) == v for k, v in item['complete_semantic_decision_read'].items())
        assert current['status'] == 'rejected' and current['credit'] == 0
    clarifications = [
        'Accepted unit is one complete cooperative recovery policy: helper membership is sampled each active target tick to suspend the terminal bleed clock and integrate recovery progress, with recovery tested before expiry. Generic first-death cancellation, self-countdown DBNO, source category refusal, packets, numeric constants, defects and UI are all support0. This is not a second generic DBNO or a new presentation family.',
        'All22 cited files and1469 source lines were actually read in bounded outputs by the coordinator. The exact22 source_refs include metadata/resources; they are supporting context, not22 implementations. Commit/tree/blob/excerpts are separately checked, never extra reading credit. Ten old substantive semantic decisions and the one rejected migration decision were actually read; their old source chains were not reread.',
        'Actual registered listeners, state writes and client consumers close the mod-owned policy. CreativeCore2.11.20 serializer/transport, Forge listener composition/native interaction reach, native death/effect/pose/graphics/audio engines remain external. Static branch observations do not prove a working multiplayer rescue, rendered UI, successful sound or a reproduced defect.',
        'Server target ticking requires active policy, START/server side and target alive. Hurt and helper admission have different guards. Changing the active policy or target liveness can stop this tick while another listener still observes bleeding. No unconditional time progression or global cleanup guarantee is inferred.',
        'Helper retention uses numeric distance only here. It does not recheck dimension identity, alive/removed/bleeding state, sustained input or current ingredient; exhaustion is requested without payment success governing progress. Only native interaction admission can supply additional constraints, and those internals were not read.',
        'Optional consumed-item flag prevents another shrink, but later admission still checks main-hand ingredient. Item decrement precedes state flag and helper assignment in the branch; neither an atomic payment transaction nor an economically reachable Dynasty chain is accepted.',
        'Damage abort removes server membership without sending HelperPacket stop. The helper client only needs helpActive and a target UUID resolvable in its current world, not target bleeding/membership. Target reset iterates remaining helpers and cannot clear an already removed helper through that path. Default abortOnDamage is false; this observation is conditional and not runtime reproduced.',
        'Distance pruning explicitly sends stop, switching sends a replacement start, and first qualifying helper knock-out sends stop. Bypass death skips that block; already-bleeding death only clears its current helper list before returning there. No all-death/logout/dimension/session teardown promise is made. Inspected helper state declarations and writes have no explicit disconnect reset; no external platform cleanup is inferred.',
        'Revive clears authoritative state before requests for effects/health/sound and the revived event. Kill marks terminal bleeding before die and clears state afterward even if external death handling prevents death. Event comments, death request and acknowledgement are not proof of final death or protection against every external reentrant hook.',
        'getBleeding uses orElseGet(Bleeding::new), so absent capability can yield a fresh unretained state on each lookup; normal attach wiring is present but not a universal successful capability retrieval proof. Root persistent flag, NBT client synchronization and in-memory combat tracker copy remain unchanged rejected migration evidence0.',
        'Client overlay cleanup requires nonnull local player and actual callback; helper state is a separate stream from victim snapshot, with no dimension/session/sequence or queued absent-target recovery shown. No per-overlay-type filter is present. Empty sound.tick is not a finite-lifetime proof. Give-up receiver checks bleeding, not the client hold duration.',
        'No rescue or upstream optional ban/death/permission policy is installed in Dynasty. Study only informs explicit authority, participant qualification and complete feedback exits; Boss Immune still needs an actual final control-refusal reason. No ordinary-constitution gray text, art, UI button/background or production change.'
    ]
    observations = [x['stage'] + ': ' + x['observation'] for x in p['full_chain']] + clarifications
    limits = p['critical_boundaries'] + clarifications + [x['missing'] + ' ' + x['impact'] for x in p['native_gaps']]
    now = datetime.now(timezone.utc).isoformat()
    review = {'recorded_utc': now, 'reviewer_thread_id': '01a16364-cac0-7ca2-a042-a5312781ca34',
              'proposal_author_thread_id': '01a16392-312e-72f2-a4dd-56e184f9cb02',
              'proposal_path': str(proposal.relative_to(R)), 'proposal_sha256': sha(raw),
              'decision': 'ACCEPT_ONE_COMPLETE_COOPERATIVE_HELPER_GATED_RECOVERY_POLICY_WITH_EXPLICIT_LIMITS',
              'semantic_key': key, 'recommended_credit': 1, 'review_alone_ledger_credit': 0,
              'actual_source_checks': checks, 'semantic_comparisons': comparisons,
              'migration_rejection_preserved': screen,
              'complete_chain_observations': observations, 'limitations': limits,
              'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0, 'active_hours_claimed': 0}
    review_raw = encode(review)
    row = {'id': key, 'status': 'reviewed_effective', 'repo': p['repo'], 'commit': commit,
           'category': 'native_cooperative_membership_gated_terminal_refusal_release_and_feedback_exit',
           'semantic_dedup_key': key,
           'count_unit': 'one complete helper-membership recovery policy; generic DBNO and all presentation/support merged0 extra',
           'source_refs': refs, 'full_chain_observation': '\n'.join(observations),
           'concrete_observation': 'Live helper count controls both paused terminal countdown and accumulated recovery; release wins a simultaneous expiry tie. Helper admission/transfer/pruning and target release are actual consumers. Authority and helper-client acknowledgement have asymmetric exits. Distinct from self-timed DBNO, one-time idol membership, effect-strength group counts and quorum-armed independent victim timers; whole1 only.',
           'application_to_boss_immune': p['application'], 'limitations': '\n'.join(limits),
           'research_credit': 1, 'reviewed_utc': now,
           'independent_review': {'path': str(review_path.relative_to(R)), 'sha256': sha(review_raw), 'accepted_credit': 1}}
    rows.append(row)
    dedup['groups'].append({'family': 'continuous-helper-gated-recovery-policy-20261103',
                            'credited_chains': [key], 'rationale': row['concrete_observation']})
    assert lp.read_bytes() == before and dp.read_bytes() == dbefore and proposal.read_bytes() == raw
    assert migration_path.read_bytes() == migration_before
    with review_path.open('xb') as handle:
        handle.write(review_raw)
    lp.write_bytes(encode(rows))
    dp.write_bytes(encode(dedup))
    verify()
    assert json.loads(lp.read_bytes())[:-1] == json.loads(before)
    assert migration_path.read_bytes() == migration_before
    result = {'recorded_utc': now, 'decision': review['decision'], 'new_effective_credit': 1,
              'prior_total': 466, 'accepted_total': 467, 'remaining': 533,
              'prior_ledger_sha256': sha(before), 'current_ledger_sha256': sha(lp.read_bytes()),
              'old466_complete_records_identical': True, 'review': row['independent_review'],
              'proposal_sha256': sha(raw), 'old_migration_rejection_unchanged': True,
              'formal_design_gate_satisfied': False, 'native_acceptance': False,
              'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0, 'active_hours_claimed': 0}
    with acceptance_path.open('xb') as handle:
        handle.write(encode(result))
    print(json.dumps({'acceptance': str(acceptance_path.relative_to(R)),
                      'sha256': sha(acceptance_path.read_bytes()), 'accepted_total': 467,
                      'remaining': 533, 'ledger_sha256': sha(lp.read_bytes())}))


if __name__ == '__main__':
    main()
