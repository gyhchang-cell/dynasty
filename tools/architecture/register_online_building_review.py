#!/usr/bin/env python3
"""Register manually studied online building instances and local screenshot evidence.

This checks records, not whether research happened. Manual visual study must
precede use; search results, downloaded images and automated IDs earn no credit.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'docs/architecture/continuation-20261022/references'
FIELDS = ('layout', 'proportion', 'facade', 'roof', 'material', 'circulation', 'terrain')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', default='hkmemory-online/review.json')
    args = parser.parse_args()
    review_path = (REF / args.review).resolve()
    review_path.relative_to(REF)
    batch = json.loads(review_path.read_text())
    register = REF / 'full-buildings.json'
    data = json.loads(register.read_text())
    entries = [e for e in data['entries'] if e.get('manual_review_file') != args.review]
    for case in batch['cases']:
        for field in (*FIELDS, 'identity', 'dedup', 'relevance', 'key'):
            if not case.get(field, '').strip():
                raise ValueError(f'Missing manual observation: {field}')
        if urlparse(case['official_url']).scheme != 'https':
            raise ValueError('Verifiable HTTPS source required')
        evidence = []
        for file in case['evidence']:
            path = (review_path.parent / file).resolve()
            path.relative_to(REF)
            if not path.is_file() or path.stat().st_size < 1000:
                raise ValueError(f'Missing visual evidence: {path}')
            evidence.append(str(path.relative_to(REF)))
        if not evidence:
            raise ValueError('At least one actually viewed screenshot required')
        notes = {f'{f if f != "terrain" else "terrain_connection"}_observation': case[f]
                 for f in FIELDS}
        entries.append({
            'id': f'{batch["batch"]}-{case["key"]}',
            'status': 'REVIEWED_COMPLETE_DESIGN_REFERENCE_ONLY',
            'source_kind': 'official_online_building_instance',
            'credited_scopes': [batch['scope']],
            'target': batch['target'],
            'verifiable_source': {'official_url': case['official_url'],
                                  'supplementary_url': case.get('supplementary_source'),
                                  'additional_viewed_url': case.get('additional_viewed_source'),
                                  'observed_on': batch['date']},
            'complete_building_identity': case['identity'],
            'evidence_actually_viewed': evidence,
            'evidence_sha256': {f: hashlib.sha256((REF / f).read_bytes()).hexdigest()
                                for f in evidence},
            'manual_review_file': args.review,
            'manual_review_sha256': hashlib.sha256(review_path.read_bytes()).hexdigest(),
            'deduplication_basis': {'building_instance': case['dedup'],
                                     'count_unit': 'One complete building; all photos and parts merged'},
            'relevance_to_current_task': case['relevance'],
            'complete_boundary_and_relevance': case['relevance'],
            'native_collision_or_generation_validated': False,
            'measured_dimensions_verified': False,
            **notes,
        })
    identities = [e['complete_building_identity'] for e in entries]
    ids = [e['id'] for e in entries]
    if len(identities) != len(set(identities)) or len(ids) != len(set(ids)):
        raise ValueError('Duplicate building identity or record ID')
    for scope in data['scope_status']:
        count = sum(scope['scope'] in e['credited_scopes'] for e in entries)
        scope['credited_verified_complete_buildings'] = count
        scope['remaining'] = max(0, data['minimum_related_complete_buildings'] - count)
        scope['new_architecture_may_start'] = count >= data['minimum_related_complete_buildings']
    data['entries'] = entries
    data['reviewed_batches'] = [b for b in data['reviewed_batches'] if b['file'] != args.review] + [{
        'file': args.review,
        'candidates_actually_viewed': len(batch['cases']) + len(batch['excluded_or_deferred']),
        'accepted_complete_designs': len(batch['cases']),
        'excluded_or_deferred': len(batch['excluded_or_deferred']),
        'native_game_acceptance': False,
    }]
    register.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(data['scope_status'], ensure_ascii=False))


if __name__ == '__main__':
    main()
