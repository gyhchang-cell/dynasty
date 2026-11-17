"""Independent, read-only replay of the texture owner's version evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / 'docs/art/armor-continuation-20261102'
OUT = ROOT / 'docs/cod4/audit-20261022/coordinator-armor-history-review-20261102.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inv_path = OWNER / 'version-inventory.json'
    inv = json.loads(inv_path.read_text())
    baseline_path = OWNER / 'source-baseline.json'
    baseline = json.loads(baseline_path.read_text())
    v15_path = ROOT / 'docs/art/remaining-textures-v15/delivery-manifest.json'
    v15 = {r['source_path']: r['sha256'] for r in json.loads(v15_path.read_text())['files']}
    selected = {}
    inputs = [inv_path, baseline_path, v15_path]
    for name in ['armor-vanilla-v23', 'armor-sacred-v25', 'armor-expansion-v26', 'armor-foundations-v29']:
        path = ROOT / f'docs/art/{name}/source-check.json'
        inputs.append(path)
        for row in json.loads(path.read_text())['items']:
            selected[row['id']] = row['sha256']
    checks, errors = [], []
    for rel, expected in baseline.items():
        if sha(ROOT / rel) != expected:
            errors.append(f'baseline_changed:{rel}')
    for row in inv['rows']:
        for kind in ['icons', 'wearable']:
            for entry in row[kind]:
                actual = sha(ROOT / entry['path'])
                check = {'path': entry['path'], 'sha256': actual, 'category': row['category']}
                if actual != entry['sha256']:
                    errors.append(f'inventory_changed:{entry["path"]}')
                if row['category'] == 'V15_REDRAW_REVIEW_ONLY':
                    check['v15_match'] = actual == v15.get(entry['path'])
                    if not check['v15_match']:
                        errors.append(f'v15_disagreement:{entry["path"]}')
                if kind == 'icons':
                    model = json.loads((ROOT / entry['model']).read_text())
                    item = entry['id'].split(':', 1)[1]
                    binding = (model.get('original_texture') == f'dynasty:textures/item/{item}.png'
                               if model.get('loader') == 'dynasty:original_item'
                               else model.get('textures', {}).get('layer0') == f'dynasty:item/{item}')
                    check['binding_matches'] = binding
                    if not binding or sha(ROOT / entry['model']) != entry['model_sha256']:
                        errors.append(f'model_binding:{item}')
                    if row['category'] == 'SELECTED_ORIGINAL':
                        check['selected_match'] = actual == selected.get(item)
                        if not check['selected_match']:
                            errors.append(f'selected_disagreement:{item}')
                checks.append(check)
    rules = ROOT / 'docs/art/USER_TEXTURE_REQUIREMENTS.md'
    global_rules = Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md')
    if rules.read_bytes() != global_rules.read_bytes():
        errors.append('rule_copies_differ')
    sheets = [OWNER / n for n in ['v15_redraw_review_only-icons.png', 'protected_fine_old-icons.png', 'v15-current-worn-atlases.png']]
    # The coordinator viewed these exact full sheets with view_image, separately
    # from this hash replay. No rendered wearing claim is inferred from them.
    result = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'status': 'READ_ONLY_HISTORY_CONFIRMED' if not errors else 'REVIEW_REQUIRED',
        'owner_evidence': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in inputs],
        'rules_sha256': sha(rules),
        'protected_paths_replayed': len(baseline),
        'resource_checks': checks,
        'visual_sheets_actually_viewed': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in sheets],
        'coordinator_visual_observations': [
            'Cloth crossed straps, plain leather, dark-iron gold edging, silver round shoulders, and draco-king crown/shoulder structures are visibly different designs; these current icons are not blank vanilla substitutions.',
            'Silver/sea-silk/draco-king boots are narrow; draco-king shoulder discs and crown are large. These observations do not authorize redoing previously modified protected art.',
            'Five protected old families visibly retain their individual bronze, general, jade, sky and xuantian designs.',
            'Ten shown worn atlases carry corresponding material/color motifs, but flat atlases alone cannot establish complete face orientation, seams, or in-game wearing.'
        ],
        'history_counts': {'selected_original_icons': 52, 'fine_old_icons': 20,
                           'v15_icons': 40, 'v15_worn': 20},
        'confirmed_never_redrawn_sets': 0,
        'limits': [
            'History confirmation is limited to current bytes and recorded prior installed versions; it is not whole armor acceptance.',
            'Selected originals were independently checked against original crop/pad RGBA in armor-priority-inventory-20261102.json; this replay checks their installed hashes and actual model bindings.',
            'No new artwork, texture/model changes, applicable 1000-reference credit, UV-seam acceptance, or native game acceptance.',
            'The owner is continuing a separate 56-atlas UV review. No TODO is deleted on the strength of this history review.'
        ],
        'production_mutations': 0, 'research_credit_added': 0,
        'game_starts': 0, 'checklist_deletions': 0, 'errors': errors
    }
    if errors:
        raise RuntimeError(json.dumps(errors))
    with OUT.open('x') as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': str(OUT.relative_to(ROOT)), 'sha256': sha(OUT),
                      'protected_paths': len(baseline), 'errors': errors}))


if __name__ == '__main__':
    main()
