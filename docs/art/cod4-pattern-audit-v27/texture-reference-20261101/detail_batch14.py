"""Integer source atlas enlargement; normal/slim comparisons are one design."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from collect import ROOT as R,OUT as D
x=json.loads((D/'batch-14-candidates.json').read_text())
rows=[r for r in x['rows'] if 'armoroftheages' in r['path']]
for start in range(0,len(rows),4):
 out=R/f'build/art-reference-20261101/batch14-detail-{start//4+1:02}.png'
 page=Image.new('RGB',(1080,1140),'#43494e');d=ImageDraw.Draw(page)
 d.text((5,5),'PRIMARY SOURCE PIXELS / INTEGER ENLARGEMENT / NOT DYNASTY OR GAME',fill='white')
 for i,r in enumerate(rows[start:start+4]):
  ox=(i%2)*540;oy=30+(i//2)*555
  im=Image.open(R/r['local_path']).convert('RGBA');factor=512//max(im.size)
  im=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)
  for y in range(0,512,16):
   for xx in range(0,512,16):d.rectangle((ox+xx,oy+y,ox+xx+15,oy+y+15),fill='#70777c' if (xx//16+y//16)%2 else '#7f868b')
  page.paste(im,(ox,oy),im)
  d.text((ox+4,oy+520),r['reference_id']+' '+Path(r['path']).name+f' x{factor}',fill='white')
  r['supplemental_detail_view']=str(out.relative_to(R))
 page.save(out)
(D/'batch-14-candidates.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
print('Source details generated, not yet visually reviewed:',len(rows))
