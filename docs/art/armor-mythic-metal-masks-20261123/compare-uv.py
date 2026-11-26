from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = OUT/'source/src/main/resources/assets'
PROV = json.loads((OUT/'provenance.json').read_text())
PIN = OUT.parent/'armor-mythic-uv-20261122'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    with Image.open(path) as im:
        return im.convert('RGBA')
for row in PROV['files']:
    assert sha(OUT/'source'/row['path'])==row['sha256']
sheet=Image.new('RGB',(1080,530),'#52585c')
draw=ImageDraw.Draw(sheet)
for x,label in [(8,'set / four inventory icons'),(275,'active helmet atlas'),(555,'head'),(644,'ornament'),(775,'waist front'),(871,'waist back'),(967,'')]:
    draw.text((x,8),label,fill='white')
def paste(im,x,y,s):
    big=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST)
    sheet.paste(big,(x,y),big)
def relative(path): return str(path.relative_to(ROOT))

data={}
for i, name in enumerate(('banglum','metallurgium')):
    y=45+i*205
    draw.text((8,y),name,fill='white')
    items={}
    specialized=SOURCE/f'mythicmetals/textures/models/{name}_model.png'
    baseline=SOURCE/'minecraft/textures/models/armor'
    for j, slot in enumerate(('helmet','chestplate','leggings','boots')):
        stem=f'{name}_{slot}'
        model=SOURCE/f'mythicmetals/models/item/{stem}.json'
        tex=json.loads(model.read_text())['textures']['layer0']
        assert tex==f'mythicmetals:item/armor/{stem}'
        icon=SOURCE/f'mythicmetals/textures/item/armor/{stem}.png'
        paste(load(icon),8+j*60,y+30,3)
        atlas=specialized if slot=='helmet' else baseline/f'{name}_layer_{2 if slot=="leggings" else 1}.png'
        items[f'mythicmetals:{stem}']={'model':relative(model),'icon':relative(icon),'active_atlas':relative(atlas)}
    atlas=load(specialized)
    assert atlas.size==(64,32)
    paste(atlas,275,y,3)
    legs=load(baseline/f'{name}_layer_2.png')
    ornament=(9,17,10,20) if name=='banglum' else (2,3,3,6)
    coords={'head':(atlas,(8,8,16,16)), 'ornament_front_sample':(atlas,ornament),
            'waist_front':(legs,(20,20,28,32)), 'waist_back':(legs,(32,20,40,32))}
    result={}
    for x,(part,(im,bounds)) in zip((555,644,775,871,967),coords.items()):
        crop=im.crop(bounds)
        paste(crop,x,y,7)
        result[part]={'bounds':bounds,'alpha_rows':[''.join('#' if crop.getpixel((u,v))[3] else '.' for u in range(crop.width)) for v in range(crop.height)]}
    data[name]={'items':items,'active_specialized_atlas_size':atlas.size,'atlas_regions':result,
                'crop_scope':'unposed UV rectangles; not projected visibility'}
sheet.save(OUT/'banglum-metallurgium-source.png')
(OUT/'slot-and-uv-evidence.json').write_text(json.dumps(data,indent=2)+'\n')
for k,v in data.items():
 print(k,{n:r['alpha_rows'] for n,r in v['atlas_regions'].items()})
