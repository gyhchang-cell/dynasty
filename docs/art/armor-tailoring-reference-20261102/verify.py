"""Verify original reference bytes, bounded read evidence and untouched shared production assets."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import zipfile
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    baseline = read(D / 'source-baseline.json')
    changes = [p for p, h in baseline.items() if not (R / p).is_file() or sha(R / p) != h]
    ctx = read(D / 'collection-context.json')
    assert sha(R / ctx['collector']) == ctx['collector_sha256']
    assert sha(R / ctx['prior_ledger']) == ctx['prior_ledger_sha256']
    prior = read(R / ctx['prior_ledger'])
    assert len(prior['groups']) == 104 and len(prior['case_to_group']) == 227
    assert set(ctx['skipped_previously_reviewed_cases']) == set(prior['case_to_group'])
    for row in prior['source_reviews']:
        assert sha(R / row['path']) == row['sha256']
    receipt = read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(receipt['targets']) == len(set(receipt['targets'])) == 24
    assert receipt['sha256'] == sha(R / receipt['snapshot']) == sha(R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md') == sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    prov, review = read(D / 'provenance.json'), read(D / 'semantic-review.json')
    worn, probes = read(D / 'selected-worn-provenance.json'), read(D / 'native-rectangle-study.json')
    icons = [a for c in prov['cases'] for a in c['icons']]
    cases = {c['case_key'] for c in prov['cases']}
    assert len(cases) == 37 and len(icons) == 104 and not cases & set(prior['case_to_group'])
    flat = [c for row in review['observations'] for c in row['cases']]
    assert len(flat) == len(set(flat)) == 37 and set(flat) == cases
    assert len(worn['textures']) == 23 and len({a['sha256'] for a in worn['textures']}) == worn['distinct_png_sha256'] == 21
    assert worn['counted_as_additional_designs'] == 0
    assert len(review['pages_opened']) == 12 and all((D / p).is_file() for p in review['pages_opened'])
    groups = {g['semantic_group']: g for g in prior['groups']}
    new = append = 0
    for row in review['observations']:
        key = row['semantic_group']
        if row['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP':
            assert key not in groups
            groups[key] = {'semantic_group': key, 'cases': [], 'observations': []}
            new += 1
        else:
            assert row['credit'] == 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and key == row['prior_group'] and key in groups
            append += 1
        groups[key]['cases'] = sorted(set(groups[key]['cases']) | set(row['cases']))
        groups[key]['observations'].append({'source': str((D / 'semantic-review.json').relative_to(R)), 'observation': row['observation']})
    assert new == 13 and append == 2
    owners = {}
    for key, group in groups.items():
        for case in group['cases']:
            assert case not in owners
            owners[case] = key
    assert len(owners) == review['combined_name_families'] == 264
    assert len(groups) == review['combined_conservative_learning_groups'] == 117
    assert not review['gate_met'] and review['new_artwork'] == review['production_changes'] == 0
    with ExitStack() as stack:
        jars = {row['path']: stack.enter_context(zipfile.ZipFile(row['path'])) for row in prov['archives']}
        for row in prov['archives']:
            assert sha(Path(row['path'])) == row['sha256']
        for row in prov['indexes']:
            assert sha(R / row['path']) == row['sha256']
        for a in icons + worn['textures']:
            assert sha(D / a['local']) == a['sha256'] == hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
    assert sha(R / probes['target_uv_contract']) == probes['target_uv_contract_sha256']
    worn_by_entry = {a['entry']: a for a in worn['textures']}
    assert len(probes['source_rectangles']) == 12 and len(probes['zero_alpha_entries']) == 5
    for row in probes['source_rectangles']:
        a = worn_by_entry[row['entry']]
        assert a['sha256'] == row['sha256'] and a['runtime_binding_proven'] is False
        im = Image.open(D / a['local']).convert('RGBA')
        for name in ['cap', 'terminal', 'body_strip']:
            if name not in row:
                continue
            values = im.crop(row[name]['source_rect']).getchannel('A').tobytes()
            assert len(values) == row[name]['pixels']
            assert sum(v > 0 for v in values) == row[name]['visible']
            assert sum(v == 255 for v in values) == row[name]['opaque']
        if 'rows_visible' in row:
            assert row['rows_visible'] == [sum(v > 0 for v in im.crop((16, y, 40, y + 1)).getchannel('A').tobytes()) for y in range(20, 32)]
    for row in probes['zero_alpha_entries']:
        assert Image.open(D / worn_by_entry[row['entry']]['local']).convert('RGBA').getchannel('A').getbbox() is None
    methods = read(D / 'application-methods.json')
    assert len(methods['methods']) == 3 and methods['production_changes'] == 0 and not methods['gate_met']
    old_roles = read(R / 'docs/art/armor-reference-study-20261102/application-principles.json')
    for material in old_roles['protected_selected_materials'].values():
        for icon in material['icons_to_preserve']:
            assert sha(R / icon['path']) == icon['sha256']
    cumulative = {**{k: v for k, v in prior.items() if k not in {'groups', 'case_to_group', 'source_reviews', 'name_families', 'conservative_learning_groups'}},
                  'source_reviews': prior['source_reviews'] + [{'path': str((D / 'semantic-review.json').relative_to(R)), 'sha256': sha(D / 'semantic-review.json')}],
                  'groups': [g for _, g in sorted(groups.items())], 'case_to_group': dict(sorted(owners.items())),
                  'name_families': len(owners), 'conservative_learning_groups': len(groups)}
    (D / 'combined-semantic-ledger.json').write_text(json.dumps(cumulative, ensure_ascii=False, indent=2) + '\n')
    accounting = {
        'required_valid_related_independent_designs': 1000, 'reviewed_name_families': 264,
        'conservative_learning_groups_in_current_subset': 117,
        'validated_independent_design_total': None,
        'pending_reason': '含缺部位、单件或稀疏附层的学习组；未完成全部组的完整适用性及跨组独立设计验收。不能用117直接宣称117套已验收设计。',
        'maximum_credit_under_current_one_per_group_policy': 117,
        'unfilled_minimum_under_current_policy': 883,
        'gap_limit': '883只是即使当前117组全合格仍至少剩余的缺口；当前真实缺口可能更大。',
        'source_png_count_is_never_design_credit': True, 'reference_gate_met': False,
    }
    (D / 'reference-gate-accounting.json').write_text(json.dumps(accounting, ensure_ascii=False, indent=2) + '\n')
    result = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
              'source_protected_paths': len(baseline), 'source_unchanged': not changes, 'changed_paths': changes,
              'native_icon_png_viewed': 104, 'new_name_families': 37, 'worn_entries_viewed': 23, 'unique_worn_png': 21,
              'source_rectangles_studied': 12, 'application_methods': 3,
              'new_learning_groups': 13, 'combined_learning_groups': 117, 'combined_name_families': 264,
              'minimum_open_reference_gap_under_current_policy': 883, 'reference_gate_met': False,
              'rules_sha256': receipt['sha256'], 'production_changes': 0, 'new_artwork': 0, 'game_starts': 0, 'checklist_deletions': 0}
    (D / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    assert not changes


if __name__ == '__main__':
    main()
