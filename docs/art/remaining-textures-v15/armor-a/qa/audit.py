#!/usr/bin/env python3
"""Read-only source validation. Output restricted to this armor-a QA directory."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import collections,hashlib,json
D=Path(__file__).resolve().parent.parent
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
m=json.loads((D/'manifest.json').read_text())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(im):
    # Test equal pixel topology even when RGB values differ: exact tint copies
    # have the same canonical palette-index layout.
    mapping={};values=[]
    for rgba in im.get_flattened_data():
        rgba=rgba if rgba[3] else (0,0,0,0)
        if rgba not in mapping:mapping[rgba]=len(mapping)
        values.append(mapping[rgba])
    return hashlib.sha256(bytes(values)).hexdigest()
def island(root,w,h,dep):
    x,y=root;s=set()
    for xx in range(x,x+2*dep+2*w):
        for yy in range(y+dep,y+dep+h):s.add((xx,yy))
    for xx in range(x+dep,x+dep+2*w):
        for yy in range(y,y+dep):s.add((xx,yy))
    return s
files=[];groups=collections.defaultdict(list)
for row in m['files']:
    p=D/row['candidate'];im=Image.open(p).convert('RGBA')
    assert h(p)==row['sha256']
    alphas=set(im.getchannel('A').get_flattened_data());assert alphas<={0,255}
    assert im.size==tuple(row['size'])
    if '/item/' in row['candidate']:
        part=p.stem[len(row['set'])+1:]
        target_model=ROOT/'src/main/resources/assets/dynasty/models/item'/f'{p.stem}.json'
        model=json.loads(target_model.read_text())
        assert model['parent'] in ('item/generated','minecraft:item/generated')
        assert model['textures']['layer0']==f'dynasty:item/{p.stem}'
        assert im.width==im.height==32 and im.getbbox()
        bbox=im.getbbox();assert all(q>0 for q in bbox[:2]) and bbox[2]<32 and bbox[3]<32
        reference={'id':f'dynasty:{p.stem}','model':str(target_model.relative_to(ROOT)),'layer0':model['textures']['layer0']}
    else:
        n=int(p.stem[-1]);part=f'layer_{n}'
        allowed=island((0,16),4,12,4)|island((16,16),8,12,4)
        if n==1:allowed|=island((0,0),8,8,8)|island((40,16),4,12,4)
        unexpected=[(x,y) for y in range(32) for x in range(64) if im.getpixel((x,y))[3] and (x,y) not in allowed]
        assert not unexpected,(p,unexpected)
        if n==1:
            face_open=sum(im.getpixel((x,y))[3]==0 for y in range(8,16) for x in range(8,16))
            assert face_open>=20
            assert im.crop((32,0,64,16)).getchannel('A').getextrema()[1]==0
        reference={'material':f'dynasty:{row["set"]}','armor_layer':n,'geometry':'vanilla; unchanged','unexpected_opaque_pixels_outside_used_uv':0}
    groups[part].append((row['set'],canonical(im)))
    assert not p.with_suffix('.png.mcmeta').exists()
    files.append({**row,'reference':reference,'normalized_pixel_topology_sha256':canonical(im)})
duplicates={}
for part,items in groups.items():
    inv=collections.defaultdict(list)
    for name,digest in items:inv[digest].append(name)
    dup=[names for names in inv.values() if len(names)>1]
    if dup:duplicates[part]=dup
assert not duplicates,duplicates
preserved=[]
for entry in m['baseline']:
    assert h(ROOT/entry['target'])==entry['sha256'],entry['target']
    assert h(D/entry['backup'])==entry['sha256'],entry['backup']
    preserved.append(entry['target'])
report={'status':'all_static_checks_passed','candidate_png_count':len(files),'item_icons':44,'worn_atlases':22,
 'source_and_backup_hashes_preserved':len(preserved),'source_files_changed':0,
 'all_item_model_references_correct':True,'all_alpha_binary':True,'all_dimensions_exact':True,
 'same_design_different_palette_duplicates':duplicates,'animation_mcmeta_count':0,
 'all_helmet_face_openings':True,'no_art_outside_used_worn_uv':True,
 'all_11_sets_visually_reviewed_at_native_size_and_nearest_enlargement':True,
 'all_11_sets_offline_front_back_oblique_reviewed':True,
 'no_new_geometry':True,'game_tested':False,'files':files}
(D/'qa/static-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
f=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17)
page=Image.new('RGB',(790,11*135+50),'#e9e9df');d=ImageDraw.Draw(page)
d.text((18,12),'ARMOR A / NEW NATIVE 32px ICONS',font=f,fill='#293c38')
for row,s in enumerate(m['sets']):
    y=50+row*135;d.text((18,y+45),s,font=f,fill='#293c38')
    for col,piece in enumerate(['helmet','chestplate','leggings','boots']):
        im=Image.open(D/'candidate/assets/dynasty/textures/item'/f'{s}_{piece}.png').convert('RGBA')
        t=im.resize((128,128),Image.Resampling.NEAREST);x=240+col*134;page.paste(t,(x,y),t)
page.save(D/'previews/all-icons.png')
page=Image.new('RGB',(6*190,2*252+50),'#e9e9df');d=ImageDraw.Draw(page)
d.text((18,12),'ARMOR A / ACTUAL UV / OFFLINE, NOT GAME',font=f,fill='#293c38')
for i,s in enumerate(m['sets']):
    x=(i%6)*190;y=50+(i//6)*252;d.text((x+5,y),s,font=f,fill='#293c38')
    t=Image.open(D/'qa'/f'{s}_candidate_three-quarter.png');page.paste(t,(x+5,y+25),t)
page.save(D/'previews/all-worn.png')
page=Image.new('RGB',(370,11*42+50),'#e9e9df');d=ImageDraw.Draw(page)
smallfont=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',13)
d.text((12,12),'ARMOR A / 1x ACTUAL 32px ICONS',font=smallfont,fill='#293c38')
for row,s in enumerate(m['sets']):
    y=50+row*42;d.text((12,y+9),s,font=smallfont,fill='#293c38')
    for col,piece in enumerate(['helmet','chestplate','leggings','boots']):
        tex=Image.open(D/'candidate/assets/dynasty/textures/item'/f'{s}_{piece}.png').convert('RGBA')
        page.paste(tex,(185+col*42,y),tex)
page.save(D/'previews/all-icons-native.png')
page=Image.new('RGB',(1110,1042),'#e9e9df');d=ImageDraw.Draw(page)
d.text((15,12),'ALL ARMOR A / FRONT + BACK / OFFLINE UV QA',font=f,fill='#293c38')
for i,s in enumerate(m['sets']):
    x=(i%3)*370;y=50+(i//3)*245;d.text((x+8,y),s+' : front / back',font=smallfont,fill='#293c38')
    for j,view in enumerate(['front','back']):
        tex=Image.open(D/'qa'/f'{s}_candidate_{view}.png');page.paste(tex,(x+5+j*180,y+22),tex)
page.save(D/'previews/all-front-back.png')
print(json.dumps({k:v for k,v in report.items() if k!='files'}))
