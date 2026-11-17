"""One independently read control-continuity policy, with explicit engine gaps."""
from datetime import datetime, timezone
import hashlib
import json
import re
from accept_weedwood_20261103 import sha, encode, git
from ledger import O, R, verify


def main():
    proposal = R / 'docs/cod4/audit-20261022/program-feedback-review-20261101/immune-reference-batch-025-completion-001.json'
    review_path = O / 'coordinator-petrify-pose-latch-review-20261103.json'
    acceptance_path = O / 'coordinator-petrify-pose-latch-acceptance-20261103.json'
    assert not review_path.exists() and not acceptance_path.exists()
    raw = proposal.read_bytes()
    assert sha(raw) == '066ba4582dce9830218af2c6997bd8195aa99c5ceaee5756f3a5bcbe551acb41'
    p = json.loads(raw)
    assert p['status'] == 'pending_independent_semantic_review_mod_owned_chain'
    assert type(p['research_credit']) is int and p['research_credit'] == 0
    assert type(p['maximum_proposed_credit']) is int and p['maximum_proposed_credit'] == 1
    triage = p['supersedes_petrify_triage']
    assert sha((R / triage['path']).read_bytes()) == triage['sha256']
    lp, dp = O / 'reviewed.json', O / 'semantic-dedup.json'
    before, dbefore = lp.read_bytes(), dp.read_bytes()
    assert sha(before) == '04e9b07113db4d9fec2b48af1efceab6ae8827a44952e98a7872f5dd7173e209'
    rows, dedup = json.loads(before), json.loads(dbefore)
    assert len(rows) == 465
    key = p['semantic_family']
    assert key not in {row['semantic_dedup_key'] for row in rows}
    prov = p['provenance']
    manifest_raw = (R / prov['manifest_path']).read_bytes()
    assert sha(manifest_raw) == prov['manifest_sha256']
    manifest = next(x for x in json.loads(manifest_raw) if x['repo'] == p['repo'])
    repo, commit = R / prov['bare_git_path'], p['commit']
    assert git(repo, 'rev-parse', commit + '^{commit}').decode().strip() == commit == manifest['commit']
    assert git(repo, 'rev-parse', commit + '^{tree}').decode().strip() == manifest['git_tree'] == prov['git_tree']
    files = {x['path']:x for x in manifest['files']}
    prior = json.loads((R / 'docs/cod4/audit-20261022/program-feedback-review-20261101/immune-reference-batch-024.json').read_text())
    checks, refs = [], []
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
        mode = 'actual new whole cited range read in this independent review'
        if i in [10,15,16,17]:
            assert any(x['path'] == ref['path'] and x['file_sha256'] == ref['file_sha256'] and x['lines'][0] <= lo <= hi <= x['lines'][1] for x in prior['source_refs'])
            mode = 'identical actual same-turn024 lifecycle range reused;0 rereading credit'
        elif i == 3:
            mode = 'new1..28 and168 plus actual same-turn02429..167 and169..339 cover full339-line class'
        elif i == 4:
            mode = 'new1..64 and101..113 plus actual same-turn02465..100 cover full113-line class'
        elif i == 18:
            mode = 'new971..999 plus actual same-turn024960..970 cover cited complete registration method'
        checks.append({**ref,'excerpt_sha256':sha(b''.join(lines[lo-1:hi])),
                       'actual_current_turn_source_read_mode':mode,'source_identity_verified':True,'support_credit':0})
        refs.append({'path':ref['path'],'source_path':rel,'lines':[lo,hi],'file_sha256':sha(data),
                     'url':f'https://github.com/{p["repo"]}/blob/{commit}/{rel}#L{lo}-L{hi}'})
    assert len(checks) == 25
    by = {row['id']:row for row in rows}
    comparisons = []
    for item in p['dedup_snapshot']['comparisons']:
        row = by[item['accepted_id']]
        assert all(row.get(field) == item['full_semantic_decision_read'].get(field) for field in ['id','category','semantic_dedup_key','full_chain_observation','concrete_observation','limitations'])
        comparisons.append({'id':row['id'],'full_record_sha256':sha(json.dumps(row,ensure_ascii=False,sort_keys=True).encode()),
                            'substantive_decision_fields_actually_read':True,'old_source_chain_reread':False,'distinction':item['distinction']})
    assert len(comparisons) == 11
    for item in p['pending_peer_comparison']:
        peer = item['proposal']
        assert sha((R / peer['path']).read_bytes()) == peer['sha256']
        assert by[prior['semantic_family']]['research_credit'] == 1
        comparisons.append({'id':prior['semantic_family'],'status_now':'024 already independently accepted this same turn',
                            'full_semantic_decision_reused':True,'old_source_chain_reread':False,
                            'distinction':item['shared_support']})
    screen = p['migration_overlap_screen']
    migration_raw = (R / screen['path']).read_bytes()
    assert sha(migration_raw) == screen['sha256']
    migration_rows = [json.loads(line) for line in migration_raw.splitlines() if line.strip()]
    assert len(migration_rows) == screen['rows']
    pattern = re.compile(screen['pattern'], re.I)
    fields = ['family','trigger','input','output','preservation','application_limit']
    matches = [row['candidate_id'] for row in migration_rows if pattern.search(' '.join(str(row.get(field,'')) for field in fields))]
    assert matches == screen['matches'] == []
    clarifications = [
        'Accepted unit is one mod-owned callback-continuity pose-capture/re-render/release policy. Actual creative-subitem source, registered effect and complete direct ItemElixir callbacks are read. Native1.12 use dispatcher, status admission/merge/expiry, attribute engine and NBT getter defaults remain external. No successful survival brewing/drinking/payment or engine invocation certified.',
        'ItemElixir shrink precedes metadata/effect lookup. For noncreative one-item stack native empty-stack metadata behavior is unexpanded; valid-player status alone does not prove intended effect resolution after consumption. Creative branch does not shrink here. Invalid effect and non-player null dereference are not declared safe. The support arrow override has no own universal server gate; inherited actual hit-callback dispatch and final hurt conditions remain unknown.',
        'BASILISK28 and PETRIFY34 use two instances of one class with shared NBT names and movement-modifier UUID. Pose capture depends on storedTick != currentTick-1, not first-application identity, duration, owner or explicit initialization. Missing numeric key behavior is not substituted. Duplicate same-tick calls may recapture current fields; drift and native effect iteration ordering not reproduced.',
        'performEffect keeps current XYZ rather than original position, overwrites current yaw/pitch and head yaw, and has no server-only guard or NoAI control. LivingUpdate later zeros XZ when either effect is active; LivingJump first applies lightweight then resets XZ and only clamps Y when greater than-0.1. External displacement, all attacks/use and vertical physics are not blanket prevented.',
        'Actual FogColors callback uses local Minecraft player and rewrites current plus previous pose from local NBT, without freshness/hasKey/captured-tick or view-entity validation. It is an observed event consumer, not proof of camera final authority, sync with server or dedicated pose packet/ACK.',
        'Absent effect ceases these writes, without restoring an original orientation/AI flag or clearing petrify NBT. A later tick-gap callback recaptures current pose; no exact native expiry/removal tick or remote-side release guarantee. ElixirEffect.isActive uses registry-name object identity== and scanned current collection, not its own positive-duration check.',
        'stuckTicks is a separate shared FOV-only tail: any SHOCKED/ROOT_BOUND/BASILISK/PETRIFY renews5. After all absent, five END callbacks change5 to4,3,2,1,removed. FOV checks mere key presence and sets1, so a lingering key is not proof continued motion/pose control. Actual pause/render/event ordering and native rendering pixels remain unexecuted.',
        'Basilisk arrow excludes Matriarch but shortens other bosses rather than universally refusing them; barb omits bosses, shock-barb requests shock before Matriarch break. Different delivery sources do not automatically inherit arrow policy. Registered names/typed factories and complete mod arrow overrides read; native arrow physical success is support-only0.',
        'Eleven complete prior substantive semantic decisions read, with the initially clipped014 decision recovered in a separate full bounded output; their old sources not reread. Mowzie/controller and other frozen pose primitives remain prior owners; distinct unit is consecutive-callback capture plus actual render reapplication and separate release tail. Shared ROOT_BOUND zero-XZ/jump,024 SHOCKED FOV,017 elixir delivery, registry, two statuses and arrow colors all0 extra.',
        'Original025 triage is immutable and remains0. This completion only supersedes incomplete petrify chain scope; unrelated CorrosiveBoots triage was not accepted. Actual pinned source checks are evidence integrity, not additional references or native gameplay acceptance.'
    ]
    observations = [item['stage']+': '+item['observation'] for item in p['full_chain']] + clarifications
    limits = p['critical_boundaries'] + clarifications
    now = datetime.now(timezone.utc).isoformat()
    review = {'recorded_utc':now,'reviewer_thread_id':'01a16364-cac0-7ca2-a042-a5312781ca34',
              'proposal_author_thread_id':'01a16392-312e-72f2-a4dd-56e184f9cb02','proposal_path':str(proposal.relative_to(R)),
              'proposal_sha256':sha(raw),'original_incomplete_triage':triage,
              'decision':'ACCEPT_ONE_MOD_OWNED_CONSECUTIVE_TICK_POSE_LATCH_RENDER_RELEASE_POLICY',
              'recommended_credit':1,'review_alone_ledger_credit':0,'semantic_key':key,'actual_source_checks':checks,
              'semantic_comparisons':comparisons,'migration_keyword_screen':{'fields':fields,'pattern':screen['pattern'],'matches':matches,'exhaustive_semantic_uniqueness_proved':False},
              'complete_chain_observations':observations,'limitations':limits,
              'production_changes':0,'game_starts':0,'checklist_deletions':0,'active_hours_claimed':0}
    review_raw = encode(review)
    row = {'id':key,'status':'reviewed_effective','repo':p['repo'],'commit':commit,
           'category':'native_callback_continuity_qualified_pose_latch_with_local_render_reapplication_and_distinct_visual_release',
           'semantic_dedup_key':key,'count_unit':'one complete mod-owned capture/re-render/release policy; native engine gaps explicit; all variants/support0',
           'source_refs':refs,'full_chain_observation':'\n'.join(observations),
           'concrete_observation':'Consecutive callback ticks reuse stored orientation; gaps and same-tick repeats can recapture. Common motion and local FogColors pose consumers gate on active effect, while shared stuckTicks outlives it only to normalize FOV. No actor replacement, NoAI restoration or authoritative clear receipt. Two effects and all producers/render/transport wrappers merged1.',
           'application_to_boss_immune':p['application'],'limitations':'\n'.join(limits),'research_credit':1,'reviewed_utc':now,
           'independent_review':{'path':str(review_path.relative_to(R)),'sha256':sha(review_raw),'accepted_credit':1}}
    rows.append(row)
    dedup['groups'].append({'family':'consecutive-callback-pose-render-release-policy-20261103','credited_chains':[key],'rationale':row['concrete_observation']})
    assert lp.read_bytes() == before and dp.read_bytes() == dbefore and proposal.read_bytes() == raw
    with review_path.open('xb') as handle:handle.write(review_raw)
    lp.write_bytes(encode(rows));dp.write_bytes(encode(dedup));verify()
    assert json.loads(lp.read_bytes())[:-1] == json.loads(before)
    result = {'recorded_utc':now,'decision':review['decision'],'new_effective_credit':1,'prior_total':465,'accepted_total':466,
              'remaining':534,'prior_ledger_sha256':sha(before),'current_ledger_sha256':sha(lp.read_bytes()),
              'old465_records_identical':True,'review':row['independent_review'],'proposal_sha256':sha(raw),
              'native_engine_effect_dispatch_certified':False,'unrelated_corrosive_triage_accepted':False,'formal_design_gate_satisfied':False,
              'production_changes':0,'game_starts':0,'checklist_deletions':0,'active_hours_claimed':0}
    with acceptance_path.open('xb') as handle:handle.write(encode(result))
    print(json.dumps({'acceptance':str(acceptance_path.relative_to(R)),'sha256':sha(acceptance_path.read_bytes()),'accepted_total':466,'remaining':534,'ledger_sha256':sha(lp.read_bytes())}))


if __name__ == '__main__':
    main()
