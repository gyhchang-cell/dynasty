"""Install only the twelve selected inventory icons, preserving original pixels."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).resolve().parent
R = D.parents[2]
A = R / 'src/main/resources/assets/dynasty'
rows = json.loads((D / 'selection.json').read_text())
baseline = json.loads((D / 'baseline.json').read_text())
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for row in rows:
    for sub, extension in [('textures/item', 'png'), ('models/item', 'json')]:
        target = A / sub / (row['id'] + '.' + extension)
        assert target.read_bytes() == (D / 'before' / sub / target.name).read_bytes(), 'Concurrent change: ' + str(target)

sys.path.insert(0, str(R / 'tools/art/inventory-refresh'))
from publish_originals import publish
publish(ids={row['id'] for row in rows})

report = []
for row in rows:
    target = A / 'textures/item' / (row['id'] + '.png')
    original = Image.open(D / 'sources' / target.name).convert('RGBA')
    crop = original.crop(row['crop_bounds'])
    expected = Image.new('RGBA', (crop.width + 4, crop.height + 4))
    expected.paste(crop, (2, 2))
    runtime = Image.open(target).convert('RGBA')
    assert expected.size == runtime.size and expected.tobytes() == runtime.tobytes(), row['id']
    assert runtime.width == runtime.height, 'Inventory sprite must not stretch: ' + row['id']
    assert not runtime.getchannel('A').crop((0, 0, runtime.width, 2)).getbbox()
    assert not runtime.getchannel('A').crop((0, runtime.height - 2, runtime.width, runtime.height)).getbbox()
    report.append({'id': row['id'], 'originalSize': original.size, 'runtimeSize': runtime.size,
                   'originalRgbaPreserved': True, 'sha256': digest(target)})

for row in rows:
    model = A / 'models/item' / (row['id'] + '.json')
    assert model.read_bytes() == (D / 'before/models/item' / model.name).read_bytes(), 'Unexpected model transform change: ' + row['id']
assert (R / 'src/main/resources/assets/minecraft/atlases/blocks.json').read_bytes() == (D / 'control-before/src/main/resources/assets/minecraft/atlases/blocks.json').read_bytes(), 'Unexpected atlas change'

selected = {str((A / 'textures/item' / (row['id'] + '.png')).relative_to(R)) for row in rows}
changed = [rel for rel, old in baseline.items() if digest(R / rel) != old]
assert selected <= set(changed)
other = sorted(set(changed) - selected)
(D / 'source-check.json').write_text(json.dumps({'items': report, 'changedPngs': changed,
    'otherBaselinePngsUnchanged': len(baseline) - len(changed),
    'concurrentOtherChangesNotOverwritten': other, 'clientStarted': False}, ensure_ascii=False, indent=2) + '\n')

font = ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc', 21)
for compare in [False, True]:
    height = 1720 if compare else 900
    sheet = Image.new('RGB', (1120, height), '#555b60')
    draw = ImageDraw.Draw(sheet)
    title = '十二件原版比例微调对照 · 每组上旧 / 下新 · 非游戏截图' if compare else '竹甲 / 织锦袍 / 朱砂符甲 · 原版比例微调 · 实际资源 · 非游戏截图'
    draw.text((15, 12), title, font=font, fill='white')
    for index, row in enumerate(rows):
        x = index % 4 * 280
        y = index // 4 * (550 if compare else 280) + 52
        for old in ([True, False] if compare else [False]):
            path = (D / 'before' if old else A) / 'textures/item' / (row['id'] + '.png')
            image = Image.open(path).convert('RGBA')
            image.thumbnail((230, 230), Image.Resampling.NEAREST)
            yy = y + (245 if compare and not old else 0)
            sheet.paste(image, (x + (280 - image.width) // 2, yy + (235 - image.height) // 2), image)
        draw.text((x + 12, y + (490 if compare else 238)), row['name'], font=font, fill='white')
    sheet.save(D / ('comparison.png' if compare else 'after.png'))
print('PASS twelve original RGBA icons; unrelated PNG changes preserved:', other)
