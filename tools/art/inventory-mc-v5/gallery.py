from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-mc-v5';font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20)
rows=json.loads((D/'selected.json').read_text());extra=[{'id':'raw_silk','name':'生丝'},{'id':'silk','name':'丝绸'},{'id':'roof_tile','name':'琉璃瓦'},{'id':'brocade','name':'锦缎'}]
for name,items,cols in [('this-round-50',rows,5),('materials-4',extra,4),('this-round-54',rows+extra,6)]:
 cell=200;h=200;out=Image.new('RGB',(cols*cell,math.ceil(len(items)/cols)*h+40),'#565c61');dr=ImageDraw.Draw(out);dr.text((12,8),'本轮原创像素贴图 · 原稿缩略展示 · 非游戏截图',font=font,fill='white')
 for i,r in enumerate(items):
  p=D/'sources'/(r['id']+'.png')
  if not p.exists():continue
  im=Image.open(p).convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((165,155),Image.Resampling.NEAREST);x=i%cols*cell;y=40+i//cols*h;out.paste(im,(x+(cell-im.width)//2,y+(160-im.height)//2),im);dr.text((x+12,y+168),r['name'],font=font,fill='white')
 out.save(D/(name+'.png'))
print('source count',len(list((D/'sources').glob('*.png'))))
