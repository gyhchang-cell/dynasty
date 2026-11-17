"""Pinned local armor atlases; color, tier and overlay are not independent sets."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
jar=Path('/Users/a15356015027/Public/.minecraft/versions/测试/mods/samurai_dynasty-0.0.48-1.20.1-neo.jar')
names=[]
for material in ['blue','red','iron','netherite']:
 for tier in ['light_','master_','']:names.append(f'{material}_samurai_armor_{tier}textures')
names+=['netherite_samurai_armor_textures_mask','amethyst_samurai_armor_textures','amethyst_samurai_armor_textures_mask','amethyst_samurai_armor_textures_new','etyrite_samurai_armor_textures','etyrite_samurai_armor_textures_gray','quartz_samurai_armor_textures','quartz_samurai_armor_textures_mask','kimono_textures','ninja_iron_armor_textures','ninja_gold_armor_textures','ninja_netherite_armor_textures','straw_hat_armor_textures','mask_straw_hat_armor_textures','oni_mask','oni_mask_red','oni_mask_white','kitsune_mask','goggle_create_samurai_armor_textures','mage_samurai_armor_textures','steel_armor_textures','draco_samurai_armor_textures','fiery_samurai_armor_textures','tyr_samurai_armor_textures','ignitium_samurai_armor_textures','living_samurai_armor_textures','neptunium_samurai_armor_textures','sculk_samurai_armor_textures','ironwood_samurai_armor_textures']
entries=['assets/samurai_dynasty/textures/armor/'+n+'.png' for n in names]
entries+=['assets/samurai_dynasty/textures/models/armor/ars_nouveau/ars_samurai_armor_textures_'+c+'.png' for c in ['black','white']]
rows=[];sha=hashlib.sha256(jar.read_bytes()).hexdigest()
with zipfile.ZipFile(jar) as z:
 for entry in entries:
  data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA');dst=RAW/'local-batch20'/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
  rows.append(dict(reference_id=f'VIS-{746+len(rows):03}',repo=jar.name,path=entry,jar=str(jar),jar_sha256=sha,
    local_path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch20')
(OUT/'batch-20-candidates.json').write_text(json.dumps(dict(policy='Actual local armor material atlas source only, no runtime slot/model/tint claims. Same equipment color, tier and mask variants merge, no whole atlas directly called chest appearance.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(count=len(rows),entries=[(r['reference_id'],Path(r['path']).name,r['dimensions']) for r in rows]),ensure_ascii=False))
