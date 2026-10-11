#!/usr/bin/env python3
"""Original cuboid memorial and lacquer coffer; actual 16px, four-color portrait UVs."""
from pathlib import Path
import base64, hashlib, json, uuid
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / 'src/main/resources/assets/dynasty'
DOC = ROOT / 'docs/art/cod3-remains-v1'
PALETTE = {'.': '#ffffff', 'D': '#433526', 'B': '#97713c', 'L': '#d7b46e'}
PORTRAITS = {
    'rebel_general_statue': [
        '........', '..LLLL..', '..BDDB..', '..BBBBL.', '..BDLBL.', '.BBBDBL.', '.DD.DBL.', '........',
    ],
    'lootable_remains': [
        '........', '........', '.LLLLLL.', '.LDDD DL.'.replace(' ', ''), '.BBDDBB.', '.BBLLBB.', '.DDDDDD.', '........',
    ],
}
def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def atlas(name):
    image = Image.new('RGB', (16, 16), '#ffffff')
    islands = {}
    for y, row in enumerate(PORTRAITS[name]):
        assert len(row) == 8
        for x, key in enumerate(row):
            for dy in range(2):
                for dx in range(2):
                    image.putpixel((x*2+dx, y*2+dy), tuple(bytes.fromhex(PALETTE[key][1:])))
            if key != '.': islands.setdefault(key, [x*2, y*2, x*2+2, y*2+2])
    path = ASSETS / f'textures/block/{name}.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return islands, path

def part(name, group, a, b, material='B'):
    return dict(name=name, group=group, a=a, b=b, material=material)

STATUE = [
    part('plinth', 'root', [1,0,1], [15,2,15], 'D'),
    part('kneeling_shin', 'left_leg', [3,2,10], [7,4,15]),
    part('kneeling_knee', 'left_leg', [2,2,6], [8,5,10], 'L'),
    part('kneeling_thigh', 'left_leg', [3,3,8], [7,8,12]),
    part('planted_shin', 'right_leg', [9,2,3], [13,9,6]),
    part('planted_foot', 'right_leg', [8,2,1], [14,4,7], 'D'),
    part('raised_thigh', 'right_leg', [9,7,3], [13,10,11]),
    part('raised_knee', 'right_leg', [8,7,2], [14,10,6], 'L'),
    part('pelvis', 'pelvis', [5,5,7], [11,9,13]),
    part('left_skirt_plate', 'pelvis', [2,6,5], [4,10,13], 'L'),
    part('right_skirt_plate', 'pelvis', [12,6,5], [14,11,12], 'L'),
    part('waist', 'waist', [5,9,7], [11,11,12], 'D'),
    part('chest', 'chest', [4,11,6], [12,17,12]),
    part('breastplate', 'chest', [5,12,5], [11,16,6], 'L'),
    part('left_pauldron', 'left_arm', [2,15,5], [5,18,13], 'L'),
    part('left_upper_arm', 'left_arm', [2,11,7], [5,15,11]),
    part('resting_forearm', 'left_arm', [3,9,4], [6,12,10]),
    part('resting_hand', 'left_arm', [4,8,3], [7,10,7], 'L'),
    part('right_pauldron', 'right_arm', [11,15,5], [14,18,13], 'L'),
    part('right_upper_arm', 'right_arm', [11,12,7], [14,15,11]),
    part('raised_forearm', 'right_arm', [10,13,4], [12,19,8]),
    part('sword_hand', 'right_arm', [9,16,2], [14,18,7], 'L'),
    part('neck', 'neck', [6,17,7], [10,19,11], 'D'),
    part('lower_helmet', 'head', [4,19,5], [12,22,12]),
    part('helmet_crown', 'head', [5,22,6], [11,24,11], 'L'),
    part('helmet_brow', 'head', [3,21,4], [13,23,6], 'L'),
    part('visor', 'head', [5,19,4], [11,21,5], 'D'),
    part('left_cheekguard', 'head', [3,18,6], [5,22,11]),
    part('right_cheekguard', 'head', [11,18,6], [13,22,11]),
    part('cape_top', 'cape', [3,11,12], [13,17,14], 'D'),
    part('cape_left', 'cape', [3,7,12], [6,11,14], 'D'),
    part('cape_center', 'cape', [6,9,12], [10,11,14], 'D'),
    part('cape_right', 'cape', [10,5,12], [13,11,14], 'D'),
    part('planted_blade', 'weapon', [11,2,3], [13,14,5], 'L'),
    part('crossguard', 'weapon', [9,14,2], [15,16,6]),
    part('hilt', 'weapon', [11,16,3], [13,20,5], 'D'),
    part('pommel', 'weapon', [10,20,2], [14,22,6], 'L'),
]
COFFER = [
    part('body', 'root', [1,1,1], [15,14,15], 'D'),
    part('lid', 'root', [1,14,1], [15,16,15]),
    part('left_binding', 'root', [2,0,0], [4,16,16]),
    part('right_binding', 'root', [12,0,0], [14,16,16]),
    part('front_lock', 'root', [6,7,0], [10,12,1], 'L'),
    part('rear_hinge', 'root', [6,12,15], [10,16,16], 'L'),
    part('foot_left', 'root', [1,0,1], [5,1,15], 'D'),
    part('foot_right', 'root', [11,0,1], [15,1,15], 'D'),
]
def model(name, parts, islands, half=None, weapon=True):
    elements = []
    for p in parts:
        if not weapon and p['group'] == 'weapon': continue
        a, b = list(p['a']), list(p['b'])
        if half is not None:
            lo, hi = (0,16) if half == 'lower' else (16,32)
            a[1], b[1] = max(a[1],lo), min(b[1],hi)
            if b[1] <= a[1]: continue
            a[1] -= lo; b[1] -= lo
        materials = {face: p['material'] for face in ('north','south','east','west','up','down')}
        # Faces use complete two-pixel islands; no white background, auto UV or filtering.
        if p['material'] == 'B': materials.update(up='L', down='D', south='D')
        elements.append(dict(name=p['name'], **{'from': a, 'to': b}, faces={f:dict(texture='#atlas',uv=islands[key]) for f,key in materials.items()}))
    return dict(credit='Dynasty original cuboid art; 16px four-color portrait UV',
                textures={'atlas':f'dynasty:block/{name}', 'particle':f'dynasty:block/{name}'},
                texture_size=[16,16], elements=elements,
                display={'gui': {'rotation':[30,225,0], 'translation':[0,-1,0], 'scale':[.42,.42,.42]} if name.endswith('statue') else {'rotation':[30,225,0], 'scale':[.6,.6,.6]}})

