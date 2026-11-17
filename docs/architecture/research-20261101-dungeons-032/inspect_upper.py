#!/usr/bin/env python3
"""Show the actual narrow upper ring, not a guessed full high room."""
import importlib.util
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[2] / 'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR

spec = importlib.util.spec_from_file_location('details', OUT.parent / 'research-20261101-dungeons-002/inspect_details.py')
details = importlib.util.module_from_spec(spec)
spec.loader.exec_module(details)


def main():
    c = json.loads((OUT / 'sources.json').read_text())['candidates'][0]
    with ZipFile(c['source_archive']) as z:
        d = read(z.read(c['member']))
    pal = d.get('palette') or d['palettes'][0]
    states = {tuple(b['pos']): pal[b['state']] for b in d['blocks']}
    im = Image.new('RGB', (1200, 700), '#edf0f2')
    draw = ImageDraw.Draw(im)
    rows = []
    for i, y in enumerate((18, 19)):
        left = 45 + i * 600
        draw.text((left, 20), f'T01 upper y={y}; +X right / +Z down', fill='#17252c')
        for z in range(d['size'][2]):
            for x in range(d['size'][0]):
                s = states.get((x, y, z))
                cs = s if s and s['Name'] not in AIR else None
                draw.rectangle((left+x*30, 60+z*30, left+(x+1)*30, 60+(z+1)*30), fill=details.shade(cs), outline='#bfc6ca')
        rows.append(dict(y=y, original_states=[dict(position=list(p), state=s) for p,s in states.items() if p[1] == y]))
    draw.text((20, 620), 'Original y19 socket [7,19,7] final_state=spruce_planks; no actor placement or collision run.', fill='#17252c')
    draw.text((20, 645), 'Class colours; cyan ladder; upper platform is a small ring, not a full enclosed high room.', fill='#17252c')
    im.save(OUT / 'T01-upper-ring.png')
    (OUT / 'upper-original-states.json').write_text(json.dumps(dict(id='T01', prior_identity='001-F11', planes=rows, building_credit=0), ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
