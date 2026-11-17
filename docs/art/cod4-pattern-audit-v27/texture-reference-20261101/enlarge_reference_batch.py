"""Analysis-only integer source enlargement. Never writes a production PNG."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
from collect import ROOT as R,OUT as D
number=int(sys.argv[1]);path=D/f'batch-{number:02}-candidates.json'
x=json.loads(path.read_text());rows=x['rows']
for start in range(0,len(rows),4):
 out=R/f'build/art-reference-20261101/batch{number:02}-full-detail-{start//4+1:02}.png'
 page=Image.new('RGB',(1080,1140),'#43494e');d=ImageDraw.Draw(page)
 d.text((5,5),'SOURCE PIXELS ONLY / INTEGER ENLARGEMENT / NOT DYNASTY OR GAME',fill='white')
 for i,r in enumerate(rows[start:start+4]):
  ox=(i%2)*540;oy=30+(i//2)*555
  im=Image.open(R/r['local_path']).convert('RGBA');factor=max(1,512//max(im.size))
  if max(im.size)>512:raise ValueError('Source too large: use fullsize source review instead of downsampling')
  im=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)
  for y in range(0,512,16):
   for xx in range(0,512,16):d.rectangle((ox+xx,oy+y,ox+xx+15,oy+y+15),fill='#70777c' if (xx//16+y//16)%2 else '#7f868b')
  page.paste(im,(ox,oy),im)
  d.text((ox+4,oy+520),r['reference_id']+' '+Path(r['path']).name+f' x{factor}',fill='white')
  r['supplemental_detail_view']=str(out.relative_to(R))
 page.save(out)
path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(generated_not_reviewed=len(rows),sheets=sorted({r['supplemental_detail_view'] for r in rows}))))
