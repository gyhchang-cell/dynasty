"""Verify completed-family research, non-armor exclusions and unchanged production assets."""
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
    baseline, ctx = read(D / 'source-baseline.json'), read(D / 'collection-context.json')
    changes = [p for p, h in baseline.items() if not (R / p).is_file() or sha(R / p) != h]
    assert sha(R / ctx['collector']) == ctx['collector_sha256']
    assert sha(R / ctx['prior_ledger']) == ctx['prior_ledger_sha256']
    prior = read(R / ctx['prior_ledger'])
    assert len(prior['groups']) == 117 and len(prior['case_to_group']) == 264
    for row in prior['source_reviews']:
        assert sha(R / row['path']) == row['sha256']
    assert set(ctx['skipped_previously_reviewed_cases']) == set(prior['case_to_group'])
    receipt = read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(receipt['targets']) == len(set(receipt['targets'])) == 24
    assert receipt['sha256'] == sha(R / receipt['snapshot']) == sha(R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md') == sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    prov, review = read(D / 'provenance.json'), read(D / 'semantic-review.json')
    cases = {c['case_key'] for c in prov['cases']}
    icons = [a for c in prov['cases'] for a in c['icons']]
    assert len(cases) == 40 and len(icons) == 112 and not cases & set(prior['case_to_group'])
    assert sha(D / 'provenance-index-selection.json') == prov['same_family_completion']['initial_selection_sha256']
    initial = read(D / 'provenance-index-selection.json')
    assert sum(len(c['icons']) for c in initial['cases']) == 90
    additions = read(D / 'same-family-completion.json')
    assert len(additions) == prov['same_family_completion']['added_png'] == 22
    assert prov['same_family_completion']['new_name_families'] == prov['same_family_completion']['additional_design_credit'] == 0
    actual_assets = {(c['case_key'], a['jar'], a['entry'], a['sha256']) for c in prov['cases'] for a in c['icons']}
    assert all((a['case_key'], a['jar'], a['entry'], a['sha256']) in actual_assets for a in additions)
    flat = [c for row in review['observations'] for c in row['cases']]
    excluded = {row['case_key'] for row in review['excluded_cases']}
    assert len(flat) == len(set(flat)) == 39 and excluded == {'alexsmobs:falconry'}
    assert set(flat).isdisjoint(excluded) and set(flat) | excluded == cases
    assert len(review['pages_opened']) == 6 and all((D / p).is_file() for p in review['pages_opened'])
    groups = {g['semantic_group']: g for g in prior['groups']}
    new = append = 0
    for row in review['observations']:
        key = row['semantic_group']
        if row['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP':
            assert key not in groups
            groups[key] = {'semantic_group': key, 'cases': [], 'observations': []}
            new += 1
        else:
            assert row['credit'] == 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group'] == key and key in groups
            append += 1
        groups[key]['cases'] = sorted(set(groups[key]['cases']) | set(row['cases']))
        groups[key]['observations'].append({'source': str((D / 'semantic-review.json').relative_to(R)), 'observation': row['observation']})
    owners = {}
    for key, group in groups.items():
        for case in group['cases']:
            assert case not in owners
            owners[case] = key
    assert new == 19 and append == 2 and len(groups) == 136 and len(owners) == 303
    assert not review['gate_met'] and review['new_artwork'] == review['production_changes'] == 0
    with ExitStack() as stack:
        jars = {row['path']: stack.enter_context(zipfile.ZipFile(row['path'])) for row in prov['archives']}
        for row in prov['archives']:
            assert sha(Path(row['path'])) == row['sha256']
        for row in prov['indexes']:
            assert sha(R / row['path']) == row['sha256']
        for a in icons:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
        for exclusion in review['excluded_cases']:
            source = exclusion['source']
            data = jars[source['jar']].read(source['entry'])
            assert hashlib.sha256(data).hexdigest() == source['sha256']
            assert 'Eagles wearing one' in json.loads(data)[source['inspected_key']]
    cumulative = {**{k: v for k, v in prior.items() if k not in {'groups', 'case_to_group', 'source_reviews', 'name_families', 'conservative_learning_groups'}},
                  'source_reviews': prior['source_reviews'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
                  'groups': [g for _, g in sorted(groups.items())], 'case_to_group': dict(sorted(owners.items())),
                  'reviewed_case_keys': sorted(set(owners) | excluded), 'excluded_cases': review['excluded_cases'],
                  'name_families': 304, 'armor_name_families': 303, 'conservative_learning_groups': 136,
                  'schema_note': 'name_families counts reviewed names including exclusions; case_to_group only applicable armor names. Use reviewed_case_keys for next-batch skip.'}
    (D / 'combined-semantic-ledger.json').write_text(json.dumps(cumulative, ensure_ascii=False, indent=2) + '\n')
    accounting = {'required_valid_related_independent_designs': 1000, 'reviewed_name_families': 304,
                  'armor_name_families_after_exclusion': 303, 'excluded_non_player_equipment': 1,
                  'conservative_learning_groups_in_current_subset': 136, 'validated_independent_design_total': None,
                  'maximum_credit_under_current_one_per_group_policy': 136, 'unfilled_minimum_under_current_policy': 864,
                  'gap_limit': '136组中仍有单件、不完整套件及材料反例；864仅为全部合格时的最低缺口，不是完整独立设计验收数。', 'reference_gate_met': False}
    (D / 'reference-gate-accounting.json').write_text(json.dumps(accounting, ensure_ascii=False, indent=2) + '\n')
    result = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
              'source_protected_paths': len(baseline), 'source_unchanged': not changes, 'changed_paths': changes,
              'native_icon_png_viewed': 112, 'same_family_completion_png': 22, 'reviewed_new_name_families': 40,
              'excluded_non_player_equipment': 1, 'new_learning_groups': 19, 'combined_learning_groups': 136,
              'combined_reviewed_name_families': 304, 'combined_armor_name_families': 303,
              'minimum_open_reference_gap_under_current_policy': 864, 'reference_gate_met': False,
              'rules_sha256': receipt['sha256'], 'production_changes': 0, 'new_artwork': 0, 'game_starts': 0, 'checklist_deletions': 0}
    (D / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
