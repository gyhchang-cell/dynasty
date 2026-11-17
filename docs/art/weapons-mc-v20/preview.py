from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'src/main/resources/assets/dynasty';rows=json.loads((D/'selection.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',23)
o=Image.new('RGB',(1280,730),'#555b60');d=ImageDraw.Draw(o);d.text((20,12),'实际运行资源 · 上：旧图  下：新原稿 · 非游戏截图',font=font,fill='white');review=[]
for i,row in enumerate(rows):
 for old,y in [(True,60),(False,360)]:
  p=(D/'before'/A.relative_to(R) if old else A)/'textures/item'/f"{row['id']}.png";im=Image.open(p).convert('RGBA');im=im.resize((280,280),Image.Resampling.NEAREST);o.paste(im,(i*320+20,y),im)
 d.text((i*320+35,655),row['name'],font=font,fill='white')
 orig=Image.open(D/'sources'/f"{row['id']}.png").convert('RGBA');crop=orig.crop(orig.getbbox());expected=Image.new('RGBA',(crop.width+4,crop.height+4));expected.paste(crop,(2,2));target=Image.open(A/'textures/item'/f"{row['id']}.png").convert('RGBA');assert target.size==expected.size and target.tobytes()==expected.tobytes()
 assert abs(target.width/target.height-1)<.1
 review.append({'id':row['id'],'sourceSize':orig.size,'runtimeSize':target.size,'originalRgbaExact':True,'display':row['display'],'runtimeSha256':hashlib.sha256((A/'textures/item'/f"{row['id']}.png").read_bytes()).hexdigest()})
o.save(D/'comparison.png');(D/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
