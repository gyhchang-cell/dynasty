from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib,math
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'src/main/resources/assets/dynasty';rows=json.loads((D/'selection.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22);small=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',17)
o=Image.new('RGB',(1280,60+math.ceil(len(rows)/4)*570),'#555b60');d=ImageDraw.Draw(o);d.text((20,12),'实际运行资源 · 每组上：旧图 / 下：新原稿 · 非游戏截图',font=font,fill='white');review=[]
for i,row in enumerate(rows):
 x=i%4*320;y=i//4*570+60
 for old,yy in [(True,y),(False,y+260)]:
  p=(D/'before'/A.relative_to(R) if old else A)/'textures/item'/f"{row['id']}.png";im=Image.open(p).convert('RGBA');im=im.resize((240,240),Image.Resampling.NEAREST);o.paste(im,(x+40,yy),im)
 d.text((x+30,y+510),row['name'],font=font,fill='white')
 orig=Image.open(D/'sources'/f"{row['id']}.png").convert('RGBA');crop=orig.crop(row.get('crop_bounds',orig.getbbox()));expected=Image.new('RGBA',(crop.width+4,crop.height+4));expected.paste(crop,(2,2));target=Image.open(A/'textures/item'/f"{row['id']}.png").convert('RGBA');assert target.size==expected.size and target.tobytes()==expected.tobytes()
 review.append({'id':row['id'],'sourceSize':orig.size,'runtimeSize':target.size,'originalRgbaExact':True,'runtimeSha256':hashlib.sha256((A/'textures/item'/f"{row['id']}.png").read_bytes()).hexdigest()})
o.save(D/'comparison.png');(D/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
# Compact new-only sheet and 32px inventory-size sheet; scales only presentation files.
for size,name in [(220,'after.png'),(32,'inventory-32px.png')]:
 w=max(220,size+40);h=max(90,size+50);p=Image.new('RGB',(4*w,math.ceil(len(rows)/4)*h),'#555b60');draw=ImageDraw.Draw(p)
 for i,row in enumerate(rows):
  im=Image.open(A/'textures/item'/f"{row['id']}.png").convert('RGBA').resize((size,size),Image.Resampling.NEAREST);x=i%4*w;y=i//4*h;p.paste(im,(x+(w-size)//2,y),im);draw.text((x+15,y+size+8),row['name'],font=small,fill='white')
 p.save(D/name)
