"""Read-only check of existing effect PNGs and metadata. No shader/Java/runtime claims."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import json,hashlib
from collect import ROOT,OUT,RAW
folder=RAW/'existing-effects';folder.mkdir(parents=True,exist_ok=True)
rows=[]
for name in ['dragon_slayer_decal','guanyu_brocade','tianjiang_stream']:
 p=ROOT/f'src/main/resources/assets/dynasty/textures/effect/{name}.png';data=p.read_bytes();im=Image.open(p).convert('RGBA');pixels=list(im.get_flattened_data());a=im.getchannel('A');copy=folder/p.name;copy.write_bytes(data)
 metadata=None;mp=p.with_name(p.name+'.mcmeta')
 if mp.exists():
  md=mp.read_bytes();saved=folder/mp.name;saved.write_bytes(md);metadata=dict(path=str(mp.relative_to(ROOT)),saved=str(saved.relative_to(ROOT)),sha256=hashlib.sha256(md).hexdigest(),content=json.loads(md))
 border=[im.getpixel((x,0)) for x in range(im.width)]+[im.getpixel((x,im.height-1)) for x in range(im.width)]+[im.getpixel((0,y)) for y in range(im.height)]+[im.getpixel((im.width-1,y)) for y in range(im.height)]
 rows.append(dict(name=name,path=str(p.relative_to(ROOT)),source_sha256=hashlib.sha256(data).hexdigest(),frozen_copy=str(copy.relative_to(ROOT)),dimensions=list(im.size),alpha_bbox=a.getbbox(),nonzero_alpha_pixels=sum(x[3]>0 for x in pixels),partial_alpha_pixels=sum(0<x[3]<255 for x in pixels),visible_rgba_colors=len({x for x in pixels if x[3]}),border_nonzero_samples=sum(x[3]>0 for x in border),edge_samples_include_corners_twice=True,
  left_right_edge_rgba_differences=sum(im.getpixel((0,y))!=im.getpixel((im.width-1,y)) for y in range(im.height)),top_bottom_edge_rgba_differences=sum(im.getpixel((x,0))!=im.getpixel((x,im.height-1)) for x in range(im.width)),metadata=metadata,
  source_animation_section_declared=bool(metadata and 'animation' in metadata['content']),new_reference_credit=0))
# Faithful integer enlargement for two small source PNGs only, not a generated texture.
page=Image.new('RGB',(1100,650),'#454b50');dr=ImageDraw.Draw(page);dr.text((8,8),'EXISTING DYNASTY SOURCE PIXELS / NOT NEW ART OR GAME / INTEGER SCALE',fill='white')
for row,x in zip([rows[0],rows[2]],[12,580]):
 im=Image.open(ROOT/row['frozen_copy']).convert('RGBA');f=16;dr.text((x,34),row['name']+' '+str(im.size)+' x16',fill='white')
 for yy in range(52):
  for xx in range(52):dr.rectangle((x+xx*10,64+yy*10,x+9+xx*10,73+yy*10),fill='#62696e' if (xx+yy)%2 else '#555c61')
 preview=im.resize((im.width*f,im.height*f),Image.Resampling.NEAREST);page.paste(preview,(x,64),preview)
sheet=folder/'small-sources.png';page.save(sheet)
# Resource JSON declaration-only search; absence here is not Java/render absence.
terms=['effect/dragon_slayer_decal','effect/guanyu_brocade','effect/tianjiang_stream'];matches=[]
for p in (ROOT/'src/main/resources').rglob('*.json'):
 text=p.read_text(errors='replace')
 hits=[term for term in terms if term in text]
 if hits:matches.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),terms=hits))
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),purpose='Current effect PNG source/alpha/metadata only; not production gate credit.',rows=rows,small_source_sheet=str(sheet.relative_to(ROOT)),json_declaration_matches=matches,
 no_java_read=True,no_game=True,production_changes=0,new_reference_designs=0,
 limits='Metadata records declared filtering, not actual sampler/runtime. Non-square PNG does not prove animation. Border discontinuity is only source data, not established rendering bug. Fine original brocade is protected, no unilateral redraw.')
(OUT/'existing-effect-source-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(rows=[{k:r[k] for k in ['name','dimensions','partial_alpha_pixels','visible_rgba_colors','border_nonzero_samples','left_right_edge_rgba_differences','source_animation_section_declared']} for r in rows],json_matches=matches,sheet=str(sheet)),ensure_ascii=False))
