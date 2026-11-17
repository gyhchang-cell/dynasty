"""Record actual independent whole-chain source review, never native execution."""
from datetime import datetime, timezone
import hashlib
import json
from accept_weedwood_20261103 import sha, encode, git
from ledger import O, R, verify


def main():
    proposal = R / 'docs/cod4/audit-20261022/program-feedback-review-20261101/immune-reference-batch-024.json'
    review_path = O / 'coordinator-cumulative-conduction-review-20261103.json'
    acceptance_path = O / 'coordinator-cumulative-conduction-acceptance-20261103.json'
    assert not review_path.exists() and not acceptance_path.exists()
    raw = proposal.read_bytes()
    p = json.loads(raw)
    assert p['status'] == 'pending_independent_semantic_review'
    assert type(p['research_credit']) is int and p['research_credit'] == 0
    assert type(p['maximum_proposed_credit']) is int and p['maximum_proposed_credit'] == 1
    lp, dp = O / 'reviewed.json', O / 'semantic-dedup.json'
    before, dbefore = lp.read_bytes(), dp.read_bytes()
    assert sha(before) == 'e19796076f0e7ecdff556cc9dea05b9b7fcd68d67ed94544dffd68acf2976ff3'
    rows, dedup = json.loads(before), json.loads(dbefore)
    assert len(rows) == 464
    key = p['semantic_family']
    assert key not in {r['semantic_dedup_key'] for r in rows}
    prov = p['provenance']
    manifest_raw = (R / prov['manifest_path']).read_bytes()
    assert sha(manifest_raw) == prov['manifest_sha256']
    manifest = next(x for x in json.loads(manifest_raw) if x['repo'] == p['repo'])
    repo, commit = R / prov['bare_git_path'], p['commit']
    assert git(repo, 'rev-parse', commit + '^{commit}').decode().strip() == commit == manifest['commit']
    assert git(repo, 'rev-parse', commit + '^{tree}').decode().strip() == manifest['git_tree'] == prov['git_tree']
    files = {x['path']: x for x in manifest['files']}
    earlier = [json.loads((R / f'docs/cod4/audit-20261022/program-feedback-review-20261101/immune-reference-batch-{n:03}.json').read_text()) for n in [22, 23]]
    checks, refs = [], []
    exact_reuse = {6, 16, 30, 31, 32, 33, 34, 35}
    for i, ref in enumerate(p['source_refs']):
        data = (R / ref['path']).read_bytes()
        rel, (lo, hi) = ref['upstream_path'], ref['lines']
        entry = files[rel]
        assert R / ref['path'] == R / entry['source']
        assert sha(data) == ref['file_sha256'] == entry['sourceSha256']
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == ref['git_blob_sha1'] == entry['source_blob']
        assert git(repo, 'show', commit + ':' + rel) == data
        lines = data.splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        if i in exact_reuse:
            assert any(x['path'] == ref['path'] and x['file_sha256'] == ref['file_sha256'] and x['lines'][0] <= lo <= hi <= x['lines'][1] for old in earlier for x in old['source_refs'])
        read_mode = 'new actual full cited range read'
        if i in exact_reuse:
            read_mode = 'identical actual same-turn022/023 cited range reused; zero repeat-reading credit'
        elif i == 8:
            read_mode = 'actual new84..157 plus same-turn02329..83 and158..167 together cover29..167'
        elif i == 10:
            read_mode = 'actual new65 plus same-turn02366..100 together cover65..100'
        checks.append({**ref, 'excerpt_sha256':sha(b''.join(lines[lo-1:hi])),
                       'actual_current_turn_source_read_mode':read_mode,
                       'source_identity_verified':True, 'support_credit':0})
        refs.append({'path':ref['path'], 'source_path':rel, 'lines':[lo,hi], 'file_sha256':sha(data),
                     'url':f'https://github.com/{p["repo"]}/blob/{commit}/{rel}#L{lo}-L{hi}'})
    assert len(checks) == 36
    by = {row['id']:row for row in rows}
    comparisons = []
    for item in p['dedup_snapshot']['comparisons']:
        row = by[item['accepted_id']]
        assert all(row.get(field) == item['full_semantic_decision_read'].get(field) for field in ['id','category','semantic_dedup_key','full_chain_observation','concrete_observation','limitations'])
        comparisons.append({'id':row['id'], 'full_record_sha256':sha(json.dumps(row,ensure_ascii=False,sort_keys=True).encode()),
                            'substantive_decision_fields_actually_read':True, 'old_source_chain_reread':False,
                            'distinction':item['distinction']})
    assert len(comparisons) == 6
    for item in p['pending_peer_comparison']:
        peer_raw = (R / item['path']).read_bytes()
        assert sha(peer_raw) == item['sha256']
        peer = json.loads(peer_raw)
        assert peer['semantic_family'] == item['semantic_family']
        assert by[peer['semantic_family']]['research_credit'] == 1
        comparisons.append({'id':peer['semantic_family'], 'status_now':'already independently accepted earlier this same turn, not pending',
                            'substantive_decision_fields_actually_read':True,
                            'old_source_chain_reread':False, 'distinction':item['distinction'],
                            'correction':'Original pending label preserved only as historical proposal state; no credit transfer. Shared rubber boots or transport helpers0.'})
    migration = p['migration_overlap_screen']
    migration_raw = (R / migration['path']).read_bytes()
    assert sha(migration_raw) == migration['sha256']
    migration_rows = [json.loads(line) for line in migration_raw.splitlines() if line.strip()]
    assert len(migration_rows) == migration['rows']
    migration_by = {row['candidate_id']:row for row in migration_rows}
    migration_checks = []
    for item in migration['comparisons']:
        row = migration_by[item['candidate_id']]
        assert all(row.get(field) == value for field, value in item['full_semantic_decision_read'].items())
        migration_checks.append({'candidate_id':row['candidate_id'], 'actual_full_semantic_decision_read':True,
                                 'old_source_chain_reread':False, 'distinction':item['distinction']})
    clarifications = [
        'Cave-jelly producer is a mod-owned update caller: its own conditional has no explicit server-only guard, starts shock with source and initial seed both itself, ignores spawn return, and emits sound independently. Source lifetime is not guarded in EntityShock beyond nonnull. Actual engine scheduling/client duplication and accepted spawn are unproved.',
        'maxJumps is a three-tick round budget, not number of victims. All previous roots and passengers remain cumulative conductors even when insulated or hurt refused. Each old node may select one new candidate per round, and empty rounds still consume budget. Wet source controls initial round budget; current node wetness separately controls expansion radius and damage multiplier.',
        'Candidate sorting starts at index1 as if self occupied0; tied positions or filtering can invalidate that assumption. Lowermost-living riding roots are excluded by the shown predicate, not a universally normalized unique mount identity. This is exact source behavior, not guaranteed nearest-target fairness.',
        'Selection and edge insertion precede all equipment and damage outcomes. Every nonempty ItemRubberBoots in the equipment-and-armor iterable receives damageItem2; the predicate is not feet-only and does not stop after the first stack. Breaking a boot during that call leaves current blocked flag true. Native damageItem durability/destruction is external and no actual break was executed.',
        'wasShocked follows root attackEntityFrom return when not insulated. Root false or insulation requests the registered SHOCKED potion; root hurttrue skips this fallback. Recursive living passengers are attacked and enrolled even if root hurtfalse, with no own rubber check or edge and no own negative-hurt fallback. Direct potion request does not certify final admission, hard input stun or successful control.',
        'ElixirShocked contributes movement attribute modifier-0.95 operation2 and a probabilistic server tick status message. Exact final movement, tick expiry, native addPotionEffect readiness/admission and NoAI/input behavior are not certified. Direct shock route does not post SplashPotionEvent; delivery-veto semantics remain owned by earlier017.',
        'MessageEntity writes byte count, reads signedbyte and compacts missing current-world integer IDs; chain consumer pairs the compacted list. Missing endpoints may change pair associations. A hypothetical128-entry count may decode as negative and yield no entities, not proof actual oversized traffic/crash. No UUID/epoch/sequence/refusal reason/success ACK is supplied.',
        'Topology cue is independent of hurt/effect success, uses fixed current endpoint vectors, and is not target-tethered over particle life. ParticleFactory admission return, renderer queue capacity, alive filtering and later world-render tick all remain separate from packet production. maxAge5 is source state, not five rendered frames. Beam blend/depthMask settings are bounded state observations, not complete renderer/native depth or pixel/audio proof.',
        'The actual mod lifecycle calls registerEventHandlers at183 and proxy.registerEventHandlers at230, both inside already-read lifecycle ranges. ClientProxy960..970 registers WorldRenderHandler; only cited bounded renderer/factory ranges are read. Sound registry producer and client request do not certify BLSoundEvent internals, audio assets or actual playback. Alternative arrow damage branch was read inside complete EntityShock but its complete arrow creation lifecycle not researched separately.',
        'One complete policy is cumulative propagation through denied-damage roots plus conditional status request and result-independent edge feedback. Six old whole semantic decisions and two newly accepted same-turn022/023 decisions compared, one migration rubber-boat false-positive decision read. Their old source chains were not reread. Source wrappers, effects, packets, registry, particle factory and shared rubber class each contribute0 extra.'
    ]
    observations = [item['stage'] + ': ' + item['observation'] for item in p['full_chain']] + clarifications
    limits = p['critical_boundaries'] + clarifications
    now = datetime.now(timezone.utc).isoformat()
    review = {'recorded_utc':now,'reviewer_thread_id':'01a16364-cac0-7ca2-a042-a5312781ca34',
              'proposal_author_thread_id':'01a16392-312e-72f2-a4dd-56e184f9cb02',
              'proposal_path':str(proposal.relative_to(R)),'proposal_sha256':sha(raw),
              'decision':'ACCEPT_ONE_CUMULATIVE_CONDUCTION_NEGATIVE_HURT_STATUS_POLICY',
              'recommended_credit':1,'review_alone_ledger_credit':0,'semantic_key':key,
              'actual_source_checks':checks,'semantic_comparisons':comparisons,'migration_false_positive_decision':migration_checks,
              'complete_chain_observations':observations,'limitations':limits,
              'production_changes':0,'game_starts':0,'checklist_deletions':0,'active_hours_claimed':0}
    review_raw = encode(review)
    row = {'id':key,'status':'reviewed_effective','repo':p['repo'],'commit':commit,
           'category':'native_cumulative_conduction_with_damage_refusal_status_fallback_and_result_independent_edge_cues',
           'semantic_dedup_key':key,'count_unit':'one complete mod-owned cumulative propagation/insulation/outcome/fallback/cue policy; all support0',
           'source_refs':refs,'full_chain_observation':'\n'.join(observations),
           'concrete_observation':'Cumulative electrical carrier enrolls roots before equipment/hurt checks; rubber insulation suppresses root damage but not later propagation, while negative root hurt requests a normal-admission status. Living passengers enroll under a separate path. Topology cue is unqualified by effect success and compacts missing endpoints. One policy, not one per victim/effect/packet/wrapper.',
           'application_to_boss_immune':p['application'],'limitations':'\n'.join(limits),'research_credit':1,'reviewed_utc':now,
           'independent_review':{'path':str(review_path.relative_to(R)),'sha256':sha(review_raw),'accepted_credit':1}}
    rows.append(row)
    dedup['groups'].append({'family':'cumulative-conduction-negative-hurt-status-policy-20261103','credited_chains':[key],'rationale':row['concrete_observation']})
    assert lp.read_bytes() == before and dp.read_bytes() == dbefore and proposal.read_bytes() == raw
    with review_path.open('xb') as handle:handle.write(review_raw)
    lp.write_bytes(encode(rows));dp.write_bytes(encode(dedup));verify()
    assert json.loads(lp.read_bytes())[:-1] == json.loads(before)
    result = {'recorded_utc':now,'decision':review['decision'],'new_effective_credit':1,'prior_total':464,'accepted_total':465,
              'remaining':535,'prior_ledger_sha256':sha(before),'current_ledger_sha256':sha(lp.read_bytes()),
              'old464_records_identical':True,'review':row['independent_review'],'proposal_sha256':sha(raw),
              'native_effect_or_damage_success_certified':False,'formal_design_gate_satisfied':False,
              'production_changes':0,'game_starts':0,'checklist_deletions':0,'active_hours_claimed':0}
    with acceptance_path.open('xb') as handle:handle.write(encode(result))
    print(json.dumps({'acceptance':str(acceptance_path.relative_to(R)),'sha256':sha(acceptance_path.read_bytes()),'accepted_total':465,'remaining':535,'ledger_sha256':sha(lp.read_bytes())}))


if __name__ == '__main__':
    main()
