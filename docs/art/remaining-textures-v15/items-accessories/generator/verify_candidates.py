"""Read-only candidate/source checks; writes this batch's report only."""
from pathlib import Path
from PIL import Image
import json, hashlib, collections

R = Path('/Users/a15356015027/Desktop/dynasty')
O = R / 'docs/art/remaining-textures-v15/items-accessories'
allowed = json.loads((O / 'allowed.json').read_text())
base = {x['id']: x for x in json.loads((O / 'manifest/baseline.json').read_text())}
designs = {x['id']: x for x in json.loads((O / 'manifest/all-items.json').read_text())}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rows = []
dupes = collections.defaultdict(list)
for id in allowed:
    b = base[id]
    p = O / 'candidate/assets/dynasty/textures/item' / (id + '.png')
    im = Image.open(p).convert('RGBA')
    opaque = {px for px in im.get_flattened_data() if px[3]}
    alphas = sorted(set(im.getchannel('A').get_flattened_data()))
    bbox = list(im.getchannel('A').getbbox())
    j = json.loads((R / b['model']).read_text())
    row = {
        'id': id, 'candidate': str(p.relative_to(O)), 'sha256': sha(p),
        'size': list(im.size), 'opaque_colors': len(opaque), 'alpha': alphas,
        'bbox': bbox, 'transparent_border': bbox[0] >= 1 and bbox[1] >= 1 and bbox[2] <= 31 and bbox[3] <= 31,
        'backup_matches_source_baseline': sha(O / b['backup']) == b['source_sha256'],
        'source_unchanged': sha(R / b['source']) == b['source_sha256'],
        'model': b['model'], 'model_parent': j.get('parent'),
        'model_layer0': j.get('textures', {}).get('layer0'),
        'model_layer0_matches': j.get('textures', {}).get('layer0') == 'dynasty:item/' + id,
        'source_mcmeta_exists': (R / (b['source'] + '.mcmeta')).exists(),
        'manifest_sha_matches': sha(p) == designs[id]['sha256'],
        'design': designs[id]['design']}
    rows.append(row)
    dupes[row['sha256']].append(id)

report = {
    'count': len(rows), 'candidate_only': True, 'game_tested': False,
    'exact_allowed_scope': {p.stem for p in (O / 'candidate/assets/dynasty/textures/item').glob('*.png')} == set(allowed),
    'all_native_32_rgba_binary_alpha': all(r['size'] == [32, 32] and r['alpha'] == [0, 255] for r in rows),
    'all_transparent_border': all(r['transparent_border'] for r in rows),
    'all_backups_match_baseline': all(r['backup_matches_source_baseline'] for r in rows),
    'all_source_unchanged': all(r['source_unchanged'] for r in rows),
    'all_models_reference_candidate_names': all(r['model_layer0_matches'] for r in rows),
    'all_models_generated_items': all(r['model_parent'] in ['minecraft:item/generated', 'item/generated'] for r in rows),
    'all_manifest_sha_matches': all(r['manifest_sha_matches'] for r in rows),
    'existing_animation_metadata': [r['id'] for r in rows if r['source_mcmeta_exists']],
    'duplicate_png_groups': [v for v in dupes.values() if len(v) > 1],
    'opaque_color_range': [min(r['opaque_colors'] for r in rows), max(r['opaque_colors'] for r in rows)],
    'visual_review_pages': ['previews/all-%02d.png' % i for i in range(1, 8)],
    'rows': rows}
assert report['count'] == 138 and report['exact_allowed_scope']
assert report['all_native_32_rgba_binary_alpha'] and report['all_transparent_border']
assert report['all_backups_match_baseline'] and report['all_source_unchanged']
assert report['all_models_reference_candidate_names'] and report['all_models_generated_items']
assert report['all_manifest_sha_matches']
assert not report['existing_animation_metadata'] and not report['duplicate_png_groups']
(O / 'manifest/verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, ensure_ascii=False, indent=2))
