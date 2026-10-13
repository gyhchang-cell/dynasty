"""Review production decal triangles, not game screenshots."""
import importlib.util,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/art/armor-crack-v1'
spec=importlib.util.spec_from_file_location('impact_review',ROOT/'tools/art/weapon-impact/review.py');review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
data=json.loads((OUT/'actual-triangles.json').read_text());data.pop('measurements')
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
angles=[('front',0,'color'),('45',45,'color'),('side',90,'color'),('back',180,'color'),('black',45,'black'),('gray',45,'gray')]
sheet=Image.new('RGB',(280*6,90+310*2),(224,222,211));d=ImageDraw.Draw(sheet)
d.text((20,15),'MORALE CRACK / PRODUCTION PIXEL PLANES / FIXED SCALE / SOFTWARE ONLY',fill=(30,31,30),font=font)
d.text((20,40),'Intentional front-surface decal, edge-on invisible. Opaque diagnostics, no game transparency/light acceptance.',fill=(30,31,30),font=font)
for row,(name,v) in enumerate(data.items()):
 frame=next(f for f in v['frames'] if f['age']==3)
 for col,(label,yaw,mode) in enumerate(angles):
  sheet.paste(review.image(frame,yaw,mode),(col*280,90+row*310));d.text((col*280+8,90+row*310+282),name+' '+label,fill=(30,31,30),font=font)
sheet.save(OUT/'software-views.png')
sheet=Image.new('RGB',(280*7,90+310*2),(224,222,211));d=ImageDraw.Draw(sheet)
d.text((20,15),'MORALE CRACK / REAL JAVA SPLIT-CHIP-EXPIRE / OPAQUE SOFTWARE ONLY',fill=(30,31,30),font=font)
for row,(name,v) in enumerate(data.items()):
 for col,frame in enumerate(v['frames']):
  sheet.paste(review.image(frame,0),(col*280,90+row*310));d.text((col*280+8,90+row*310+282),name+' t='+str(frame['age']),fill=(30,31,30),font=font)
sheet.save(OUT/'software-timeline.png');print('Generated actual pixel-plane diagnostics; native visuals pending')
