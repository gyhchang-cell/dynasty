from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,zipfile
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'src/main/resources/assets/dynasty';rows=json.loads((D/'selection.json').read_text());ids={r['id'] for r in rows};out=[]
f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',14);sheet=Image.new('RGB',(1080,60+((len(rows)+7)//8)*100),'#565c61');dr=ImageDraw.Draw(sheet);dr.text((10,10),'32px库存尺寸预览 · 非游戏截图',font=f,fill='white')
for i,r in enumerate(rows):
 p=D/'sources'/f'{r["id"]}.png';im=Image.open(p).convert('RGBA');assert im.getextrema()[3][0]==0,r['id'];bbox=im.getbbox();assert bbox,r['id'];small=im.crop(bbox);small.thumbnail((32,32),Image.Resampling.NEAREST);x=i%8*135;y=60+i//8*100;sheet.paste(small,(x+50,y),small);dr.text((x+3,y+40),r['name'],font=f,fill='white');out.append({'id':r['id'],'originalSize':im.size,'alphaBounds':bbox,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
sheet.save(D/'inventory-size-review.png');(D/'source-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
with zipfile.ZipFile(D/'originals-106.zip','w',zipfile.ZIP_STORED) as z:
 for r in rows:z.write(D/'sources'/f'{r["id"]}.png',f'{r["id"]}.png')
baseline=json.loads((D/'baseline.json').read_text());changed=[name for name,h in baseline.items() if Path(name).stem not in ids and hashlib.sha256((A/'textures/item'/name).read_bytes()).hexdigest()!=h];(D/'preservation.json').write_text(json.dumps({'untargetedChanges':changed,'targets':len(rows)},indent=2));print('Checked',len(rows),'source images; other changes:',changed)
