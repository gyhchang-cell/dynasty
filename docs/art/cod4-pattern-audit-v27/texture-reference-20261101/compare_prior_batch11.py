"""Reopen historical item icons; no alias/name match is a visual acceptance."""
from pathlib import Path
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[3]
B=R/'build/art-reference-20261101/prior-comparison-batch11';B.mkdir(parents=True,exist_ok=True)
prior=[]
for f in ['armor-vanilla-v23','armor-imperial-v24']:
    index=f'docs/art/{f}/research/index.json'
    prior += [{**r,'prior_index':index} for r in json.loads((R/index).read_text())]
current={r['reference_id']:r for r in json.loads((D/'review-batch-11.json').read_text())['rows']}
cases=[
('iceandfire','armor_amythest_chestplate',363),('iceandfire','armor_copper_metal_chestplate',373),
('iceandfire','deathworm_red_chestplate',375),('iceandfire','dragonsteel_fire_chestplate',381),
('iceandfire','tide_blue_chestplate',401),('iceandfire','forest_troll_leather_chestplate',416),
('iceandfire','myrmex_desert_chestplate',426),('iceandfire','sheep_chestplate',430),
('alexscaves','darkness_chestplate',432),('alexscaves','diving_chestplate',434),
('alexscaves','primordial_helmet',440),('alexscaves','polarity',443),
('alexsmobs','centipede_leggings',445),('alexsmobs','crocodile_chestplate',446),
('alexsmobs','emu_leggings',447),('alexsmobs','flying_fish_boots',449),
('alexsmobs','frontier_cap',450),('alexsmobs','froststalker_helmet',451),
('alexsmobs','rocky_chestplate',455),('alexsmobs','spiked_turtle_shell',458),
('alexsmobs','unsettling_kimono',460),('cataclysm','bloom_stone_pauldrons',461),
('cataclysm','bone_reptile_chestplate',462),('cataclysm','cursium_chestplate',463),
('cataclysm','ignitium_chestplate',465),('cataclysm','monstrosity_helmet',468)]
rows=[];hashes={}
for ns,name,n in cases:
    cur=current[f'VIS-{n:03}']
    old=next((r for r in prior if f'assets/{ns}/textures/' in r['entry'] and Path(r['entry']).name==name+'.png' and Path(r['jar']).is_file()),None)
    row={'case':f'{ns}:{name}','current_reference':cur['reference_id'],'current_png':cur['local_path'],
        'status':'PRIOR_ICON_NOT_FOUND','new_case_credit':0}
    if old:
        jar=old['jar']
        if jar not in hashes:hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
        with zipfile.ZipFile(jar) as z:data=z.read(old['entry'])
        assert hashlib.sha256(data).hexdigest()==old['sha256']
        target=B/(ns+'__'+name+'.png');target.write_bytes(data);Image.open(target).verify()
        row.update(prior=old,prior_jar_sha256=hashes[jar],prior_local_png=str(target.relative_to(R)),
            status='PAIRED_SOURCES_NOT_YET_MANUALLY_COMPARED')
    rows.append(row)
for lo in range(0,len(rows),6):
    page=Image.new('RGB',(1440,1080),'#454b50');dr=ImageDraw.Draw(page)
    dr.text((8,8),'HISTORICAL ICON vs CURRENT SOURCE ATLAS / VISUAL SEMANTIC PAIRING / NOT GAME OR NEW DESIGNS',fill='white')
    sheet=B/f'compare-{lo//6+1:02}.png'
    for i,row in enumerate(rows[lo:lo+6]):
        x=(i%2)*720;y=40+(i//2)*345
        dr.text((x+8,y),row['case']+' / '+row['current_reference'],fill='white')
        for col,k in enumerate(['prior_local_png','current_png']):
            if k not in row:continue
            im=Image.open(R/row[k]).convert('RGBA');factor=max(1,min(330//im.width,270//im.height))
            im=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST);page.paste(im,(x+8+350*col,y+25),im)
        if 'prior_local_png' not in row:dr.text((x+8,y+100),'PRIOR ICON UNAVAILABLE',fill='white')
        dr.text((x+8,y+310),'old icon                           actual wearable atlas',fill='white')
        row['comparison_sheet']=str(sheet.relative_to(R))
    page.save(sheet)
(D/'prior-batch11-pairs.json').write_text(json.dumps({'purpose':'Visual dedup of equipment case, not PNG-file credit', 'new_credit':0,'rows':rows},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pairs':len(rows),'prior_icons_available':sum('prior_local_png' in r for r in rows),'not_found':[r['case'] for r in rows if 'prior_local_png' not in r]}))
