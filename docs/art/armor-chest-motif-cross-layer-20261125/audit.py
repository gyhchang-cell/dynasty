"""Verify the old generated chest motif is reachable from the leggings slot."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ART = ROOT / 'docs/art'
BASE = ART / 'armor-current-bindings-20261113'
SCOPE = ART / 'armor-open-face-waist-20261120/five-set-uv-scope.json'
ORIGINS = ART / 'armor-original-uv-20261120/origin-comparison.json'
REGISTRY = ART / 'armor-registered-coverage-20261120/registered-armor-audit.json'
FRONT = (20, 20, 28, 32)
MOTIF = (21, 23, 27, 29)
ABOVE_WAIST_MOTIF = (21, 23, 27, 27)

def read(path):
    return json.loads(path.read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def digest(path):
    return sha(path.read_bytes())

def location(path):
    return str(path.relative_to(ROOT))

def proof(path):
    return {'path': location(path), 'sha256': digest(path)}

def image(path):
    with Image.open(path) as im:
        return im.convert('RGBA')

def coords(box):
    left, top, right, bottom = box
    return [(u, v) for v in range(top, bottom) for u in range(left, right)]

def main():
    pinned = read(BASE/'consumer-provenance.json')
    sources = {}
    for key in ('HumanoidArmorLayer', 'HumanoidModel', 'ForgeHooksClient', 'IClientItemExtensions'):
        rel, = [n for n in pinned['entries'] if n.endswith('/'+key+'.java')]
        f = BASE/'consumer'/rel
        assert digest(f) == pinned['entries'][rel]
        sources[key] = f
    armor_layer = sources['HumanoidArmorLayer'].read_text()
    assert re.search(r'renderArmorPiece\([^\n]*EquipmentSlot\.LEGS',armor_layer)
    assert 'getItemBySlot(p_117122_)' in armor_layer
    assert 'case LEGS:\n            p_117126_.body.visible = true;' in armor_layer
    assert 'return p_117129_ == EquipmentSlot.LEGS;' in armor_layer
    assert 'usesInnerModel(slot) ? 2 : 1' in armor_layer
    assert 'texOffs(16, 16).addBox(-4.0F, 0.0F, -2.0F, 8.0F, 12.0F, 4.0F' in sources['HumanoidModel'].read_text()
    gear = ROOT/'src/main/java/com/dynasty/DynastyGear.java'
    assert not re.search(r'getArmorTexture|getHumanoidArmorModel|initializeClient',gear.read_text())

    s = read(SCOPE)
    uv_file = ROOT/s['contract']
    assert digest(uv_file) == s['contract_sha256']
    uv = read(uv_file)
    assert 'body' in uv['slot_parts']['LEGS']
    origins = read(ORIGINS)
    generator_commit, = origins['generator_hashes']
    generator_paths = ['gen_armor_layers.py','gen_dynasty3.py','gen_armor2.py','gen_armor3.py']
    for generator in generator_paths:
        data = subprocess.check_output(['git','show',f'{generator_commit}:tools/art/{generator}'],cwd=ROOT)
        assert sha(data) == origins['generator_hashes'][generator_commit][generator]
        if generator in generator_paths[:2]:
            assert b'range(23, 29)' in data and b'range(21, 27)' in data
    registry = read(REGISTRY)
    registry_items = registry['families']
    src_atlases = registry['worn_atlases']
    sheet = Image.new('RGB',(900,685),'#53595c')
    draw = ImageDraw.Draw(sheet)
    for x,title in [(9,'LEGS item'),(225,'L1 body front'),(360,'L2 body front'),(495,'L1 motif'),(610,'L2 motif'),(730,'L2 above V=27')]:
        draw.text((x,10),title,fill='white')
    def paste_crop(im, box, x, y):
        cut = im.crop(box)
        enlarged = cut.resize((cut.width*8,cut.height*8),Image.Resampling.NEAREST)
        sheet.paste(enlarged,(x,y),enlarged)

    rows = {}
    for i,(family,data) in enumerate(s['family_scopes'].items()):
        chest, = [r for r in registry_items[family] if r['slot']=='CHESTPLATE']
        legs, = [r for r in registry_items[family] if r['slot']=='LEGGINGS']
        assert (chest['layer'],legs['layer']) == (1,2)
        assert (chest['material'],legs['material']) == (f'dynasty:{family}',)*2
        first,second = [ROOT/r['worn_atlas'] for r in (chest,legs)]
        for path in (first,second):
            origin, = [r for r in origins['rows'] if r['path']==location(path)]
            assert digest(path) == src_atlases[location(path)]['sha256'] == origin['current_sha256']
            assert origin['founding_generator_pixel_match'][generator_commit]
        scope, = [r for r in data['uv_work'] if r['target_slot']=='LEGGINGS']
        assert scope['atlas']==location(second) and scope['target_ids']==[legs['id']]
        assert scope['editable_uv_bounds']['NORTH']==list(FRONT)
        assert scope['clear_upper_torso_baseline']['NORTH']==[20,20,28,27]
        l1,l2 = image(first),image(second)
        a,b = ([im.getpixel(p) for p in coords(MOTIF)] for im in (l1,l2))
        same = sum(p==q for p,q in zip(a,b))
        opaque = sum(p[3]==255 for p in b)
        high = sum(l2.getpixel(p)[3]==255 for p in coords(ABOVE_WAIST_MOTIF))
        assert (same,opaque,high)==(36,36,24)
        assert all(l2.getpixel((u,v))[3]==255 for u,v in coords(FRONT))
        y = 37+i*128
        draw.text((9,y+14),legs['id'],fill='white')
        for im,box,x in [(l1,FRONT,225),(l2,FRONT,360),(l1,MOTIF,495),(l2,MOTIF,610),(l2,ABOVE_WAIST_MOTIF,730)]:
            paste_crop(im,box,x,y)
        rows[family] = {'chest_item':chest['id'],'leggings_item':legs['id'],'layer_1':proof(first),'layer_2':proof(second),
            'torso_front_uv_half_open':FRONT,'generator_chest_motif_uv_half_open':MOTIF,
            'above_waist_motif_uv_half_open':ABOVE_WAIST_MOTIF,'layer_2_front_opaque_pixels':96,
            'motif_identical_rgba_pixels':same,'layer_2_motif_opaque_pixels':opaque,'motif_opaque_above_waist':high}
    assert len(rows)==5
    sheet.save(OUT/'chest-motif-layer-comparison.png')
    (OUT/'slot-coordinate-evidence.json').write_text(json.dumps({'coordinates':'zero-based UV rectangles [u0,v0,u1,v1), PNG top-left',
         'forge_version':pinned['version'],'forge_sources':{k:proof(f) for k,f in sources.items()},
         'dynasty_gear':proof(gear),'registry':proof(REGISTRY),'scope':proof(SCOPE),'uv_contract':proof(uv_file),
         'generator_commit':generator_commit,'origin_receipt':proof(ORIGINS),'rows':rows,
         'scope_limit':'static default asset path; final visibility, local overrides, and player instance untested',
         'reference_credit':0,'gate_met':False},ensure_ascii=False,indent=2)+'\n')
    print({k:(v['leggings_item'],v['motif_identical_rgba_pixels'],v['motif_opaque_above_waist']) for k,v in rows.items()})

if __name__=='__main__':
    main()
