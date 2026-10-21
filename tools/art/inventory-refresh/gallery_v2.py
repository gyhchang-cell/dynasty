"""Contact sheets from runtime PNG pixels. Never presented as game screenshots."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v2';A=R/'src/main/resources/assets/dynasty';names=json.loads((A/'lang/zh_cn.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',17)
selection=json.loads((D/'selection.json').read_text());extras=json.loads((D/'extra-selection.json').read_text());second=json.loads((D/'material-second-review.json').read_text())
groups={'corrections':['jade_brush_holder','qilin_hoof_charm'],'materials':[x[0] for x in selection if x[1]=='materials']+[x[0] for x in second],'accessories':[x[0] for x in selection if x[1]=='accessories' and x[0] not in ['jade_brush_holder','qilin_hoof_charm']]+[x[0] for x in extras]}
for label,ids in groups.items():
 cols=2 if label=='corrections' else 5;width=250 if cols==2 else 160;height=245 if cols==2 else 150;im=Image.new('RGB',(cols*width,((len(ids)+cols-1)//cols)*height+36),'#62686c');dr=ImageDraw.Draw(im);dr.text((8,8),'实际16px资源放大 · 非游戏截图',font=font,fill='white')
 for i,id in enumerate(ids):
  x=i%cols*width;y=i//cols*height+36;p=A/'textures/item'/f'{id}.png';pic=Image.open(p).convert('RGBA');n=128 if cols==2 else 96;large=pic.resize((n,n),Image.Resampling.NEAREST);im.paste(large,(x+(width-n)//2,y),large);dr.text((x+8,y+n+5),names.get('item.dynasty.'+id,id),font=font,fill='white')
  if cols==2:
   old=D/'before/textures/item'/f'{id}.png'
   if old.exists():
    prev=Image.open(old).convert('RGBA').resize((48,48),Image.Resampling.NEAREST);im.paste(prev,(x+20,y+167),prev);dr.text((x+80,y+181),'修改前',font=font,fill='white')
 im.save(D/f'{label}.png')
