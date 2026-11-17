"""Keep model-referenced sprites outside block/item folders in the block atlas."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def with_model_sprites(sources):
    sprites=set()
    for path in (ROOT/'src/main/resources/assets/dynasty/models').rglob('*.json'):
        model=json.loads(path.read_text())
        for value in model.get('textures',{}).values():
            if isinstance(value,str) and value.startswith('dynasty:') and not value.startswith(('dynasty:block/','dynasty:item/')):
                texture=ROOT/'src/main/resources/assets/dynasty/textures'/ (value.split(':',1)[1]+'.png')
                if texture.is_file():sprites.add(value)
    existing={s.get('resource') for s in sources if s.get('type')=='minecraft:single'}
    return sources+[{'type':'minecraft:single','resource':s} for s in sorted(sprites-existing)]
if __name__=='__main__':
    path=ROOT/'src/main/resources/assets/minecraft/atlases/blocks.json'
    data=json.loads(path.read_text());data['sources']=with_model_sprites(data['sources'])
    path.write_text(json.dumps(data,indent=2)+'\n');print('Atlas sources:',len(data['sources']))
