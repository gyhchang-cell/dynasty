"""Validate reviewed source bytes, unique semantic ownership and shared-file protection."""
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
    context = read(D / 'collection-context.json')
    assert sha(R / context['collector']) == context['collector_sha256']
    assert sha(R / context['prior_ledger']) == context['prior_ledger_sha256']
    prior = read(R / context['prior_ledger'])
    assert len(prior['groups']) == 82 and len(prior['case_to_group']) == 192
    assert set(context['skipped_previously_reviewed_cases']) == set(prior['case_to_group'])
    for row in prior['source_reviews']:
        assert sha(R / row['path']) == row['sha256']
    receipt = read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(set(receipt['targets'])) == len(receipt['targets']) == 24
    assert receipt['sha256'] == sha(R / receipt['snapshot']) == sha(R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md') == sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    prov, review = read(D / 'provenance.json'), read(D / 'semantic-review.json')
    cases = {c['case_key'] for c in prov['cases']}
    assets = [a for c in prov['cases'] for a in c['icons']]
    assert len(cases) == 35 and len(assets) == 126 and not prov['worn_textures']
    assert not cases & set(prior['case_to_group'])
    flat = [c for g in review['observations'] for c in g['cases']]
    assert len(flat) == len(set(flat)) == 35 and set(flat) == cases
    assert len(review['pages_opened']) == 5 and all((D / p).is_file() for p in review['pages_opened'])
    assert review['gate_met'] is False and review['production_changes'] == review['new_artwork'] == 0
    groups = {g['semantic_group']: g for g in prior['groups']}
    counts = {'NEW_CONSERVATIVE_LEARNING_GROUP': 0, 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS': 0}
    for row in review['observations']:
        key = row['semantic_group']
        counts[row['credit']] += 1
        if row['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP':
            assert key not in groups
            groups[key] = {'semantic_group': key, 'cases': [], 'observations': []}
        else:
            assert key == row['prior_group'] and key in groups
        groups[key]['cases'] = sorted(set(groups[key]['cases']) | set(row['cases']))
        groups[key]['observations'].append({'source': str((D / 'semantic-review.json').relative_to(R)), 'observation': row['observation']})
    assert counts == {'NEW_CONSERVATIVE_LEARNING_GROUP': 22, 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS': 1}
    owners = {}
    for key, group in groups.items():
        for case in group['cases']:
            assert case not in owners, case
            owners[case] = key
    assert len(groups) == review['combined_conservative_learning_groups'] == 104
    assert len(owners) == review['combined_name_families'] == 227
    with ExitStack() as stack:
        jars = {row['path']: stack.enter_context(zipfile.ZipFile(row['path'])) for row in prov['archives']}
        for row in prov['archives']:
            assert sha(Path(row['path'])) == row['sha256']
        for row in prov['indexes']:
            assert sha(R / row['path']) == row['sha256']
        for a in assets:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
    cumulative = {
        **{k: v for k, v in prior.items() if k not in {'groups', 'case_to_group', 'source_reviews', 'name_families', 'conservative_learning_groups'}},
        'source_reviews': prior['source_reviews'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
        'groups': [g for _, g in sorted(groups.items())], 'case_to_group': dict(sorted(owners.items())),
        'name_families': len(owners), 'conservative_learning_groups': len(groups),
    }
    (D / 'combined-semantic-ledger.json').write_text(json.dumps(cumulative, ensure_ascii=False, indent=2) + '\n')
    result = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
        'source_protected_paths': len(baseline), 'source_unchanged': not changes, 'changed_paths': changes,
        'new_name_families_viewed': 35, 'new_native_icon_png_viewed': 126, 'new_conservative_learning_groups': 22,
        'append_prior_groups_zero_new_credit': 1, 'combined_name_families': 227, 'combined_learning_groups': 104,
        'reference_gate_met': False, 'rules_sha256': receipt['sha256'], 'production_changes': 0,
        'new_artwork': 0, 'game_starts': 0, 'checklist_deletions': 0,
    }
    (D / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
