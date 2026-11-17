"""Fixed primary 16px spell icons: GUI/symbol readability, never whole armor cases."""
from pathlib import Path
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
import io,json,hashlib,zipfile
prior=[r for p in OUT.glob('review-batch-*.json') for r in json.loads(p.read_text())['rows']]
seen={(r.get('jar'),r.get('path')) for r in prior}
jar=next(r['jar'] for r in prior if 'irons_spellbooks' in r.get('jar',''))
sha=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
names=['counterspell','echoing_strikes','fang_ward','fortify','haste','evasion','planar_sight','lightning_bolt','volt_strike','guiding_bolt','sunbeam','fire_arrow','magic_arrow','poison_arrow','blood_slash','flaming_strike','shadow_slash','frostwave','gust','thunderstorm','blessing_of_life','healing_circle','root','oakskin','divine_smite','electrocute','sonic_boom','summon_swords','ray_of_frost','ray_of_siphoning','heat_surge','shockwave']
rows=[]
with zipfile.ZipFile(jar) as z:
 for name in names:
  entry='assets/irons_spellbooks/textures/gui/spell_icons/'+name+'.png'
  assert (jar,entry) not in seen
  data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA');dst=RAW/'local-batch23'/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
  rows.append(dict(reference_id=f'VIS-{896+len(rows):03}',repo=Path(jar).name,path=entry,jar=jar,jar_sha256=sha,local_path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch23')
(OUT/'batch-23-candidates.json').write_text(json.dumps(dict(policy='Original GUI spell icon readability only. Arrow/color/state variants merge; not source of literal academy identity glyphs, new items or whole equipment references.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(rows),'source PNGs, not yet reviewed.')
