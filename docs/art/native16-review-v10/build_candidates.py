"""Original 16x16 pixel grids. Outputs REVIEW candidates only; never installs.

Every output pixel comes from the explicit grids / integer rectangles below.
No imagegen, noise, resampling, quantization, imported texture pixels or filters.
Pillow resize is used only for labelled QA sheets, never the source PNGs.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

DOC = Path(__file__).resolve().parent
ASSET = DOC / 'candidate/assets/dynasty'
TEX = ASSET / 'textures/block'
BEFORE = DOC / 'before/assets/dynasty'
TEX.mkdir(parents=True, exist_ok=True)

def grid(rows, palette):
    assert len(rows) == 16 and all(len(r) == 16 for r in rows)
    im = Image.new('RGB', (16, 16))
    im.putdata([tuple(bytes.fromhex(palette[k].lstrip('#'))) for r in rows for k in r])
    return im

def save(name, im):
    assert im.size == (16,16)
    im.save(TEX / (name + '.png'))

# Warm, pale stone. Broad, stepped grain rather than isolated bright pixels.
marble = grid([
    '4444433333322223',
    '4454433333222223',
    '4444333333222334',
    '3333333443323334',
    '3333334444333344',
    '2233334444433444',
    '2233333444433333',
    '3332333333333333',
    '4442333333222333',
    '4443333343222334',
    '4433333444333344',
    '3332233444333443',
    '3322233344333333',
    '3322333333344433',
    '3333334444444433',
    '3444444444333333',
], dict(zip('2345', ['b9bbb2','c5c7be','d3d4ca','deded3'])))
save('marble_block', marble)

# Neutral original host rock, not a copy of Minecraft stone.
rock = grid([
    '3333332222333333',
    '3334422222333333',
    '3334422223333344',
    '3333222333333444',
    '2222233333444443',
    '2222333333444333',
    '2333333333333333',
    '3333333332222233',
    '3344433322211233',
    '3344433332112233',
    '3333333332222333',
    '3322233333333333',
    '3322233344433333',
    '3323333444433333',
    '3333333444333333',
    '3333333222333333',
], dict(zip('1234', ['666762','72746e','80827b','8c8e86'])))

def ore(kind):
    im = rock.copy()
    d = ImageDraw.Draw(im)
    if kind == 'jade':
        colors = ['456957','58886a','72a282','94b89a']
        patches = [(2,2,['.aaa.','abcca','abbda','.aa..']),
                   (10,4,['.aa','acb','abb','.a.']),
                   (7,10,['.aaa','acbb','abda','.aa.'])]
    else:
        colors = ['615b78','7d6d9c','9c85b7','bea2cf']
        patches = [(10,1,['.aa.','acba','abda','.ba.']),
                   (2,5,['.aa.','acba','abba','.a..']),
                   (9,10,['..a.','.bca','abda','.aa.'])]
    for x,y,rows in patches:
        for v,row in enumerate(rows):
            for u,c in enumerate(row):
                if c != '.': d.point((x+u,y+v), fill='#'+colors['abcd'.index(c)])
    return im

save('jade_ore', ore('jade'))

# Forge atlas is painted for the EXISTING automatic UVs. Upper slab north:
# u0..16, v2..6; stem north u5..11, v6..13; foot north u1..15,v13..16.
metal = dict(zip('123456', ['434b49','515957','606865','707874','828984','989e96']))
base = grid([
    '3333333333444433',
    '3333443333444433',
    '3344443333333333',
    '3344433333333333',
    '3333333333332233',
    '3333332223332233',
    '3323322223333333',
    '3322333333344433',
    '3333333333444433',
    '3333344433333333',
    '3333444433333333',
    '3333443333223333',
    '3333333332223333',
    '3344433332233333',
    '3344433333333333',
    '3333333333444433',
], metal)

def forge_surfaces():
    side=base.copy(); d=ImageDraw.Draw(side)
    d.line((0,2,15,2),fill='#'+metal['5'])
    d.line((0,5,15,5),fill='#'+metal['2'])
    d.line((1,13,14,13),fill='#'+metal['4'])
    # Sparing cast-metal marks, not all-around highlight borders.
    d.line((3,3,5,3),fill='#'+metal['4'])
    d.line((10,14,12,14),fill='#'+metal['2'])
    bottom=base.copy(); d=ImageDraw.Draw(bottom)
    d.rectangle((3,4,12,11),fill='#'+metal['2'])
    d.rectangle((5,5,10,10),fill='#'+metal['3'])
    top=base.copy(); d=ImageDraw.Draw(top)
    # The raised strike plate is only paint on the existing solid work surface.
    d.rectangle((2,3,13,12),fill='#'+metal['2'])
    d.rectangle((3,4,12,11),fill='#'+metal['4'])
    d.line((3,4,9,4),fill='#'+metal['5'])
    d.line((4,7,6,7),fill='#'+metal['3'])
    d.line((8,9,10,9),fill='#'+metal['3'])
    d.line((8,10,9,10),fill='#'+metal['3'])
    for x in (1,14):
        d.line((x,6,x,9),fill='#456957')
        d.line((x,7,x,8),fill='#58886a')
    front=side.copy(); d=ImageDraw.Draw(front)
    # A narrow jade status inset on the stem, not an invented furnace hole.
    d.rectangle((6,7,9,11),fill='#'+metal['1'])
    d.rectangle((7,8,8,10),fill='#456957')
    d.line((7,8,7,9),fill='#58886a')
    d.point((2,3),fill='#'+metal['5']); d.point((13,3),fill='#'+metal['5'])
    active=front.copy(); d=ImageDraw.Draw(active)
    d.rectangle((7,8,8,10),fill='#72a282')
    d.line((7,8,7,9),fill='#b2d4ae')
    top_active=top.copy(); d=ImageDraw.Draw(top_active)
    for x in (1,14):
        d.line((x,6,x,9),fill='#72a282')
        d.line((x,7,x,8),fill='#b2d4ae')
    return {'jade_mending_forge':base,'jade_mending_forge_side':side,
            'jade_mending_forge_bottom':bottom,'jade_mending_forge_top':top,
            'jade_mending_forge_front':front,'jade_mending_forge_front_active':active,
            'jade_mending_forge_top_active':top_active}

for name,im in forge_surfaces().items():save(name,im)

def write_json(rel, data):
    p=ASSET/rel;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

model=json.loads((BEFORE/'models/block/jade_mending_forge.json').read_text())
model['textures']={'all':'dynasty:block/jade_mending_forge',
    'particle':'dynasty:block/jade_mending_forge',
    **{k:'dynasty:block/jade_mending_forge_'+k for k in ('front','side','top','bottom')}}
for element_index,e in enumerate(model['elements']):
    for direction,face in e['faces'].items():
        face['texture']='#'+{'north':'front','south':'side','east':'side','west':'side','up':'top','down':'bottom'}[direction]
        if direction == 'up' and element_index != 2:
            face['texture']='#all'
write_json('models/block/jade_mending_forge.json',model)
write_json('models/block/jade_mending_forge_active.json',{
    'parent':'dynasty:block/jade_mending_forge',
    'textures':{k:'dynasty:block/jade_mending_forge_'+k+'_active' for k in ('front','top')}})
state=json.loads((BEFORE/'blockstates/jade_mending_forge.json').read_text())
for key,value in state['variants'].items():
    if 'lit=true' in key:value['model']='dynasty:block/jade_mending_forge_active'
write_json('blockstates/jade_mending_forge.json',state)

def sheet(ids, name):
    # Original 1x swatches plus nearest-neighbour 8x / 3x3 repetition at 3x.
    width=970;height=245*len(ids)+60
    im=Image.new('RGB',(width,height),'#ecebe5');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
    d.text((20,15),'REVIEW ONLY | Original 16x16 grids | Nearest-neighbour QA | NOT in-game',font=font,fill='#252c29')
    for i,tid in enumerate(ids):
        y=60+i*245
        old=Image.open(BEFORE/'textures/block'/f'{tid}.png').convert('RGB')
        preview_id = 'jade_mending_forge_front' if tid == 'jade_mending_forge' else tid
        new=Image.open(TEX/f'{preview_id}.png').convert('RGB')
        d.text((20,y),tid,font=font,fill='#252c29')
        for x,asset,title in [(20,old,'Before / 1x + 8x'),(200,new,'Candidate / 1x + 8x')]:
            d.text((x,y+27),title,font=small,fill='#454c46')
            im.paste(asset,(x+140,y+60))
            im.paste(asset.resize((128,128),Image.Resampling.NEAREST),(x,y+56))
        for x,asset,title in [(405,old,'Before / 3x3 tiles'),(585,new,'Candidate / 3x3 tiles')]:
            d.text((x,y+27),title,font=small,fill='#454c46')
            tile=Image.new('RGB',(48,48))
            for u in range(3):
                for v in range(3):tile.paste(asset,(16*u,16*v))
            im.paste(tile.resize((144,144),Image.Resampling.NEAREST),(x,y+56))
        d.text((785,y+62),f'{len(new.getcolors(256))} colors',font=font,fill='#252c29')
        d.text((785,y+91),'16 x 16 native',font=small,fill='#454c46')
        d.text((785,y+114),'Opaque / static',font=small,fill='#454c46')
        if tid == 'jade_mending_forge':
            d.text((785,y+142),'Front atlas shown;',font=small,fill='#454c46')
            d.text((785,y+161),'see model preview.',font=small,fill='#454c46')
        d.line((20,y+226,width-20,y+226),fill='#bcc3b9')
    (DOC/'previews').mkdir(exist_ok=True)
    im.save(DOC/'previews'/name)

sheet(['marble_block','jade_ore','jade_mending_forge'],'first-three-comparison.png')

if __name__=='__main__':
    print('Wrote first-three review candidates and reference JSON. No src installation.')
    import sys
    if '--include-followup' in sys.argv:
        save('dragon_crystal_ore', ore('dragon'))
        sheet(['jade_ore','dragon_crystal_ore'],'ore-followup-comparison.png')
        print('Added one justified ore companion; retained existing deepslate/cloud/approved brick.')
