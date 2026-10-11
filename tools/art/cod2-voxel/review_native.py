"""Arrange original Forge screenshots for inspection; keep every full original."""
import argparse
from PIL import Image,ImageDraw
from build_models import OUT

p=argparse.ArgumentParser();p.add_argument('run');args=p.parse_args()
assert args.run and all(c.isalnum() or c in '-_' for c in args.run)
source=OUT/'native'/args.run;output=OUT/'native-review';output.mkdir(exist_ok=True)
files=sorted(source.glob('[0-9][0-9]-*.png'))
assert files,'No actual native screenshots'
for page in range((len(files)+7)//8):
    subset=files[page*8:page*8+8]
    canvas=Image.new('RGB',(1160,2070),(240,238,231));draw=ImageDraw.Draw(canvas)
    draw.text((12,12),f'ACTUAL FORGE {args.run} / original screenshot crops / page {page+1}',fill=(25,30,30))
    for i,path in enumerate(subset):
        image=Image.open(path).convert('RGB');w,h=image.size
        image=image.crop((int(w*600/2800),int(h*200/1800),int(w*2200/2800),int(h*1500/1800)))
        image=image.resize((560,455),Image.Resampling.NEAREST)
        x=10+(i%2)*580;y=50+(i//2)*500;canvas.paste(image,(x,y))
        stage,name,label=path.stem.split('-',2)
        draw.text((x,y+460),stage+' '+name+' / '+label,fill=(25,30,30))
    canvas.save(output/f'{args.run}-page{page+1}.png')
print(len(files),'original screenshots /',page+1,'inspection sheets; no original edited')
