"""Supplement native prior-family comparison and explicitly approximate raw UV crops."""
from pathlib import Path
import json,hashlib,zipfile
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2];A=D/'source/src/main/resources/assets/atum'
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert not (D/'raw-context-uv.json').exists()
prov=json.loads((D/'provenance.json').read_text())
with zipfile.ZipFile(prov['archive']) as z:
 root=z.namelist()[0]
 for s in ['helmet','chest','legs','boots']:
  for sub,ext in [('models/item','json'),('textures/item','png')]:
   rel=f'src/main/resources/assets/atum/{sub}/wanderer_{s}.{ext}';entry=root+rel;b=z.read(entry);p=D/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   prov['entries'].append({'entry':entry,'path':str(p.relative_to(D)),'sha256':sha(b),'purpose':'D59 actual referenced Wanderer icons/models comparison'})
save('provenance.json',prov)
out=Image.new('RGB',(880,900),'#555b60');dr=ImageDraw.Draw(out);dr.text((8,8),'NATIVE WHOLE ICON FAMILY COMPARISON / NOT GAME',fill='white')
for j,prefix in enumerate(['wanderer','desert_iron','desert_gold','desert_diamond']):
 for i,s in enumerate(['helmet','chest','legs','boots']):
  ident=f'wanderer_{s}' if prefix=='wanderer' else f'desert_{s}_{prefix.split("_")[1]}'
  p=A/'textures/item'/f'{ident}.png';im=Image.open(p).convert('RGBA')
  # Keep prior/native layers separate: diagnostic composite shown in separate reviewed page.
  im=im.resize((160,160),Image.Resampling.NEAREST);out.paste(im,(i*220+30,j*218+35),im);dr.text((i*220+10,j*218+202),ident,fill='white')
out.save(D/'prior-native-icons.png')
ctxpath=R/'docs/art/armor-mortem-whole-20261112/raw-standard-uv.json';ctx=json.loads(ctxpath.read_text());parts={}
for row in ctx['rows']:
 for p in row['parts']:parts.setdefault(p['part'],p['rectangles'])
save('raw-context-uv.json',{'source':str(ctxpath),'sha256':sha(ctxpath.read_bytes()),'parts':parts,'exact_neoforge_20_4_232_geometry':False,'face_order':'Raw inherited rectangle order; do not interpret UP/DOWN as anatomical names','runtime_or_seam_acceptance':False})
rows=[]
for part,rects in parts.items():
 # All declared context parts shown. Repeated arm/leg labels remain raw crop diagnostics.
 paths=[A/'textures/models/armor'/f'desert_{m}_armor_{layer}{ov}.png' for m in ['iron','gold','diamond'] for layer in [1,2] for ov in ['', '_overlay']]
 out=Image.new('RGB',(1000,50+len(paths)*92),'#555b60');dr=ImageDraw.Draw(out);dr.text((8,8),f'{part} RAW UV CONTEXT / NOT EXACT GEOMETRY / NOT GAME',fill='white')
 for j,p in enumerate(paths):
  im=Image.open(p).convert('RGBA');dr.text((8,50+j*92),p.stem,fill='white');measure=[]
  for k,rect in enumerate(rects):
   tile=im.crop(rect);measure.append({'bounds':rect,'nonzero_alpha':sum(v>0 for v in tile.getchannel('A').get_flattened_data())})
   tile=tile.resize((tile.width*4,tile.height*4),Image.Resampling.NEAREST);out.paste(tile,(290+k*110,50+j*92),tile);dr.text((290+k*110,50+j*92+58),str(rect),fill='white')
  rows.append({'part':part,'texture':str(p.relative_to(D)),'rectangles':measure})
 out.save(D/f'raw-{part}.png')
save('raw-uv-alpha.json',rows)
cross=[]
for category in ['item','models/armor']:
 names=([f'desert_{s}_{{}}{ov}.png' for s in ['helmet','chest','legs','boots'] for ov in ['', '_overlay']] if category=='item' else [f'desert_{{}}_armor_{layer}{ov}.png' for layer in [1,2] for ov in ['', '_overlay']])
 for pattern in names:
  images=[Image.open(A/'textures'/category/pattern.format(m)).convert('RGBA') for m in ['iron','gold','diamond']]
  cross.append({'pattern':pattern,'category':category,'same_alpha_all_three':len({im.getchannel('A').tobytes() for im in images})==1,'same_RGBA_all_three':len({im.tobytes() for im in images})==1})
save('material-variant-dedup.json',{'rows':cross,'credit_policy':'Three material variants are at most one pending semantic family; compare against earlier Wanderer family before independent credit.'})
print('Saved prior native icons and raw UV pages:',list(parts))
