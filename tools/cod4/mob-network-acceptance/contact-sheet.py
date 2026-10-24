from pathlib import Path
from PIL import Image,ImageDraw
import sys,json
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/mob-network-acceptance'/sys.argv[1]
role=sys.argv[2] if len(sys.argv)>2 else 'host'
images=sorted(O.glob(role+'-view-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
for page in range(0,len(images),10):
 subset=images[page:page+10];w,h=600,400;sheet=Image.new('RGB',(w*2,h*5),(230,230,230));draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(subset):
  n=int(p.stem.split('-')[-1]);inp=json.loads((O/(role+'-input-'+str(n)+'.json')).read_text());img=Image.open(p);img.thumbnail((w,h-28));x=(i%2)*w;y=(i//2)*h;sheet.paste(img,(x,y+28));draw.text((x+8,y+6),inp['name'],fill='black')
 sheet.save(O/f'{role}-contact-{page//10+1:02}.jpg',quality=91)
print('Raw world screenshots:',len(images),'Contact pages:',(len(images)+9)//10)
