from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
D=Path(__file__).resolve().parent;rows=[r for r in json.loads((D/'selection.json').read_text()) if (D/'sources'/f'{r["id"]}.png').exists()];f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20)
for comparison in [False,True]:
 cw=260;ch=330 if comparison else 260;sheet=Image.new('RGB',(cw*3,55+math.ceil(len(rows)/3)*ch),'#565c61');dr=ImageDraw.Draw(sheet);dr.text((12,12),'物品原稿 · '+('修改前 / 修改后' if comparison else '缩略展示')+' · 非游戏截图',font=f,fill='white')
 for i,r in enumerate(rows):
  x=i%3*cw;y=55+i//3*ch;offset=80 if comparison else 0
  if comparison:
   old=Image.open(D/'before/textures'/f'{r["id"]}.png').convert('RGBA');old=old.resize((64,64),Image.Resampling.NEAREST);sheet.paste(old,(x+98,y),old)
  im=Image.open(D/'sources'/f'{r["id"]}.png').convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((220,200),Image.Resampling.NEAREST);sheet.paste(im,(x+(cw-im.width)//2,y+offset+(200-im.height)//2),im);dr.text((x+20,y+offset+212),r['name'],font=f,fill='white')
 sheet.save(D/('comparison.png' if comparison else 'this-round-6.png'))
sheet=Image.new('RGB',(900,150),'#565c61');dr=ImageDraw.Draw(sheet)
for i,r in enumerate(rows):
 im=Image.open(D/'sources'/f'{r["id"]}.png').convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((32,32),Image.Resampling.NEAREST);sheet.paste(im,(i*150+58,20),im);dr.text((i*150+10,75),r['name'],font=f,fill='white')
sheet.save(D/'inventory-size-review.png')
print('Reviewed gallery sources:',len(rows))
