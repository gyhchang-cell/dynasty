#!/usr/bin/env python3
"""Verify saved architecture research and the existing Wangsi source repair.

Python/file checks only. No Java, Gradle, Minecraft or architecture generation.
The registrar is replayed in an isolated temporary copy, never against live files.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL = Path('docs/architecture/continuation-20261022')
OUT = ROOT / REL
REF = OUT / 'references'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def command(args, cwd=ROOT):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result.stdout


def main():
    json_paths = sorted(OUT.rglob('*.json'))
    for path in json_paths:
        read(path)
    register = read(REF / 'full-buildings.json')
    entries = register['entries']
    for field in ('id', 'complete_building_identity'):
        assert len({e[field] for e in entries}) == len(entries), field
    evidence_checks = 0
    manual_hash_checks = 0
    local_source_checks = 0
    jar_hashes = {}
    for entry in entries:
        for field in register['required_record_fields']:
            assert entry[field], (entry['id'], field)
        assert set(entry['evidence_actually_viewed']) == set(entry['evidence_sha256'])
        for file, expected in entry['evidence_sha256'].items():
            assert sha((REF / file).read_bytes()) == expected, file
            evidence_checks += 1
        if 'manual_review_sha256' in entry:
            assert sha((REF / entry['manual_review_file']).read_bytes()) == entry['manual_review_sha256']
            manual = read(REF / entry['manual_review_file'])
            matching = [case for case in manual['cases']
                        if entry['id'] == manual['batch'] + '-' + case['key']]
            assert len(matching) == 1
            for field in ('layout', 'proportion', 'facade', 'roof', 'material', 'circulation', 'terrain'):
                registered_field = ('terrain_connection' if field == 'terrain' else field) + '_observation'
                assert entry[registered_field] == matching[0][field]
            manual_hash_checks += 1
        source = entry['verifiable_source']
        if 'local_jar' in source:
            jar_path = Path(source['local_jar'])
            if str(jar_path) not in jar_hashes:
                jar_hashes[str(jar_path)] = sha(jar_path.read_bytes())
            assert jar_hashes[str(jar_path)] == source['jar_sha256']
            with zipfile.ZipFile(jar_path) as archive:
                assert sha(archive.read(source['member'])) == source['nbt_sha256']
            local_source_checks += 1
        assert entry['native_collision_or_generation_validated'] is False
    batches = register['reviewed_batches']
    assert len({b['file'] for b in batches}) == len(batches)
    accepted = sum(b['accepted_complete_designs'] for b in batches)
    candidates = sum(b['candidates_actually_viewed'] for b in batches)
    excluded = sum(b['excluded_or_deferred'] for b in batches)
    assert accepted == len(entries) == candidates - excluded
    for scope in register['scope_status']:
        count = sum(scope['scope'] in e['credited_scopes'] for e in entries)
        assert count == scope['credited_verified_complete_buildings']
        assert scope['remaining'] == max(0, register['minimum_related_complete_buildings'] - count)
        assert scope['new_architecture_may_start'] == (count >= register['minimum_related_complete_buildings'])

    # Re-run the new manual batches twice, using a disposable copy of the inputs.
    isolated_reviews = ('hkmemory-third/review.json', 'ctc-next/review.json',
                        'amo-pingshan/review.json', 'cemeteries-001/review.json',
                        'macau-001/review.json', 'macau-002/review.json',
                        'tungwah-001/review.json', 'new-territories-001/review.json',
                        'new-territories-002/review.json', 'taiwan-001/review.json',
                        'new-territories-003/review.json', 'new-territories-004/review.json',
                        'new-territories-005/review.json',
                        'whole-candidates-004/review-batch-004.json',
                        'new-territories-007/review.json',
                        'taiwan-003/review.json', 'taiwan-004/review.json',
                        'taiwan-005/review.json', 'taiwan-006/review.json',
                        'taiwan-007/review.json', 'taiwan-008/review.json',
                        'taiwan-009/review.json', 'taiwan-010/review.json')
    with tempfile.TemporaryDirectory(prefix='dynasty-architecture-verification-') as tmp:
        scratch = Path(tmp)
        scratch_ref = scratch / REL / 'references'
        scratch_ref.mkdir(parents=True)
        shutil.copy2(REF / 'full-buildings.json', scratch_ref)
        script = scratch / 'tools/architecture/register_online_building_review.py'
        script.parent.mkdir(parents=True)
        shutil.copy2(ROOT / 'tools/architecture/register_online_building_review.py', script)
        local_script = script.with_name('register_whole_building_review.py')
        shutil.copy2(ROOT / 'tools/architecture/register_whole_building_review.py', local_script)
        for review in isolated_reviews:
            folder = Path(review).parent
            shutil.copytree(REF / folder, scratch_ref / folder)
        baseline = (scratch_ref / 'full-buildings.json').read_bytes()
        for _ in range(2):
            for review in isolated_reviews:
                registrar = local_script if review.startswith('whole-candidates-') else script
                command([sys.executable, str(registrar), '--review', review], cwd=scratch)
            assert (scratch_ref / 'full-buildings.json').read_bytes() == baseline

    # Link the new photo ledgers to manual cases and successful downloads.
    # This checks saved records, not whether a human has actually studied pixels.
    photo_ledger_checks = 0
    for folder in ('new-territories-003', 'new-territories-004', 'new-territories-005',
                   'new-territories-007', 'taiwan-003', 'taiwan-004', 'taiwan-005',
                   'taiwan-006', 'taiwan-007', 'taiwan-008', 'taiwan-009', 'taiwan-010'):
        review_folder = REF / folder
        manual = read(review_folder / 'review.json')
        ledger = read(review_folder / 'manual-visual-ledger.json')
        photos = ledger['actual_photos_viewed']
        studied_groups = manual['cases'] + manual['excluded_or_deferred']
        expected = {file: case['key'] for case in studied_groups
                    for file in case['evidence'] if file.endswith('.jpg')}
        assert len(photos) == len(expected)
        assert {p['file'] for p in photos} == set(expected)
        downloads = {}
        for receipt in review_folder.glob('download-*.json'):
            rows = read(receipt)
            # Category/source discovery receipts may be a single object, and
            # source-page downloads have no image file. Neither proves pixels.
            if not isinstance(rows, list):
                continue
            downloads.update({r['file']: r for r in rows
                              if isinstance(r, dict) and r.get('file', '').endswith('.jpg')
                              and r.get('returncode', r.get('curl_exit')) == 0})
        for photo in photos:
            file = photo['file']
            raw = (review_folder / file).read_bytes()
            assert photo['building_key'] == expected[file]
            assert photo['viewed_on'] in manual.get('study_dates', [manual['date']])
            assert photo['per_photo_building_credit'] == 0
            assert sha(raw) == photo['sha256'] and len(raw) == photo['bytes']
            download = downloads[file]
            assert download.get('returncode', download.get('curl_exit')) == 0
            assert download.get('url', download.get('source_url')) == photo['source_url']
            assert photo['observed'] and photo['attribution']
            photo_ledger_checks += 1
        assert ledger['distinct_building_groups'] == len(studied_groups)
        if manual['excluded_or_deferred']:
            assert ledger['accepted_building_groups'] == len(manual['cases'])
            assert ledger['deferred_building_groups'] == len(manual['excluded_or_deferred'])
        for case in studied_groups:
            assert case['applicable_learning'] and case['unknown'] and case['photo_attribution']

    # Excluded local candidates still need authentic sources and viewed-image hashes.
    local_folder = REF / 'whole-candidates-004'
    local_candidates = read(local_folder / 'candidates.json')['candidates']
    local_review = read(local_folder / 'review-batch-004.json')
    local_ledger = read(local_folder / 'manual-visual-ledger.json')
    viewed = {row['candidate']: row for row in local_ledger['viewed']}
    assert not local_review['accepted']
    assert set(viewed) == set(local_review['not_credited'])
    candidate_jar_hashes = {}
    for candidate in local_candidates:
        jar = Path(candidate['source_jar'])
        if jar not in candidate_jar_hashes:
            candidate_jar_hashes[jar] = sha(jar.read_bytes())
        assert candidate_jar_hashes[jar] == candidate['source_jar_sha256']
        with zipfile.ZipFile(jar) as archive:
            assert sha(archive.read(candidate['member'])) == candidate['nbt_sha256']
        row = viewed[candidate['id']]
        assert local_review['viewed_evidence'][candidate['id']] == [row['file']]
        assert sha((local_folder / row['file']).read_bytes()) == row['sha256']
        assert row['per_image_building_credit'] == 0 and row['observation']

    # Read-only scene/task mapping is a dated source snapshot, not gameplay acceptance.
    scene_map = read(OUT / 'scene-task-material-map-20261030.json')
    for file, expected in scene_map['source_sha256'].items():
        assert sha((ROOT / file).read_bytes()) == expected, file
    assert scene_map['java_executed'] is False
    assert scene_map['new_architecture_created'] is False
    assert scene_map.get('current_reference_scope_status',
                         scene_map['reference_scope_status']) == register['scope_status']
    assert len(scene_map['scenes']) == 4

    # Keep the large primary PDF and the manual page ledger linked to the study.
    # Rendered but unviewed pages must never acquire whole-building credit.
    macau = REF / 'macau-001'
    publication = read(macau / 'pdf-source.json')
    pdf_raw = (macau / publication['file']).read_bytes()
    assert sha(pdf_raw) == publication['sha256']
    assert len(pdf_raw) == publication['bytes']
    viewed_pairs = read(macau / 'render-index.json')['actually_viewed_pairs']
    macau_cases = read(macau / 'review.json')['cases']
    for case in macau_cases:
        assert case['pdf_pages_1based'] in viewed_pairs, case['key']

    current = read(OUT / 'wangsi-sign-support-20261026.json')
    historical = read(OUT / 'wangsi-sign-worldgen-compatibility-20261024.json')
    assert current['production_source_changed'] is True
    assert current['java_executed'] is False
    for file, expected in current['input_sha256'].items():
        assert sha((ROOT / file).read_bytes()) == expected, file
    piece = 'src/main/java/com/dynasty/dungeon/WangsiPiece.java'
    piece_raw = (ROOT / piece).read_bytes()
    assert sha(piece_raw) == current['source_current_sha256'] == current['proposed_source_sha256']
    assert current['source_before_sha256'] == historical['source_sha256']
    assert current['piece_count_preserved'] == 48
    signs = current['signs']
    assert len(signs) == 4 and sum(len(s['rows']) for s in signs) == 16
    assert sum(s['before_fix_required_support']['status'] == 'EXPLICIT_AIR' for s in signs) == 3
    assert all(s['proposed_support_in_same_piece'] for s in signs)
    assert all(s['proposed_required_support']['palette_index'] in (3, 4) for s in signs)
    patch = OUT / current['proposed_patch']
    assert sha(patch.read_bytes()) == current['proposed_patch_sha256']
    command(['git', 'apply', '--reverse', '--check', str(patch)])
    with tempfile.TemporaryDirectory(prefix='dynasty-wangsi-patch-') as tmp:
        scratch = Path(tmp)
        target = scratch / piece
        target.parent.mkdir(parents=True)
        target.write_bytes(piece_raw)
        command(['git', 'apply', '--reverse', str(patch)], cwd=scratch)
        assert sha(target.read_bytes()) == current['source_before_sha256']
        command(['git', 'apply', str(patch)], cwd=scratch)
        assert target.read_bytes() == piece_raw

    mapped = current['mapped_sources']
    jar = Path(mapped['path'])
    assert sha(jar.read_bytes()) == mapped['sha256'] == historical['source_jar_sha256']
    excerpts = 0
    with zipfile.ZipFile(jar) as archive:
        for member in mapped['members']:
            raw = archive.read(member['path'])
            assert sha(raw) == member['sha256']
            for part in member['excerpts']:
                lines = raw.decode().splitlines()[part['first_line'] - 1:part['last_line']]
                assert '\n'.join(lines) == part['text']
                excerpts += 1
        for observation in historical['observations']:
            raw = archive.read(observation['member'])
            assert sha(raw) == observation['member_sha256']
            a, b = observation['lines']
            excerpt = ''.join(raw.decode().splitlines(keepends=True)[a - 1:b])
            assert sha(excerpt.encode()) == observation['excerpt_sha256']
    for evidence in historical['provided_runtime_evidence']:
        assert sha((ROOT / evidence['file']).read_bytes()) == evidence['sha256']

    # Inspect the coordinator's saved native evidence, without running its QA.
    receipt_file = OUT / 'external-native-evidence-20261026.json'
    receipt = read(receipt_file)
    assert receipt['java_executed_by_this_conversation'] is False
    assert receipt['production_source_edited_during_this_continuation'] is False
    assert receipt['building_reference_progress'] == register['scope_status']
    implementation_references = receipt['sign_initialization_reference_progress']
    assert implementation_references['independent_external_initialization_implementations_reviewed'] == 1
    assert implementation_references['remaining'] == 999
    assert implementation_references['requirement_met'] is False
    external_files_checked = 0
    external_qa_current_drift = {}
    external_reports = {}
    for name, evidence in receipt['reports'].items():
        assert evidence['executed_by_this_conversation'] is False
        for file, expected in evidence['external_file_sha256'].items():
            assert sha((ROOT / file).read_bytes()) == expected, file
            external_files_checked += 1
        for file, expected in evidence['source_current_sha256'].items():
            assert sha((ROOT / file).read_bytes()) == expected, file
        report = read(ROOT / evidence['report'])
        assert report['status'] == evidence['report_status']
        assert report['game_clients_started'] == 0
        assert report['game_content_removed'] is False
        external_reports[name] = report
        # QA runners are shared with later suites. A changed wrapper is recorded;
        # it is never presented as an unchanged source of the historical run.
        external_qa_current_drift[name] = [
            file for file, expected in evidence['historical_qa_source_sha256'].items()
            if sha((ROOT / file).read_bytes()) != expected
        ]
    sign_native = external_reports['wangsi_sign']
    assert sign_native['status'] == 'NATIVE_GENERATION_AND_SAVE_REOPEN_PASS'
    assert sign_native['complete_structure_pieces'] == sign_native['native_FULL_chunks_each_phase'] == 48
    assert sign_native['user_original_world_touched'] is False
    assert sign_native['full_ecology_task_complete'] is False
    for flag in ('all_sign_records_identical_after_reopen', 'native_support_survival_checks',
                 'attached_neighbor_notification_preserved_signs', 'detached_native_NBT_roundtrip',
                 'normal_save_shutdown_each_phase'):
        assert sign_native[flag] is True, flag
    sign_folder = (ROOT / receipt['reports']['wangsi_sign']['report']).parent
    generate = read(sign_folder / 'generate.json')
    reopen = read(sign_folder / 'reopen.json')
    for phase in (generate, reopen):
        assert phase['status'] == 'PASS' and phase['save_completed'] is True
        assert phase['pieces'] == phase['full_chunks'] == 48
        assert phase['seed'] == 20261023 and phase['connected_players'] == 0
        assert phase['manual_piece_block_or_actor_placement'] is False
        assert phase['player_journey_or_visual_acceptance'] is False
        assert len(phase['observations']) == 4
        assert {tuple(s['messages']) for s in phase['observations']} == {tuple(s['rows']) for s in signs}
        for sign in phase['observations']:
            assert sign['facing'] == 'north' and sign['waxed'] and sign['can_survive'] and sign['has_level']
            assert sign['color'] == ('red' if sign['messages'][0] == '阴阳界' else 'black')
    assert generate['observations'] == reopen['observations']
    interaction_native = external_reports['natural_interactions']
    interaction_folder = (ROOT / receipt['reports']['natural_interactions']['report']).parent
    natural = read(interaction_folder / 'natural_interactions.json')
    assert natural['status'] == 'PASS' and natural['natural_interactions_verified'] == 15
    assert natural['manual_placement'] is False and natural['players'] == 0
    assert natural['actual_client_interaction_or_timing_test'] is False
    observed = natural['observations']
    layouts = [o for o in observed if o['kind'] == 'natural_structure']
    interactions = [o for o in observed if o['kind'] == 'natural_interaction']
    assert len(layouts) == 3 and {o['orientation'] for o in layouts} == {'north'}
    assert len(interactions) == 15
    assert {o['id'] for o in interactions} == set(interaction_native['natural_interaction_ids'])
    for observed_block in interactions:
        for flag in ('expected_registered_block', 'collision_nonempty', 'outline_nonempty',
                     'approach_ground_support', 'approach_body_clear'):
            assert observed_block[flag] is True, (observed_block['id'], flag)
    assert interaction_native['whole_task_complete'] is False

    bridge_file = 'src/main/java/com/dynasty/DynastyCompassBridge.java'
    language_file = 'src/main/resources/assets/dynasty/lang/zh_cn.json'
    bridge_raw = (ROOT / bridge_file).read_bytes()
    assert 'new Destination("yinsi_wangsi_cheng","阴司枉死城","underworld","yinsi_wangsi_cheng",false)' in bridge_raw.decode()
    language = read(ROOT / language_file)
    for key in ('structure.dynasty.yinsi_wangsi_cheng', 'structure.dynasty.yinsi_wangsi_cheng.name'):
        assert language[key] == '阴司枉死城'

    owned = [piece, 'tools/architecture', str(REL)]
    command(['git', 'diff', '--check', '--', *owned])
    delivery = read(OUT / 'DELIVERY.json')
    assert delivery['checklist_deleted'] == [] and delivery['java_executed'] is False
    assert delivery['reference_scope']['scope_status'] == register['scope_status']
    assert delivery['reference_scope']['credited_verified_complete_buildings'] == accepted
    assert delivery['reference_scope']['candidates_visually_reviewed'] == candidates
    assert delivery['reference_scope']['excluded_or_deferred_candidates'] == excluded
    mismatches = [file for file, expected in delivery['input_sha256'].items()
                  if sha((ROOT / file).read_bytes()) != expected]
    assert mismatches == delivery['current_input_snapshot_mismatches']

    result = {
        'date': delivery['date'], 'status': 'PASS_STATIC_CONSISTENCY_ONLY',
        'reference_count': accepted, 'remaining': 1000 - accepted,
        'cod6_reference_count': register['scope_status'][1]['credited_verified_complete_buildings'],
        'candidates_reviewed': candidates, 'excluded_or_deferred': excluded,
        'reviewed_batches': len(batches), 'evidence_hash_checks': evidence_checks,
        'online_manual_review_hash_checks': manual_hash_checks,
        'new_photo_ledger_hash_and_download_checks': photo_ledger_checks,
        'new_excluded_local_candidate_source_and_image_checks': len(local_candidates),
        'scene_task_material_source_hash_checks': len(scene_map['source_sha256']),
        'local_whole_design_source_checks': local_source_checks,
        'local_reference_jars_verified': len(jar_hashes),
        'json_files_parsed': len(json_paths), 'registration_idempotent_in_isolated_copy': True,
        'macau_primary_pdf_sha256_verified': publication['sha256'],
        'macau_studied_page_pairs': len(viewed_pairs),
        'macau_credited_whole_buildings': len(macau_cases),
        'current_sign_analysis_source_members': len(mapped['members']),
        'current_sign_analysis_excerpts': excerpts,
        'historical_sign_source_observations': len(historical['observations']),
        'historical_sign_source_members': len({o['member'] for o in historical['observations']}),
        'provided_external_runtime_evidence_hash_checks': len(historical['provided_runtime_evidence']),
        'external_runtime_evidence_executed_by_this_task': False,
        'external_native_receipt_sha256': sha(receipt_file.read_bytes()),
        'new_external_native_file_hash_checks': external_files_checked,
        'external_native_wangsi_sign_generation_save_reopen': 'PASS_BOUNDED_COORDINATOR_EVIDENCE',
        'external_native_interaction_placements': 15,
        'external_natural_layout_orientation_set': ['north'],
        'external_historical_qa_sources_current_drift': external_qa_current_drift,
        'source_and_evidence_hashes_match': True, 'sign_source_fix_applied': True,
        'sign_patch_reverse_check': 'PASS', 'sign_patch_isolated_round_trip': 'PASS',
        'preserved_city_pieces': 48, 'preserved_chinese_signs': 4, 'preserved_chinese_rows': 16,
        'existing_wangsi_chinese_navigation_source_checked': True,
        'navigation_input_sha256': {
            bridge_file: sha(bridge_raw), language_file: sha((ROOT / language_file).read_bytes()),
        },
        'new_architecture_created': False, 'java_executed': False,
        'execution_scope': 'This Python verifier and the current conversation; imported native evidence is listed separately',
        'compiled_by_this_conversation': False,
        'native_generation_replayed_by_this_conversation': False,
        'checklist_deleted': [],
        'historical_input_snapshot_mismatches': mismatches,
        'limitations': [
            'Saved evidence and source consistency checks do not replace manual architectural study',
            'This conversation did not execute native generation, Java, Gradle or a game client',
            'External native evidence covers one Wangsi generation/save-reopen case and 15 natural NORTH-layout interaction placements only',
            'Nonempty collision/outline and a nearby standing position do not prove every model-state alignment, full routes, client display or timed interactions',
            '1000 related whole buildings not met; no new architecture produced or task marked complete',
            'Historical input hashes are preserved; concurrently changed inputs require separate acceptance',
        ],
    }
    report_date = delivery['date'].replace('-', '')
    (OUT / f'verification-{report_date}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
