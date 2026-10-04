"""Compose QA only. Artwork is authored at native resolution by build_art.py."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from zipfile import ZipFile
from io import BytesIO
import json,shutil,sys
DOC=Path(__file__).resolve().parent
ROOT=DOC.parents[2];A=DOC/'candidate/assets/dynasty';B=DOC/'before/assets/dynasty'
OUT=DOC/'previews';OUT.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
def load(path):return Image.open(path).convert('RGBA')
def zoom(im,w):return im.resize((w,w),Image.Resampling.NEAREST)
def paste(c,im,xy,w=None):
    if w:im=zoom(im,w)
    c.paste(im,xy,im)
def wall(im):
    out=Image.new('RGBA',(48,48))
    for y in range(3):
        for x in range(3):out.paste(im,(16*x,16*y))
    return out

c=Image.new('RGB',(1100,830),'#e8e6de');d=ImageDraw.Draw(c)
d.text((20,16),'NATIVE 16 REWORK | Current source / rejected v10 / new v11 / v11 3x3 repeat',font=font,fill='#25302c')
for i,tid in enumerate(['marble_block','jade_ore','dragon_crystal_ore']):
    y=60+i*250;d.text((20,y),tid,font=font,fill='#25302c')
    for x,title,p in [(20,'Current source',B/'textures/block'/f'{tid}.png'),
                       (220,'Previous v10',ROOT/'docs/art/native16-review-v10/candidate/assets/dynasty/textures/block'/f'{tid}.png'),
                       (420,'New v11',A/'textures/block'/f'{tid}.png')]:
        im=load(p);d.text((x,y+27),title,font=small,fill='#555d55')
        paste(c,im,(x,y+54),128);paste(c,im,(x+144,y+56))
    im=load(A/'textures/block'/f'{tid}.png')
    paste(c,wall(im),(642,y+48),192)
    d.text((860,y+59),f'16 x 16 / {len(im.getcolors(256))} colors',font=font,fill='#25302c')
    d.text((860,y+88),'Explicit pixel clusters',font=small,fill='#555d55')
    d.text((860,y+109),'No noise / no downsample',font=small,fill='#555d55')
    d.line((20,y+240,1080,y+240),fill='#b8bdae')
c.save(OUT/'block-comparison.png')

def checker(size,light=False):
    colors=('#deddd3','#c8ccc1') if light else ('#263230','#32413d')
    im=Image.new('RGB',size,colors[0]);d=ImageDraw.Draw(im)
    for y in range(0,size[1],16):
        for x in range(0,size[0],16):
            if (x//16+y//16)%2:d.rectangle((x,y,x+15,y+15),fill=colors[1])
    return im

c=Image.new('RGB',(1040,775),'#e8e6de');d=ImageDraw.Draw(c)
d.text((20,16),'THREE ACCESSORIES | Current 32px source -> original native 16px candidates',font=font,fill='#25302c')
for i,tid in enumerate(['bronze_mirror','jade_pendant','storm_charm']):
    y=62+i*232;d.text((20,y),tid,font=font,fill='#25302c')
    for x,title,p in [(20,'Current 32 x 32',B/'textures/item'/f'{tid}.png'),(215,'New 16 x 16',A/'textures/item'/f'{tid}.png')]:
        im=load(p);d.text((x,y+28),title,font=small,fill='#555d55')
        bg=checker((144,144));paste(bg,im,(8,8),128);c.paste(bg,(x,y+51));paste(c,im,(x+153,y+51))
    im=load(A/'textures/item'/f'{tid}.png')
    for x,light in [(438,False),(626,True)]:
        bg=checker((160,160),light);paste(bg,im,(16,16),128);c.paste(bg,(x,y+51))
    d.text((816,y+61),f'{len(im.getcolors(256))-1} opaque colors',font=font,fill='#25302c')
    d.text((816,y+89),'Alpha = 0 or 255',font=small,fill='#555d55')
    d.text((816,y+113),'16px GUI read:',font=small,fill='#555d55')
    for k in range(3):
        d.rectangle((816+k*28,y+143,839+k*28,y+166),fill='#9f9f95',outline='#626860');paste(c,im,(820+k*28,y+147))
    d.line((20,y+221,1020,y+221),fill='#b8bdae')
c.save(OUT/'accessory-comparison.png')

# Every new atlas at 1x/8x and 3x3; atlas repetition is QA, not a wall proposal.
names=sorted(p.stem for p in (A/'textures/block').glob('jade_mending_forge*.png'))
c=Image.new('RGB',(1120,950),'#e8e6de');d=ImageDraw.Draw(c)
d.text((20,16),'FORGE ATLAS QA | Actual cuboid UVs preserved | Original 1x, nearest 8x, 3x3 repeat',font=font,fill='#25302c')
for i,n in enumerate(names):
    x=20+(i%3)*368;y=60+(i//3)*290
    im=load(A/'textures/block'/f'{n}.png');label=n.removeprefix('jade_mending_forge').strip('_')or'base'
    d.text((x,y),label,font=font,fill='#25302c');paste(c,im,(x,y+33),128);paste(c,im,(x+141,y+34));paste(c,wall(im),(x+190,y+52),144)
    d.text((x,y+220),f'{len(im.getcolors(256))} colors / atlas, not all six faces',font=small,fill='#555d55')
c.save(OUT/'forge-atlas-qa.png')
for name in ['forge-model-comparison.png','forge-six-face-comparison.png']:
    shutil.copy2(DOC/'qa'/name,OUT/name)

z=ZipFile('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar')
refs={n:Image.open(BytesIO(z.read('assets/minecraft/textures/block/'+n+'.png'))).convert('RGBA') for n in ['stone_bricks','calcite','stone','iron_ore','emerald_ore']}
c=Image.new('RGB',(1060,1000),'#e8e6de');d=ImageDraw.Draw(c)
d.text((20,16),'VANILLA SCALE + TILING CHECK | References for comparison only, never in candidate PNGs',font=font,fill='#25302c')
items=list(refs.items())+[(n,load(A/'textures/block'/f'{n}.png')) for n in ['marble_block','jade_ore','dragon_crystal_ore']]
items+=[('palace_bricks / unchanged',load(ROOT/'src/main/resources/assets/dynasty/textures/block/palace_bricks.png'))]
for i,(n,im) in enumerate(items):
    x=20+(i%5)*207;y=60+(i//5)*205;d.text((x,y),n,font=small,fill='#25302c');paste(c,im,(x,y+30),128);paste(c,im,(x+146,y+30))
blocks=[refs['stone_bricks'],load(A/'textures/block/marble_block.png'),items[-1][1],refs['stone']]
mixed=Image.new('RGB',(16*16,16*6))
for y in range(6):
    for x in range(16):mixed.paste(blocks[x//4],(x*16,y*16))
paste(c,mixed.convert('RGBA'),(20,515),None)
# Non-square scaling must preserve 16 columns x6 rows, not use the square helper.
c.paste(mixed.resize((1024,384),Image.Resampling.NEAREST),(20,515))
d.text((20,481),'Vanilla stone bricks | New marble | Approved palace bricks (unchanged) | Vanilla stone',font=font,fill='#25302c')
d.text((20,926),'This is a texture comparison, not a screenshot from a running world.',font=font,fill='#25302c')
c.save(OUT/'vanilla-context.png')

# Native 1x contact, including actual alpha holes.
files=sorted((A/'textures').rglob('*.png'))
c=Image.new('RGB',(470,32*len(files)+32),'#e8e6de');d=ImageDraw.Draw(c)
for i,p in enumerate(files):
    im=load(p);paste(c,im,(12,16+i*32));d.text((45,17+i*32),p.stem,font=small,fill='#25302c')
c.save(OUT/'native-1x.png')
print('Wrote comparison, native-size, tiling, inventory, and vanilla QA sheets.')
