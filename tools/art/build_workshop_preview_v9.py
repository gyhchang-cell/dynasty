"""Preview real JSON/native geometry; vanilla supporting materials from locally owned jar."""
import json
from pathlib import Path
from zipfile import ZipFile
from workshop_assets_v9 import WORKSHOPS, ROOT

doc=ROOT/'docs/art/vanilla-v9'
support=doc/'vanilla-support';support.mkdir(parents=True,exist_ok=True)
jar=Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝/Dynasty 王朝.jar')
with ZipFile(jar) as z:
    for name in ('amethyst_block','brown_terracotta','coal_block'):
        (support/f'{name}.png').write_bytes(z.read(f'assets/minecraft/textures/block/{name}.png'))
data=[]
for _,id,zh,en,textures,boxes in WORKSHOPS:
    urls={key:('vanilla-support/' if value.startswith('minecraft:') else 'block/')+value.split('/')[-1]+'.png' for key,value in textures.items()}
    data.append({'id':id,'name':zh,'textures':urls,'boxes':boxes})
template=(ROOT/'tools/art/workshop_preview_v9.html').read_text()
(doc/'models.html').write_text(template.replace('__WORKSHOP_DATA__',json.dumps(data,ensure_ascii=False)))
print('Created native model preview. Vanilla support textures are local preview-only, not redistributed in mod.')
