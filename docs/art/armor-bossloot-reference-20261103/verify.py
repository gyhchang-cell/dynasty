"""Check fixed inputs, exact copies, cumulative ownership, and production safeguards."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import zipfile

D = Path(__file__).resolve().parent
R = D.parents[2]


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (D / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    ctx, baseline = read(D / 'collection-context.json'), read(D / 'source-baseline.json')
    changes = [p for p, h in baseline.items() if not (R / p).is_file() or sha(R / p) != h]
    assert sha(R / ctx['collector']) == ctx['collector_sha256']
    assert sha(R / ctx['prior_ledger']) == ctx['prior_ledger_sha256']
    prior = read(R / ctx['prior_ledger'])
    assert len(prior['groups']) == 154 and len(prior['case_to_group']) == 361 and len(prior['reviewed_case_keys']) == 374
    for row in prior['source_reviews']:
        assert sha(R / row['path']) == row['sha256']
    assert set(ctx['skipped_previously_reviewed_cases']) == set(prior['reviewed_case_keys'])
    receipt = read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(receipt['targets']) == len(set(receipt['targets'])) == 24
    assert receipt['sha256'] == sha(R / receipt['snapshot']) == sha(R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md') == sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    prov, review = read(D / 'provenance.json'), read(D / 'semantic-review.json')
    selected, supplements = read(D / 'provenance-index-selection.json'), read(D / 'same-family-completion.json')
    icons = [a for c in prov['cases'] for a in c['icons']]
    key = lambda a: (a['jar'], a['entry'], a['sha256'])
    original = [a for c in selected['cases'] for a in c['icons']]
    assert len(original) == 88 and len(supplements) == 15 and len(icons) == 103
    assert {key(a) for a in icons} == {key(a) for a in original + supplements}
    cases = {c['case_key'] for c in prov['cases']}
    assert len(cases) == 32 and not cases & set(prior['reviewed_case_keys'])
    for index in prov['indexes']:
        assert sha(R / index['path']) == index['sha256']
    assert len(review['pages_opened']) == 6 and all((D / p).is_file() for p in review['pages_opened'])
    included = [c for row in review['observations'] for c in row['cases']]
    excluded = []
    assert len(included) == len(set(included)) == 32 and set(included) == cases
    names = read(D / 'name-normalization.json')
    assert names == {'aliases': {'royalvariations:royal_knight_cuirass': 'royalvariations:royal_knight'}, 'raw_names': 33, 'normalized_names': 32}
    original_cases = {c['case_key'] for c in selected['cases']}
    assert {names['aliases'].get(c, c) for c in original_cases} == cases
    with ExitStack() as stack:
        jars = {a['path']: stack.enter_context(zipfile.ZipFile(a['path'])) for a in prov['archives']}
        for a in prov['archives']:
            assert sha(Path(a['path'])) == a['sha256']
        for a in icons:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
    groups = {g['semantic_group']: g for g in prior['groups']}
    new = append = 0
    for row in review['observations']:
        k = row['semantic_group']
        if row['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP':
            assert k not in groups
            groups[k] = {'semantic_group': k, 'cases': [], 'observations': []}
            new += 1
        else:
            assert row['credit'] == 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group'] == k and k in groups
            append += 1
        groups[k]['cases'] = sorted(set(groups[k]['cases']) | set(row['cases']))
        groups[k]['observations'].append({'source': str((D / 'semantic-review.json').relative_to(R)), 'observation': row['observation']})
    owners = {}
    for k, group in groups.items():
        for c in group['cases']:
            assert c not in owners
            owners[c] = k
    assert new == 14 and append == 3 and len(groups) == 168 and len(owners) == 393
    excluded_all = prior['excluded_cases'] + excluded
    reviewed = sorted(set(owners) | {e['case_key'] for e in excluded_all})
    assert len(reviewed) == 406 and len(excluded_all) == 13
    cumulative = {**prior, 'source_reviews': prior['source_reviews'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
                  'groups': [g for _, g in sorted(groups.items())], 'case_to_group': dict(sorted(owners.items())),
                  'excluded_cases': excluded_all, 'reviewed_case_keys': reviewed,
                  'name_families': 406, 'armor_name_families': 393, 'conservative_learning_groups': 168}
    save('combined-semantic-ledger.json', cumulative)
    save('reference-gate-accounting.json', {'required_valid_related_independent_designs': 1000,
         'reviewed_name_families': 406, 'armor_name_families_after_exclusion': 393,
         'excluded_non_player_equipment': 1, 'excluded_player_accessory_or_slot_unproven': 12,
         'excluded_from_full_armor_gate': 13, 'conservative_learning_groups_in_current_subset': 168,
         'validated_independent_design_total': None, 'maximum_credit_under_current_one_per_group_policy': 168,
         'unfilled_minimum_under_current_policy': 832, 'reference_gate_met': False,
         'gap_limit': '学习组包含不完整套及反例，尚非独立完整设计验收；832仅为全部学习组合格时的最低缺口。'})
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
              'source_protected_paths': len(baseline), 'source_unchanged': not changes, 'changed_paths': changes,
              'native_icon_png_viewed': 103, 'native_worn_entries_viewed': 0, 'distinct_worn_payloads': 0,
              'new_learning_groups': 14, 'combined_learning_groups': 168,
              'combined_reviewed_names': 406, 'combined_armor_names': 393,
              'reference_gate_met': False, 'rules_sha256': receipt['sha256'],
              'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0}
    assert review['new_artwork'] == review['production_changes'] == 0 and not review['gate_met']
    save('verification.json', result)
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
