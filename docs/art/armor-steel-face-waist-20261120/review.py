from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ART = ROOT / 'docs/art'
PARTS = ('helmet','chestplate','leggings','boots')

def read(path):
    return json.loads(path.read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def verified(base, provenance, path):
    record = next(r for r in provenance['sources'] if r['path'] == path)
    p = base / record['local']
    data = p.read_bytes()
    assert sha(data) == record['sha256']
    assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest() == record['git_blob_sha1']
    return p

def main():
    cases = [
        ('armor-pneumatic-reference-20261111','pneumaticcraft','compressed_iron','src/main/resources',
          ['textures/armor/compressed_iron_1.png','textures/armor/compressed_iron_2.png'],
          ['src/main/java/me/desht/pneumaticcraft/common/core/ModItems.java',
           'src/main/java/me/desht/pneumaticcraft/common/item/CompressedIronArmorItem.java',
           'src/main/java/me/desht/pneumaticcraft/lib/Textures.java']),
        ('armor-engineering-reference-20261111','immersiveengineering','armor_steel','src/generated/resources',
          ['textures/models/armor_steel.png','textures/models/armor_steel_legs.png'],
          ['src/main/java/blusunrize/immersiveengineering/common/register/IEItems.java',
           'src/main/java/blusunrize/immersiveengineering/common/items/SteelArmorItem.java']),
    ]
    inventory=read(ART/'armor-worn-uv-20261102/face-and-seam-inventory.json')
    coords={p['part']:{f['direction']:f['crop'] for f in p['faces']} for p in inventory['entries'][0]['parts']}
    sheet=Image.new('RGB',(1150,462),'#52585c')
    d=ImageDraw.Draw(sheet)
    for x,t in [(8,'set / inventory'),(233,'full L1'),(431,'full L2'),(629,'head front'),(703,'hat front'),
                (777,'waist front'),(861,'waist back'),(946,'waist side'),(1015,'waist side'),(1085,'top cap')]:
        d.text((x,10),t,fill='white')
    def paste(im,x,y,scale):
        enlarged=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
        sheet.paste(enlarged,(x,y),enlarged)
    def file(p):
        return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
    output={}
    for i,(folder,ns,stem,model_root,atlases,java_paths) in enumerate(cases):
        base=ART/folder
        prov=read(base/'provenance.json')
        java=[verified(base,prov,p) for p in java_paths]
        for p in java:
            assert 'getArmorTexture' in p.read_text() or p==java[0] or p.name=='Textures.java'
        y=43+i*220
        d.text((8,y),ns,fill='white')
        models=[]
        for j,slot in enumerate(PARTS):
            item=stem+'_'+slot
            model=verified(base,prov,f'{model_root}/assets/{ns}/models/item/{item}.json')
            ref=read(model)['textures']['layer0']
            owner,tex=ref.split(':',1)
            assert owner==ns
            icon=verified(base,prov,f'src/main/resources/assets/{ns}/textures/{tex}.png')
            paste(Image.open(icon).convert('RGBA'),8+55*j,y+30,3)
            models.append({'id':f'{ns}:{item}','model':file(model),'icon':file(icon),'layer':2 if slot=='leggings' else 1})
        paths=[verified(base,prov,f'src/main/resources/assets/{ns}/{a}') for a in atlases]
        images=[Image.open(p).convert('RGBA') for p in paths]
        assert all(a.size==(64,32) for a in images)
        for j,im in enumerate(images):paste(im,233+j*198,y,3)
        crops={}
        for layer,part,direction,x in [(1,'head','NORTH',629),(1,'hat','NORTH',703),(2,'body','NORTH',777),
             (2,'body','SOUTH',861),(2,'body','WEST',946),(2,'body','EAST',1015),
             (2,'body','DOWN',1085),(2,'body','UP',None)]:
            rect=coords[part][direction]
            img=images[layer-1].crop(rect)
            rows=[''.join('#' if img.getpixel((xx,yy))[3] else '.' for xx in range(img.width))
                  for yy in range(img.height)]
            crops[f'L{layer}/{part}/{direction}']={'bounds':rect,'visible_pixels_by_row':[r.count('#') for r in rows],'alpha_rows':rows}
            if x is not None:paste(img,x,y,7)
        output[ns]={'source_commit':prov['commit'],'repository':prov['repository'],'java':[file(p) for p in java],
                    'items':models,'atlases':[file(p) for p in paths],'crops':crops}
    sheet.save(OUT/'fixed-source-faces.png')
    (OUT/'bindings-and-faces.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    for k,v in output.items():
        print(k,{face:rows['visible_pixels_by_row'] for face,rows in v['crops'].items()})
if __name__=='__main__':
    main()
