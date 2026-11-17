"""Copy a bounded set of exact native worn references, never adapt their UV or production art."""
from io import BytesIO
from pathlib import Path
import hashlib
import importlib.util
import json
import zipfile
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[2]


def main():
    prov = json.loads((D / 'provenance.json').read_text())
    wanted = {
        'aether': ['valkyrie_layer_1', 'valkyrie_layer_2', 'zanite_layer_1', 'zanite_layer_2'],
        'magistuarmory': ['gambeson_layer_1', 'gambeson_layer_1_overlay', 'gambeson_layer_2', 'gambeson_layer_2_overlay', 'halfarmor_layer_1', 'crusader_layer_1', 'crusader_layer_2', 'chainmail_layer_1', 'chainmail_layer_2'],
        'dark_souls_expansion': ['hollow_armor__layer_1', 'hollow_armor__layer_2'],
        'immersive_armors': ['robe/body_middle', 'robe/body_middle_overlay', 'robe/body_lower', 'robe/body_lower_overlay', 'robe/leggings_middle', 'robe/leggings_middle_overlay', 'robe/leggings_lower', 'robe/leggings_lower_overlay'],
    }
    rows = []
    for archive in prov['archives']:
        with zipfile.ZipFile(archive['path']) as z:
            for ns, entries in wanted.items():
                for stem in entries:
                    entry = f'assets/{ns}/textures/models/armor/{stem}.png'
                    if entry not in z.namelist():
                        continue
                    data = z.read(entry)
                    h = hashlib.sha256(data).hexdigest()
                    im = Image.open(BytesIO(data)); im.load()
                    local = Path('worn-references') / ns / f'{h[:12]}-{stem.replace("/", "-")}.png'
                    (D / local).parent.mkdir(parents=True, exist_ok=True)
                    (D / local).write_bytes(data)
                    rows.append({'jar': archive['path'], 'entry': entry, 'sha256': h,
                                 'size': list(im.size), 'local': str(local),
                                 'role': 'RAW_WORN_LAYOUT_REFERENCE_NOT_AUTOMATICALLY_VANILLA_BOUND',
                                 'runtime_binding_proven': False})
    assert len(rows) == 23
    manifest = {'textures': rows, 'distinct_png_sha256': len({a['sha256'] for a in rows}),
                'counted_as_additional_designs': 0,
                'limits': '灰度、附层与拆分身体贴片只作材料/布局观察；相同尺寸不证明与Dynasty几何兼容，不当游戏内验收。'}
    (D / 'selected-worn-provenance.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('fixed_collector', R / 'docs/art/armor-reference-study-20261102/collect.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.D = D
    module.draw_worn(rows)
    print(json.dumps({'selected_worn_entries': len(rows), 'sizes': sorted({tuple(a['size']) for a in rows})}))


if __name__ == '__main__':
    main()
