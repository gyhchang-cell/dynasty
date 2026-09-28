"""Validate the release resources without launching or writing a player world."""
import hashlib
import json
import subprocess
from pathlib import Path
from zipfile import ZipFile
from workshop_assets_v9 import WORKSHOPS, NEW, ROOT, ASSET, DATA, RES

doc=ROOT/'docs/art/vanilla-v9'
manifest=json.loads((doc/'manifest.json').read_text())
assert len(manifest)==34
assert {r['id']+'.png' for r in manifest}=={p.name for p in (ASSET/'textures/block').glob('*.png')}
for row in manifest:
    texture=ROOT/row['target']
    assert hashlib.sha256(texture.read_bytes()).hexdigest()==row['sha256']
    w,h,c=map(int,subprocess.check_output(['magick','identify','-format','%w %h %k',str(texture)],text=True).split())
    assert (w,h)==(16,16) and c<=10
vanilla=ZipFile('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝/Dynasty 王朝.jar')
for _,id,_,_,_,boxes in WORKSHOPS:
    model=json.loads((ASSET/'models/block'/f'{id}.json').read_text())
    assert len(model['elements'])==len(boxes)
    assert all(e['from']==a and e['to']==b for e,(a,b,_) in zip(model['elements'],boxes))
    for ref in model['textures'].values():
        ns,path=ref.split(':')
        asset=f'assets/{ns}/textures/{path}.png'
        assert (RES/asset).exists() if ns=='dynasty' else asset in vanilla.namelist()
    state=json.loads((ASSET/'blockstates'/f'{id}.json').read_text())
    assert len(state['variants'])==8
    for facing,y in [('north',0),('east',90),('south',180),('west',270)]:
        for lit in ('false','true'):
            variant=state['variants'][f'facing={facing},lit={lit}']
            assert variant.get('y',0)==y
    for lang in ('zh_cn','en_us'):
        assert json.loads((ASSET/'lang'/f'{lang}.json').read_text())[f'block.dynasty.{id}']
for id in NEW:
    recipe=json.loads((DATA/'recipes'/f'{id}.json').read_text())
    assert recipe['result']['item']==f'dynasty:{id}'
    assert set(''.join(recipe['pattern']))-{' '}==set(recipe['key'])
    loot=json.loads((DATA/'loot_tables/blocks'/f'{id}.json').read_text())
    assert loot['pools'][0]['entries'][0]['name']==f'dynasty:{id}'
jar=ROOT/'build/libs/dynasty-1.4.0.jar'
with ZipFile(jar) as z:
    names=z.namelist()
    assert not any('com/dynasty/qa/WorkshopTest' in n for n in names)
    for r in manifest:
        assert z.read(f'assets/dynasty/textures/block/{r["id"]}.png')==(ROOT/r['target']).read_bytes()
    for id in NEW:
        assert f'data/dynasty/recipes/{id}.json' in names
        assert f'assets/dynasty/models/block/{id}.json' in names
result={'textures':34,'max_size':'16x16','max_colors':10,'workshop_models':8,'state_variants':64,'new_recipes':4,'model_texture_references':'PASS','test_class_excluded':True,'jar_sha256':hashlib.sha256(jar.read_bytes()).hexdigest()}
(doc/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
