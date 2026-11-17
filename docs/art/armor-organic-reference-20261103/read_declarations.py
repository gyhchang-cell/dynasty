"""Read actual item JSON references and complete only matching part prefixes."""
from pathlib import Path
from io import BytesIO
import hashlib
import importlib.util
import json
import re
import zipfile
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[2]


def main():
    assert not (D / 'resource-declarations.json').exists()
    prov = json.loads((D / 'provenance.json').read_text())
    decls, additions, malformed = [], [], []
    part_re = re.compile(r'_(helmet|chestplate|leggings|boots)$')
    for archive in prov['archives']:
        jar = archive['path']
        with zipfile.ZipFile(jar) as z:
            models = []
            for e in z.namelist():
                if '/models/item/' not in e or not e.endswith('.json'):
                    continue
                try:
                    model = json.loads(z.read(e))
                except (ValueError, UnicodeError) as exc:
                    malformed.append({'jar': jar, 'entry': e, 'reason': type(exc).__name__, 'used': False})
                    continue
                loc = model.get('textures', {}).get('layer0')
                if not isinstance(loc, str) or ':' not in loc or not part_re.search(Path(e).stem):
                    continue
                ns, path = loc.split(':', 1)
                texture = f'assets/{ns}/textures/{path}.png'
                models.append((e, model, loc, texture))
            for case in prov['cases']:
                known = {a['entry'] for a in case['icons'] if a['jar'] == jar}
                if not known:
                    continue
                matching_prefixes = {part_re.sub('', Path(e).stem) for e, model, loc, tex in models if tex in known}
                for e, model, loc, tex in models:
                    if part_re.sub('', Path(e).stem) not in matching_prefixes:
                        continue

                    def copy(entry, directory, is_image=False):
                        b = z.read(entry)
                        h = hashlib.sha256(b).hexdigest()
                        ns = entry.split('/')[1]
                        local = Path(directory) / ns / f'{h[:12]}-{Path(entry).name}'
                        (D / local).parent.mkdir(parents=True, exist_ok=True)
                        (D / local).write_bytes(b)
                        result = {'jar': jar, 'entry': entry, 'sha256': h, 'local': str(local)}
                        if is_image:
                            result['size'] = list(Image.open(BytesIO(b)).size)
                        return result

                    texture = copy(tex, 'references', True)
                    declaration = {'case_key': case['case_key'], 'part': part_re.search(Path(e).stem).group(1),
                                   'model': copy(e, 'declarations'), 'texture': texture,
                                   'texture_location': loc, 'parent': model.get('parent'), 'json_pointer': '/textures/layer0'}
                    decls.append(declaration)
                    if not any(a['sha256'] == texture['sha256'] for a in case['icons']):
                        case['icons'].append(texture)
                        additions.append({**texture, 'case_key': case['case_key'], 'reason': 'Actual JSON reference; same confirmed model part-prefix'})
    (D / 'resource-declarations.json').write_text(json.dumps(decls, ensure_ascii=False, indent=2) + '\n')
    (D / 'same-family-completion.json').write_text(json.dumps(additions, ensure_ascii=False, indent=2) + '\n')
    (D / 'unrelated-malformed-models.json').write_text(json.dumps(malformed, ensure_ascii=False, indent=2) + '\n')
    # Preserve the immutable initial candidate provenance. The completed copy has all reviewed parts.
    prov['icon_png'] = sum(len(c['icons']) for c in prov['cases'])
    (D / 'completed-provenance.json').write_text(json.dumps(prov, ensure_ascii=False, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('charts', R / 'docs/art/armor-reference-study-20261102/collect.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.D = D
    # Preserve the original index-selection chart files as well.
    before = {p.name for p in D.glob('icons-*.png')}
    for name in before:
        (D / name).rename(D / ('index-' + name))
    m.draw_icons(prov['cases'])
    print(json.dumps({'initial_icons': 57, 'added_same_family_parts': len(additions),
                      'completed_icons': prov['icon_png'], 'model_declarations': len(decls),
                      'unrelated_malformed_models_not_used': len(malformed)}))


if __name__ == '__main__':
    main()
