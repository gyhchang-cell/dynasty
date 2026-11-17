"""Bounded native apparel atlases; exact copies only, no adaptation to Dynasty UV."""
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
    choices = {
        'candlelight:chefs': ['assets/candlelight/textures/models/armor/cook.png'],
        'vinery:winemaker': ['assets/vinery/textures/models/armor/winemaker.png'],
        'brewery:brewfest': ['assets/brewery/textures/models/armor/dirndl.png', 'assets/brewery/textures/models/armor/lederhosen.png'],
        'kaleidoscope_cookery:farmer': ['assets/minecraft/textures/models/armor/cookery_farmer_layer_1.png', 'assets/minecraft/textures/models/armor/cookery_farmer_layer_2.png'],
        'wooledboots:wooled_leather': ['assets/minecraft/textures/models/armor/myleather_layer_1.png'],
        'wooledboots:wooled_iron': ['assets/minecraft/textures/models/armor/myiron_layer_1.png'],
    }
    rows = []
    for case in prov['cases']:
        if case['case_key'] not in choices:
            continue
        for jar in sorted({a['jar'] for a in case['icons']}):
            with zipfile.ZipFile(jar) as z:
                for entry in choices[case['case_key']]:
                    assert entry in z.namelist()
                    data = z.read(entry); h = hashlib.sha256(data).hexdigest()
                    im = Image.open(BytesIO(data)); im.load()
                    local = Path('worn-references') / f'{h[:12]}-{Path(entry).name}'
                    (D / local).parent.mkdir(parents=True, exist_ok=True); (D / local).write_bytes(data)
                    rows.append({'case_key': case['case_key'], 'jar': jar, 'entry': entry, 'sha256': h,
                                 'size': list(im.size), 'local': str(local), 'runtime_binding_proven': False})
    assert len(rows) == 10
    data = {'textures': rows, 'distinct_payloads': len({a['sha256'] for a in rows}), 'additional_design_credit': 0,
            'limits': '原生图集材料与层布局研究；同尺寸、文件名或主体位置不证明使用原版身体UV。版本、附层与图标对应不算新增独立设计，不当游戏验收。'}
    (D / 'selected-worn-provenance.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('fixed_collector', R / 'docs/art/armor-reference-study-20261102/collect.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); module.D = D
    module.draw_worn(rows)
    print(json.dumps({'entries': len(rows), 'unique': data['distinct_payloads'], 'sizes': sorted({tuple(a['size']) for a in rows})}))


if __name__ == '__main__':
    main()
