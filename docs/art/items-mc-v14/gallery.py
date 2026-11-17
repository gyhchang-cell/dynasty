from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
D=Path(__file__).resolve().parent
rows=[r for r in json.loads((D/'selection.json').read_text()) if (D/'sources'/f'{r["id"]}.png').exists()]
f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18)
for page in range(math.ceil(len(rows)/30)):
 rs=rows[page*30:page*30+30];sheet=Image.new('RGB',(1100,60+math.ceil(len(rs)/5)*215),'#565c61');dr=ImageDraw.Draw(sheet);dr.text((15,15),'本批运行原稿 · 缩略预览 · 非游戏截图',font=f,fill='white')
 for i,r in enumerate(rs):
  im=Image.open(D/'sources'/f'{r["id"]}.png').convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((175,165),Image.Resampling.NEAREST);x=i%5*220;y=60+i//5*215;sheet.paste(im,(x+(220-im.width)//2,y),im);dr.text((x+10,y+175),r['name'],font=f,fill='white')
 sheet.save(D/f'gallery-{page+1}.png')
print('Gallery:',len(rows))
