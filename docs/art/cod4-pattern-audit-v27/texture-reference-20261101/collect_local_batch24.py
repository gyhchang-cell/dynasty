"""Existing fixed primary stone-relief surfaces, not building design/counts."""
from pathlib import Path
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
import io,json,hashlib,zipfile
prior=[r for p in OUT.glob('review-batch-*.json') for r in json.loads(p.read_text())['rows']];seen={(r.get('jar'),r.get('path')) for r in prior}
jar=next(r['jar'] for r in prior if 'samurai_dynasty' in r.get('jar',''));sha=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
names=['dragon_spirit_stone_front','dragon_spirit_stone_back','dragon_spirit_stone_left','dragon_spirit_stone_right','dragon_spirit_stone_top','dragon_spirit_stone_bottom','dragon_spirit_stone_block','spirit_stone','chiseled_pattern_spirit_stone_bricks','chiseled_spirit_stone_bricks','mosaic_spirit_stone_bricks','pattern_mossy_spirit_stone_bricks','pattern_spirit_stone_bricks']
rows=[];models=[]
with zipfile.ZipFile(jar) as z:
 for name in names:
  entry='assets/samurai_dynasty/textures/block/'+name+'.png';assert (jar,entry) not in seen
  data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA');dst=RAW/'local-batch24'/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
  rows.append(dict(reference_id=f'VIS-{928+len(rows):03}',repo=Path(jar).name,path=entry,jar=jar,jar_sha256=sha,local_path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
 for entry in ['assets/samurai_dynasty/blockstates/dragon_spirit_stone.json','assets/samurai_dynasty/models/block/dragon_spirit_stone.json','assets/samurai_dynasty/models/block/cube_bottom_top_sides.json','assets/samurai_dynasty/models/block/dragon_spirit_stone_block.json','assets/samurai_dynasty/models/item/dragon_spirit_stone.json']:
  data=z.read(entry);dst=RAW/'local-batch24'/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
  models.append(dict(entry=entry,local_path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),content=json.loads(data)))
sheets(rows,prefix='batch24')
(OUT/'batch-24-candidates.json').write_text(json.dumps(dict(policy='13surface PNGs only,6relief faces oneobject, clean/moss variants merged;0architecture examples, no new model/production.',rows=rows),ensure_ascii=False,indent=2)+'\n')
(OUT/'batch24-primary-model-chain.json').write_text(json.dumps(dict(jar=jar,jar_sha256=sha,models=models,formal_new_credit=0),ensure_ascii=False,indent=2)+'\n')
print('13PNG and5primaryresource JSON prepared, not yet reviewed.')
print(json.dumps(models[2]['content'],ensure_ascii=False))
