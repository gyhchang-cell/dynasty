from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'selection.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20)
for compare in [False,True]:
 width=1200 if compare else 1000;cw=width//4;ch=350 if compare else 260
 out=Image.new('RGB',(width,2*ch+50),'#565c61');dr=ImageDraw.Draw(out)
 dr.text((15,10),'本轮8件饰品 · '+('修改前 / 原稿接入后' if compare else '原稿缩略展示')+' · 非游戏截图',font=font,fill='white')
 for i,row in enumerate(rows):
  x=i%4*cw;y=50+i//4*ch
  if compare:
   old=Image.open(D/'before/textures/item'/f"{row['id']}.png").convert('RGBA');old.thumbnail((96,96),Image.Resampling.NEAREST)
   if old.width<96:old=old.resize((96,96),Image.Resampling.NEAREST)
   out.paste(old,(x+(cw-old.width)//2,y),old);offset=110
  else:offset=0
  a=Image.open(D/'sources'/f"{row['id']}.png").convert('RGBA');a=a.crop(a.getbbox());a.thumbnail((cw-40,205),Image.Resampling.NEAREST)
  out.paste(a,(x+(cw-a.width)//2,y+offset+(210-a.height)//2),a)
  dr.text((x+25,y+offset+218),row['name'],font=font,fill='white')
 out.save(D/('comparison.png' if compare else 'this-round-8.png'))
