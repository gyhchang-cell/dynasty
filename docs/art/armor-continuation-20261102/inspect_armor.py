"""Read current armor and version receipts; write evidence only in this folder."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).resolve().parent
R = D.parents[2]
A = R / 'src/main/resources/assets/dynasty'
SLOTS = ('helmet', 'chestplate', 'leggings', 'boots')
PROTECTED = {'general', 'jade', 'sky', 'bronze', 'xuantian'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads((R / p).read_text())

def png(p):
    with Image.open(p) as im:
        im.load()
        return im.convert('RGBA')

def main():
    rules = R / 'docs/art/USER_TEXTURE_REQUIREMENTS.md'
    global_rules = Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md')
    assert rules.read_bytes() == global_rules.read_bytes(), 'Rule copies differ'
    sets = sorted(p.name.removesuffix('_layer_1.png') for p in (A/'textures/models/armor').glob('*_layer_1.png'))
    gear = R/'src/main/java/com/dynasty/DynastyGear.java'
    code = gear.read_text()
    registered = set(re.findall(r'armor\("([a-z_]+)_(?:helmet|chestplate|leggings|boots)"',code) + re.findall(r'\{"([a-z_]+)", DynastyArmorMaterials\.',code))
    assert registered == set(sets), 'Registered armor families and current atlas families differ'
    targets = [f'dynasty:{s}_{slot}' for s in sets for slot in SLOTS]
    application = '本批只核对28套盔甲的112图标、56穿戴图与112模型绑定；保存原始哈希，保护获选及精致旧稿。v15旧图不算未改；未新增美术，不声称穿戴/实机通过，不改共享Jar和清单。'
    subprocess.run([sys.executable, str(R/'tools/art/snapshot_texture_requirements.py'), '--batch-dir', str(D), '--targets', *targets, '--application', application], check=True, capture_output=True)
    latest = {}
    history_sources = []
    for batch in ('armor-vanilla-v23', 'armor-sacred-v25', 'armor-expansion-v26', 'armor-foundations-v29'):
        f = R/f'docs/art/{batch}/source-check.json'
        history_sources.append({'path':str(f.relative_to(R)), 'sha256':sha(f)})
        for row in json.loads(f.read_text())['items']:
            latest[row['id']] = {'batch':batch, 'sha256':row['sha256']}
    v15 = read('docs/art/remaining-textures-v15/delivery-manifest.json')
    past = {row['source_path']:row for row in v15['files']}
    lang = json.loads((A/'lang/zh_cn.json').read_text())
    rows, errors, baseline = [], [], {}
    legacy = []
    for s in sets:
        row = {'set':s, 'icons':[], 'wearable':[], 'category':'PROTECTED_FINE_OLD' if s in PROTECTED else 'SELECTED_ORIGINAL' if f'{s}_helmet' in latest else 'V15_REDRAW_REVIEW_ONLY'}
        if row['category'] == 'V15_REDRAW_REVIEW_ONLY': legacy.append(s)
        for slot in SLOTS:
            item = f'{s}_{slot}'
            f = A/f'textures/item/{item}.png'
            m = A/f'models/item/{item}.json'
            im = png(f)
            model = json.loads(m.read_text())
            for p in (f,m): baseline[str(p.relative_to(R))] = sha(p)
            current = sha(f)
            old = past.get(str(f.relative_to(R)))
            selected = latest.get(item)
            binding = model.get('original_texture') == f'dynasty:textures/item/{item}.png' if model.get('loader') == 'dynasty:original_item' else model.get('textures',{}).get('layer0') == f'dynasty:item/{item}'
            entry = {'id':f'dynasty:{item}', 'name':lang.get(f'item.dynasty.{item}',item), 'path':str(f.relative_to(R)), 'sha256':current, 'size':list(im.size), 'model':str(m.relative_to(R)), 'model_sha256':sha(m), 'binding_matches':binding, 'v15_matches':current == old['sha256'] if old else None, 'selected':selected, 'selected_matches':current == selected['sha256'] if selected else None, 'alpha_bbox':im.getchannel('A').getbbox()}
            row['icons'].append(entry)
            if not binding or (selected and current != selected['sha256']): errors.append(entry['id'])
            if row['category']=='V15_REDRAW_REVIEW_ONLY' and not entry['v15_matches']: errors.append(f'{item}: unexplained historical difference')
        for layer in (1,2):
            f = A/f'textures/models/armor/{s}_layer_{layer}.png'
            im = png(f)
            old = past.get(str(f.relative_to(R)))
            baseline[str(f.relative_to(R))] = sha(f)
            entry = {'layer':layer, 'path':str(f.relative_to(R)), 'sha256':sha(f), 'size':list(im.size), 'v15_matches':sha(f)==old['sha256'] if old else None, 'status':'NOT_WEARING_OR_SEAM_ACCEPTANCE'}
            row['wearable'].append(entry)
            if im.width*32 != im.height*64: errors.append(f'{s}: bad atlas aspect')
        rows.append(row)
    baseline_path = D/'source-baseline.json'
    if baseline_path.exists():
        assert json.loads(baseline_path.read_text()) == baseline, 'Source changed since this batch began; preserve baseline and review concurrency'
    else:
        baseline_path.write_text(json.dumps(baseline, indent=2)+'\n')
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
    for group in ('V15_REDRAW_REVIEW_ONLY','PROTECTED_FINE_OLD'):
        subset = [r for r in rows if r['category']==group]
        sheet = Image.new('RGB',(980,55+len(subset)*158),(78,83,88))
        dr=ImageDraw.Draw(sheet)
        dr.text((12,8),f'CURRENT SOURCE / {group} / integer nearest enlargement / NOT GAME',font=font,fill='white')
        for i,r in enumerate(subset):
            y=50+i*158
            dr.text((12,y+20),r['set'],font=font,fill='white')
            for j,entry in enumerate(r['icons']):
                im=png(R/entry['path']); factor=4 if im.width==32 else 1
                big=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)
                x=180+j*195
                sheet.paste(big,(x,y),big)
                dr.text((x,y+132),SLOTS[j],font=font,fill='white')
        sheet.save(D/f'{group.lower()}-icons.png')
    uvrows=[r for r in rows if r['category']=='V15_REDRAW_REVIEW_ONLY']
    sheet=Image.new('RGB',(1200,55+len(uvrows)*154),(78,83,88)); dr=ImageDraw.Draw(sheet)
    dr.text((12,8),'CURRENT WORN PNG / nearest x4 / NOT GAME / no icon-to-wear acceptance',font=font,fill='white')
    for i,r in enumerate(uvrows):
        y=50+i*154;dr.text((8,y+20),r['set'],font=font,fill='white')
        for j,entry in enumerate(r['wearable']):
            im=png(R/entry['path'])
            # x4 keeps the full standard 64x32 atlas visible without overlap.
            big=im.resize((256,128),Image.Resampling.NEAREST)
            sheet.paste(big,(200+j*470,y),big)
            dr.text((465+j*470,y+20),f'layer {j+1}',font=font,fill='white')
    sheet.save(D/'v15-current-worn-atlases.png')
    report={'recorded_at':datetime.now(timezone.utc).isoformat(), 'rules_sha256':sha(rules), 'registered_families_source':str(gear.relative_to(R)), 'registered_families_source_sha256':sha(gear), 'counts':{'sets':len(sets),'inventory_icons':len(sets)*4,'wearable_png':len(sets)*2,'model_bindings':len(sets)*4,'selected_original_icons':sum(r['category']=='SELECTED_ORIGINAL' for r in rows)*4,'fine_old_icons':len(PROTECTED)*4,'historically_redrawn_v15_icons':len(legacy)*4},'rows':rows,'historical_sources':history_sources, 'errors':errors,'new_artwork':0,'game_starts':0,'source_mutations':0,'limitations':['Historical hash agreement is not visual approval.','Inventory icons and worn UV are separate.','No seam/wearing/game acceptance; no prompt deletion.']}
    (D/'version-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'counts':report['counts'],'errors':errors,'sheets':3},ensure_ascii=False))
    assert not errors

if __name__=='__main__': main()
