"""Read-only source-rectangle study. Coordinates alone do not prove foreign renderer binding."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).resolve().parent
R = D.parents[2]


def rect_alpha(im, rect):
    patch = im.crop(rect)
    values = patch.getchannel('A').tobytes()
    return {'source_rect': list(rect), 'visible': sum(a > 0 for a in values),
            'opaque': sum(a == 255 for a in values), 'pixels': len(values)}


def main():
    manifest = json.loads((D / 'selected-worn-provenance.json').read_text())
    entries = {a['entry']: a for a in manifest['textures']}
    prefixes = {
        'magistuarmory': 'assets/magistuarmory/textures/models/armor/',
        'aether': 'assets/aether/textures/models/armor/',
        'dark_souls_expansion': 'assets/dark_souls_expansion/textures/models/armor/',
    }
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)
    result = {'scope': 'SOURCE_RECTANGLE_PROBES_NOT_FOREIGN_MODEL_BINDING',
              'target_uv_contract': 'docs/art/armor-worn-uv-20261102/uv-contract.json',
              'target_uv_contract_sha256': hashlib.sha256((R / 'docs/art/armor-worn-uv-20261102/uv-contract.json').read_bytes()).hexdigest(),
              'foreign_runtime_binding_proven': False, 'source_rectangles': [], 'zero_alpha_entries': []}
    for a in manifest['textures']:
        im = Image.open(D / a['local']).convert('RGBA')
        if im.getchannel('A').getbbox() is None:
            result['zero_alpha_entries'].append({'entry': a['entry'], 'sha256': a['sha256']})
    selections = {
        'sleeve': [('magistuarmory', s) for s in ['gambeson_layer_1', 'halfarmor_layer_1', 'crusader_layer_1', 'chainmail_layer_1']] + [('aether', s) for s in ['valkyrie_layer_1', 'zanite_layer_1']],
        'waist': [('magistuarmory', s) for s in ['gambeson_layer_2', 'crusader_layer_2', 'chainmail_layer_2']] + [('aether', s) for s in ['valkyrie_layer_2', 'zanite_layer_2']] + [('dark_souls_expansion', 'hollow_armor__layer_2')],
    }
    for section, choices in selections.items():
        sheet = Image.new('RGB', (1280, 75 + len(choices) * 125), '#44494e')
        draw = ImageDraw.Draw(sheet)
        draw.text((10, 8), 'READ-ONLY SOURCE PIXELS / not game / not foreign model UV validation', fill='white', font=font)
        draw.text((10, 31), 'Native atlas x3 | ' + ('[48,16,52,20) x12 | [40,31,56,32) x8' if section == 'sleeve' else '[16,20,40,32) x5 | top to bottom alpha counts'), fill='white', font=font)
        for i, (ns, stem) in enumerate(choices):
            a = entries[prefixes[ns] + stem + '.png']
            im = Image.open(D / a['local']).convert('RGBA')
            y = 65 + i * 125
            draw.text((10, y), ns + ':' + stem, fill='white', font=font)
            native = im.resize((192, 96), Image.Resampling.NEAREST)
            sheet.paste(native, (385, y), native)
            row = {'entry': a['entry'], 'sha256': a['sha256'], 'probe_kind': section}
            if section == 'sleeve':
                cap, terminal = (48, 16, 52, 20), (40, 31, 56, 32)
                row['cap'] = rect_alpha(im, cap)
                row['terminal'] = rect_alpha(im, terminal)
                for box, pos, factor in [(cap, (630, y + 15), 12), (terminal, (740, y + 30), 8)]:
                    crop = im.crop(box); crop = crop.resize((crop.width * factor, crop.height * factor), Image.Resampling.NEAREST)
                    sheet.paste(crop, pos, crop)
                draw.text((920, y + 25), f"cap {row['cap']['visible']}/16; row {row['terminal']['visible']}/16", font=font, fill='white')
            else:
                box = (16, 20, 40, 32)
                row['body_strip'] = rect_alpha(im, box)
                row['rows_visible'] = [rect_alpha(im, (16, v, 40, v + 1))['visible'] for v in range(20, 32)]
                crop = im.crop(box).resize((120, 60), Image.Resampling.NEAREST)
                sheet.paste(crop, (630, y + 15), crop)
                draw.text((800, y + 25), str(row['rows_visible']), font=font, fill='white')
            result['source_rectangles'].append(row)
        sheet.save(D / f'{section}-source-rectangles.png')
    result['no_asset_edits'] = True
    result['limits'] = '对外部原图仅报告来源矩形像素；不能按64×32尺寸把它们当作Dynasty原版模型面或复制贴片。目标项目面方向与袖口问题依据之前已核实的实际UV契约，未重复验收。'
    (D / 'native-rectangle-study.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'rectangles_read': len(result['source_rectangles']), 'zero_alpha_entries': len(result['zero_alpha_entries'])}))


if __name__ == '__main__':
    main()
