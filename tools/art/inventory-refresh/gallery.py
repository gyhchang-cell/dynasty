"""Display actual runtime PNGs at integer zoom, without smoothing or redrawing."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v1';A=R/'src/main/resources/assets/dynasty';m=json.loads((D/'generated-manifest.json').read_text());names=json.loads((A/'lang/zh_cn.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18)
for group,rows in [('accessories-first',m['accessories'][:10]),('accessories-next',m['accessories'][10:]),('materials',m['materials'])]:
 cols=5 if group.startswith('accessories') else 10;cell=160 if cols==5 else 110;h=148 if cols==5 else 124;im=Image.new('RGB',(cols*cell,((len(rows)+cols-1)//cols)*h+40),'#565c61');dr=ImageDraw.Draw(im);dr.text((12,8),'运行资源 · 16px 原图整数放大 · 非游戏截图',font=font,fill='white')
 for i,row in enumerate(rows):
  x=i%cols*cell;y=i//cols*h+40;pic=Image.open(A/'textures/item'/f"{row['id']}.png").convert('RGBA');zoom=pic.resize((96,96) if cols==5 else (80,80),Image.Resampling.NEAREST);im.paste(zoom,(x+(cell-zoom.width)//2,y),zoom);label=names.get('item.dynasty.'+row['id'],row['id']);dr.text((x+4,y+zoom.height+5),label,font=font,fill='white')
 im.save(D/(group+'-gallery.png'))
