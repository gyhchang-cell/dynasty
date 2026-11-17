from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent
plan=json.loads((D/'plan.json').read_text());sheet=Image.new('RGB',(1000,1500),'#555b60');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18)
count=0
for i,p in enumerate(plan):
 f=D/'generation'/f"{p['id']}.json";revision=D/'generation'/f"{p['id']}-revision.json"
 if not f.exists():continue
 row=json.loads((revision if revision.exists() else f).read_text());im=Image.open(row['generated']).convert('RGBA');b=im.getbbox();w=max(b[2]-b[0],b[3]-b[1]);x=(b[0]+b[2]-w)//2;y=(b[1]+b[3]-w)//2;im=im.crop((x,y,x+w,y+w)).resize((210,210),Image.Resampling.NEAREST);xx=i%4*250;yy=i//4*250;sheet.paste(im,(xx+20,yy+8),im);draw.text((xx+10,yy+221),p['name'],font=font,fill='white');count+=1
sheet.save(D/'drafts.png');print('Drafts available:',count)
