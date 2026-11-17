"""Pinned source water/ring/trail/crack texture study; numbered stages are one family."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
prior=[r for p in OUT.glob('review-batch-*.json') for r in json.loads(p.read_text())['rows']]
seen={(r['jar'],r['path']) for r in prior if r.get('jar') and r.get('path')};base=json.loads((OUT/'batch-18-candidates.json').read_text())['rows']
jars=list(dict.fromkeys(r['jar'] for r in base));rows=[];already=[]
for jar in jars:
 name=Path(jar).name
 with zipfile.ZipFile(jar) as z:
  if 'alexscaves-' in name:
   entries=[n for n in z.namelist() if n.endswith('.png') and any(t in n for t in ['/textures/entity/deep_one/water_bolt','/textures/entity/deep_one/wave_','/textures/particle/water_tremor_','/textures/particle/trail.','/textures/particle/trail_mirrored.','/textures/particle/teletor_trail.'])]
  elif 'Cataclysm-' in name:
   entries=[n for n in z.namelist() if n.endswith('.png') and any(t in n for t in ['/textures/entity/ignis/ignis_armor_crack','/textures/entity/ignis/ignis_shield_crack','/textures/entity/sea/spear/water_spear_','/textures/entity/sea/wave/wave_','/textures/particle/ring_','/textures/particle/shock_wave.','/textures/entity/flame_strike_sigil.','/textures/entity/soul_flame_strike_sigil.','/textures/entity/void_rune.'])]
  elif 'goety-2.' in name:
   entries=[n for n in z.namelist() if n.endswith('.png') and (n.startswith('assets/goety/textures/entity/water_jet/') or n.startswith('assets/goety/textures/entity/projectiles/slash/') or n in ['assets/goety/textures/entity/projectiles/'+s+'.png' for s in ['trail','minor_trail','pointed_trail','solid_trail']] or n.startswith('assets/goety/textures/particle/crack_'))]
  else:continue
  sha=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
  for entry in sorted(entries):
   if (jar,entry) in seen:already.append(dict(jar=jar,path=entry));continue
   data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA');dst=RAW/'local-batch22'/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
   rows.append(dict(reference_id=f'VIS-{832+len(rows):03}',repo=name,path=entry,jar=jar,jar_sha256=sha,local_path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0))
sheets(rows,prefix='batch22')
(OUT/'batch-22-candidates.json').write_text(json.dumps(dict(policy='Water/ring/trail/armor crack reference PNGs only. Same family numbered states, overlay and mirrored variants merge; no inference of Java/render UV or animation order.',preexisting_exact_entries_skipped=already,rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(count=len(rows),exact_prior_skips=len(already),rows=[(r['reference_id'],r['path'],r['dimensions']) for r in rows]),ensure_ascii=False))
