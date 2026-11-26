from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
from itertools import combinations
import hashlib
import json
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ART = ROOT / 'docs/art'
PROV = ART/'armor-three-consumers-20261112/source/mojang-client-provenance.json'
SOURCE = json.loads(PROV.read_text())
ARCHIVE = ROOT/SOURCE['local']
CONTRACT = ART/'armor-worn-uv-20261102/face-and-seam-inventory.json'
sha = lambda data: hashlib.sha256(data).hexdigest()

def unpack(z, path, entries):
    data = z.read(path)
    entries[path] = sha(data)
    return data

def image(z, path, entries):
    return Image.open(BytesIO(unpack(z,path,entries))).convert('RGBA')

def visible_mask(im):
    return tuple(value>0 for value in im.getchannel('A').get_flattened_data())

def face(im, rect):
    cut = im.crop(rect)
    return {'bounds':rect,'alpha_rows':[''.join('#' if cut.getpixel((x,y))[3] else '.'
           for x in range(cut.width)) for y in range(cut.height)]}

def main():
    assert sha(ARCHIVE.read_bytes()) == SOURCE['sha256']
    model = json.loads(CONTRACT.read_text())['entries'][0]
    uv = {p['part']:{f['direction']:f['crop'] for f in p['faces']} for p in model['parts']}
    sheet = Image.new('RGB',(1050,610),'#52585c')
    canvas = ImageDraw.Draw(sheet)
    for x,title in ((8,'Minecraft 1.12.2'),(254,'64x32 atlas 1'),(455,'64x32 atlas 2'),(660,'head front'),(750,'hat front'),(840,'waist front'),(932,'waist back')):
        canvas.text((x,12),title,fill='white')
    def paste(im,x,y,factor):
        enlarged=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)
        sheet.paste(enlarged,(x,y),enlarged)
    records={}
    all_sets={}
    with zipfile.ZipFile(ARCHIVE) as z:
        for row,(folder,stem) in enumerate([('gold','golden'),('diamond','diamond'),('chainmail','chainmail')]):
            y=40+row*180
            canvas.text((8,y),folder,fill='white')
            entries={}
            parts=[]
            for j,part in enumerate(('helmet','chestplate','leggings','boots')):
                name=stem+'_'+part
                model=json.loads(unpack(z,f'assets/minecraft/models/item/{name}.json',entries))
                texture=model['textures']['layer0'].removeprefix('minecraft:')
                assert texture==f'items/{folder}_{part}'
                icon=image(z,f'assets/minecraft/textures/{texture}.png',entries)
                parts.append(icon)
                paste(icon,8+j*59,y+29,3)
            layers=[image(z,f'assets/minecraft/textures/models/armor/{folder}_layer_{layer}.png',entries) for layer in (1,2)]
            assert all(i.size==(64,32) for i in layers)
            for j,im in enumerate(layers):
                paste(im,254+j*201,y,3)
            crops={}
            for key,n,part,direction,x in [
                ('head',1,'head','NORTH',660),('hat',1,'hat','NORTH',750),
                ('waist_front',2,'body','NORTH',840),('waist_back',2,'body','SOUTH',932),
                ('waist_left',2,'body','WEST',840),('waist_right',2,'body','EAST',932),
                ('waist_top_cap',2,'body','DOWN',660),('waist_bottom_cap',2,'body','UP',750),
            ]:
                rect=uv[part][direction]
                crops[key]=face(layers[n-1],rect)
                if key in ('head','hat','waist_front','waist_back'):
                    paste(layers[n-1].crop(rect),x,y,8)
            records[folder]={'archive_entry_hashes':entries,'uv_faces':crops}
            all_sets[folder]=parts+layers
    controls=ART/'armor-worn-uv-20261102/vanilla-controls'
    dedup={}
    for a,b in combinations(all_sets,2):
        dedup[f'{a}/{b}']=[visible_mask(x)==visible_mask(y) for x,y in zip(all_sets[a],all_sets[b])]
    for name,images in all_sets.items():
        compare=[visible_mask(l)==visible_mask(Image.open(controls/f'iron_layer_{i}.png'))
                 for i,l in enumerate(images[-2:],1)]
        records[name]['alpha_layout_match_to_1_20_1_iron']=compare
    sheet.save(OUT/'source-control-sheet.png')
    (OUT/'native-reference-evidence.json').write_text(json.dumps({'archive':SOURCE,'sets':records,
        'slot_order':['head','chest','legs','feet','layer1','layer2'],'pairwise_same_alpha_layout':dedup},indent=2)+'\n')
    for name,record in records.items():
        print(name, {k:v['alpha_rows'] for k,v in record['uv_faces'].items() if k in ('head','hat','waist_front')},record['alpha_layout_match_to_1_20_1_iron'])
    print(dedup)

if __name__=='__main__':
    main()
