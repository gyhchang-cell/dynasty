"""Read-only extraction of prior-study icons to compare the SAME armor case with current atlases."""
from pathlib import Path
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw

D=Path(__file__).resolve().parent
R=D.parents[3]
B=R/'build/art-reference-20261101/prior-comparison'
B.mkdir(parents=True,exist_ok=True)
indices=[R/'docs/art/armor-vanilla-v23/research/index.json',R/'docs/art/armor-imperial-v24/research/index.json']
prior=[]
for p in indices:
    for row in json.loads(p.read_text()):
        prior.append({**row,'prior_index':str(p.relative_to(R))})
current=[]
for name in ['review-batch-01.json','review-batch-04.json']:
    current.extend(json.loads((D/name).read_text())['rows'])
PAIRS=[('irons_spellbooks','archevoker',20),('irons_spellbooks','cryomancer',23),
       ('irons_spellbooks','pyromancer',32),('irons_spellbooks','shadowwalker',33),
       ('irons_spellbooks','paladin',29),('enigmaticlegacy','crying',72),
       ('aether','valkyrie',122),('aether','neptune',115),('aether','gravitite',113),
       ('immersiveengineering','faraday',80),('create','cardboard',84),
       ('create','copper_diving',86),('create','netherite_diving',88),
       ('goety','cursed_paladin',143),('botania','manasteel',17),
       ('botania','terrasteel',19),('botania','manaweave',18)]
rows=[];jar_hashes={}
for ns,key,num in PAIRS:
    found=[r for r in prior if f'assets/{ns}/textures/' in r['entry'] and Path(r['entry']).stem.startswith(key+'_') and '/unused/' not in r['entry']]
    # Chest preferred: material hierarchy is more visible than an isolated boot.
    found.sort(key=lambda r:(not any(k in Path(r['entry']).stem for k in ['chestplate','robe']),'/packs/' in r['entry'],r['entry']))
    old=next((r for r in found if Path(r['jar']).is_file()),None)
    cur=next(r for r in current if r['reference_id']==f'VIS-{num:03}')
    item={'case':ns+':'+key,'current_reference':cur['reference_id'],'current_png':cur['local_path'],
          'status':'PENDING_LOCAL_PRIOR_SOURCE','new_case_credit':0}
    if old:
        try:
            p=Path(old['jar'])
            if str(p) not in jar_hashes:jar_hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
            with zipfile.ZipFile(p) as z:data=z.read(old['entry'])
            if hashlib.sha256(data).hexdigest()!=old['sha256']:raise ValueError('Prior entry no longer matches recorded SHA256')
            dest=B/(ns+'__'+key+'__'+Path(old['entry']).name);dest.write_bytes(data)
            Image.open(dest).verify()
            item.update(status='SOURCE_PAIRED_NOT_YET_VISUALLY_COMPARED',prior=old,
                prior_jar_sha256=jar_hashes[str(p)],prior_local_png=str(dest.relative_to(R)),
                limitation='Inventory icon vs wearable atlas; different revision/source version is not assumed pixel-identical or a new semantic case.')
        except Exception as exc:item['error']=str(exc)
    rows.append(item)
for lo in range(0,len(rows),6):
    page=Image.new('RGB',(1440,1080),'#41474c');dr=ImageDraw.Draw(page)
    dr.text((8,8),'PRIOR STUDY ICON vs CURRENT PINNED ATLAS / SAME CASE / not production or game / ZERO automatic credit',fill='white')
    for i,row in enumerate(rows[lo:lo+6]):
        x=(i%2)*720;y=40+(i//2)*345
        dr.text((x+10,y),row['case']+' / '+row['current_reference'],fill='white')
        for col,k in enumerate(['prior_local_png','current_png']):
            if k not in row:continue
            im=Image.open(R/row[k]).convert('RGBA');factor=max(1,min(330//im.width,270//im.height))
            preview=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)
            page.paste(preview,(x+col*350+10,y+25),preview)
        dr.text((x+10,y+305),'prior icon                          pinned wearable atlas',fill='white')
        row['comparison_sheet']=str((B/f'compare-{lo//6+1:02}.png').relative_to(R))
    page.save(B/f'compare-{lo//6+1:02}.png')
(D/'prior-case-pairs.json').write_text(json.dumps({'purpose':'Actual prior-vs-current same armor case semantic review; file hashes establish provenance only','new_credit':0,'rows':rows},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pairs_prepared':sum('prior_local_png'in r for r in rows),'prior_unavailable':[r['case'] for r in rows if 'prior_local_png' not in r],'new_credit':0}))
