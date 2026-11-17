"""Inventory current armor without publishing or changing any artwork."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'src/main/resources/assets/dynasty'
ART = ROOT / 'docs/art'
OUT = ROOT / 'docs/cod4/audit-20261022/armor-priority-inventory-20261102.json'
PROTECTED = {'general', 'jade', 'sky', 'bronze', 'xuantian'}
PARTS = ['helmet', 'chestplate', 'leggings', 'boots']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT / 'src/main/java/com/dynasty/DynastyGear.java'
    code = source.read_text()
    direct = re.findall(r'armor\("([a-z_]+)_(?:helmet|chestplate|leggings|boots)"', code)
    table = re.findall(r'\{"([a-z_]+)", DynastyArmorMaterials\.', code)
    sets = list(dict.fromkeys(direct + table))
    assert len(sets) == 28
    manifest_path = ART / 'inventory-refresh-v1/generated-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    selected = {r['id']: r for group in manifest.values() for r in group}
    worn_baseline_path = ART / 'armor-foundations-v29/preservation-check.json'
    worn_baseline = json.loads(worn_baseline_path.read_text())
    baseline_path = ART / 'armor-foundations-v29/baseline.json'
    baseline = json.loads(baseline_path.read_text()) if baseline_path.exists() else {}
    rows = []
    errors = []
    for family in sets:
        row = {'set': family, 'protected_older_design': family in PROTECTED,
               'inventory_icons': [], 'wearable_atlases': []}
        for part in PARTS:
            ident = family + '_' + part
            image_path = ASSETS / 'textures/item' / (ident + '.png')
            model_path = ASSETS / 'models/item' / (ident + '.json')
            model = json.loads(model_path.read_text())
            with Image.open(image_path) as image:
                image = image.convert('RGBA')
                item = {'id': 'dynasty:' + ident, 'path': str(image_path.relative_to(ROOT)),
                        'sha256': sha(image_path), 'dimensions': list(image.size),
                        'model': str(model_path.relative_to(ROOT)),
                        'model_sha256': sha(model_path), 'model_declaration': model}
                if ident in selected:
                    choice = selected[ident]
                    original_path = ROOT / choice['source']
                    with Image.open(original_path) as original:
                        original = original.convert('RGBA')
                        bounds = choice.get('crop_bounds', original.getbbox())
                        crop = original.crop(bounds)
                        # Compare in memory; no image is created on disk or published.
                        expected = Image.new('RGBA', (crop.width + 4, crop.height + 4))
                        expected.paste(crop, (2, 2))
                        pixels_equal = image.size == expected.size and image.tobytes() == expected.tobytes()
                    reference = 'dynasty:textures/item/' + ident + '.png'
                    binding = model.get('loader') == 'dynasty:original_item' and model.get('original_texture') == reference
                    item.update(status='SELECTED_ORIGINAL_INSTALLED_PRESERVE' if pixels_equal and binding
                                else 'SELECTED_VERSION_OR_BINDING_REQUIRES_REVIEW',
                                selected_original=choice['source'], original_sha256=sha(original_path),
                                original_crop_rgba_matches=pixels_equal, original_loader_binding=binding)
                    if not pixels_equal or not binding:
                        errors.append(ident)
                elif family in PROTECTED:
                    item['status'] = 'PROTECTED_OLDER_DESIGN_DO_NOT_REDRAW'
                else:
                    item['status'] = 'NO_CURRENT_SELECTED_ORIGINAL_ENTRY_REVIEW_OLD_ART_FIRST'
                row['inventory_icons'].append(item)
        for layer in (1, 2):
            path = ASSETS / 'textures/models/armor' / f'{family}_layer_{layer}.png'
            with Image.open(path) as image:
                dimensions = list(image.size)
            rel = str(path.relative_to(ROOT))
            # A matching historical byte hash establishes unchanged files, not style acceptance.
            previous = baseline.get(rel) if isinstance(baseline, dict) else None
            row['wearable_atlases'].append({
                'path': rel, 'sha256': sha(path), 'dimensions': dimensions,
                'v29_baseline_hash': previous,
                'matches_v29_baseline': sha(path) == previous if isinstance(previous, str) else None,
                'status': 'PROTECTED_OLDER_DESIGN_DO_NOT_REDRAW' if family in PROTECTED
                          else 'SEPARATE_WORN_UV_REVIEW_REQUIRED_NOT_INFERRED_FROM_ICON'
            })
        rows.append(row)
    canonical = [r for r in rows if all(i['status'] == 'SELECTED_ORIGINAL_INSTALLED_PRESERVE'
                                      for i in r['inventory_icons'])]
    pending = [r['set'] for r in rows if r['set'] not in PROTECTED and r not in canonical]
    report = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'status': 'READ_ONLY_PRIORITY_INVENTORY' if not errors else 'VERSION_REVIEW_REQUIRED',
        'human_priority': '做贴图的先做确实没改过的盔甲；已改好及精致旧稿保持；遵守已保存用户标准',
        'source_sha256': {str(source.relative_to(ROOT)): sha(source),
                          str(manifest_path.relative_to(ROOT)): sha(manifest_path),
                          str(baseline_path.relative_to(ROOT)): sha(baseline_path),
                          str(worn_baseline_path.relative_to(ROOT)): sha(worn_baseline_path),
                          'docs/art/USER_TEXTURE_REQUIREMENTS.md': sha(ART / 'USER_TEXTURE_REQUIREMENTS.md'),
                          str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        'sets': len(rows), 'inventory_icons': 4 * len(rows), 'wearable_atlases': 2 * len(rows),
        'selected_original_installed_sets': [r['set'] for r in canonical],
        'selected_original_installed_icons': 4 * len(canonical),
        'protected_older_sets': sorted(PROTECTED),
        'icon_families_requiring_old_art_review': pending,
        'not_selected_does_not_mean_unmodified_or_low_quality': True,
        'selected_version_errors': errors, 'rows': rows,
        'historical_v29_preservation_summary': worn_baseline,
        'limitations': [
            'Pixel/source and resource-binding inventory, not new visual/UV/game acceptance.',
            'Current selected originals are preserved, not newly counted as research or completion.',
            'Nonselected IDs require existing history and actual visual review before deciding to redraw.',
            'Inventory icon and wearable atlas statuses are separate; no body model edits authorized here.'
        ], 'new_texture_batches': 0, 'production_mutations': 0, 'game_starts': 0,
        'reference_credit': 0, 'checklist_deletions': 0, 'no_automation': True
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'sets', 'selected_original_installed_icons',
                                           'icon_families_requiring_old_art_review', 'selected_version_errors']},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
