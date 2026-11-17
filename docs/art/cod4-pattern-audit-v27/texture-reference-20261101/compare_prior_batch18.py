"""One exact historical bow source, never infer novelty from a different pack folder."""
from pathlib import Path
import hashlib,json,zipfile
from PIL import Image,ImageDraw
from collect import ROOT,OUT,RAW

prior_index='docs/art/basic-weapons-thicker-v2/references-300.json'
old=next(r for r in json.loads((ROOT/prior_index).read_text()) if r['path']=='assets/goetyawaken/textures/item/dark_netherite_bow.png')
current=next(r for r in json.loads((OUT/'review-batch-18.json').read_text())['rows'] if r['reference_id']=='VIS-692')
jar=Path(old['archive'])
with zipfile.ZipFile(jar) as z:data=z.read(old['path'])
assert hashlib.sha256(data).hexdigest()==old['sha256']
folder=RAW/'prior-comparison-batch18';folder.mkdir(parents=True,exist_ok=True)
dst=folder/'goetyawaken__dark_netherite_bow.png';dst.write_bytes(data)
page=Image.new('RGB',(620,300),'#454b50');d=ImageDraw.Draw(page)
d.text((12,10),'REFERENCE ONLY / SAME EQUIPMENT / NOT GAME OR NEW DYNASTY ART',fill='white')
for i,(label,path) in enumerate([('CURRENT VIS-692',ROOT/current['local_path']),('HISTORICAL #92',dst)]):
 im=Image.open(path).convert('RGBA');assert im.size==(16,16)
 preview=im.resize((192,192),Image.Resampling.NEAREST);page.paste(preview,(25+i*310,65),preview);d.text((25+i*310,42),label,fill='white')
sheet=folder/'compare.png';page.save(sheet)
row=dict(case='goetyawaken-dark-netherite-bow',current_reference='VIS-692',prior=dict(jar=str(jar),entry=old['path'],sha256=old['sha256'],size=old['size'],prior_index=prior_index),
 prior_jar_sha256=hashlib.sha256(jar.read_bytes()).hexdigest(),prior_local_png=str(dst.relative_to(ROOT)),comparison_sheet=str(sheet.relative_to(ROOT)),
 exact_png_equal=current['sha256']==old['sha256'],status='EXTRACTED_NOT_YET_VISUALLY_COMPARED',accepted_credit=0)
(OUT/'prior-batch18-pairs.json').write_text(json.dumps(dict(rows=[row],new_design_credit=0),ensure_ascii=False,indent=2)+'\n')
print(sheet)
