"""Check exact reference provenance, semantic coverage and unchanged shared assets."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import zipfile

D = Path(__file__).resolve().parent
R = D.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    baseline = read(D / 'source-baseline.json')
    changes = [p for p, h in baseline.items() if not (R / p).is_file() or sha(R / p) != h]
    prov = read(D / 'provenance.json')
    review = read(D / 'semantic-review.json')
    context = read(D / 'collection-context.json')
    receipt = read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(set(receipt['targets'])) == len(receipt['targets']) == 24
    assert receipt['sha256'] == sha(R / receipt['snapshot']) == sha(R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md') == sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    assert sha(R / context['collector']) == context['collector_sha256']
    groups = {}
    prior_cases = set()
    for row in context['prior_ledgers']:
        path = R / row['path']
        assert sha(path) == row['sha256']
        for observation in read(path)['observations']:
            key = observation['semantic_group']
            group = groups.setdefault(key, {'semantic_group': key, 'cases': set(), 'observations': []})
            group['cases'].update(observation['cases'])
            prior_cases.update(observation['cases'])
            group['observations'].append({'source': row['path'], 'observation': observation['observation']})
    assert len(groups) == 57 and len(prior_cases) == 120
    assert prior_cases == set(context['skipped_previously_reviewed_cases'])
    cases = {c['case_key'] for c in prov['cases']}
    assert len(cases) == 72 and not cases & prior_cases
    assert sum(len(c['icons']) for c in prov['cases']) == 259 and prov['worn_textures'] == []
    flat = [c for g in review['observations'] for c in g['cases']]
    assert len(flat) == len(set(flat)) == 72 and set(flat) == cases
    new = [g for g in review['observations'] if g['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP']
    append = [g for g in review['observations'] if g['credit'] == 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS']
    assert len(new) == 25 and len(append) == 2
    for observation in review['observations']:
        key = observation['semantic_group']
        if observation in new:
            assert key not in groups
            groups[key] = {'semantic_group': key, 'cases': set(), 'observations': []}
        else:
            assert key in groups
            source, anchor = observation['prior_group'].split('#')
            assert key == anchor and any(g['semantic_group'] == key for g in read(R / source)['observations'])
        groups[key]['cases'].update(observation['cases'])
        groups[key]['observations'].append({'source': str((D / 'semantic-review.json').relative_to(R)), 'observation': observation['observation']})
    owners = {}
    for key, group in groups.items():
        for case in group['cases']:
            assert case not in owners, (case, owners.get(case), key)
            owners[case] = key
    assert len(groups) == 82 and len(owners) == 192
    assert review['combined_conservative_learning_groups'] == 82 and review['combined_name_families'] == 192
    assert review['gate_met'] is False and review['new_artwork'] == review['production_changes'] == 0
    assert len(review['pages_opened']) == 11 and all((D / p).is_file() for p in review['pages_opened'])
    assets = [a for c in prov['cases'] for a in c['icons']]
    with ExitStack() as stack:
        jars = {a['path']: stack.enter_context(zipfile.ZipFile(a['path'])) for a in prov['archives']}
        for row in prov['indexes']:
            assert sha(R / row['path']) == row['sha256']
        for row in prov['archives']:
            assert sha(Path(row['path'])) == row['sha256']
        for a in assets:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
    cumulative = {
        'scope': 'Actual viewed subset only; conservative learning groups, not a completed global 1000-design register.',
        'source_reviews': context['prior_ledgers'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
        'groups': [{**g, 'cases': sorted(g['cases'])} for _, g in sorted(groups.items())],
        'case_to_group': dict(sorted(owners.items())), 'name_families': len(owners),
        'conservative_learning_groups': len(groups), 'required_distinct_related_designs': 1000,
        'gate_met': False, 'production_authorized_by_this_register': False,
    }
    (D / 'combined-semantic-ledger.json').write_text(json.dumps(cumulative, ensure_ascii=False, indent=2) + '\n')
    result = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
        'source_protected_paths': len(baseline), 'source_unchanged': not changes, 'changed_paths': changes,
        'new_icon_name_families_viewed': 72, 'new_icon_png_viewed': 259, 'new_worn_png': 0,
        'new_conservative_learning_groups': 25, 'append_prior_groups_zero_new_credit': 2,
        'prior_groups_reused': 57, 'combined_groups': 82, 'combined_name_families': 192,
        'reference_gate_met': False, 'rules_sha256': receipt['sha256'],
        'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0,
    }
    (D / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
