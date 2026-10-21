from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,zipfile,io,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/art/weapon-tier-v11';T=O/'textures';T.mkdir(exist_ok=True)
with zipfile.ZipFile('/Users/a15356015027/Public/.minecraft/versions/1.20.1/1.20.1.jar') as z:base=Image.open(io.BytesIO(z.read('assets/minecraft/textures/item/iron_sword.png'))).convert('RGBA')
colors=[(68,68,68),(255,255,255),(24,24,24),(190,190,190),(216,216,216),(107,107,107),(150,150,150),(73,54,21),(104,78,30),(137,103,39),(40,30,11)]
letters='abcdefghijk';reverse={c:letters[i] for i,c in enumerate(colors)}
original=[''.join(reverse.get(base.getpixel((x,y))[:3],'.') if base.getpixel((x,y))[3] else '.' for x in range(16)) for y in range(16)]
# Keep vanilla guard, grip and pommel coordinates. Edit only blade rows by pixel.
forms=[
('sword_bronze','青铜剑','铜叶刃：短阔剑尖，朴素铜色',[(1,13,'aaa'),(2,12,'abbc'),(3,11,'abdec'),(4,10,'abdec'),(5,9,'abdec'),(6,8,'aedc'),(7,7,'aedc')],['694C32','EBD3A1','352B25','B98E53','D6B378','89683E','B08A52']),
('sword_silver','官银剑','银脊刃：菱形刃肩，细长开锋',[(0,14,'aa'),(1,13,'abc'),(2,12,'abdc'),(3,11,'abdec'),(4,9,'abedec'),(5,8,'abedc'),(6,7,'aedec'),(7,6,'aedec')],['4B5B69','F3F3E7','27333D','A9C1CA','D2DFDE','718896','9FB2B9']),
('sword_jade','玉剑','玉节刃：单侧节肩，清晰玉锋',[(0,14,'aa'),(1,13,'abc'),(2,12,'abdc'),(3,10,'abdec'),(4,9,'abdec'),(5,9,'abdc'),(6,7,'abdec'),(7,6,'aedec')],['416850','EBF0CA','253F34','86B58B','B8D4A2','648365','97AD78'])]

manifest=[];grids={};checks=[]
for n,label,idea,blade,metal in forms:
 assert (R/'src/main/resources/assets/dynasty/models/item'/f'{n}.json').exists()
 runtime=R/'src/main/resources/assets/dynasty/textures/item'/f'{n}.png';before=hashlib.sha256(runtime.read_bytes()).hexdigest()
 grid=[list(row) for row in original]
 for y in range(8):
  for x in range(6,16):grid[y][x]='.'
 for y,x,row in blade:
  for i,ch in enumerate(row):grid[y][x+i]=ch
 pal={k:tuple(bytes.fromhex(v))+(255,) for k,v in zip(letters,metal+['493615','684E1E','896727','281E0B'])};pal['.']=(0,0,0,0)
 im=Image.new('RGBA',(16,16))
 for y in range(16):
  for x in range(16):im.putpixel((x,y),pal[grid[y][x]])
 # Entire lower hilt geometry and exact vanilla wooden grip colours retained.
 assert all(grid[y][x]==original[y][x] for y in range(8,16) for x in range(16))
 assert all(im.getpixel((x,y))==base.getpixel((x,y)) for y in range(16) for x in range(16) if original[y][x] in 'hijk')
 pts={(x,y) for y in range(16) for x in range(16) if im.getpixel((x,y))[3]};seen={next(iter(pts))};queue=list(seen)
 for x,y in queue:
  for dx in [-1,0,1]:
   for dy in [-1,0,1]:
    p=(x+dx,y+dy)
    if p in pts and p not in seen:seen.add(p);queue.append(p)
 assert seen==pts,n
 im.save(T/f'{n}.png');grids[n]=[''.join(row) for row in grid]
 checks.append({'id':n,'vanilla_hilt_geometry':True,'vanilla_wood_pixels':True,'single_connected_silhouette':True,'runtime_sha256':before});assert hashlib.sha256(runtime.read_bytes()).hexdigest()==before
 manifest.append({'id':n,'name':label,'idea':idea,'palette':metal})
f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22);sm=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',15)
c=Image.new('RGB',(960,370),'#30383E');d=ImageDraw.Draw(c)
for i,(n,label,idea) in enumerate([('vanilla','原版铁剑','原版比例对照')]+[(m['id'],m['name'],m['idea'].split('：')[0]) for m in manifest]):
 x=i*240;d.rectangle((x+6,8,x+233,361),fill='#465058');im=base if n=='vanilla' else Image.open(T/f'{n}.png');lg=im.resize((192,192),Image.Resampling.NEAREST);c.paste(lg,(x+24,23),lg);d.text((x+18,232),label,font=f,fill='#E9E4D8');d.text((x+18,266),idea,font=sm,fill='#C4D3D8');mini=im.resize((32,32),Image.Resampling.NEAREST);c.paste(mini,(x+20,304),mini);d.text((x+65,309),'物品栏大小对照',font=sm,fill='#C4D3D8')
c.save(O/'review.png');(O/'pixel-grids.json').write_text(json.dumps({'grids':grids,'variants':manifest},ensure_ascii=False,indent=2));(O/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
with zipfile.ZipFile(O/'swords-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in T.glob('*.png'):z.write(p,'textures/'+p.name)
 z.write(O/'pixel-grids.json','pixel-grids.json');z.write(__file__,'create.py')
print('3 existing swords, 16px, original grip/guard geometry preserved; review only')
