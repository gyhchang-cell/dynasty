"""Validate frozen source bytes, static binding reconstruction, semantic ledger and safeguards."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import zipfile
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[2]


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(n, data):
    (D / n).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    ctx = read(D / 'collection-context.json')
    for base in ['collector', 'chart_collector', 'prior_ledger']:
        assert sha(R / ctx[base]) == ctx[base + '_sha256']
    prior = read(R / ctx['prior_ledger'])
    assert (len(prior['groups']), len(prior['case_to_group']), len(prior['reviewed_case_keys'])) == (189, 443, 457)
    assert set(ctx['skipped_previously_reviewed_cases']) == set(prior['reviewed_case_keys'])
    for row in prior['source_reviews']:
        assert sha(R / row['path']) == row['sha256']
    baseline = read(D / 'source-baseline.json')
    changes = [p for p, h in baseline.items() if not (R / p).is_file() or sha(R / p) != h]
    assert len(baseline) == 289
    receipt = read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(receipt['targets']) == len(set(receipt['targets'])) == 24
    assert receipt['sha256'] == sha(R / receipt['snapshot']) == sha(R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md') == sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    prov, review = read(D / 'provenance.json'), read(D / 'semantic-review.json')
    decls, cp, study = read(D / 'resource-declarations.json'), read(D / 'binding-class-provenance.json'), read(D / 'declared-layout-study.json')
    assert sha(R / prov['source_provenance']) == prov['source_provenance_sha256']
    icons = [a for c in prov['cases'] for a in c['icons']]
    worn = prov['worn_textures']
    cases = {c['case_key'] for c in prov['cases']}
    assert len(cases) == 14 and not cases & set(prior['reviewed_case_keys'])
    assert len(icons) == len(decls) == 56 and len(worn) == 28 and len(cp['classes']) == 73
    assert sha(Path(cp['javap'])) == cp['javap_sha256']
    assert len(review['pages_opened']) == 7 and all((D / p).is_file() for p in review['pages_opened'])
    with ExitStack() as stack:
        jars = {a['path']: stack.enter_context(zipfile.ZipFile(a['path'])) for a in prov['archives']}
        for a in prov['archives']:
            assert sha(Path(a['path'])) == a['sha256']
        for a in icons + worn + [a['model'] for a in decls] + cp['classes']:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
            if 'size' in a:
                with Image.open(D / a['local']) as image:
                    assert list(image.size) == a['size']
        for a in cp['classes']:
            assert sha(D / a['disassembly']) == a['disassembly_sha256']
        for a in decls:
            model = read(D / a['model']['local'])
            assert model['parent'] == a['parent'] and a['parent'] in ['item/generated', 'minecraft:item/generated']
            assert model['textures']['layer0'] == a['texture_location']
            ns, tex = a['texture_location'].split(':')
            assert a['texture']['entry'] == f'assets/{ns}/textures/{tex}.png'
            assert a['texture'] in next(c['icons'] for c in prov['cases'] if c['case_key'] == a['case_key'])
        for c in prov['cases']:
            assert {a['part'] for a in decls if a['case_key'] == c['case_key']} == {'helmet', 'chestplate', 'leggings', 'boots'}
    before = sha(D / 'declared-layout-study.json')
    spec = importlib.util.spec_from_file_location('source_study', D / 'study_declared_layout.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.main()
    assert sha(D / 'declared-layout-study.json') == before
    assert len(study['chains']) == 56 and len({c['registered_item'] for c in study['chains']}) == 56
    assert study['name_families_with_declared_chain'] == 14
    assert study['source_atlas_rectangles_probed'] == 22 and study['nonstandard_atlases_not_forced'] == 6
    assert all(not c['game_acceptance'] and not c['global_renderer_override_excluded'] for c in study['chains'])
    for a in study['probes']:
        if a['probed']:
            if a['worn']['layer'] == 1:
                assert a['cap_alpha_gt_zero'] == 0 and a['four_side_last_rows_alpha_gt_zero'] == [0] * 4
            else:
                assert a['body_rows_alpha_ge_128'][:7] == [0] * 7
                assert a['body_rows_alpha_ge_128'][7] in [16, 24] and a['body_rows_alpha_ge_128'][8:] == [24] * 4
    flat = [c for row in review['observations'] for c in row['cases']]
    assert len(flat) == len(set(flat)) == 14 and set(flat) == cases and not review['excluded_cases']
    groups = {g['semantic_group']: g for g in prior['groups']}
    new = append = 0
    for row in review['observations']:
        k = row['semantic_group']
        if row['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP':
            assert k not in groups
            groups[k] = {'semantic_group': k, 'cases': [], 'observations': []}; new += 1
        else:
            assert row['credit'] == 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group'] == k and k in groups
            append += 1
        groups[k]['cases'] = sorted(set(groups[k]['cases']) | set(row['cases']))
        groups[k]['observations'].append({'source': str((D / 'semantic-review.json').relative_to(R)), 'observation': row['observation']})
    owners = {}
    for k, g in groups.items():
        for c in g['cases']:
            assert c not in owners; owners[c] = k
    reviewed = sorted(set(owners) | {e['case_key'] for e in prior['excluded_cases']})
    assert (new, append, len(groups), len(owners), len(reviewed)) == (1, 4, 190, 457, 471)
    save('combined-semantic-ledger.json', {**prior,
        'source_reviews': prior['source_reviews'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
        'groups': [g for _, g in sorted(groups.items())], 'case_to_group': dict(sorted(owners.items())),
        'reviewed_case_keys': reviewed, 'name_families': 471, 'armor_name_families': 457, 'conservative_learning_groups': 190})
    save('reference-gate-accounting.json', {
        'required_valid_related_independent_designs': 1000, 'reviewed_name_families': 471,
        'armor_name_families_after_exclusion': 457, 'excluded_non_player_equipment': 1,
        'excluded_player_accessory_or_slot_unproven': 13, 'excluded_from_full_armor_gate': 14,
        'conservative_learning_groups_in_current_subset': 190, 'validated_independent_design_total': None,
        'maximum_credit_under_current_one_per_group_policy': 190, 'unfilled_minimum_under_current_policy': 810,
        'reference_gate_met': False,
        'gap_limit': '190学习组含局部、变体和反例，不等于190个已验完整独立设计；810仅为所有组合格时最低缺口。'})
    assert all(review[k] == 0 for k in ['new_artwork', 'production_changes', 'game_starts']) and not review['gate_met']
    result = {'checked_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
        'source_protected_paths': 289, 'source_unchanged': not changes, 'changed_paths': changes,
        'native_icon_entries_viewed': 56, 'distinct_icon_payloads': len({a['sha256'] for a in icons}),
        'native_worn_entries_viewed': 28, 'distinct_worn_payloads': len({a['sha256'] for a in worn}),
        'model_json_declarations_checked': 56, 'class_declarations_checked': 73,
        'complete_static_item_chains': 56, 'complete_static_name_families': 14,
        'source_atlas_rectangles_probed': 22, 'nonstandard_atlases_not_forced': 6,
        'new_learning_groups': 1, 'combined_learning_groups': 190, 'combined_reviewed_names': 471,
        'combined_armor_names': 457, 'reference_gate_met': False, 'rules_sha256': receipt['sha256'],
        'binding_class_provenance_sha256': sha(D / 'binding-class-provenance.json'),
        'binding_reader_sha256': sha(D / 'read_binding_classes.py'),
        'study_script_sha256': sha(D / 'study_declared_layout.py'), 'declared_layout_sha256': before,
        'analysis_chart_script_sha256': sha(D / 'draw_review_icons.py'),
        'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0}
    save('verification.json', result)
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
