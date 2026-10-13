"""Inspect production Java wind triangles at fixed scale; software only."""
import importlib.util,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('impact_review',ROOT/'tools/art/weapon-impact/review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
OUT=ROOT/'docs/art/tang-wind-v1'
data=json.loads((OUT/'actual-triangles.json').read_text())
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
angles=[('front',0,'color'),('45',45,'color'),('side',90,'color'),('back',180,'color'),('black',45,'black'),('gray',45,'gray')]
sheet=Image.new('RGB',(280*6,90+310*len(data)),(224,222,211));draw=ImageDraw.Draw(sheet)
draw.text((20,15),'TANG WIND / ACTUAL JAVA TRIANGLES / FIXED WORLD SCALE / SOFTWARE ONLY',fill=(30,31,30),font=font)
draw.text((20,40),'Opaque shape diagnostic. No game light/blending/player-model acceptance. Bottom line = one block.',fill=(30,31,30),font=font)
for row,(name,v) in enumerate(data.items()):
 frame=next(f for f in v['frames'] if f['age']==3)
 for col,(label,yaw,mode) in enumerate(angles):
  sheet.paste(review.image(frame,yaw,mode),(col*280,90+row*310));draw.text((col*280+8,90+row*310+282),name+' '+label,fill=(30,31,30),font=font)
sheet.save(OUT/'software-views.png')
sheet=Image.new('RGB',(280*7,90+310*2),(224,222,211));draw=ImageDraw.Draw(sheet)
draw.text((20,15),'TANG WIND / REAL JAVA ONSET-EXTEND-EXPIRE / SOFTWARE OPAQUE DIAGNOSTIC',fill=(30,31,30),font=font)
for row,name in enumerate(['observer-straight','own-first-person-straight']):
 for col,frame in enumerate(data[name]['frames']):
  sheet.paste(review.image(frame,45),(col*280,90+row*310));draw.text((col*280+8,90+row*310+282),name+' t='+str(frame['age']),fill=(30,31,30),font=font)
sheet.save(OUT/'software-timeline.png')
print('Generated real-triangle software diagnostics; graphics pending')
