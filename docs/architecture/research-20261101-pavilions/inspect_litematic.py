"""Decode two fixed local reference files; draw research-only cube diagrams.

Does not load a game, write templates/assets, award credit, or copy the design.
Packed state indices span 64-bit words. Negative region sizes select a minimum
corner; they do not reverse the serialized X/Z/Y index order.
"""
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read
from whole_building_candidates import iso, plans
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
SOURCE = Path('/Users/a15356015027/Desktop/投影_1.20.1_合集')


def decode(path):
    raw = path.read_bytes()
    data = read(raw)
    assert data['Version'] == 6 and len(data['Regions']) == 1
    region = next(iter(data['Regions'].values()))
    size = [abs(region['Size'][a]) for a in ('x', 'y', 'z')]
    origin = [region['Position'][a] + min(0, region['Size'][a] + 1)
              for a in ('x', 'y', 'z')]
    palette = region['BlockStatePalette']
    bits = max(2, (len(palette)-1).bit_length())
    words = [v & ((1 << 64)-1) for v in region['BlockStates']]
    assert len(words) == math.ceil(math.prod(size)*bits/64)
    cells, states = {}, {}
    for index in range(math.prod(size)):
        offset = index*bits
        word, shift = divmod(offset, 64)
        value = words[word] >> shift
        if shift+bits > 64:
            value |= words[word+1] << (64-shift)
        state = value & ((1 << bits)-1)
        assert state < len(palette)
        pos = (index % size[0], index // (size[0]*size[2]),
               index // size[0] % size[2])
        if palette[state]['Name'] != 'minecraft:air':
            cells[pos] = palette[state]['Name']
            states[pos] = palette[state]
    assert len(cells) == data['Metadata']['TotalBlocks']
    assert math.prod(size) == data['Metadata']['TotalVolume']
    return data, region, cells, states, size, origin, hashlib.sha256(raw).hexdigest()


def main():
    rows = []
    for ident, name in [('PAV01', '抱憾亭.litematic'),
                        ('PAV02', '八角亭1.litematic')]:
        path = SOURCE / name
        data, region, cells, states, size, origin, digest = decode(path)
        sheet = Image.new('RGB', (1520, 1400), '#edf0f2')
        for col in range(2):
            sheet.paste(iso(cells, size, col, ident+' stored complete selection'), (col*760, 0))
            sheet.paste(iso(cells, size, col, ident+' low cutaway y<=6', 6), (col*760, 680))
        ImageDraw.Draw(sheet).text((15, 1372),
            'RESEARCH ONLY: cube approximation, not texture, collision, or native acceptance',
            fill='#17252c')
        sheet.save(OUT / (ident+'-whole.png'))
        for level in (0, 2, 6, 8):
            plans(cells, size, level, ident).save(OUT / (ident+f'-y{level}.png'))
        rows.append({
            'id': ident, 'local_source': str(path), 'source_sha256': digest,
            'source_metadata': data['Metadata'],
            'version': data['Version'], 'subversion': data['SubVersion'],
            'minecraft_data_version': data['MinecraftDataVersion'],
            'source_signed_region_position': region['Position'],
            'source_signed_region_size': region['Size'],
            'decoded_selection_size': size, 'region_minimum_origin': origin,
            'nonair_cells': len(cells), 'stored_volume': math.prod(size),
            'occupied_bounds': [[min(p[a] for p in cells), max(p[a] for p in cells)]
                                for a in range(3)],
            'material_counts': dict(Counter(cells.values())),
            'layer_counts': dict(sorted(Counter(p[1] for p in cells).items())),
            'non_full_cube_states': [dict(position=p, state=s) for p, s in states.items()
                if any(k in s['Name'] for k in ('stairs', 'slab', 'trapdoor', 'fence', 'chain', 'banner'))],
            'author_attribution_limit': 'Local metadata says XIXI; original publication and reuse license unknown. Research only.',
            'automatic_building_credit': 0,
            'diagrams_created_not_yet_claimed_viewed': [ident+'-whole.png']+
                [ident+f'-y{n}.png' for n in (0, 2, 6, 8)],
        })
    (OUT / 'decoded-sources.json').write_text(json.dumps({
        'scope': 'Two local complete-selection reference files, manual relevance and completeness still required',
        'production_assets_written': False, 'java_executed': False,
        'automatic_building_credit': 0, 'sources': rows,
    }, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'decoded': len(rows), 'automatic_credit': 0,
                      'output': str(OUT)}))


if __name__ == '__main__':
    main()
