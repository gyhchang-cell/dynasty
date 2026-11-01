"""Local, fixed Goety focus glyphs for direction/guard/command pattern study."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image
from collect import ROOT, OUT, RAW, sheets

names='''arrow_rain barricade blackguard bolting bombardment bulwark call call_active call_type charge command cyclone discharge entangling flying iron_hide launch leaping lightning order razor_wind rotation shocking shockwave soul_armor stellar sword telekinesis thunderbolt thunderstorm trident_storm troop troop_active updraft vanguard whirlwind windblast water_whip tidal surging monsoon'''.split()
jar=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods/[诡厄巫法] goety-2.5.49.3.jar')
jar_sha=hashlib.sha256(jar.read_bytes()).hexdigest()
prior={}
for f in ['docs/art/accessories-mc-v11/references/sources.json','docs/art/armor-vanilla-v23/research/index.json','docs/art/armor-imperial-v24/research/index.json']:
    data=json.loads((ROOT/f).read_text())
    for r in data.get('sources',[]) if isinstance(data,dict) else data:
        prior.setdefault(r['sha256'],[]).append({'index':f,'path':r.get('texture',r.get('entry',r.get('path')))})
rows=[]
with zipfile.ZipFile(jar) as z:
    meta=z.read('META-INF/mods.toml').decode('utf-8',errors='replace')
    for name in names:
        # Active/type postfix comes after spell in the actual archive names.
        entry='assets/goety/textures/item/focus/'+(name.replace('_active','_spell_active').replace('_type','_spell_type') if name.endswith(('_active','_type')) else name+'_spell')+'.png'
        data=z.read(entry); im=Image.open(io.BytesIO(data)).convert('RGBA')
        target=RAW/'local-batch10'/Path(entry).name
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        sha=hashlib.sha256(data).hexdigest()
        rows.append({'reference_id':f'VIS-{322+len(rows):03}','repo':'Goety / local pinned 2.5.49.3 original art',
            'path':entry,'jar':str(jar),'jar_sha256':jar_sha,'archive_metadata_excerpt':meta[:1800],
            'local_path':str(target.relative_to(ROOT)),'sha256':sha,'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),
            'dimensions':list(im.size),'decoded':True,'status':'EXTRACTED_NOT_VIEWED','distinct_family_proposed_credit':0,
            'exact_prior_png_matches_not_semantic_acceptance':prior.get(sha,[])})
sheets(rows,prefix='batch10')
(OUT/'batch-10-candidates.json').write_text(json.dumps({'policy':'Extracted source PNG is not a unique design or accepted target case. Base focus frame, state and recolor must merge.', 'rows':rows},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'raw_pngs':len(rows),'prior_byte_matches':sum(bool(r['exact_prior_png_matches_not_semantic_acceptance']) for r in rows),'sheets':sorted({r['review_sheet'] for r in rows})}))
