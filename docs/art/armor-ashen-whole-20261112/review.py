"""Read-only reference study: no production assets and no external Java execution."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw

B = Path(__file__).resolve().parent
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, v):
    (B/n).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n')

prov = json.loads((B/'provenance.json').read_text())
assert sha(B/'embers-fixed-source.zip') == prov['archive_sha256']
z = zipfile.ZipFile(B/'embers-fixed-source.zip')
prefix = z.namelist()[0]
entries = {}
for p in sorted((B/'source').rglob('*')):
    if p.is_file():
        rel = p.relative_to(B/'source').as_posix()
        assert p.read_bytes() == z.read(prefix+rel), rel
        entries[rel] = sha(p)
save('verified-source-entries.json', entries)
J = B/'source/src/main/java/com/rekindled/embers'
model = (J/'model/AshenArmorModel.java').read_text()
registry = (J/'RegistryManager.java').read_text()
main = (J/'Embers.java').read_text()
assert 'AshenArmorModel.init(context)' in (J/'entity/render/AncientGolemRenderer.java').read_text()
assert 'AncientGolemRenderer::new' in main
assert 'extends AshenArmorItem' in (J/'item/AshenArmorGemItem.java').read_text()
assert 'consumer.accept(AshenArmorModel.ARMOR_MODEL_GETTER)' in (J/'item/AshenArmorItem.java').read_text()
ids = dict(zip(['ashen_goggles','ashen_cloak','ashen_leggings','ashen_boots'],['HELMET','CHESTPLATE','LEGGINGS','BOOTS']))
bindings = []
for name, slot in ids.items():
    line = next(l.strip() for l in registry.splitlines() if 'ITEMS.register("'+name+'"' in l)
    assert 'ArmorItem.Type.'+slot in line and 'new AshenArmorGemItem(' in line
    p = B/f'source/src/generated/resources/assets/embers/models/item/{name}.json'
    declaration = json.loads(p.read_text())
    tex = declaration['textures']['layer0']
    namespace, path = tex.split(':')
    png = B/f'source/src/main/resources/assets/{namespace}/textures/{path}.png'
    assert Image.open(png).size == (16,16)
    bindings.append(dict(id='embers:'+name, slot=slot, registration=line, item_model=str(p.relative_to(B)), texture=str(png.relative_to(B)), texture_sha256=sha(png)))
atlas = Image.open(B/'source/src/main/resources/assets/embers/textures/models/armor/robe.png').convert('RGBA')
assert atlas.size == (64,64)
all_parts = {}
for slot, expected in [('Head',15),('Chest',18),('Legs',4),('Feet',4)]:
    assert f'LayerDefinition.create(AshenArmorModel.create{slot}Mesh(), 64, 64)' in main
    section = model.split(f'public static MeshDefinition create{slot}Mesh() {{')[1].split('return mesh;')[0]
    cubes = []
    for match in re.finditer(r'(\w+)\.addOrReplaceChild\("([^"]+)",\s*(.*?);', section, re.S):
        parent, name, body = match.groups()
        box = re.search(r'\.addBox\(([^)]*)\)',body)
        if not box:
            continue
        fields = [v.strip() for v in box[1].split(',')]
        xyzwhd = [float(v.rstrip('fF')) for v in fields[:6]]
        u,v = map(int,re.search(r'texOffs\((\d+),\s*(\d+)\)',body).groups())
        w,h,d = map(int,xyzwhd[3:])
        rects = {'DOWN':[u+d,v,u+d+w,v+d], 'UP':[u+d+w,v+d,u+d+2*w,v], 'WEST':[u,v+d,u+d,v+d+h], 'NORTH':[u+d,v+d,u+d+w,v+d+h], 'EAST':[u+d+w,v+d,u+d+w+d,v+d+h], 'SOUTH':[u+d+w+d,v+d,u+2*d+2*w,v+d+h]}
        assert all(0<=a<=64 for r in rects.values() for a in r)
        inflate = (0.01 if slot=='Head' else 0.1) if len(fields)>6 else 0
        cubes.append(dict(parent=parent,name=name,origin=xyzwhd[:3],size=xyzwhd[3:],uv=[u,v],signed_raw_box_rects=rects,inflate=inflate,source_expression=match[0]))
    assert len(cubes)==expected, (slot,len(cubes))
    all_parts[slot]=cubes
    sheet=Image.new('RGB',(1200,len(cubes)*96+30),(80,85,89)); draw=ImageDraw.Draw(sheet)
    draw.text((8,8),f'{slot} native raw box face crops; not baked orientation / not game',(255,255,255))
    for i,c in enumerate(cubes):
        y=30+i*96;draw.text((8,y),c['name'],(255,255,255))
        for k,(face,r) in enumerate(c['signed_raw_box_rects'].items()):
            x=180+k*165; draw.text((x,y),face,(255,255,255))
            x1,y1,x2,y2=r
            crop=atlas.crop((min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)))
            factor=min(8,130//crop.width,70//crop.height)
            crop=crop.resize((crop.width*factor,crop.height*factor),Image.Resampling.NEAREST)
            sheet.paste(crop,(x,y+18),crop)
    sheet.save(B/f'raw-faces-{slot.lower()}.png')
save('geometry-and-raw-uv.json',dict(atlas_size=[64,64],slots=all_parts,cubes=41,raw_rectangles=246,baked_orientation_accepted=False,notes='Signed net rectangles only; no manual world-face or runtime visibility claim.'))
save('static-bindings.json',dict(native_items=bindings,model_initialization='Embers.registerRenderers → AncientGolemRenderer constructor → AshenArmorModel.init(context)',layers='Embers.registerLayerDefinitions; four 64x64 meshes',wear_texture='embers:textures/models/armor/robe.png',gems='AshenArmorGemItem.attachGem stores gemN; model checks gem0..6 only on cloak; these are not separate designs',runtime_accepted=False))
print(json.dumps(dict(source_entries=len(entries),native_items=len(bindings),cubes=41,raw_rectangles=246),ensure_ascii=False))
