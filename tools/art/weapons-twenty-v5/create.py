"""Extend the accepted editable pixel sources. No generated/high-resolution painting."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,zipfile,io,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/art/weapons-twenty-v5';T=O/'textures';T.mkdir(exist_ok=True)
J=Path('/Users/a15356015027/Public/.minecraft/versions/1.20.1/1.20.1.jar')
def v(n):
 with zipfile.ZipFile(J) as z:return Image.open(io.BytesIO(z.read('assets/minecraft/textures/item/'+n+'.png'))).convert('RGBA')
def c(h):return tuple(bytes.fromhex(h))+(255,)
wood=[(73,54,21),(137,103,39),(104,78,30),(40,30,11)]
steel=[(68,68,68),(255,255,255),(24,24,24),(190,190,190),(216,216,216),(107,107,107),(150,150,150)]
swords=[
('tie_jian','铁剑','404950 F4F5ED 20292F AEBBBF D6DFDC 657078 8F9C9D','3C2B23 A27A4B 70513A 241C19','none',False),
('sword_bronze','青铜剑','63472D E4BE7B 31271F AD7C3F C69A58 7B5833 9A713E','432C21 A67B4C 76543A 281D18','none',False),
('sword_silver','官银剑','536374 F8F4DD 283341 B8CBD2 DCE8E7 7C8D9C A4B6BE','493126 A17B4D 735038 281F1D','silver',False),
('sword_jade','玉剑','325D4F E6F2CB 203E37 70AA83 A3CCA0 497D66 639579','543B29 AE8C4C 7E6238 302820','jade',False),
('qinggang_sword','青釭剑','324D65 E1EDF0 202F42 789FB5 AFCBD5 4E7189 6D8B9E','283849 8092A3 4D6073 1B2632','hook',False),
('yitian_sword','倚天剑','49425F F4EDF4 2B293D A8A0BD D4CCDE 706380 93819F','462D4D A7788E 705270 291E32','wing',False),
('supreme_sword','尚方宝剑','6B512A F8E6AC 352B22 C6A352 E5C66F 917239 AD8C46','50272B B55A49 873A35 2F1C22','seal',False),
('peach_sword','桃木剑','654032 E5B984 382820 A76D47 C28B58 7D5137 935F3B','4C2D26 A56742 75432E 2D1D1B','wood',False),
('xuan_tie_jian','玄铁剑·候选','293B48 B5D0D5 18252E 506E81 7F9BAA 354F62 486578','3D2830 98705C 694744 241C24','heavy',True),
('chi_bing_gang_jian','赤柄钢剑·候选','3D4C56 EEF2E9 202C33 A5BAC3 CFDDE0 647B85 8EA0A5','52282A BD6650 8D3E39 301C21','red',True)]
bows=[
('lie_gong','猎弓','493615 896727 684E1E 281E0B','633728 A76B45 D1AB77','plain',False),
('luoyan_bow','落雁弓','45515B A9B8B8 75858B 28343D','594633 A88D5C E0D7AE','feather',False),
('tianlang_bow','天狼弓','303B55 92A7B5 5C718D 1D273D','6D6572 B0B4C0 DDE4D9','fang',False),
('sunbow','射日弓','6F4321 E8B45A AD7737 39291D','9A4828 D58A41 F4D182','sun',False),
('zhuque_bow','朱雀弓','682C27 D97C46 A44B31 352123','A76A31 E6AE51 F5D18A','flame',False),
('tong_gu_gong','铜箍弓·候选','483020 A57943 785331 281C15','75402D BE754B E1A66E','copper',True),
('qing_zhu_gong','青竹弓·候选','414B24 9AAB54 6C7F38 25301C','63452C A87B48 D0B278','bamboo',True),
('shou_gu_gong','兽骨弓·候选','655F4C D1C8A4 9C987E 393A32','5B3D31 A17B55 D9C5A0','bone',True),
('tie_tai_gong','铁胎弓·候选','454B54 A8B5B8 76848C 292F39','604330 A88552 CBB67C','plates',True),
('xuan_tie_gong','玄铁弓·候选','253847 8BA4B2 4C677B 182531','70513C B08E57 D9C58A','horn',True)]
manifest=[];checks=[]
def add(im,src,x,y,col):
 if 0<=x<im.width and 0<=y<im.height and not src.getpixel((x,y))[3]:im.putpixel((x,y),c(col))
for n,label,met,handle,style,candidate in swords:
 src=v('iron_sword');mp=dict(zip(steel,met.split()))|dict(zip(wood,handle.split()));im=src.copy()
 for y in range(16):
  for x in range(16):
   z=src.getpixel((x,y))
   if z[3] and z[:3] in mp:im.putpixel((x,y),c(mp[z[:3]]))
 for xy in [(3,13),(2,14)]:
  if not im.getpixel(xy)[3]:im.putpixel(xy,c(handle.split()[0]))
 if n=='tie_jian':im=Image.open(R/'docs/art/weapons-nine-v4/textures/iron_jian.png').convert('RGBA')
 if style=='red':im=Image.open(R/'docs/art/weapons-nine-v4/textures/red_jian.png').convert('RGBA')
 if style not in ['none','wood','red']:
  im=im.resize((32,32),Image.Resampling.NEAREST);base=im.copy();accent=met.split()[4];dark=met.split()[0]
  # Extensions around guard retain the accepted blade and full grip.
  pts={'silver':[(3,12),(3,13),(4,11),(17,24),(18,24)],'jade':[(3,11),(4,10),(5,10),(17,25),(18,26),(19,26)],'hook':[(3,11),(3,10),(4,10),(18,25),(19,25),(19,24)],'wing':[(2,10),(3,10),(4,11),(5,11),(17,25),(18,26),(19,27),(20,27)],'seal':[(2,11),(3,10),(4,10),(17,25),(18,25),(18,26),(19,26)],'heavy':[(3,11),(3,12),(2,12),(17,24),(18,25),(18,26)]}[style]
  for x,y in pts:add(im,base,x,y,accent);add(im,base,x,y+1,dark)
  if style=='seal':
   for x,y in [(8,17),(9,17),(9,18),(10,18)]:im.putpixel((x,y),c('BE4940'))
 im.save(T/(n+'.png'));manifest.append({'id':n,'name':label,'type':'sword','candidate':candidate,'size':im.size})
for n,label,pal,binding,style,candidate in bows:
 for frame in range(4):
  source='bow' if frame==0 else f'bow_pulling_{frame-1}';src=v(source);im=src.copy();mp=dict(zip(wood,pal.split()));bind=binding.split()
  for y in range(16):
   for x in range(16):
    z=src.getpixel((x,y))
    if z[:3] in mp and z[3]:im.putpixel((x,y),c(mp[z[:3]]))
    elif z[:3] in [(107,107,107),(150,150,150)] and x<=6 and 4<=y<=8:im.putpixel((x,y),c(bind[0 if z[0]==107 else 1]))
  if style in ['copper','bamboo']:
   approved='copper_bow' if style=='copper' else 'bamboo_bow';suffix='' if not frame else f'_pulling_{frame-1}'
   im=Image.open(R/f'docs/art/weapons-nine-v4/textures/{approved}{suffix}.png').convert('RGBA')
  if style not in ['plain','copper','bamboo']:
   im=im.resize((32,32),Image.Resampling.NEAREST);base=im.copy()
   # Anchor ornaments to the actual wooden limb in EACH pulled frame.
   for yy in [3,9]:
    xs=[x for x in range(16) if src.getpixel((x,yy))[:3] in wood and src.getpixel((x,yy))[3]]
    if not xs:continue
    xx=min(xs)*2;y=yy*2
    patterns={'feather':[(-1,0),(-2,-1),(-3,-2),(-4,-3),(-2,0),(-3,-1)],'fang':[(-1,0),(-2,0),(-3,-1),(-3,-2)],'sun':[(-1,0),(-2,-1),(-2,-2),(-1,-3),(0,-3)],'flame':[(-1,0),(-2,-1),(-3,-2),(-3,-3),(-2,-3),(-1,-4)],'bone':[(-1,0),(-2,-1),(-3,-1),(-3,0),(-2,1)],'plates':[(-1,-1),(-1,0),(-1,1),(-2,-1),(-2,0)],'horn':[(-1,0),(-2,0),(-3,-1),(-4,-2),(-4,-3)]}[style]
    for j,(dx,dy) in enumerate(patterns):add(im,base,xx+dx,y+dy,bind[2 if j%3 else 1])
    for dx,dy in patterns:
     if not im.getpixel((max(0,xx+dx),max(0,y+dy)))[3]:continue
     add(im,im.copy(),xx+dx,y+dy+1,pal.split()[0])
  # No original body pixels erased; string preserved exactly after nearest-neighbor scaling.
  scale=im.width//16;ref=src.resize(im.size,Image.Resampling.NEAREST)
  assert all(not ref.getpixel((x,y))[3] or im.getpixel((x,y))[3] for y in range(im.height) for x in range(im.width))
  stringok=all(im.getpixel((x,y))==ref.getpixel((x,y)) for y in range(im.height) for x in range(im.width) if ref.getpixel((x,y))==(68,68,68,255));assert stringok
  dest=n+('' if not frame else f'_pulling_{frame-1}');im.save(T/(dest+'.png'))
  checks.append({'file':dest+'.png','body_retained':True,'string_identical':True,'added_pixels':sum(im.getpixel((x,y))[3]>0 and not ref.getpixel((x,y))[3] for y in range(im.height) for x in range(im.width))})
  if not frame:manifest.append({'id':n,'name':label,'type':'bow','candidate':candidate,'size':im.size})
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(O/'checks.json').write_text(json.dumps(checks,indent=2));(O/'design-source.json').write_text(json.dumps({'swords':swords,'bows':bows},ensure_ascii=False,indent=2))
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20);small=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',14)
for kind in ['sword','bow']:
 rows=[x for x in manifest if x['type']==kind];can=Image.new('RGB',(1200,570),'#252d34');d=ImageDraw.Draw(can)
 for i,row in enumerate(rows):
  x=i%5*240;y=i//5*285;d.rounded_rectangle((x+7,y+7,x+233,y+278),10,fill='#343e46');im=Image.open(T/(row['id']+'.png')).convert('RGBA');large=im.resize((192,192),Image.Resampling.NEAREST);can.paste(large,(x+24,y+15),large);d.text((x+16,y+217),row['name'],font=font,fill='#eddbb7');d.text((x+16,y+250),('候选稿 · 不新增游戏物品' if row['candidate'] else '现有物品 · 本地替换'),font=small,fill='#c2cacc')
 can.save(O/(kind+'s-review.png'))
print('20 items, 50 PNGs; 40 bow body/string checks passed.')
