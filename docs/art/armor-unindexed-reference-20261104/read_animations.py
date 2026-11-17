"""Read native animation metadata; frame crops exist only inside analysis charts."""
from pathlib import Path
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).resolve().parent


def main():
    assert not (D / 'animation-source.json').exists()
    p = json.loads((D / 'provenance.json').read_text())
    rows = []
    for case in p['cases']:
        with zipfile.ZipFile(case['icons'][0]['jar']) as z:
            for source in case['icons']:
                e = source['entry'] + '.mcmeta'
                if e not in z.namelist():
                    continue
                b = z.read(e); meta = json.loads(b); anim = meta['animation']
                im = Image.open(D / source['local']).convert('RGBA')
                # These eight fixed inputs have no explicit width/height: native square frame default.
                assert 'width' not in anim and 'height' not in anim and im.width == 16
                w = h = min(im.size)
                assert im.height % h == 0 and im.width == w
                sequence = anim.get('frames', list(range(im.height // h)))
                indices = [a['index'] if isinstance(a, dict) else a for a in sequence]
                assert min(indices) >= 0 and max(indices) < im.height // h
                digest = hashlib.sha256(b).hexdigest()
                local = Path('animation-declarations') / e.split('/')[1] / f'{digest[:12]}-{Path(e).name}'
                (D / local).parent.mkdir(parents=True, exist_ok=True); (D / local).write_bytes(b)
                frames = []
                for index in sorted(set(indices)):
                    rect = [0, index * h, w, (index + 1) * h]
                    frames.append({'index': index, 'source_rectangle': rect,
                                   'rgba_sha256': hashlib.sha256(im.crop(rect).tobytes()).hexdigest()})
                rows.append({'case_key': case['case_key'], 'source': source,
                             'metadata': {'jar': source['jar'], 'entry': e, 'sha256': digest, 'local': str(local)},
                             'frame_size': [w, h], 'sequence': sequence, 'frames': frames,
                             'frametime': anim.get('frametime', 1), 'interpolate': anim.get('interpolate', False),
                             'additional_design_credit': 0, 'source_pixels_changed': False})
    assert len(rows) == 8 and sum(len(a['frames']) for a in rows) == 56
    (D / 'animation-source.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 13)
    im = Image.new('RGB', (1180, 80 + 100 * len(rows)), (68, 73, 78)); dr = ImageDraw.Draw(im)
    dr.text((8, 10), 'NATIVE ANIMATION FRAME INSPECTION / integer enlarged raw crops / NOT GAME / frames != designs', font=font, fill='white')
    for i, row in enumerate(rows):
        y = 60 + i * 100
        dr.text((8, y), row['case_key'].split(':')[1], font=font, fill='white')
        dr.text((8, y + 20), Path(row['source']['entry']).stem, font=font, fill='#b7c0c4')
        dr.text((8, y + 40), f"{len(row['frames'])} source frames / {len(row['sequence'])} sequence entries", font=font, fill='#b7c0c4')
        raw = Image.open(D / row['source']['local']).convert('RGBA')
        for j, frame in enumerate(row['frames']):
            crop = raw.crop(frame['source_rectangle']).resize((48, 48), Image.Resampling.NEAREST)
            x = 320 + j * 68; im.paste(crop, (x, y), crop)
            dr.text((x, y + 55), str(frame['index']), font=font, fill='white')
    im.save(D / 'animation-frames.png')
    print('8 exact metadata sources / 56 frame slots inspected as two armor families, zero extra design credit')


if __name__ == '__main__':
    main()
