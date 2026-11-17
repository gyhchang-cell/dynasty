"""Editable native 16px grid for the existing pojun_axe; no new item IDs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib,io,zipfile
R=Path(__file__).resolve().parents[3];O=R/'docs/art/axe-study-v12';T=O/'textures';T.mkdir(exist_ok=True)
# Wide single cutting face, a short back lug, and an uninterrupted diagonal shaft.
grid=[
'................',
'......oooo......',
'.....ohhhmo.....',
'....ohhmmmso....',
'...ohhmmmmsooo..',
'...ohmmmssohbmo.',
'...ohmmssolbso..',
'...ohmssolbdo...',
'....ossoawdo....',
'.....oolwdo.....',
'......lwdo......',
'.....lwdo.......',
'....lwdo........',
'...lwdo.........',
'..lwdo..........',
'...do...........']
pal={'.':(0,0,0,0),'o':(36,43,48,255),'h':(217,228,220,255),'m':(143,165,163,255),'s':(83,109,112,255),'b':(180,143,71,255),'a':(206,170,89,255),'l':(162,118,54,255),'w':(107,76,35,255),'d':(53,40,24,255)}
assert len(grid)==16 and all(len(r)==16 for r in grid)
im=Image.new('RGBA',(16,16))
for y,row in enumerate(grid):
 for x,c in enumerate(row):im.putpixel((x,y),pal[c])
im.save(T/'pojun_axe.png')
old=Image.open(R/'docs/art/weapon-tier-v11/textures/pojun_axe.png').convert('RGBA')
f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',24);sm=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18)
c=Image.new('RGB',(960,490),'#30383e');d=ImageDraw.Draw(c)
for i,(pic,title) in enumerate([(old,'上一稿'),(im,'破军战斧 · 大刃面'),(im,'纯黑剪影')]):
 x=35+i*310;d.text((x,20),title,font=f,fill='#f0e4c8')
 if i==2:
  pic=pic.copy();pic.paste((0,0,0,255),(0,0,16,16),pic.getchannel('A'))
 enlarged=pic.resize((256,256),Image.Resampling.NEAREST);c.paste(enlarged,(x,70),enlarged)
 d.text((x,353),'物品栏大小',font=sm,fill='#cbd4d8')
 for j,s in enumerate([16,32,48]):
  a=pic.resize((s,s),Image.Resampling.NEAREST);c.paste(a,(x+j*70,390),a)
d.text((35,455),'现有物品 pojun_axe；其他八件保留；透明底原生16×16',font=sm,fill='#d8dfdf');c.save(O/'review.png')
# Eight approved designs are frozen, independent of future axe revisions.
freeze={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'docs/art/weapon-tier-v11/textures').glob('*.png') if p.stem!='pojun_axe'}
(O/'approved-eight.json').write_text(json.dumps(freeze,indent=2))
(O/'pixel-source.json').write_text(json.dumps({'existing_id':'pojun_axe','grid':grid,'palette':pal},indent=2))
oldhead=sum(old.getpixel((x,y))[3]>0 for y in range(8) for x in range(16))
newhead=sum(im.getpixel((x,y))[3]>0 for y in range(8) for x in range(16))
points={(x,y) for y in range(16) for x in range(16) if im.getpixel((x,y))[3]}
seen=set();todo=[next(iter(points))]
while todo:
 q=todo.pop()
 if q in seen:continue
 seen.add(q)
 todo.extend((q[0]+dx,q[1]+dy) for dx in [-1,0,1] for dy in [-1,0,1] if (q[0]+dx,q[1]+dy) in points-seen)
assert seen==points
(O/'checks.json').write_text(json.dumps({'size':[16,16],'alpha_values':sorted(set(im.getchannel('A').getdata())),'connected_silhouette':True,'upper_eight_rows_old_pixels':oldhead,'upper_eight_rows_new_pixels':newhead,'approved_other_textures_unchanged':all(hashlib.sha256((R/'docs/art/weapon-tier-v11/textures'/n).read_bytes()).hexdigest()==h for n,h in freeze.items()),'game_tested':False},indent=2))
(O/'index.html').write_text('<meta charset="utf-8"><title>破军战斧·大刃面</title><style>body{background:#30383e;color:#eee;font:18px sans-serif;margin:30px}img{max-width:100%;image-rendering:pixelated}</style><h1>破军战斧</h1><p>加大斧头、完整刃面、短尾榫、斜向木柄。现有物品，没有新增注册。</p><img src="review.png"><p>参考整理：550候选，剔除28张部件/蒙版等后522张，71个非原版模组命名空间，含材质与版本变体，并非522种原创造型。未达到100模组/1000张要求。</p>')
print('upper head pixels',oldhead,'->',newhead)
