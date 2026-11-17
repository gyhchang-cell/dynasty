#!/usr/bin/env python3
"""Check new manual research records against a preserved earlier checkpoint.

File checks and isolated Python registrar replays only. This does not establish
that pixels were studied, recheck production sources, or execute native code.
"""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from verify_continuation import OUT, REF, REL, ROOT, command, read, sha

FIELDS = ('layout', 'proportion', 'facade', 'roof', 'material', 'circulation', 'terrain')


def canonical(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, help='Path relative to research output')
    parser.add_argument('--review', action='append', required=True,
                        help='New review path relative to references, in registration order')
    parser.add_argument('--report', required=True, help='Output path relative to research output')
    args = parser.parse_args()
    reviews = args.review
    assert len(reviews) == len(set(reviews))
    for rel in [args.baseline, args.report]:
        (OUT / rel).resolve().relative_to(OUT.resolve())
    for rel in reviews:
        (REF / rel).resolve().relative_to(REF.resolve())
    baseline = read(OUT / args.baseline)
    register = read(REF / 'full-buildings.json')
    entries, batches = register['entries'], register['reviewed_batches']
    old_entries = [e for e in entries if e.get('manual_review_file') not in reviews]
    old_batches = [b for b in batches if b['file'] not in reviews]
    assert len(old_entries) == baseline['previous_accepted']
    assert canonical(old_entries) == baseline['previous_entries_canonical_sha256']
    assert canonical(old_batches) == baseline['previous_batches_canonical_sha256']
    prior_report = baseline['previous_whole_static_report']
    assert sha((OUT / prior_report['file']).read_bytes()) == prior_report['sha256']
    for field in ('id', 'complete_building_identity'):
        assert len({e[field] for e in entries}) == len(entries), field
    assert len({b['file'] for b in batches}) == len(batches)
    assert sum(b['accepted_complete_designs'] for b in batches) == len(entries)
    candidates = sum(b['candidates_actually_viewed'] for b in batches)
    excluded = sum(b['excluded_or_deferred'] for b in batches)
    assert candidates - excluded == len(entries)
    for scope in register['scope_status']:
        count = sum(scope['scope'] in e['credited_scopes'] for e in entries)
        assert count == scope['credited_verified_complete_buildings']
        minimum = register['minimum_related_complete_buildings']
        assert scope['remaining'] == max(0, minimum - count)
        assert scope['new_architecture_may_start'] == (count >= minimum)

    photos_checked = evidence_checked = manual_checked = candidates_checked = json_checked = 0
    batch_results = []
    for rel in reviews:
        folder = (REF / rel).parent
        for file in folder.glob('*.json'):
            read(file)
            json_checked += 1
        manual = read(REF / rel)
        ledger = read(folder / 'manual-visual-ledger.json')
        cases = manual['cases'] + manual['excluded_or_deferred']
        assert manual['java_executed'] is False and manual['no_new_architecture'] is True
        assert len({c['key'] for c in cases}) == len(cases)
        expected = {f: c['key'] for c in cases for f in c['evidence'] if f.endswith('.jpg')}
        photos = ledger['actual_photos_viewed']
        assert len(photos) == len(expected)
        assert {p['file'] for p in photos} == set(expected)
        downloads = {}
        for receipt in folder.glob('download-*.json'):
            rows = read(receipt)
            if not isinstance(rows, list):
                continue
            for row in rows:
                if (isinstance(row, dict) and row.get('file', '').endswith('.jpg')
                        and row.get('returncode', row.get('curl_exit')) == 0):
                    downloads[row['file']] = row
        metadata = {p['key'] + '.jpg': p for p in read(folder / 'photo-sources.json')}
        for photo in photos:
            file = photo['file']
            raw = (folder / file).read_bytes()
            assert photo['building_key'] == expected[file]
            assert photo['viewed_on'] == manual['date']
            assert photo['per_photo_building_credit'] == 0
            assert photo['observed'].strip() and photo['attribution'].strip()
            assert sha(raw) == photo['sha256'] and len(raw) == photo['bytes']
            assert len(raw) > 1000 and raw.startswith(b'\xff\xd8')
            assert downloads[file].get('url', downloads[file].get('source_url')) == photo['source_url']
            meta = metadata[file]
            assert meta['original_url'] == photo['source_url']
            assert meta['author'] and meta['photo_date'] and meta['license']
            assert meta['source_url'] in photo['source_page']
            photos_checked += 1
        assert ledger['distinct_building_groups'] == len(cases)
        assert ledger['accepted_building_groups'] == len(manual['cases'])
        assert ledger['deferred_building_groups'] == len(manual['excluded_or_deferred'])
        for case in cases:
            for field in (*FIELDS, 'identity', 'dedup', 'relevance', 'applicable_learning'):
                assert case[field].strip(), (rel, case['key'], field)
            assert case['unknown'] and case['photo_attribution']
            assert urlparse(case['official_url']).scheme == 'https'
            candidates_checked += 1
        for case in manual['cases']:
            entry = next(e for e in entries if e['id'] == manual['batch'] + '-' + case['key'])
            assert entry['manual_review_file'] == rel
            assert entry['manual_review_sha256'] == sha((REF / rel).read_bytes())
            assert entry['complete_building_identity'] == case['identity']
            assert entry['native_collision_or_generation_validated'] is False
            for field in FIELDS:
                registered = ('terrain_connection' if field == 'terrain' else field) + '_observation'
                assert entry[registered] == case[field]
            for file, expected_sha in entry['evidence_sha256'].items():
                assert sha((REF / file).read_bytes()) == expected_sha
                evidence_checked += 1
            manual_checked += 1
        batch_results.append({'review': rel, 'photos': len(photos), 'candidates': len(cases),
                              'accepted': len(manual['cases']),
                              'deferred': len(manual['excluded_or_deferred'])})

    with tempfile.TemporaryDirectory(prefix='dynasty-new-reference-check-') as temp:
        scratch = Path(temp)
        scratch_ref = scratch / REL / 'references'
        scratch_ref.mkdir(parents=True)
        shutil.copy2(REF / 'full-buildings.json', scratch_ref)
        script = scratch / 'tools/architecture/register_online_building_review.py'
        script.parent.mkdir(parents=True)
        shutil.copy2(ROOT / 'tools/architecture/register_online_building_review.py', script)
        for rel in reviews:
            shutil.copytree((REF / rel).parent, (scratch_ref / rel).parent)
        initial = (scratch_ref / 'full-buildings.json').read_bytes()
        for _ in range(2):
            for rel in reviews:
                command([sys.executable, str(script), '--review', rel], cwd=scratch)
            assert (scratch_ref / 'full-buildings.json').read_bytes() == initial
    command(['git', 'diff', '--check', '--', 'tools/architecture', str(REL)])
    result = {
        'date': '2026-10-31', 'status': 'PASS_NEW_REFERENCE_RECORDS_ONLY',
        'baseline': args.baseline, 'baseline_sha256': sha((OUT / args.baseline).read_bytes()),
        'prior_entries_and_batches_preserved': True, 'prior_whole_static_report': prior_report,
        'registry_sha256': sha((REF / 'full-buildings.json').read_bytes()),
        'scope_status': register['scope_status'], 'total_batches': len(batches),
        'total_candidate_review_events': candidates, 'total_accepted': len(entries),
        'total_historical_exclusions_or_deferrals': excluded,
        'new_batches': batch_results, 'new_candidate_checks': candidates_checked,
        'new_photo_hash_metadata_and_download_checks': photos_checked,
        'new_accepted_evidence_hash_checks': evidence_checked,
        'new_accepted_manual_review_hash_checks': manual_checked,
        'new_batch_json_files_parsed': json_checked,
        'new_registration_inputs_replayed_twice_in_isolated_copy': len(reviews),
        'scoped_git_diff_check': 'PASS', 'java_executed': False,
        'production_sources_reaudited': False, 'full_static_suite_repeated': False,
        'new_architecture_created': False, 'whole_game_tasks_completed': False,
        'checklist_deleted': [],
        'limitations': [
            'Hash/download checks validate saved records, not actual visual study or semantic relevance.',
            'Manual per-photo observations and semantic deduplication remain in each review and ledger.',
            'No Java, Gradle, compiler, native generation, client, save or gameplay check was executed.',
            'Prior full static report remains a historical checkpoint, not a new whole-game acceptance.',
        ],
    }
    (OUT / args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('limitations',)},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
