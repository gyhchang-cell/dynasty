"""Verify fixed local source bytes, declaration chains, probes and conservative credit."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime, timezone
from collections import Counter
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


def save(name, data):
    (D / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    ctx = read(D / 'collection-context.json')
    assert sha(R / ctx['collector']) == ctx['collector_sha256']
    assert sha(R / ctx['prior_ledger']) == ctx['prior_ledger_sha256']
    prior = read(R / ctx['prior_ledger'])
    assert (len(prior['groups']), len(prior['case_to_group']), len(prior['reviewed_case_keys'])) == (182, 421, 434)
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
    decls, cp = read(D / 'resource-declarations.json'), read(D / 'binding-class-provenance.json')
    study = read(D / 'binding-and-rectangle-study.json')
    icons = [a for c in prov['cases'] for a in c['icons']]
    worn = prov['worn_textures']
    cases = {c['case_key'] for c in prov['cases']}
    assert len(cases) == 8 and not cases & set(prior['reviewed_case_keys'])
    assert len(icons) == len(decls) == 32 and len(worn) == 20 and len(cp['classes']) == 30
    assert sha(Path(cp['javap'])) == cp['javap_sha256']
    for index in prov['indexes']:
        assert sha(R / index['path']) == index['sha256']
    assert len(review['pages_opened']) == 7 and all((D / p).is_file() for p in review['pages_opened'])
    with ExitStack() as stack:
        jars = {a['path']: stack.enter_context(zipfile.ZipFile(a['path'])) for a in prov['archives']}
        for archive in prov['archives']:
            assert sha(Path(archive['path'])) == archive['sha256']
        for a in icons + worn + [a['model'] for a in decls] + cp['classes']:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
            if 'size' in a:
                with Image.open(D / a['local']) as im:
                    assert list(im.size) == a['size']
        for c in cp['classes']:
            assert sha(D / c['disassembly']) == c['disassembly_sha256']
        for a in decls:
            model = read(D / a['model']['local'])
            assert model['parent'] == a['parent'] and a['parent'] in ['item/generated', 'minecraft:item/generated']
            assert model['textures']['layer0'] == a['texture_location']
            ns, path = a['texture_location'].split(':')
            assert a['texture']['entry'] == f'assets/{ns}/textures/{path}.png'
            assert a['texture'] in next(c['icons'] for c in prov['cases'] if c['case_key'] == a['case_key'])
        assert Counter(a['case_key'] for a in decls) == Counter({k: 4 for k in cases})
    # Recompute static declarations and raw probes from their pinned disassemblies/PNGs.
    # main() only rewrites the same analysis JSON/chart; no Java is started here.
    before_json, before_chart = sha(D / 'binding-and-rectangle-study.json'), sha(D / 'binding-focus.png')
    spec = importlib.util.spec_from_file_location('binding_study', D / 'study_bindings.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()
    assert sha(D / 'binding-and-rectangle-study.json') == before_json and sha(D / 'binding-focus.png') == before_chart
    assert len(study['chains']) == 16 and len(study['probes']) == 8 and len(study['unresolved']) == 4
    assert len({c['case_key'] for c in study['chains']}) == 4
    assert len({c['registered_item'] for c in study['chains']}) == 16
    for c in study['chains']:
        assert not c['game_acceptance'] and not c['global_renderer_override_excluded']
    for p in study['probes']:
        if p['layer'] == 1:
            assert p['cap_alpha_gt_zero'] == 0 and p['four_side_last_row_alpha_gt_zero'] == [0] * 4
            assert p['body_rows_alpha_ge_128'] == [16, 22, 24, 24, 24, 24, 24, 24, 24, 12, 4, 0]
        else:
            assert p['body_rows_alpha_ge_128'] == [0] * 7 + [24] * 5
            assert [(a[0], a[1], a[2][3]) for a in p['weak_alpha_pixels_in_upper_body_probe']] == [(16, y, 1) for y in [23, 24, 25]]
    flat = [c for row in review['observations'] for c in row['cases']]
    assert len(flat) == len(set(flat)) == 8 and set(flat) == cases == set(review['case_observations'])
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
    reviewed = sorted(set(owners) | {e['case_key'] for e in prior['excluded_cases']})
    assert (new, append, len(groups), len(owners), len(reviewed), len(prior['excluded_cases'])) == (2, 1, 184, 429, 442, 13)
    save('combined-semantic-ledger.json', {**prior,
        'source_reviews': prior['source_reviews'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
        'groups': [g for _, g in sorted(groups.items())], 'case_to_group': dict(sorted(owners.items())),
        'reviewed_case_keys': reviewed, 'name_families': 442, 'armor_name_families': 429, 'conservative_learning_groups': 184})
    save('reference-gate-accounting.json', {
        'required_valid_related_independent_designs': 1000, 'reviewed_name_families': 442,
        'armor_name_families_after_exclusion': 429, 'excluded_non_player_equipment': 1,
        'excluded_player_accessory_or_slot_unproven': 12, 'excluded_from_full_armor_gate': 13,
        'conservative_learning_groups_in_current_subset': 184, 'validated_independent_design_total': None,
        'maximum_credit_under_current_one_per_group_policy': 184, 'unfilled_minimum_under_current_policy': 816,
        'reference_gate_met': False,
        'gap_limit': '学习组含局部、材料变体和反例，尚未验收为完整独立设计；816只是所有组合格时的最低缺口。'})
    assert all(review[k] == 0 for k in ['new_artwork', 'production_changes', 'game_starts']) and not review['gate_met']
    result = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
        'source_protected_paths': 289, 'source_unchanged': not changes, 'changed_paths': changes,
        'native_icon_png_viewed': 32, 'native_worn_entries_viewed': 20,
        'distinct_worn_payloads': len({a['sha256'] for a in worn}),
        'model_json_declarations_checked': 32, 'class_declarations_checked': 30,
        'complete_static_item_chains': 16, 'sets_with_complete_static_chain': 4,
        'sets_with_unresolved_worn_chain': 4, 'source_rectangle_probes': 8,
        'new_learning_groups': 2, 'combined_learning_groups': 184,
        'combined_reviewed_names': 442, 'combined_armor_names': 429,
        'reference_gate_met': False, 'rules_sha256': receipt['sha256'],
        'study_script_sha256': sha(D / 'study_bindings.py'),
        'binding_study_sha256': sha(D / 'binding-and-rectangle-study.json'),
        'class_provenance_sha256': sha(D / 'binding-class-provenance.json'),
        'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'checklist_deletions': 0,
    }
    save('verification.json', result)
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
