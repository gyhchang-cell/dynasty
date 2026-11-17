"""Pinned local archery PNGs. Drawing states, overlays and legacy skins are one design."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
from collect import ROOT,OUT,RAW,sheets
folder=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods')
names=['[Alex 的洞穴] alexscaves-2.0.2.jar','[冰火传说] iceandfire-2.1.13-1.20.1-beta-5.jar',
 '[天境] aether-1.20.1-1.5.2-neoforge.jar','[天境：新生代] aether-redux-2.0.19-1.20.1-neoforge.jar',
 '[暮色森林] twilightforest-1.20.1-4.3.2508-universal.jar','[深入天境] deep_aether-1.20.1-1.1.7.jar',
 '[灾变] L_Enders_Cataclysm-3.16.jar','[诡厄巫法] goety-2.5.49.3.jar',
 '[诡厄巫法：启示录] GoetyRevelation-2.3.1.jar','[诡厄巫法：觉醒] goetyawaken-1.3.4.jar']
prior={}
for f in sorted(OUT.glob('review-batch-*.json')):
 for r in json.loads(f.read_text())['rows']:
  for a in r.get('assets',[r]):prior.setdefault(a['sha256'],r.get('reference_id'))
rows=[]
for name in names:
 jar=folder/name;archive_sha=hashlib.sha256(jar.read_bytes()).hexdigest()
 with zipfile.ZipFile(jar) as z:
  for entry in sorted(n for n in z.namelist() if n.endswith('.png') and '/textures/' in n and '/item' in n
                      and '/focus/' not in n and any(t in Path(n).name for t in ['bow','quiver','arrow']) and 'rainbow' not in n):
   data=z.read(entry);im=Image.open(io.BytesIO(data)).convert('RGBA')
   dst=RAW/'local-batch18'/name/entry;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
   sha=hashlib.sha256(data).hexdigest()
   rows.append(dict(reference_id=f'VIS-{611+len(rows):03}',repo=name,path=entry,jar=str(jar),jar_sha256=archive_sha,
    local_path=str(dst.relative_to(ROOT)),sha256=sha,rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
    dimensions=list(im.size),decoded=True,status='EXTRACTED_NOT_VIEWED',distinct_family_proposed_credit=0,
    earlier_exact_png_reference=prior.get(sha)))
sheets(rows,prefix='batch18')
(OUT/'batch-18-candidates.json').write_text(json.dumps(dict(policy='States, clear/solid layers, projectile variants, built-in legacy packs and overlays do not multiply bow designs. Source art only, no production assets or acceptance.',rows=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(pngs=len(rows),sheets=sorted({r['review_sheet'] for r in rows}),
 dimensions=sorted({tuple(r['dimensions']) for r in rows}),rows=[(r['reference_id'],r['path']) for r in rows]),ensure_ascii=False))
