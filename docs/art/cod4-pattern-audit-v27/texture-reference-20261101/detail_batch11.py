"""Reproduce integer-scaled source atlas detail sheets without altering art."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from collect import ROOT as R, OUT as D
x=json.loads((D/'batch-11-candidates.json').read_text())
rows=[r for r in x['rows'] if max(r['dimensions'])>=128]
for start in range(0,len(rows),4):
    out=R/f'build/art-reference-20261101/batch11-detail-{start//4+1:02}.png'
    page=Image.new('RGB',(1080,1140),'#43494e');d=ImageDraw.Draw(page)
    d.text((5,5),'SOURCE ATLAS DETAIL / UNCHANGED PIXELS x4 / NOT MODEL OR GAME',fill='white')
    for i,r in enumerate(rows[start:start+4]):
        ox=(i%2)*540;oy=30+(i//2)*555
        im=Image.open(R/r['local_path']).convert('RGBA')
        im=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST)
        for y in range(0,512,16):
            for xx in range(0,512,16):
                d.rectangle((ox+xx,oy+y,ox+xx+15,oy+y+15),fill='#7c8286' if (xx//16+y//16)%2 else '#8c9296')
        page.paste(im,(ox,oy),im)
        d.text((ox+4,oy+520),r['reference_id']+' '+Path(r['path']).name,fill='white')
        r['supplemental_detail_view']=str(out.relative_to(R))
    page.save(out)
(D/'batch-11-candidates.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
print('detail source atlases:',len(rows))
