"""Use first declared animation frame in contact sheet; preserve every original source PNG."""
from pathlib import Path
import json
import textwrap
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).resolve().parent


def main():
    p = json.loads((D / 'provenance.json').read_text())
    animations = {a['source']['local']: a for a in json.loads((D / 'animation-source.json').read_text())}
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)
    small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 12)
    for page, start in enumerate(range(0, len(p['cases']), 7), 1):
        cases = p['cases'][start:start + 7]
        im = Image.new('RGB', (1300, 55 + len(cases) * 155), (68, 73, 78)); dr = ImageDraw.Draw(im)
        dr.text((8, 10), 'NATIVE SOURCE ICON STUDY / animated icons: first declared frame, all frames on animation-frames.png / NOT GAME', font=small, fill='white')
        for i, case in enumerate(cases):
            y = 50 + i * 155; ns, family = case['case_key'].split(':')
            dr.text((8, y + 5), f'{start + i + 1:02}  ' + ns[:36], font=small, fill='#b7c0c4')
            dr.multiline_text((8, y + 30), '\n'.join(textwrap.wrap(family, 34)), font=font, fill='white')
            for j, a in enumerate(case['icons']):
                image = Image.open(D / a['local']).convert('RGBA')
                if a['local'] in animations:
                    animation = animations[a['local']]; first = animation['sequence'][0]
                    index = first['index'] if isinstance(first, dict) else first
                    image = image.crop(next(f['source_rectangle'] for f in animation['frames'] if f['index'] == index))
                scale = max(1, 96 // max(image.size))
                image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
                x = 340 + j * 225; im.paste(image, (x, y), image)
                dr.text((x, y + 105), ['helmet', 'chestplate', 'leggings', 'boots'][j] + (' [animated]' if a['local'] in animations else ''), font=small, fill='white')
                dr.text((x, y + 125), a['sha256'][:12], font=small, fill='#b7c0c4')
        im.save(D / f'icons-{page:02}.png')


if __name__ == '__main__':
    main()