def source(name, parts, runtime, png):
    texture_id=str(uuid.uuid5(uuid.NAMESPACE_URL, name+'/texture'))
    groups = {}; elements=[]
    for p, e in zip(parts, runtime['elements']):
        uid=str(uuid.uuid5(uuid.NAMESPACE_URL,name+'/'+p['name']))
        elements.append(dict(name=p['name'], type='cube', uuid=uid, **{'from':e['from'],'to':e['to']}, origin=[8,0,8], rotation=[0,0,0], box_uv=False,
                             faces={f:dict(uv=d['uv'],texture=0) for f,d in e['faces'].items()}, shade=True))
        groups.setdefault(p['group'], []).append(uid)
    outliner=[]
    # Static native blocks retain named authoring groups; their poses are baked, no fake idle animation.
    for group, children in groups.items():
        outliner.append(dict(name=group, uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,name+'/group/'+group)),origin=[8,0,8],rotation=[0,0,0],children=children))
    dump(DOC / f'blockbench/{name}.bbmodel', dict(meta={'format_version':'4.10','model_format':'java_block','box_uv':False},name=name,model_identifier=name,resolution={'width':16,'height':16},elements=elements,outliner=outliner,textures=[dict(uuid=texture_id,name=name+'.png',mode='bitmap',width=16,height=16,uv_width=16,uv_height=16,source='data:image/png;base64,'+base64.b64encode(png.read_bytes()).decode())]))

def main():
    DOC.mkdir(parents=True,exist_ok=True)
    original=ROOT/'build/cod3-remains-20261011/original/lootable_remains.json'
    original.parent.mkdir(parents=True,exist_ok=True)
    if not original.exists(): original.write_bytes((ASSETS/'models/block/lootable_remains.json').read_bytes())
    for name, parts in [('lootable_remains',COFFER),('rebel_general_statue',STATUE)]:
        islands, png=atlas(name)
        full=model(name,parts,islands)
        dump(ASSETS/f'models/block/{name}.json',full)
        source(name,parts,full,png)
        if name.endswith('statue'):
            for half in ('lower','upper'):
                for weapon in (False,True):dump(ASSETS/f'models/block/{name}_{half}_{"armed" if weapon else "empty"}.json',model(name,parts,islands,half,weapon))
            variants={}
            for facing,angle in [('north',0),('east',90),('south',180),('west',270)]:
                for half in ('lower','upper'):
                    for weapon in (False,True):
                        variants[f'facing={facing},half={half},weapon={str(weapon).lower()}']=dict(model=f'dynasty:block/{name}_{half}_{"armed" if weapon else "empty"}',y=angle)
            dump(ASSETS/f'blockstates/{name}.json',{'variants':variants})
            dump(ASSETS/f'models/item/{name}.json',{'parent':f'dynasty:block/{name}'})
            dump(ROOT/f'src/main/resources/data/dynasty/loot_tables/blocks/{name}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':f'dynasty:{name}'}],'conditions':[{'condition':'minecraft:block_state_property','block':f'dynasty:{name}','properties':{'half':'lower'}},{'condition':'minecraft:survives_explosion'}]}]})
    # Item placement creates an empty memorial; an actual defeat supplies its captured sword.
    empty=model('rebel_general_statue',STATUE,atlas('rebel_general_statue')[0],weapon=False)
    dump(ASSETS/'models/block/rebel_general_statue.json',empty)
    dump(DOC/'authoring.json',dict(palette=PALETTE,parts={'statue':STATUE,'coffer':COFFER},height_blocks=1.5,width_blocks=.875,animation='Static native block; weapon parts disappear when captured sword leaves inventory.'))
    print('Generated two original 16px atlases, six block models, 16 statue states and two Blockbench sources.')
if __name__ == '__main__': main()
