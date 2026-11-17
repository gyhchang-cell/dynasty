"""Read native geometry atlas declarations; no geometry is changed or rebound."""
from pathlib import Path
import hashlib
import json
import zipfile

D = Path(__file__).resolve().parent
TARGETS = {
    'assets/geckolib/geo/item/armor/gecko_armor.geo.json',
    'assets/geckolib/geo/item/armor/wolf_armor.geo.json',
    'assets/utopiabosses/geo/item/armor/sunflower_armor.geo.json',
    'assets/utopiabosses/geo/item/armor/tree_armor.geo.json',
    'assets/callfromthedepth_/geo/deptharmorfull1.geo.json',
    'assets/biomancy/geo/item/armor/acolyte_armor.geo.json',
    'assets/biomancy/geo/item/armor/warrior_armor.geo.json',
}


def main():
    assert not (D / 'native-atlas-declarations.json').exists()
    p = json.loads((D / 'provenance.json').read_text())
    rows = []
    for a in p['archives']:
        with zipfile.ZipFile(a['path']) as z:
            for e in sorted(TARGETS & set(z.namelist())):
                b = z.read(e)
                h = hashlib.sha256(b).hexdigest()
                local = Path('atlas-declarations') / e.split('/')[1] / f'{h[:12]}-{Path(e).name}'
                (D / local).parent.mkdir(exist_ok=True, parents=True)
                (D / local).write_bytes(b)
                data = json.loads(b)
                rows.append({'jar': a['path'], 'entry': e, 'sha256': h, 'local': str(local),
                             'descriptions': [g['description'] for g in data['minecraft:geometry']],
                             'binding_to_selected_item_proven': False,
                             'scope': 'Native declared texture width/height only; do not assume item binding or vanilla UV compatibility.'})
    assert len(rows) == 8
    (D / 'native-atlas-declarations.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('8 native atlas declarations copied exactly; no binding/game/design credit')


if __name__ == '__main__':
    main()
