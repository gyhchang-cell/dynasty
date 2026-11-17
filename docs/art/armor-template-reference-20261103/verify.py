"""Verify suffix normalization, exact reference payloads, cumulative ownership and protected assets."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
import hashlib
import importlib.util
import json
import re
import zipfile

D = Path(__file__).resolve().parent
R = D.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ctx, baseline = read(D / 'collection-context.json'), read(D / 'source-baseline.json')
    changes = [p for p, h in baseline.items() if not (R / p).is_file() or sha(R / p) != h]
    assert sha(R / ctx['collector']) == ctx['collector_sha256']
    assert sha(R / ctx['prior_ledger']) == ctx['prior_ledger_sha256']
    prior = read(R / ctx['prior_ledger'])
    assert len(prior['groups']) == 136 and len(prior['case_to_group']) == 303 and len(prior['reviewed_case_keys']) == 304
    for row in prior['source_reviews']:
        assert sha(R / row['path']) == row['sha256']
    assert set(ctx['skipped_previously_reviewed_cases']) == set(prior['reviewed_case_keys'])
    receipt = read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(receipt['targets']) == len(set(receipt['targets'])) == 24
    assert receipt['sha256'] == sha(R / receipt['snapshot']) == sha(R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md') == sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    prov, review, names = read(D / 'provenance.json'), read(D / 'semantic-review.json'), read(D / 'name-normalization.json')
    icons = [a for c in prov['cases'] for a in c['icons']]
    cases = {c['case_key'] for c in prov['cases']}
    assert len(cases) == 37 and len(icons) == 111 and not prov['worn_textures']
    assert not cases & set(prior['reviewed_case_keys'])
    spec = importlib.util.spec_from_file_location('original_family_definition', R / ctx['collector'])
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    namespaces = {case.split(':')[0] for case in cases}
    aliases = defaultdict(set)
    for index in prov['indexes']:
        assert sha(R / index['path']) == index['sha256']
        for a in read(R / index['path']):
            bits = a['entry'].split('/')
            if bits[0] != 'assets' or bits[1] not in namespaces:
                continue
            norm = re.sub(r'_?(helmet|chestplate|leggings|boots)$', '', Path(a['entry']).stem)
            aliases[bits[1] + ':' + norm].add(bits[1] + ':' + module.family(a['entry']))
    assert {k: sorted(v) for k, v in sorted(aliases.items())} == names['aliases']
    assert len({n for values in aliases.values() for n in values}) == names['raw_index_name_families'] == 69
    assert len(aliases) == names['normalized_families'] == 37
    flat = [c for row in review['observations'] for c in row['cases']]
    assert len(flat) == len(set(flat)) == 37 and set(flat) == cases
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
    assert new == 9 and append == 4 and len(groups) == 145 and len(owners) == 340
    assert review['new_artwork'] == review['production_changes'] == 0 and not review['gate_met']
    with ExitStack() as stack:
        jars = {a['path']: stack.enter_context(zipfile.ZipFile(a['path'])) for a in prov['archives']}
        for row in prov['archives']:
            assert sha(Path(row['path'])) == row['sha256']
        for a in icons:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
    reviewed_keys = sorted(set(owners) | {e['case_key'] for e in prior['excluded_cases']})
    assert len(reviewed_keys) == 341
    cumulative = {**{k: v for k, v in prior.items() if k not in {'groups', 'case_to_group', 'source_reviews', 'name_families', 'conservative_learning_groups', 'armor_name_families', 'reviewed_case_keys'}},
                  'source_reviews': prior['source_reviews'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
                  'groups': [g for _, g in sorted(groups.items())], 'case_to_group': dict(sorted(owners.items())),
                  'reviewed_case_keys': reviewed_keys, 'name_families': 341, 'armor_name_families': 340,
                  'conservative_learning_groups': 145}
    (D / 'combined-semantic-ledger.json').write_text(json.dumps(cumulative, ensure_ascii=False, indent=2) + '\n')
    accounting = {'required_valid_related_independent_designs': 1000, 'reviewed_name_families': 341,
                  'armor_name_families_after_exclusion': 340, 'excluded_non_player_equipment': 1,
                  'conservative_learning_groups_in_current_subset': 145, 'validated_independent_design_total': None,
                  'maximum_credit_under_current_one_per_group_policy': 145, 'unfilled_minimum_under_current_policy': 855,
                  'gap_limit': '145是含不完整装备/反例的保守学习组，不是独立完整设计验收数；855仅是全部都合格时的最低缺口。', 'reference_gate_met': False}
    (D / 'reference-gate-accounting.json').write_text(json.dumps(accounting, ensure_ascii=False, indent=2) + '\n')
    result = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
              'source_protected_paths': len(baseline), 'source_unchanged': not changes, 'changed_paths': changes,
              'native_icon_png_viewed': 111, 'raw_name_families': 69, 'normalized_name_families': 37,
              'false_name_family_inflation_removed': 32, 'new_learning_groups': 9,
              'combined_learning_groups': 145, 'combined_reviewed_names': 341, 'combined_armor_names': 340,
              'minimum_open_reference_gap_under_current_policy': 855, 'reference_gate_met': False,
              'rules_sha256': receipt['sha256'], 'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0}
    (D / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
