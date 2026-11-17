from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,zipfile,io,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/art/swords-new-v10';T=O/'textures';T.mkdir(exist_ok=True)
with zipfile.ZipFile('/Users/a15356015027/Public/.minecraft/versions/1.20.1/1.20.1.jar') as z:base=Image.open(io.BytesIO(z.read('assets/minecraft/textures/item/iron_sword.png'))).convert('RGBA')
colors=[(68,68,68),(255,255,255),(24,24,24),(190,190,190),(216,216,216),(107,107,107),(150,150,150),(73,54,21),(104,78,30),(137,103,39),(40,30,11)]
letters='abcdefghijk';reverse={c:letters[i] for i,c in enumerate(colors)}
original=[''.join(reverse.get(base.getpixel((x,y))[:3],'.') if base.getpixel((x,y))[3] else '.' for x in range(16)) for y in range(16)]
# Keep vanilla guard, grip and pommel coordinates. Edit only blade rows by pixel.
forms=[
('sword_dragon_crystal','龙晶剑','龙牙晶刃：镂空晶脊与两级龙牙',[(0,14,'aa'),(1,13,'abc'),(2,12,'abdc'),(3,10,'ab.ec'),(4,9,'ab.deca'),(5,7,'aab.debc'),(6,7,'abedec'),(7,6,'aedec')],['246569','DAFFF1','163A47','51B7B9','95E3D7','796037','C0A564']),
('zhanlu_rendao_bamian_jian','湛卢八面剑','八面阔锋：菱形宽腹与收束剑根',[(0,14,'aa'),(1,13,'abc'),(2,11,'abbec'),(3,10,'abedec'),(4,9,'abeedc'),(5,8,'abedec'),(6,7,'aedec'),(7,7,'aedc')],['3B5148','EBE8BB','202F2D','8CA778','BACE98','786039','B89A56'])]

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
c=Image.new('RGB',(720,370),'#30383E');d=ImageDraw.Draw(c)
for i,(n,label,idea) in enumerate([('vanilla','原版铁剑','原版比例对照')]+[(m['id'],m['name'],m['idea'].split('：')[0]) for m in manifest]):
 x=i*240;d.rectangle((x+6,8,x+233,361),fill='#465058');im=base if n=='vanilla' else Image.open(T/f'{n}.png');lg=im.resize((192,192),Image.Resampling.NEAREST);c.paste(lg,(x+24,23),lg);d.text((x+18,232),label,font=f,fill='#E9E4D8');d.text((x+18,266),idea,font=sm,fill='#C4D3D8');mini=im.resize((32,32),Image.Resampling.NEAREST);c.paste(mini,(x+20,304),mini);d.text((x+65,309),'物品栏大小对照',font=sm,fill='#C4D3D8')
c.save(O/'review.png');(O/'pixel-grids.json').write_text(json.dumps({'grids':grids,'variants':manifest},ensure_ascii=False,indent=2));(O/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
with zipfile.ZipFile(O/'new-swords-review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in T.glob('*.png'):z.write(p,'textures/'+p.name)
 z.write(O/'pixel-grids.json','pixel-grids.json');z.write(__file__,'create.py')
print('2 existing swords, 16px, original grip/guard geometry preserved; review only')
