"""Read matching apparel/armor parts from the same frozen JARs, retaining native version variants."""
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
PARTS = 'helmet|chestplate|chest_plate|leggings|boots|hood|robe|hat|jacket|pants|apron|blouse|dress|regalia|shoes|trousers|hat_red|cuirass'


def main():
    original = D / 'provenance-index-selection.json'
    if not original.exists():
        original.write_bytes((D / 'provenance.json').read_bytes())
    prov = json.loads(original.read_text())
    initial = sum(len(c['icons']) for c in prov['cases'])
    aliases = {'royalvariations:royal_knight_cuirass': 'royalvariations:royal_knight'}
    grouped = {}
    for case in prov['cases']:
        key = aliases.get(case['case_key'], case['case_key'])
        grouped.setdefault(key, {'case_key': key, 'icons': [], 'status': case['status']})['icons'].extend(case['icons'])
    prov['cases'] = list(grouped.values())
    prov['icon_name_families'] = len(prov['cases'])
    (D / 'name-normalization.json').write_text(json.dumps({'aliases': aliases, 'raw_names': 33, 'normalized_names': 32}, indent=2) + '\n')
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
                    if not re.fullmatch(re.escape(family) + '_(' + PARTS + ')', Path(entry).stem):
                        continue
                    data = z.read(entry); h = hashlib.sha256(data).hexdigest()
                    if h in seen:
                        continue
                    im = Image.open(BytesIO(data)); im.load()
                    local = Path('references') / ns / f'{h[:12]}-{Path(entry).name}'
                    (D / local).parent.mkdir(parents=True, exist_ok=True); (D / local).write_bytes(data)
                    asset = {'jar': archive['path'], 'entry': entry, 'sha256': h, 'size': list(im.size), 'local': str(local),
                             'source_selection': 'MATCHING_NATIVE_APPAREL_PART_OR_VERSION_ZERO_NEW_DESIGN_CREDIT'}
                    case['icons'].append(asset); seen.add(h); additions.append({'case_key': case['case_key'], **asset})
    prov['icon_png'] = sum(len(c['icons']) for c in prov['cases'])
    prov['same_family_completion'] = {'initial_index_png': initial, 'added_png': len(additions),
                                     'initial_selection_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
                                     'new_name_families': 0, 'additional_design_credit': 0}
    (D / 'provenance.json').write_text(json.dumps(prov, ensure_ascii=False, indent=2) + '\n')
    (D / 'same-family-completion.json').write_text(json.dumps(additions, ensure_ascii=False, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('fixed_collector', R / 'docs/art/armor-reference-study-20261102/collect.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); module.D = D
    assert max(len(c['icons']) for c in prov['cases']) <= 9
    module.draw_icons(prov['cases'])
    print(json.dumps({'families': len(prov['cases']), 'initial': initial, 'added': len(additions), 'native_png': prov['icon_png']}))


if __name__ == '__main__':
    main()
