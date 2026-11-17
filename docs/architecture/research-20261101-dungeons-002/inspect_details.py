#!/usr/bin/env python3
"""Feature-selected sections of original NBT; research only, no credit or assets."""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR, color

# Two horizontal cuts followed by two off-centre vertical cuts. Chosen from
# original door/ladder positions and observed footprints, not filename guesses.
SPECS = {
 'F01': (6, 12, 3, 35), 'F02': (12, 20, 7, 7),
 'F03': (7, 13, 8, 11), 'F04': (7, 20, 39, 35),
 'F05': (14, 20, 8, 32), 'F06': (7, 12, 11, 10),
 'F07': (10, 20, 14, 32), 'F08': (7, 17, 19, 8),
 'F09': (11, 17, 15, 14), 'F10': (9, 15, 8, 4),
 'F11': (2, 7, 10, 10), 'F12': (8, 14, 24, 1),
 'F13': (3, 8, 20, 10), 'F14': (4, 7, 15, 15),
 'F15': (4, 6, 45, 31), 'F16': (6, 22, 16, 26),
}


def shade(state):
 if state is None: return '#e3e6e9'
 name = state['Name']
 if name.endswith('_door'): return '#ae51c5'
 if name.endswith(':ladder'): return '#21c0d2'
 return color(name)


def main():
 source = json.loads((OUT / 'sources.json').read_text())
 evidence = []
 for c in source['candidates']:
  with ZipFile(c['source_archive']) as z: raw = z.read(c['member'])
  assert hashlib.sha256(raw).hexdigest() == c['nbt_sha256']
  nbt = read(raw); palette = nbt.get('palette') or nbt['palettes'][0]
  states = {tuple(b['pos']): palette[b['state']] for b in nbt['blocks']}
  cells = {p: s for p, s in states.items() if s['Name'] not in AIR}
  sx, sy, sz = nbt['size']; y1, y2, xx, zz = SPECS[c['id']]
  sheet = Image.new('RGB', (1440, 1480), '#edf0f2'); draw = ImageDraw.Draw(sheet)
  cuts = [('y', y1, sx, sz), ('y', y2, sx, sz), ('x', xx, sz, sy), ('z', zz, sx, sy)]
  for i, (axis, fixed, width, height) in enumerate(cuts):
   left = (i % 2) * 720 + 45; top = (i // 2) * 710 + 60
   step = min(640 / width, 620 / height)
   draw.text((left, top - 40), f"{c['id']} {axis}={fixed}; " + ('+X right / +Z down' if axis == 'y' else 'height up'), fill='#17252c')
   for v in range(height):
    for h in range(width):
     p = (h, fixed, v) if axis == 'y' else (fixed, v, h) if axis == 'x' else (h, v, fixed)
     row = v if axis == 'y' else height - 1 - v
     x, y = left + h * step, top + row * step
     draw.rectangle((x, y, x + step, y + step), fill=shade(cells.get(p)), outline='#bfc6ca')
   for h in range(0, width, 5): draw.text((left + h * step, top - 17), str(h), fill='#17252c')
   for v in range(0, height, 5):
    row = v if axis == 'y' else height - 1 - v
    draw.text((left - 23, top + row * step), str(v), fill='#17252c')
  draw.text((20, 1433), 'PURPLE door / CYAN ladder / classification colours / absent & air merged / full-cell approximation', fill='#17252c')
  draw.text((20, 1453), 'Reference inspection only; stairs may be roof trim; no native collision, terrain placement or route certification', fill='#17252c')
  filename = c['id'] + '-details.png'; sheet.save(OUT / filename)
  ladders = defaultdict(list)
  for p, s in cells.items():
   if s['Name'] == 'minecraft:ladder': ladders[(p[0], p[2])].append(p[1])
  evidence.append(dict(id=c['id'], image=filename,
   cuts=[dict(axis=a, coordinate=f, width=w, height=h) for a, f, w, h in cuts],
   occupied_bounds=[[min(p[a] for p in cells), max(p[a] for p in cells)] for a in range(3)],
   ladder_runs=[dict(x=x, z=z, ys=sorted(ys)) for (x, z), ys in ladders.items()],
   lower_doors=c['doors'],
   limitations='Missing positions, structure_void and explicit air are visually merged; no passability solver or automatic reference credit.'))
 (OUT / 'detail-evidence.json').write_text(json.dumps(dict(entries=evidence, formal_credit_added=0), ensure_ascii=False, indent=2) + '\n')
 print('Rendered', len(evidence), 'feature-selected inspection sheets; manual review still required.')


if __name__ == '__main__': main()
