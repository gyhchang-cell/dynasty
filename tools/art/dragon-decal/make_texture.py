"""Original horned serpent surface glyph. Exact authored cells, no filtering."""
from pathlib import Path
from PIL import Image
import json

ROOT = Path(__file__).resolve().parents[3]
# Horns, broad snout, stepped coil, two claws and tapered tail.
CELLS = [
    '................',
    '....G...G.......',
    '....GG.GG.......',
    '.....TTT........',
    '....TTDTTTGG....',
    '....TTTTTTTT....',
    '.....TTGGGG.....',
    '....TTT.........',
    '...TTT..TTTT....',
    '..TTT..TT.TTT...',
    '..TTT..TT..TT...',
    '...TTGGTT..TT...',
    '....TTTT...TT...',
    '.....GG...TT....',
    '.........TT.....',
    '................',
]
PALETTE = {'.': (0, 0, 0, 0), 'T': (65, 155, 132, 255),
           'G': (223, 184, 97, 255), 'D': (35, 59, 58, 255)}

def make():
    assert len(CELLS) == 16 and all(len(row) == 16 for row in CELLS)
    small = Image.new('RGBA', (16, 16))
    small.putdata([PALETTE[c] for row in CELLS for c in row])
    result = small.resize((32, 32), Image.Resampling.NEAREST)
    out = ROOT / 'src/main/resources/assets/dynasty/textures/effect/dragon_slayer_decal.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    result.save(out)
    out.with_suffix('.png.mcmeta').write_text(json.dumps({'texture': {'blur': False, 'clamp': True}}, indent=2) + '\n')
    return result

if __name__ == '__main__':
    make()
