"""Original native 16x16 artwork. Review directory ONLY; never installs.

Pixels are declared as grids and integer clusters below. No random function,
reference-image reads, downsampling, filters, antialiasing or palette quantizing.
References informed density/material separation, not these pixel patterns.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw

DOC=Path(__file__).resolve().parent
ASSET=DOC/'candidate/assets/dynasty'
BLOCK=ASSET/'textures/block';ITEM=ASSET/'textures/item'
for p in (BLOCK,ITEM):p.mkdir(parents=True,exist_ok=True)

def grid(rows,palette):
    assert len(rows)==16 and all(len(r)==16 for r in rows),[(i,len(r),r) for i,r in enumerate(rows) if len(r)!=16]
    im=Image.new('RGBA',(16,16))
    colors={k:tuple(bytes.fromhex(v))+(255,) for k,v in palette.items()}
    colors['.']=(0,0,0,0)
    im.putdata([colors[k] for row in rows for k in row])
    return im

def save(im,name,kind='block'):
    assert im.size==(16,16)
    if kind=='block':
        assert im.getchannel('A').getextrema()==(255,255)
        im=im.convert('RGB')
    im.save((BLOCK if kind=='block' else ITEM)/(name+'.png'))

# Pale mineral stone: staggered short strata and broken calcitic grains,
# 6 colors. No regular brick mortar and no enclosed eye-shaped dark patches.
marble=grid([
    '4444455443334444',
    '4444555433334444',
    '3334554443222344',
    '3334444432223344',
    '2334444333344554',
    '2344554433444554',
    '3344565544444433',
    '4444555444433333',
    '5544333444443345',
    '5543322344554445',
    '4443322344565444',
    '4433333444554433',
    '3344443333443333',
    '3445544433333223',
    '4445544444333223',
    '4444444433344444',
],{'2':'bec4bc','3':'cfd4cd','4':'e0e2d9','5':'eaeee4','6':'f4f4e9'})
# A restrained fracture joins a midtone mass; it is not scattered noise.
d=ImageDraw.Draw(marble);d.line((10,3,11,3),fill='#b5bcb6')
save(marble,'marble_block')

# Original interlocking stone substrate, independent from the marble pattern.
stone=grid([
    '3334443322223333',
    '3344543322333344',
    '3334433333444443',
    '2223333344543333',
    '2233444333332223',
    '2334544322222233',
    '3333433222333334',
    '4443332223344544',
    '4433333333444333',
    '3332223333333223',
    '3322123344432223',
    '3332333444533333',
    '4433333443334443',
    '4433223333334543',
    '3332222234433333',
    '3333322334533333',
],{'1':'626460','2':'727671','3':'828680','4':'92958c','5':'a1a397'})

def ore(name,colors,clusters):
    im=stone.copy();pix=im.load()
    palette={k:tuple(bytes.fromhex(c))+(255,) for k,c in zip('abcde',colors)}
    for x,y,rows in clusters:
        for v,row in enumerate(rows):
            for u,key in enumerate(row):
                if key!='.':pix[x+u,y+v]=palette[key]
    save(im,name)

# Jagged, embedded fragments: no complete dark ring around a polished gem.
ore('jade_ore',['365c49','428463','66b587','a1d5ad','d1e5bb'],[
    (2,1,['.dd.','dccb','bbca','..a.']),
    (10,3,['.edb','dcba','.bb.']),
    (6,7,['.dc.','dcbb','baa.']),
    (1,11,['cd.','bba']),
    (11,11,['dc.','cba','.ba'])])
ore('dragon_crystal_ore',['4e446c','705497','a282c2','d1b7e1','eee0e8'],[
    (9,1,['.d.','dcc','bca','aba']),
    (2,5,['cd..','bdc.','.abc','..aa']),
    (10,8,['.dc.','dcba','ba..']),
    (3,12,['dcb.','bccb','.aa.'])])

# Cast dark iron, six greys; upper/lower edges belong to the existing cuboids.
iron={'1':'303638','2':'424a4b','3':'545e5d','4':'697571','5':'83908a','6':'a4ada0'}
base=grid([
    '3333444333223333',
    '3344544322233334',
    '3444443322333444',
    '3333333333444433',
    '2223333444433333',
    '2233444443332233',
    '3334454333222333',
    '3344433333223334',
    '4433333223333444',
    '4333322223344433',
    '3333222333344333',
    '3333233344333333',
    '3344333444432233',
    '3444433445332223',
    '3334443333322333',
    '3333333333333333',
],iron)
save(base,'jade_mending_forge')
side=base.copy();d=ImageDraw.Draw(side)
d.line((0,2,15,2),fill='#83908a')
d.line((0,5,15,5),fill='#303638')
d.line((0,4,15,4),fill='#424a4b')
for a,b in [((1,3),(5,3)),((10,3),(13,3)),((5,13),(10,13))]:d.line((*a,*b),fill='#697571')
d.line((1,13,4,13),fill='#83908a');d.line((11,13,14,13),fill='#83908a')
d.line((1,15,14,15),fill='#424a4b')
# Two small bronze fastenings on the head's actual side UV, not full-face trim.
for x in (3,12):
    d.point((x,2),fill='#b3975c');d.point((x,3),fill='#776449')
save(side,'jade_mending_forge_side')
front=side.copy();d=ImageDraw.Draw(front)
d.rectangle((6,7,9,11),fill='#303638')
d.line((6,7,9,7),fill='#83908a')
d.line((6,8,6,10),fill='#424a4b')
d.rectangle((7,8,8,10),fill='#356949')
d.line((7,8,7,9),fill='#67956c')
d.point((9,11),fill='#697571')
save(front,'jade_mending_forge_front')
top=grid([
    '3333444333223333',
    '3333444333223333',
    '2444555444444432',
    '2455554444433332',
    '2455444333334442',
    '2444333333445542',
    '2443333444554442',
    '2433334555443332',
    '2433445544433442',
    '2444454433334542',
    '2455443333344432',
    '2444433444443332',
    '2333444443333332',
    '2222222222222222',
    '3333333333333333',
    '3333333333333333',
],iron)
d=ImageDraw.Draw(top)
# Short hammer nicks, a few directional wear groups. No perspective painted in.
d.line((5,6,7,6),fill='#424a4b');d.line((8,10,10,10),fill='#424a4b')
d.line((5,5,6,5),fill='#a4ada0');d.line((8,9,9,9),fill='#a4ada0')
for x,y in [(1,4),(14,10)]:
    d.line((x,y,x,y+1),fill='#356949');d.point((x,y),fill='#67956c')
save(top,'jade_mending_forge_top')
bottom=base.copy();d=ImageDraw.Draw(bottom)
d.line((3,4,12,4),fill='#424a4b');d.line((3,11,12,11),fill='#424a4b')
d.line((3,5,3,10),fill='#424a4b');d.line((12,5,12,10),fill='#424a4b')
save(bottom,'jade_mending_forge_bottom')
active=front.copy();d=ImageDraw.Draw(active)
d.rectangle((7,8,8,10),fill='#70bc82');d.line((7,8,7,9),fill='#c4dda7')
save(active,'jade_mending_forge_front_active')
active=top.copy();d=ImageDraw.Draw(active)
for x,y in [(1,4),(14,10)]:
    d.line((x,y,x,y+1),fill='#70bc82');d.point((x,y),fill='#c4dda7')
save(active,'jade_mending_forge_top_active')

# Accessories: explicitly 16x16, opaque or fully transparent pixels only.
# Original silhouettes: round cast mirror, pierced hanging jade, cloth talisman.
mirror=grid([
    '................',
    '......aaa.......',
    '....aefeeaa.....',
    '...aefddcbaa....',
    '..aefdhhhcbaa...',
    '..aedhiiihcba...',
    '.aedhiijighcba..',
    '.aedhiigghhcba..',
    '.aedhiggghhcba..',
    '..acdhgghhcba...',
    '..abcddddcbaa...',
    '...abcccbbaa....',
    '....aabbaa......',
    '......ab........',
    '......aa........',
    '................',
],{'a':'473a29','b':'745332','c':'a9763b','d':'cb9a4c','e':'e5bd70','f':'f4d895',
   'g':'456558','h':'648778','i':'98b7a0','j':'d3dec2'})
save(mirror,'bronze_mirror','item')
jade=grid([
    '................',
    '.....rsr........',
    '.....r.r........',
    '......rs........',
    '.....abba.......',
    '....acddba......',
    '...acg..dba.....',
    '...acg..edba....',
    '...afggeedba....',
    '....afgeddba....',
    '....acedddba....',
    '.....acddba.....',
    '......abba......',
    '.......rs.......',
    '......srs.......',
    '................',
],{'a':'244d3d','b':'357755','c':'61aa77','d':'87c494','e':'a1d2a8','f':'cce4bc','g':'b4deb4',
   'r':'663d32','s':'b86a48'})
save(jade,'jade_pendant','item')
charm=grid([
    '................',
    '.......aea......',
    '.......aa.......',
    '.....abedda.....',
    '....abddddca....',
    '....acdghdca....',
    '....acghhdca....',
    '....acghddca....',
    '....acgghdca....',
    '....acddghca....',
    '....acdghdca....',
    '....acgddjca....',
    '....acddjjca....',
    '.....acddca.....',
    '.....aa.aa......',
    '................',
],{'a':'322f48','b':'a57f49','c':'51476d','d':'706394','e':'d1ad65',
   'g':'e6c778','h':'b99554','j':'ab6056'})
d=ImageDraw.Draw(charm)
d.rectangle((6,5,9,11),fill='#706394')
for xy in [(9,5),(8,6),(7,7),(6,8),(7,8),(8,8),(9,8),(9,9),(8,10),(7,11)]:
    d.point(xy,fill='#e6c778')
d.point((8,9),fill='#b99554');d.point((8,11),fill='#b99554')
save(charm,'storm_charm','item')

# Candidate resource wiring; no modification to live JSON/geometry/UV or Java.
before=DOC/'before/assets/dynasty'
model=json.loads((before/'models/block/jade_mending_forge.json').read_text())
model['textures']={'all':'dynasty:block/jade_mending_forge','particle':'dynasty:block/jade_mending_forge',
    **{k:'dynasty:block/jade_mending_forge_'+k for k in ('front','side','top','bottom')}}
for i,e in enumerate(model['elements']):
    for face,data in e['faces'].items():
        slot={'north':'front','south':'side','west':'side','east':'side','down':'bottom','up':'top' if i==2 else 'all'}[face]
        data['texture']='#'+slot
def put(rel,data):
    p=ASSET/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
put('models/block/jade_mending_forge.json',model)
put('models/block/jade_mending_forge_active.json',{'parent':'dynasty:block/jade_mending_forge',
    'textures':{k:'dynasty:block/jade_mending_forge_'+k+'_active' for k in ('top','front')}})
state=json.loads((before/'blockstates/jade_mending_forge.json').read_text())
for key,data in state['variants'].items():
    if 'lit=true' in key:data['model']='dynasty:block/jade_mending_forge_active'
put('blockstates/jade_mending_forge.json',state)
print('Wrote 13 native 16x16 candidate PNGs + 3 texture-reference JSONs. Live src untouched.')
