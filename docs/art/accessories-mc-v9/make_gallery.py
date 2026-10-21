from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
D=Path(__file__).resolve().parent;rows=json.loads((D/'selection.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20)
for compare in [False,True]:
 cw=220;ch=325 if compare else 235;cols=5
 out=Image.new('RGB',(cols*cw,math.ceil(len(rows)/cols)*ch+45),'#565c61');dr=ImageDraw.Draw(out)
 dr.text((15,8),'本轮17件饰品 · '+('修改前 / 原稿接入后' if compare else '原稿缩略展示')+' · 非游戏截图',font=font,fill='white')
 for i,row in enumerate(rows):
  x=i%cols*cw;y=45+i//cols*ch
  if compare:
   old=Image.open(D/'before/textures/item'/f"{row['id']}.png").convert('RGBA');old.thumbnail((80,80),Image.Resampling.NEAREST)
   if old.width<80:old=old.resize((80,80),Image.Resampling.NEAREST)
   out.paste(old,(x+(cw-old.width)//2,y),old);offset=90
  else:offset=0
  a=Image.open(D/'sources'/f"{row['id']}.png").convert('RGBA');a=a.crop(a.getbbox());a.thumbnail((cw-30,185),Image.Resampling.NEAREST)
  out.paste(a,(x+(cw-a.width)//2,y+offset+(190-a.height)//2),a)
  dr.text((x+15,y+offset+198),row['name'],font=font,fill='white')
 out.save(D/('comparison.png' if compare else 'this-round-17.png'))
