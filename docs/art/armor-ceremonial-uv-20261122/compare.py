from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ART = ROOT/'docs/art'
read = lambda p: json.loads(p.read_text())
sha = lambda data: hashlib.sha256(data).hexdigest()

def masks(im, rect):
    alpha = im.crop(rect).getchannel('A')
    return [''.join('#' if alpha.getpixel((x,y)) else '.' for x in range(alpha.width))
            for y in range(alpha.height)]

def main():
    record = ART/'armor-worn-uv-20261102/face-and-seam-inventory.json'
    uv = {p['part']:{f['direction']:f['crop'] for f in p['faces']} for p in read(record)['entries'][0]['parts']}
    sheet = Image.new('RGB',(1080,430),'#52585c')
    draw = ImageDraw.Draw(sheet)
    for x,label in [(8,'registered set'),(202,'four inventory icons'),(435,'main head front'),(530,'outer hat front'),
                    (630,'waist front'),(730,'waist back'),(830,'waist sides'),(965,'waist caps')]:
        draw.text((x,8),label,fill='white')
    def paste(im,x,y,s):
        enlarged = im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST)
        sheet.paste(enlarged,(x,y),enlarged)
    sets = {}
    for row,(directory,name,material) in enumerate([
        ('armor-tyr-whole-20261112','tyr','TYR'),
        ('armor-draco-whole-20261112','draco_arcanus','DRACO_ARCANUS'),
    ]):
        base = ART/directory
        prov = read(base/'provenance.json')
        bindings = read(base/'static-bindings.json')
        src = base/'source'
        archive = Path(prov['archive'])
        assert sha(archive.read_bytes()) == prov['archive_sha256']
        y = 48+row*165
        draw.text((8,y),name,fill='white')
        checked = {}
        with zipfile.ZipFile(archive) as z:
            def verify(p):
                r = str(p.relative_to(src))
                data = p.read_bytes()
                assert data == z.read(prov['root']+r)
                assert sha(data) == prov['entries'][r]
                checked[str(p.relative_to(ROOT))] = sha(data)
                return data
            reg = next(src.rglob('ModItems.java'))
            mat = next(src.rglob('ModArmorMaterials.java'))
            reg_data = verify(reg).decode()
            assert f'{material}("{name}"' in verify(mat).decode()
            for i,slot in enumerate(('helmet','chestplate','leggings','boots')):
                ident = f'{name}_{slot}'
                declaration, = (s for s in bindings['actual_registration_declarations'] if f'"{ident}"' in s)
                assert declaration in reg_data and f'ModArmorMaterials.{material}, ArmorItem.Type.{slot.upper()}' in declaration
                model, = (r for r in bindings['models'] if Path(r['model']).stem==ident)
                assert json.loads(verify(Path(model['model'])))['textures']['layer0']==f'forbidden_arcanus:item/armor/{ident}'
                texture = Path(model['texture'])
                verify(texture)
                paste(Image.open(texture).convert('RGBA'),202+i*54,y,3)
            atlases = [next(src.rglob(f'{name}_layer_{i}.png')) for i in (1,2)]
            for p in atlases: verify(p)
        images = [Image.open(p).convert('RGBA') for p in atlases]
        assert all(im.size==(64,32) for im in images)
        targets=[(1,'head','NORTH',435,y),(1,'hat','NORTH',530,y),
                 (2,'body','NORTH',630,y),(2,'body','SOUTH',730,y),(2,'body','WEST',830,y),
                 (2,'body','EAST',885,y),(2,'body','DOWN',965,y),(2,'body','UP',965,y+40)]
        crops={}
        for layer,part,direction,x,cy in targets:
            rect=uv[part][direction]
            im=images[layer-1]
            paste(im.crop(rect),x,cy,7)
            mask=masks(im,rect)
            crops[f'L{layer}/{part}/{direction}']={'rect':rect,'row_opaque_counts':[r.count('#') for r in mask],'visible_mask':mask}
        head=crops['L1/head/NORTH']['visible_mask']
        hat=crops['L1/hat/NORTH']['visible_mask']
        common=[sum(a==b=='.' for a,b in zip(h,o)) for h,o in zip(head,hat)]
        sets[name]={'source_commit':prov['commit'],'assets_verified':checked,'crops':crops,
                    'coindexed_clear_pixels_by_row':common,'coindexed_mask_not_projected_occlusion':True}
    sheet.save(OUT/'ceremonial-face-waist-source.png')
    (OUT/'reference-delta.json').write_text(json.dumps({'sets':sets,'uv_basis':str(record.relative_to(ROOT)),
        'uv_basis_sha256':sha(record.read_bytes()),'new_design_credit':0},indent=2)+'\n')
    for name,entry in sets.items():
        print(name,entry['coindexed_clear_pixels_by_row'],{k:v['row_opaque_counts'] for k,v in entry['crops'].items()})

if __name__=='__main__':
    main()
