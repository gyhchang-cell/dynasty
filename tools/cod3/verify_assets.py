"""Validate the checked-in cod3 catalogue, rig references and landmark resources."""
import json
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[2]
assets = root / 'src/main/resources/assets/dynasty'
catalog = json.loads((root / 'src/main/resources/data/dynasty/cod3/catalog.json').read_text())
expected = dict(intros=20, deaths=20, vfx=40, npcs=15, secrets=30, scenic=25, worldStates=10)
for group, count in expected.items():
    rows = catalog[group]
    assert len(rows) == count, (group, len(rows))
    assert len({row['id'] for row in rows}) == count, group
for group in ('intros', 'deaths'):
    bound = []
    for row in catalog[group]:
        assert 20 <= row['totalTicks'] <= 1200
        bound.extend(row['bossIds'])
        for step in row['steps']:
            assert 0 <= step['startTick'] < row['totalTicks']
            assert 1 <= step['vfx'] <= 40
    assert len(bound) == 6 and len(set(bound)) == 6
    assert 'dynasty:zhenyuan_sovereign' not in bound
for row in catalog['vfx']:
    assert row['radius'] > 0 and row['length'] > 0 and row['width'] > 0
    assert row['near'] > row['medium'] > row['far'] > 0
states = set('idle walk turn talk work react rain night danger player_near player_holds_special'.split())
for row in catalog['npcs']:
    role = row['id']
    rig = json.loads((assets / f'geo/npc/{role}.geo.json').read_text())['minecraft:geometry'][0]
    bones = rig['bones']
    names = {bone['name'] for bone in bones}
    assert len(names) == len(bones)
    for bone in bones:
        assert 'parent' not in bone or bone['parent'] in names
        for cube in bone.get('cubes', []):
            assert len(cube['origin']) == len(cube['size']) == 3
            assert all(size > 0 for size in cube['size'])
    animations = json.loads((assets / f'animations/npc/{role}.animation.json').read_text())['animations']
    assert {key.removeprefix('animation.npc.') for key in animations} == states
    for animation in animations.values():
        assert set(animation['bones']) <= names
    with Image.open(assets / f'textures/entity/npc/{role}.png') as texture:
        assert texture.size == (128, 128)
    for locale in ('zh_cn', 'en_us'):
        language = json.loads((assets / f'lang/{locale}.json').read_text())
        for suffix in ('first', 'ordinary', 'changed'):
            assert language[f'cod3.dynasty.npc.{role}.{suffix}']
        for choice in ('talk', 'changed', 'special', 'trade', 'leave'):
            assert language[f'cod3.dynasty.dialogue.{choice}']
        if role in ('lao_chen', 'han_chong', 'baibao_jin'):
            assert language[f'cod3.dynasty.npc.{role}.special']
variants = json.loads((assets / 'blockstates/story_anchor.json').read_text())['variants']
assert set(variants) == {f'kind={i}' for i in range(45)}
for i in range(45):
    json.loads((assets / f'models/block/story_anchor_{i}.json').read_text())
print('PASS: 160 catalogue entries; 15 rigs / 165 animation states; 45 landmark models; 6 safe boss bindings.')
