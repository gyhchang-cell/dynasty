from pathlib import Path
import json,hashlib,zipfile
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;rows=json.loads((D/'selection.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',21)
canvas=Image.new('RGB',(1120,620),'#565c61');dr=ImageDraw.Draw(canvas);dr.text((14,12),'本轮机械物品 · 原稿缩略展示 · 非游戏截图',font=font,fill='white');report=[]
for i,r in enumerate(rows):
 p=D/'sources'/(r['id']+'.png')
 if not p.exists():continue
 with Image.open(p) as raw:
  raw.load();im=raw.convert('RGBA');assert im.getchannel('A').getextrema()[0]==0;assert im.getbbox();report.append({'id':r['id'],'size':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});im=im.crop(im.getbbox());im.thumbnail((230,210),Image.Resampling.NEAREST)
 x=i%4*280;y=50+i//4*285;canvas.paste(im,(x+(280-im.width)//2,y+(220-im.height)//2),im)
 name=r['name'];lines=[name] if len(name)<=11 else [name[:10],name[10:]]
 for j,line in enumerate(lines):dr.text((x+12,y+225+j*25),line,font=font,fill='white')
canvas.save(D/'this-round-8.png');(D/'validation.json').write_text(json.dumps({'expected':8,'completed':len(report),'runtimeInstalled':False,'originals':report},ensure_ascii=False,indent=2));print('completed',len(report))
if len(report)==8:
 with zipfile.ZipFile(D/'mechanical-originals-8.zip','w',zipfile.ZIP_STORED) as z:
  for r in rows:z.write(D/'sources'/(r['id']+'.png'),'originals/'+r['id']+'.png')
  z.write(D/'selection.json','selection.json')
