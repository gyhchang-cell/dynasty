from pathlib import Path
from PIL import Image
from io import BytesIO
from itertools import combinations
import hashlib
import json
import warnings
import zipfile

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ARCHIVE = ART / 'armor-three-whole-20261112/wizardsreborn-fixed.zip'
SLOTS = {
    'soul_hunter': ('hood', 'costume', 'trousers', 'boots'),
    'royal_guard': ('hat', 'costume', 'trousers', 'boots'),
    'magnificent_maid': ('headwear', 'suit', 'stockings', 'boots'),
    'capitalist': ('hat', 'costume', 'trousers', 'boots'),
    'inventor_wizard': ('hat', 'costume', 'trousers', 'boots'),
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def visible_pixels(image):
    rgba = image.convert('RGBA').tobytes()
    return bytes(component for i in range(0, len(rgba), 4)
                 for component in (rgba[i:i+4] if rgba[i+3] else b'\0'*4))

def key(image):
    return (image.size, digest(visible_pixels(image)))

with zipfile.ZipFile(ARCHIVE) as source:
    images = {}
    for case, parts in SLOTS.items():
        skin = 'skin/' if case != 'inventor_wizard' else ''
        endings = [f'/textures/item/{skin}{case}_{part}.png' for part in parts]
        endings.append(f'/textures/models/armor/{skin}{case}.png')
        selected = []
        for suffix in endings:
            matches = [n for n in source.namelist() if n.endswith(suffix)]
            assert len(matches) == 1, suffix
            selected.append(Image.open(BytesIO(source.read(matches[0]))).convert('RGBA'))
        images[case] = selected

comparison = {}
for a, b in combinations(images, 2):
    dimensions = all(x.size == y.size for x,y in zip(images[a],images[b]))
    match_masks = dimensions and all(x.getchannel('A').tobytes() == y.getchannel('A').tobytes()
                                     for x,y in zip(images[a],images[b]))
    mapping = set()
    if match_masks:
        for left, right in zip(images[a], images[b]):
            x, y = visible_pixels(left), visible_pixels(right)
            mapping.update((x[i:i+4], y[i:i+4]) for i in range(0,len(x),4) if x[i+3])
    equivalent = match_masks and len(mapping) == len({x for x,_ in mapping}) == len({y for _,y in mapping})
    comparison[f'{a} vs {b}'] = {'same_alpha_masks_all_five':match_masks,
         'single_bijective_palette_mapping_over_all_five':equivalent,
         'mapping':sorted([x.hex(),y.hex()] for x,y in mapping) if equivalent else []}
assert comparison['royal_guard vs capitalist']['single_bijective_palette_mapping_over_all_five']

targets = {key(im): [] for case, imgs in images.items() if case != 'inventor_wizard' for im in imgs}
checked = 0
errors = []
for folder in sorted(ART.glob('armor-*')):
    if folder == HERE or folder.name == 'armor-skin-three-20261120':
        continue
    for path in sorted(folder.rglob('*.png')):
        try:
            with Image.open(path) as im:
                if im.size not in {(16,16),(128,64)}:
                    continue
                checked += 1
                signature = key(im)
                if signature in targets:
                    targets[signature].append(str(path.relative_to(ART)))
        except (OSError, ValueError) as exc:
            errors.append({'path':str(path.relative_to(ART)), 'error':str(exc)})
result = {
    'scope':'Existing extracted PNGs of matching dimensions in docs/art/armor-* outside these two batches. Exact visible pixels ignore hidden RGB. Source archives and semantic similarity across the entire catalog are not covered by this PNG search.',
    'same_archive_pairwise_comparison':comparison,
    'historical_dimension_matched_images_scanned':checked,
    'historical_decode_errors':errors,
    'exact_historical_asset_matches':{
        case:[targets[key(im)] for im in imgs] for case,imgs in images.items() if case != 'inventor_wizard'
    },
}
(HERE/'pixel-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(checked, len(errors), {name:sum(len(p) for p in paths) for name,paths in result['exact_historical_asset_matches'].items()})
