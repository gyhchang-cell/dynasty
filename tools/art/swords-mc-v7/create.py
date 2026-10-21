from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,zipfile,io,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/art/swords-mc-v7';T=O/'textures';T.mkdir(exist_ok=True)
with zipfile.ZipFile('/Users/a15356015027/Public/.minecraft/versions/1.20.1/1.20.1.jar') as z:base=Image.open(io.BytesIO(z.read('assets/minecraft/textures/item/iron_sword.png'))).convert('RGBA')
colors=[(68,68,68),(255,255,255),(24,24,24),(190,190,190),(216,216,216),(107,107,107),(150,150,150),(73,54,21),(104,78,30),(137,103,39),(40,30,11)]
letters='abcdefghijk';reverse={c:letters[i] for i,c in enumerate(colors)}
original=[''.join(reverse.get(base.getpixel((x,y))[:3],'.') if base.getpixel((x,y))[3] else '.' for x in range(16)) for y in range(16)]
# Keep vanilla guard, grip and pommel coordinates. Edit only blade rows by pixel.
forms=[
('yuchang_dagger','鱼肠剑','短刃：缩短剑身，保留原版握柄',[(2,12,'aaa'),(3,11,'abbc'),(4,10,'abdbc'),(5,9,'abdec'),(6,8,'aedec'),(7,7,'aedc')],['42595B','EEF4DD','253434','9DB9AF','CAD9CA','65797A','8EA29A']),
('juque_sword','巨阙重剑','重剑：宽刃面，短柄不跟着膨胀',[(0,12,'aaaa'),(1,11,'abbdc'),(2,10,'abbdec'),(3,9,'abbdec'),(4,8,'abbdec'),(5,7,'abbdec'),(6,7,'abdec'),(7,6,'aedec')],['48515B','ECF0E6','252B35','9AA9B5','CFD6D8','68737E','8D9BA4']),
('longyuan_sword','龙渊剑','直剑：窄刃长锋，连续亮刃边',[(0,14,'aa'),(1,13,'abc'),(2,12,'abdc'),(3,11,'abdc'),(4,10,'abdc'),(5,9,'abdc'),(6,8,'aedc'),(7,7,'aedc')],['34526A','E6F4EF','203244','779FB2','B5D3D5','4D6B80','7897A5']),
('liuyun_sword','流云剑','弧刃：改变刃口阶梯，柄格沿用',[(0,14,'aa'),(1,14,'bc'),(2,13,'abc'),(3,11,'abdc'),(4,10,'abdec'),(5,8,'abbdec'),(6,7,'abdec'),(7,6,'aedec')],['3F6470','EAF5E9','253C47','8BB8C2','C1DCE0','597B87','85A6AD']),
('taiyi_sword','太乙法剑','波刃：两处折转，不改成软曲线',[(0,13,'aaa'),(1,12,'abbc'),(2,12,'abdc'),(3,11,'abdc'),(4,9,'abdc'),(5,8,'abdc'),(6,8,'aedc'),(7,7,'aedc')],['57506D','EEE9F5','302B43','ADA3C2','D2C9DF','756785','9B8CA9'])]
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
c=Image.new('RGB',(1440,370),'#30383E');d=ImageDraw.Draw(c)
for i,(n,label,idea) in enumerate([('vanilla','原版铁剑','原版比例对照')]+[(m['id'],m['name'],m['idea'].split('：')[0]) for m in manifest]):
 x=i*240;d.rectangle((x+6,8,x+233,361),fill='#465058');im=base if n=='vanilla' else Image.open(T/f'{n}.png');lg=im.resize((192,192),Image.Resampling.NEAREST);c.paste(lg,(x+24,23),lg);d.text((x+18,232),label,font=f,fill='#E9E4D8');d.text((x+18,266),idea,font=sm,fill='#C4D3D8');mini=im.resize((32,32),Image.Resampling.NEAREST);c.paste(mini,(x+20,304),mini);d.text((x+65,309),'物品栏大小对照',font=sm,fill='#C4D3D8')
c.save(O/'review.png');(O/'pixel-grids.json').write_text(json.dumps({'grids':grids,'variants':manifest},ensure_ascii=False,indent=2));(O/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
with zipfile.ZipFile(O/'five-swords-review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in T.glob('*.png'):z.write(p,'textures/'+p.name)
 z.write(O/'pixel-grids.json','pixel-grids.json');z.write(__file__,'create.py')
print('5 existing swords, 16px, original grip/guard geometry preserved; review only')
