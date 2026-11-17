"""One-shot coordinator acceptance after actual independent source/semantic reading.

Research evidence only. Never executes the referenced Java or changes production.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile
from ledger import B, O, R, verify


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def main():
    proposal = O / 'reviewer-nucleeper-fear-countdown-feedback-proposal-20261102.json'
    review = O / 'independent-nucleeper-fear-countdown-feedback-review-20261102.json'
    acceptance = O / 'coordinator-nucleeper-fear-countdown-feedback-acceptance-20261102.json'
    assert not review.exists() and not acceptance.exists()
    proposal_raw = proposal.read_bytes()
    assert sha(proposal_raw) == 'caca095f7f76aa2c412334fba7b9079371b9470ea6161e949e2985fcef1f5d0d'
    p = json.loads(proposal_raw)
    ledger, dedup_file = O / 'reviewed.json', O / 'semantic-dedup.json'
    before, dedup_before = ledger.read_bytes(), dedup_file.read_bytes()
    assert sha(before) == p['baseline']['reviewed_sha256'] == 'b4e02d054acb28aa1b78b815a1d0cb4a2d1f3ac02fb56fa6a5de34c8d88b3869'
    rows, dedup = json.loads(before), json.loads(dedup_before)
    assert len(rows) == 461 and p['author_thread_id'] == '01a12516-2eaf-73e2-b615-20f8b422158c'
    assert p['proposed_maximum_credit'] == 1 and p['accepted_credit'] == p['applied_credit'] == 0
    ident, key = p['suggested_id'], p['suggested_semantic_key']
    assert ident not in {x['id'] for x in rows} and key not in {x['semantic_dedup_key'] for x in rows}
    source = B / 'sources/AlexModGuy__AlexsCaves'
    source_raw, tree_raw = [(source / n).read_bytes() for n in ['source.json', 'tree.json']]
    meta, tree = json.loads(source_raw), json.loads(tree_raw)
    assert meta['commit'] == tree['sha'] == p['commit'] and not tree['truncated']
    assert sha(source_raw) == 'b853ce996c1f7a668679343404f0784c4ce3850f8b4454902a51113ed1078794'
    assert sha(tree_raw) == '144ccb5437d0b2128f00ee57c6334069babadf14c2b0fdb414d843b9801c5042'
    manifest = {x['path']: x for x in meta['files']}
    blobs = {x['path']: x['sha'] for x in tree['tree'] if x['type'] == 'blob'}
    checks, refs = [], []

    def record(path, rel, lo, hi, role, expected=None):
        raw = path.read_bytes()
        lines = raw.splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert blob == blobs[rel]
        excerpt = sha(b''.join(lines[lo - 1:hi]))
        if expected:
            assert sha(raw) == expected['source_sha256'] == manifest[rel]['sha256']
            assert blob == expected['git_blob_sha1'] == manifest[rel]['git_blob_sha1']
            assert excerpt == expected['excerpt_sha256_raw_preserving_line_endings']
        ref = {'path': str(path.relative_to(R)), 'source_path': rel, 'lines': [lo, hi],
               'file_sha256': sha(raw), 'url': f'https://github.com/{p["repo"]}/blob/{p["commit"]}/{rel}#L{lo}-L{hi}'}
        refs.append(ref)
        checks.append({**ref, 'git_blob_sha1': blob, 'excerpt_sha256': excerpt,
                       'coordinator_actually_read': True, 'role': role, 'research_credit': 0})

    for x in p['source_ranges']:
        record(R / x['source_local'], x['path'], x['line'], x['end_line'], x['role'], x)
    assert len(checks) == 19 and len({x['path'] for x in refs}) == 11
    acquisition = B / '.work/nucleeper-20261102'
    network = []
    for name in ['acquisition.json', 'acquisition-supplement.json']:
        data = json.loads((acquisition / name).read_text())
        for x in data['results']:
            assert x['success'] and x['credit'] == 0
            path = R / x['path']
            assert sha(path.read_bytes()) == x['sha256']
            record(path, x['source_path'], 1, len(path.read_bytes().splitlines()),
                   'complete supplemental sound, siren state owner, base sound or siren block; support only')
            network.append({'path': str((acquisition / name).relative_to(R)), 'sha256': sha((acquisition / name).read_bytes())})
    assert len(checks) == 24 and len({x['path'] for x in refs}) == 16
    archive = R / 'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar'
    assert sha(archive.read_bytes()) == '1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'
    entry = 'net/minecraft/world/entity/ai/goal/AvoidEntityGoal.java'
    native = R / 'tools/cod4/legacy-migration-acceptance/.work/sources/minecraft-forge-1.20.1-47.4.10' / entry
    raw = native.read_bytes()
    with zipfile.ZipFile(archive) as z:
        assert z.read(entry) == raw
    auxiliary = [{'path': str(native.relative_to(R)), 'source_path': entry, 'lines': [1, 94],
                  'file_sha256': sha(raw), 'source_archive': str(archive.relative_to(R)),
                  'source_archive_sha256': sha(archive.read_bytes()), 'archive_entry_exact': True,
                  'coordinator_actually_read': True, 'role': 'complete native avoidance admission/continuation/start/stop/tick', 'research_credit': 0}]
    assert len(raw.splitlines()) == 94
    comparisons = []
    for c in p['semantic_comparisons']:
        row = next(x for x in rows if x['id'] == c['id'])
        assert sha(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()) == c['whole_record_canonical_sha256']
        comparisons.append({**c, 'coordinator_actually_read_fields': ['id', 'semantic_dedup_key', 'concrete_observation', 'application_to_boss_immune'], 'old_source_chain_reread': False})
    for name in ['wizardry-native-mindtrick-pre-admission-target-null-and-attack-attempt-release',
                 'botania-native-persistent-ai-pacification-change-qualified-target-cue-and-reload-restore',
                 'bumblezone-native-combat-revokes-offhand-pacification-and-target-clearing-budget']:
        row = next(x for x in rows if x['id'] == name)
        comparisons.append({'id': name, 'whole_record_canonical_sha256': sha(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()),
                            'coordinator_actually_read_fields': ['id', 'semantic_dedup_key', 'concrete_observation', 'application_to_boss_immune'],
                            'old_source_chain_reread': False, 'research_credit': 0})
    clarifications = [
        'One adjacent counterplay/anticipation feedback family, not a hurt/control-immunity implementation: externally renewed avoidance lease reverses an existing local countdown before EXPLODING; warning state, preparation cancellation and emitted entity outcome remain distinct.',
        'Native AvoidEntityGoal is now read complete: combat targeting plus range/selection, random away position, not-closer check and a nonnull path gate admission. Continuation checks navigation unfinished, not current cat distance or liveness. Scheduler timing and successful navigation remain unexpanded; fear20 is refreshed only when this registered anonymous goal actually ticks.',
        'EXPLODING disables the fear rollback branch, not every later mutable operation. Local explodeProgress reaches5 only on a later evaluation after the flag was set. Discard occurs before create/add; create is unchecked and returned add result is ignored. No durable exactly-once explosion is asserted.',
        'NucleeperSound complete source now proves canPlay checks silent+triggered, while tick checks alive+triggered but not silent and does not explicitly stop on EXPLODING. Own remove clears cache; sound tick separately requests stop when no longer alive/triggered. The cache identity is alive+integer ID only, not UUID or dimension; case1 lacks old.isStopped recreation guard, so reusing a stopped matching instance is possible in source, not a tested restart failure.',
        'Sound progress can be stale versus current countdown: time sampled before this tick update; sirenAngle uses previous progress; neither ratio nor sqrt input is clamped. Ordinary valid default progress is not proof arbitrary persisted CloseTime/config always produces finite bounded pitch/geometry.',
        'Siren complete block installs ticker; state owner computes powered/volume before clearing stale bomb pointer. setNearestNuclearBomb replaces only a closer pointer, does not reject inactive/removed input first and holds no list of alternatives. Clearing one does not promote a farther source without another request. These are exact call-order boundaries, not a measured missed alarm.',
        'Siren bomb pointer itself is not persisted; integer BombID and optional furnace coordinates are. load/getUpdateTag/packet apply do not resolve bomb identity; missing BombID getInt yields0 and omitted furnace coordinates do not explicitly clear an existing field. Constructor volume reflects POWERED only, not a loaded BombID. Server clearing/re-requests and native network/save order were not run.',
        'BlockEntityTickableSound uses looping+linear attenuation and position-only helper identity. ClientProxy case0 recreates stopped objects whereas entity case1 does not. NuclearSirenSound tick updates volume until block removal, including zero volume after deactivation; canPlay is an admission test, not its tick stop predicate. No audible or engine scheduler guarantee.',
        'Emitted explosion noGrief only gates block work. Living scan has no explicit server guard; hurt/effect results are unchecked and velocity set separately. Query is a box, and calculateDamage is unclamped, so negative damage-derived inward velocity outside spherical maximum is possible by source arithmetic; no reproduced motion or damage result. Raycat suppression does not cancel effect request.',
        'Distinct from nonrenewing refused-hit refractory wake windows, coalesced refusal charge, successful-hurt cooldown retaliation, committed NPC/victim ritual, animation phase denial, attack-attempt release, permanent goal rewrite and combat-revoked offhand pacification. Ten selected actual substantive decision fields were read, not all461 decisions or their old source chains.'
    ]
    limits = [
        'Original proposer did not have three audio files. Coordinator acquired those three plus base sound and siren block in five single bounded verified-TLS fixed-commit requests, each exact fixed-tree blob. Original proposal remains immutable; supplement is actual source reading, not five new references. No retry/account/model/TLS bypass, download-time or hours credit.',
        'Exactly19 original ranges/11 files and5 complete supplemental classes plus complete native AvoidEntityGoal94 were actually read. Large proxy/registry/config/model ranges remain bounded; no whole large-file or art/UV/design credit. Earlier clipped proxy/comparison output recovered in bounded reads; hashes alone were never semantic credit.',
        'GoalSelector/native navigation/target predicate engine, EntityType.create and world add events, base Monster damage, nuclear effect implementation, furnace implementation, siren POI registry internals, complete sound engine/UnlimitedPitch processing, packet transport and live save/reopen not expanded or run.',
        'Original proposal audio-unclosed limitations describe its historical scope; superseded only by explicitly bound supplementary source observations here, not by runtime audio acceptance. No successful item payment, damage, effect, explosion admission, visual pose/frame or sound heard is established.',
        'No production patch is authorized by this one reference; research count remains below1000. No ordinary player constitution gray text, new gameplay, copied code/assets, ecology evidence, native acceptance, TODO deletion, Java/game/display/process query or hour completion.'
    ]
    now = datetime.now(timezone.utc).isoformat()
    r = {'recorded_utc': now, 'reviewer_thread_id': '01a16364-cac0-7ca2-a042-a5312781ca34',
         'proposal_author_thread_id': p['author_thread_id'], 'proposal_path': str(proposal.relative_to(R)), 'proposal_sha256': sha(proposal_raw),
         'decision': 'ACCEPT_ONE_ADJACENT_RENEWABLE_COUNTERPLAY_AND_PHASE_FEEDBACK_LIFECYCLE_WITH_LIMITS',
         'recommended_credit': 1, 'ledger_credit_written_by_this_review': 0, 'semantic_key': key,
         'source_manifest_sha256': sha(source_raw), 'source_tree_sha256': sha(tree_raw), 'source_commit': p['commit'],
         'provenance_checks': checks, 'native_auxiliary_checks': auxiliary, 'acquisition': network,
         'semantic_comparisons': comparisons, 'complete_chain_observations': p['observed_chain'],
         'supplementary_observations_and_corrections': clarifications, 'limitations': limits,
         'game_starts': 0, 'production_changes': 0, 'art_changes': 0, 'checklist_deletions': 0, 'duration_hours_claimed': 0}
    review_raw = encoded(r)
    row = {'id': ident, 'status': 'reviewed_effective', 'repo': p['repo'], 'commit': p['commit'],
           'category': 'adjacent_external_counterplay_reversible_preparation_vs_committed_emission_and_feedback',
           'semantic_dedup_key': key, 'count_unit': 'one complete distinct lifecycle; all helpers/audio/visual/native supports0',
           'source_refs': refs, 'auxiliary_refs': auxiliary, 'full_chain_observation': '\n'.join(p['observed_chain'] + clarifications),
           'concrete_observation': '\n'.join(clarifications), 'application_to_boss_immune': p['application'],
           'limitations': '\n'.join(limits), 'research_credit': 1, 'reviewed_utc': now,
           'independent_review': {'path': str(review.relative_to(R)), 'sha256': sha(review_raw), 'accepted_credit': 1}}
    rows.append(row)
    dedup['groups'].append({'family': 'external-avoidance-lease-retracts-preparation-vs-committed-emission-20261102',
                            'credited_chains': [ident], 'rationale': clarifications[0] + ' ' + clarifications[-1]})
    assert ledger.read_bytes() == before and dedup_file.read_bytes() == dedup_before
    with review.open('xb') as stream:
        stream.write(review_raw)
    ledger.write_bytes(encoded(rows))
    dedup_file.write_bytes(encoded(dedup))
    verify()
    a = {'recorded_utc': now, 'decision': r['decision'], 'new_effective_credit': 1, 'prior_total': 461,
         'accepted_total': 462, 'remaining': 538, 'key': key, 'prior_ledger_sha256': sha(before),
         'current_ledger_sha256': sha(ledger.read_bytes()), 'proposal': {'path': str(proposal.relative_to(R)), 'sha256': sha(proposal_raw)},
         'independent_review': row['independent_review'], 'clarifications': clarifications, 'limitations': limits,
         'formal_design_gate_satisfied': False, 'production_changes': 0, 'art_changes': 0,
         'game_starts': 0, 'checklist_deletions': 0, 'duration_hours_claimed': 0}
    with acceptance.open('xb') as stream:
        stream.write(encoded(a))
    print(json.dumps({'review_sha256': sha(review_raw), 'acceptance_sha256': sha(acceptance.read_bytes()),
                      'ledger_sha256': sha(ledger.read_bytes()), 'accepted_total': 462, 'remaining': 538}))


if __name__ == '__main__':
    main()
