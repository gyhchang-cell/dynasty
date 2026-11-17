"""Show every unchanged source tile alongside the exact local animation metadata."""
from pathlib import Path
import hashlib,json,zipfile
from PIL import Image,ImageDraw
from collect import ROOT,OUT,RAW

rows=json.loads((OUT/'batch-17-candidates.json').read_text())['rows']
animated=[r for r in rows if r['dimensions'][1]>r['dimensions'][0]]
page=Image.new('RGB',(1480,1180),'#43494e');dr=ImageDraw.Draw(page)
dr.text((12,10),'REFERENCE SOURCE TILES / NEAREST INTEGER x12 / NO INTERPOLATION RENDER / NOT GAME',fill='white')
result=[]
for i,r in enumerate(animated):
 im=Image.open(ROOT/r['local_path']).convert('RGBA');w=im.width
 assert im.height%w==0
 with zipfile.ZipFile(r['jar']) as z:
  entry=r['path']+'.mcmeta';data=z.read(entry)
 metadata=json.loads(data);a=metadata['animation']
 assert not a.get('width') and not a.get('height')
 count=im.height//w
 sequence=a.get('frames',list(range(count)))
 sequence=[dict(index=n,time=a.get('frametime',1)) if isinstance(n,int) else dict(index=n['index'],time=n.get('time',a.get('frametime',1))) for n in sequence]
 used={n['index'] for n in sequence}
 dst=RAW/'batch17-animation'/f"{r['reference_id']}.png.mcmeta";dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 y=40+i*280
 dr.text((12,y),r['reference_id']+' '+Path(r['path']).name,fill='white')
 dr.text((12,y+16),f"metadata sequence {sequence}; interpolate={a.get('interpolate',False)}",fill='white')
 tiles=[]
 for j in range(count):
  patch=im.crop((0,j*w,w,(j+1)*w));preview=patch.resize((w*12,w*12),Image.Resampling.NEAREST)
  x=12+j*242
  dr.rectangle((x,y+40,x+191,y+231),fill='#666c71')
  page.paste(preview,(x,y+40),preview)
  dr.text((x,y+238),f"tile {j}: {'IN SEQUENCE' if j in used else 'NOT IN SEQUENCE'}",fill='white')
  tiles.append(dict(index=j,rgba_sha256=hashlib.sha256(patch.tobytes()).hexdigest(),in_sequence=j in used))
 result.append(dict(reference=r['reference_id'],jar=r['jar'],metadata_entry=entry,metadata_sha256=hashlib.sha256(data).hexdigest(),
  metadata_local=str(dst.relative_to(ROOT)),png=r['local_path'],png_sha256=r['sha256'],source_tiles=count,playback_sequence=sequence,
  interpolate=a.get('interpolate',False),tiles=tiles))
sheet=RAW/'batch17-animation/tiles.png';page.save(sheet)
(OUT/'batch17-animation-source.json').write_text(json.dumps(dict(rows=result,inspection_sheet=str(sheet.relative_to(ROOT)),
 source_pngs=4,total_source_tiles=sum(r['source_tiles'] for r in result),new_design_credit=0,manual_review_complete=False,
 limits='Source tiles and exact metadata only; no GPU interpolation, item registration, runtime or extra equipment cases.'),ensure_ascii=False,indent=2)+'\n')
print(sheet)
