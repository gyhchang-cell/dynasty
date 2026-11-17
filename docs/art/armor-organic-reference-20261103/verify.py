"""Validate this fixed local read batch, including exact JSON/PNG references and exclusions."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import zipfile
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[2]


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (D / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def key(a):
    return a['jar'], a['entry'], a['sha256']


def main():
    ctx = read(D / 'collection-context.json')
    for base in ['collector', 'batch_collector', 'prior_ledger']:
        assert sha(R / ctx[base]) == ctx[base + '_sha256']
    prior = read(R / ctx['prior_ledger'])
    assert (len(prior['groups']), len(prior['case_to_group']), len(prior['reviewed_case_keys'])) == (184, 429, 442)
    assert set(ctx['skipped_previously_reviewed_cases']) == set(prior['reviewed_case_keys'])
    for row in prior['source_reviews']:
        assert sha(R / row['path']) == row['sha256']
    baseline = read(D / 'source-baseline.json')
    changes = [p for p, h in baseline.items() if not (R / p).is_file() or sha(R / p) != h]
    assert len(baseline) == 289
    receipt = read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(receipt['targets']) == len(set(receipt['targets'])) == 24
    assert receipt['sha256'] == sha(R / receipt['snapshot']) == sha(R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md') == sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    initial, prov, review = read(D / 'provenance.json'), read(D / 'completed-provenance.json'), read(D / 'semantic-review.json')
    decls, added, atlas = read(D / 'resource-declarations.json'), read(D / 'same-family-completion.json'), read(D / 'native-atlas-declarations.json')
    icons = [a for c in prov['cases'] for a in c['icons']]
    old_icons = [a for c in initial['cases'] for a in c['icons']]
    cases = {c['case_key'] for c in prov['cases']}
    assert len(cases) == 15 and not cases & set(prior['reviewed_case_keys'])
    assert len(icons) == 63 and len(old_icons) == 57 and len(added) == 6 and len(decls) == 61 and len(atlas) == 8
    assert {key(a) for a in icons} == {key(a) for a in old_icons + added}
    for index in prov['indexes']:
        assert sha(R / index['path']) == index['sha256']
    assert prov['indexes'] == initial['indexes'] and prov['archives'] == initial['archives']
    assert len(review['pages_opened']) == 6 and all((D / p).is_file() for p in review['pages_opened'])
    with ExitStack() as stack:
        jars = {a['path']: stack.enter_context(zipfile.ZipFile(a['path'])) for a in prov['archives']}
        for archive in prov['archives']:
            assert sha(Path(archive['path'])) == archive['sha256']
        for a in icons + [a['model'] for a in decls] + atlas:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
            if 'size' in a:
                with Image.open(D / a['local']) as im:
                    assert list(im.size) == a['size']
        for a in decls:
            model = read(D / a['model']['local'])
            assert model['parent'] == a['parent'] and a['parent'] in ['item/generated', 'minecraft:item/generated']
            assert model['textures']['layer0'] == a['texture_location']
            ns, path = a['texture_location'].split(':')
            assert a['texture']['entry'] == f'assets/{ns}/textures/{path}.png'
            assert a['texture'] in next(c['icons'] for c in prov['cases'] if c['case_key'] == a['case_key'])
        bound_icons = {key(a['texture']) for a in decls}
        unproven = next(c for c in prov['cases'] if c['case_key'] == 'mutationcraft_origins:berserk')
        assert {key(a) for a in icons} - bound_icons == {key(a) for a in unproven['icons']}
        assert len({a['case_key'] for a in decls}) == 14
        for a in atlas:
            assert not a['binding_to_selected_item_proven']
            model = read(D / a['local'])
            assert [g['description'] for g in model['minecraft:geometry']] == a['descriptions']
        malformed = read(D / 'unrelated-malformed-models.json')
        assert len(malformed) == 1 and not malformed[0]['used']
        a = malformed[0]
        try:
            json.loads(jars[a['jar']].read(a['entry']))
        except json.JSONDecodeError:
            pass
        else:
            raise AssertionError('Unrelated malformed-source exclusion no longer matches source')
    flat = [c for row in review['observations'] for c in row['cases']] + [e['case_key'] for e in review['excluded_cases']]
    assert len(flat) == len(set(flat)) == 15 and set(flat) == cases
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
    excluded = prior['excluded_cases'] + review['excluded_cases']
    reviewed = sorted(set(owners) | {e['case_key'] for e in excluded})
    assert (new, append, len(groups), len(owners), len(reviewed), len(excluded)) == (5, 4, 189, 443, 457, 14)
    save('combined-semantic-ledger.json', {**prior,
        'source_reviews': prior['source_reviews'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
        'groups': [g for _, g in sorted(groups.items())], 'case_to_group': dict(sorted(owners.items())),
        'reviewed_case_keys': reviewed, 'excluded_cases': excluded,
        'name_families': 457, 'armor_name_families': 443, 'conservative_learning_groups': 189})
    save('reference-gate-accounting.json', {
        'required_valid_related_independent_designs': 1000, 'reviewed_name_families': 457,
        'armor_name_families_after_exclusion': 443, 'excluded_non_player_equipment': 1,
        'excluded_player_accessory_or_slot_unproven': 13, 'excluded_from_full_armor_gate': 14,
        'conservative_learning_groups_in_current_subset': 189, 'validated_independent_design_total': None,
        'maximum_credit_under_current_one_per_group_policy': 189, 'unfilled_minimum_under_current_policy': 811,
        'reference_gate_met': False,
        'gap_limit': '学习组含局部、材料变体和反例，不等于189套完整独立设计；811是所有组合格时的最低缺口，实际可能更大。'})
    assert all(review[k] == 0 for k in ['new_artwork', 'production_changes', 'game_starts']) and not review['gate_met']
    result = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
        'source_protected_paths': 289, 'source_unchanged': not changes, 'changed_paths': changes,
        'native_icon_png_viewed': 63, 'same_family_parts_added': 6,
        'item_model_declarations_checked': 61, 'native_atlas_declarations_checked': 8,
        'item_model_bound_name_families': 14, 'unproven_item_binding_excluded': 1,
        'unrelated_malformed_models_not_used': 1,
        'new_learning_groups': 5, 'combined_learning_groups': 189,
        'combined_reviewed_names': 457, 'combined_armor_names': 443,
        'reference_gate_met': False, 'rules_sha256': receipt['sha256'],
        'declaration_reader_sha256': sha(D / 'read_declarations.py'),
        'atlas_reader_sha256': sha(D / 'read_atlas_sizes.py'),
        'resource_declarations_sha256': sha(D / 'resource-declarations.json'),
        'native_atlas_declarations_sha256': sha(D / 'native-atlas-declarations.json'),
        'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0,
    }
    save('verification.json', result)
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
