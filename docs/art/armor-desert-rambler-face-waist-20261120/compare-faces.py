from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
ART=ROOT/'docs/art'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def rgba(p):
    with Image.open(p) as im:
        return im.convert('RGBA')

def record(p):
    return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}

def assets():
    desert=ART/'armor-desert-whole-20261113'
    rambler=ART/'armor-rambler-leather-whole-20261114'
    desert_record=read(desert/'provenance.json')
    rambler_record=read(rambler/'provenance.json')
    desert_fixed={desert/r['path']: r['sha256'] for r in desert_record['entries']}
    rambler_fixed={rambler/r['local']: r['sha256'] for r in rambler_record['entries']}
    tx=desert/'source/src/main/resources/assets/atum/textures/models/armor'
    rt=rambler/'source/assets/jerotesvillage/textures'
    desert_rows=[i for i in read(desert/'static-bindings.json') if i['id'].endswith('_iron')]
    rambler_rows=read(rambler/'four-slot-binary-bindings.json')['bindings']
    assert len(desert_rows)==len(rambler_rows)==4
    desert_icons=[]
    for row in desert_rows:
        model=desert/row['model']
        assert read(model)['textures']=={r['layer']:r['texture'] for r in row['layers']}
        paths=[desert/layer['path'] for layer in row['layers']]
        assert all(sha(p)==r['sha256'] for p,r in zip(paths,row['layers']))
        assert sha(model)==desert_fixed[model]
        desert_icons.append(paths)
    rambler_icons=[]
    for row in rambler_rows:
        kind=row['constructor_type'].title()
        model=rambler/'source/assets/jerotesvillage/models/item'/(row['id'].split(':')[1]+'.json')
        ref=read(model)['textures']['layer0']
        assert ref=='jerotesvillage:item/'+row['id'].split(':')[1]
        assert sha(model)==rambler_fixed[model]
        disassembly=rambler/f'RamblerLeatherArmor${kind}-python-decode.json'
        source=read(disassembly)
        method=next(m for m in source['methods'] if m['name']=='getArmorTexture')
        assert row['explicit_getArmorTexture'] in json.dumps(method)
        rambler_icons.append([rt/(ref.split(':')[1]+'.png')])
    return [
      ('Atum desert iron',desert_icons,[[tx/f'desert_iron_armor_{i}{suffix}.png' for suffix in ('','_overlay')] for i in [1,2]],desert_fixed),
      ('Jerotes Rambler leather',rambler_icons,[[rt/f'models/armor/rambler_leather_layer_{i}.png'] for i in [1,2]],rambler_fixed)
    ]

def main():
    uv=read(ART/'armor-worn-uv-20261102/face-and-seam-inventory.json')['entries'][0]
    boxes={p['part']:{f['direction']:f['crop'] for f in p['faces']} for p in uv['parts']}
    sheet=Image.new('RGB',(1100,460),'#50565a')
    draw=ImageDraw.Draw(sheet)
    for x,k in [(8,'four inventory icons'),(220,'base + overlay L1'),(414,'base + overlay L2'),(612,'head'),(690,'hat'),(780,'belt front'),(865,'belt back'),(950,'belt sides')]:
        draw.text((x,8),k,fill='white')
    report={}
    def composite(paths):
        images=[rgba(p) for p in paths]
        return Image.alpha_composite(*images) if len(images)==2 else images[0]
    def paste(im,x,y,scale):
        bigger=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
        sheet.paste(bigger,(x,y),bigger)
    for i,(label,icons,worn,fixed) in enumerate(assets()):
        y=38+i*215
        native=[p for group in icons+worn for p in group]
        assert all(sha(p)==fixed[p] for p in native)
        draw.text((8,y),label,fill='white')
        for j,paths in enumerate(icons):paste(composite(paths),8+j*50,y+28,3)
        layers=[composite(p) for p in worn]
        for j,im in enumerate(layers):paste(im,220+j*194,y,3)
        crops={}
        for layer,part,side,x in [
            (1,'head','NORTH',612),(1,'hat','NORTH',690),(2,'body','NORTH',780),
            (2,'body','SOUTH',865),(2,'body','WEST',950),(2,'body','EAST',998),
            (2,'body','DOWN',None),(2,'body','UP',None)]:
            b=boxes[part][side]
            def rows(image):
                alpha=image.crop(b).getchannel('A')
                return [''.join('#' if alpha.getpixel((u,v)) else '.' for u in range(alpha.width)) for v in range(alpha.height)]
            crops[f'L{layer}/{part}/{side}']={'bounds':b,'visible_mask_by_source_layer':[rows(rgba(p)) for p in worn[layer-1]],'combined_mask':rows(layers[layer-1])}
            if x is not None:paste(layers[layer-1].crop(b),x,y,7)
        report[label]={'icons':[[record(p) for p in icon] for icon in icons],
                       'worn_atlases':[[record(p) for p in layer] for layer in worn],'uv_crops':crops}
        print(label,{k:[r.count('#') for r in v['combined_mask']] for k,v in crops.items()})
    sheet.save(OUT/'face-waist-reference.png')
    (OUT/'source-faces.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':
    main()
