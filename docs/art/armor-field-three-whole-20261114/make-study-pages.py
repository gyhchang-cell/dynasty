from pathlib import Path
from PIL import Image,ImageDraw
import json
B=Path(__file__).resolve().parent;R=B/'source/src/main/resources/assets/dungeons_gear';view=[]
for n in ['climbing','spelunker','snow']:
 page=Image.new('RGB',(1100,1000),'#555b60');d=ImageDraw.Draw(page);d.text((10,10),f'D89 {n} / UPSTREAM SOURCE STUDY / NOT Dynasty art or game / integer NN',fill='white')
 for i,slot in enumerate(['helmet','chestplate','leggings','boots']):
  p=R/'textures/item/armor'/f'{n}_{slot}.png';im=Image.open(p).convert('RGBA');nn=im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST);page.paste(nn,(20+i*270,45),nn);d.text((20+i*270,185),slot,fill='white');view.append({'path':str(p),'size':list(im.size)})
 p=R/'textures/models/armor'/f'{n}_armor.png';im=Image.open(p).convert('RGBA');factor=min(800//im.width,700//im.height);nn=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST);page.paste(nn,(20,230),nn);d.text((840,240),str(im.size),fill='white');page.save(B/f'{n}-source-study.png');view.append({'path':str(p),'size':list(im.size)})
(B/'viewed-image-paths.json').write_text(json.dumps(view,indent=2)+'\n');print('source panels ready',len(view))
