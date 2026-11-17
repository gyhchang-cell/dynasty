"""Complete already selected armor families from their fixed native archive, without new design credit."""
from io import BytesIO
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import zipfile
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[2]


def main():
    path = D / 'provenance.json'
    original = D / 'provenance-index-selection.json'
    if not original.exists():
        original.write_bytes(path.read_bytes())
    prov = json.loads(original.read_text())
    additions = []
    for archive in prov['archives']:
        assert hashlib.sha256(Path(archive['path']).read_bytes()).hexdigest() == archive['sha256']
        with zipfile.ZipFile(archive['path']) as z:
            for case in prov['cases']:
                if archive['path'] not in {a['jar'] for a in case['icons']}:
                    continue
                ns, family = case['case_key'].split(':')
                seen = {a['sha256'] for a in case['icons']}
                for entry in sorted(z.namelist()):
                    if not entry.startswith(f'assets/{ns}/textures/item/') or not entry.endswith('.png'):
                        continue
                    stem = Path(entry).stem
                    if not re.fullmatch(re.escape(family) + r'_(helmet|chestplate|leggings|boots|hood|robe)', stem):
                        continue
                    data = z.read(entry)
                    h = hashlib.sha256(data).hexdigest()
                    if h in seen:
                        continue
                    im = Image.open(BytesIO(data)); im.load()
                    local = Path('references') / ns / f'{h[:12]}-{Path(entry).name}'
                    (D / local).parent.mkdir(parents=True, exist_ok=True)
                    (D / local).write_bytes(data)
                    a = {'jar': archive['path'], 'entry': entry, 'sha256': h, 'size': list(im.size), 'local': str(local),
                         'source_selection': 'SAME_FAMILY_COMPLETION_FROM_FIXED_ARCHIVE_NOT_NEW_DESIGN'}
                    case['icons'].append(a); seen.add(h)
                    additions.append({'case_key': case['case_key'], **a})
    prov['icon_png'] = sum(len(c['icons']) for c in prov['cases'])
    prov['same_family_completion'] = {'initial_index_png': 90, 'added_png': len(additions),
                                      'new_name_families': 0, 'additional_design_credit': 0,
                                      'initial_selection_sha256': hashlib.sha256(original.read_bytes()).hexdigest()}
    path.write_text(json.dumps(prov, ensure_ascii=False, indent=2) + '\n')
    (D / 'same-family-completion.json').write_text(json.dumps(additions, ensure_ascii=False, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('fixed_collector', R / 'docs/art/armor-reference-study-20261102/collect.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); module.D = D
    assert max(len(c['icons']) for c in prov['cases']) <= 9, 'Split wide cases before claiming full page inspection.'
    module.draw_icons(prov['cases'])
    print(json.dumps({'families': len(prov['cases']), 'initial': 90, 'added': len(additions), 'png': prov['icon_png'], 'max_parts_per_row': max(len(c['icons']) for c in prov['cases'])}))


if __name__ == '__main__':
    main()
