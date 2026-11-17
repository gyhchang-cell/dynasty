"""Original editable pixel polygons; review variants of existing IDs only."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[3];O=R/'docs/art/weapons-existing-v6';T=O/'textures';T.mkdir(exist_ok=True)
for p in T.glob('lie_gong*.png'):p.unlink()
old=R/'docs/art/weapons-twenty-v5';spec=json.loads((old/'design-source.json').read_text());manifest=[];checks=[]
lang=json.loads((R/'src/main/resources/assets/dynasty/lang/zh_cn.json').read_text())
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'src/main/resources/assets/dynasty/textures/item').glob('*.png')}
def save(im,n,group,idea,frame=''):
 assert 'item.dynasty.'+n in lang,n
 im.save(T/(n+frame+'.png'))
 assert set(im.getchannel('A').getdata())<={0,255}
 if not frame:manifest.append(dict(id=n,name=lang['item.dynasty.'+n],group=group,idea=idea,size=list(im.size)))
def poly(d,pts,fill):d.polygon(pts,fill='#'+fill)
# Pixel-coordinate silhouettes: five distinct lengths, widths, tips and guards.
forms=[
('yuchang_dagger','短身宽叶 · 紧凑护手',[(12,19),(13,12),(21,7),(24,7),(24,10),(19,18)],'A3C5BC','E1EEE0'),
('juque_sword','厚脊重剑 · 方肩宽刃',[(12,21),(9,16),(23,2),(28,2),(28,7),(16,22)],'8F9AA4','D9DDD7'),
('longyuan_sword','修长直刃 · 双翼护手',[(12,20),(11,17),(27,1),(29,1),(29,3),(15,20)],'6B9CB6','D4E6E7'),
('liuyun_sword','偏锋弧刃 · 扫尾剑尖',[(12,21),(12,16),(18,11),(25,6),(29,1),(28,9),(23,14),(17,20)],'9AAEB6','EDF0DF'),
('peach_sword','宽身木剑 · 平肩符刃',[(12,21),(10,17),(23,4),(27,3),(27,7),(16,22)],'B77A4A','DDB783')]
for n,idea,blade,mid,light in forms:
 im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
 # diagonal two-pixel grip, solid stepped guard, squared pommel
 poly(d,[(3,26),(10,19),(13,22),(6,29)],'302C30');d.line([(5,27),(11,21)],fill='#9C6947',width=3);d.line([(5,26),(10,21)],fill='#C1935A',width=1)
 poly(d,blade,'303A42');inner=[(x,y) for x,y in blade];d.line([blade[0],blade[1],blade[2]],fill='#'+mid,width=3)
 # fill an inset taper with deliberate discrete metal bands
 if n=='yuchang_dagger':poly(d,[(14,17),(15,13),(22,8),(22,10),(18,16)],mid);d.line([(14,15),(21,9)],fill='#'+light,width=2)
 elif n=='liuyun_sword':poly(d,[(14,18),(15,16),(24,9),(28,3),(27,9),(21,15)],mid);d.line([(15,16),(23,10),(28,3)],fill='#'+light,width=2)
 else:
  d.line([(13,18),(25,6)],fill='#'+mid,width=4 if n!='longyuan_sword' else 2);d.line([(12,17),(25,4)],fill='#'+light,width=2)
 poly(d,[(7,16),(9,15),(17,23),(17,25),(15,25),(7,18)],'493D32');d.line([(8,16),(16,24)],fill='#B99A57',width=2)
 d.rectangle((3,27,5,29),fill='#B99A57')
 if n=='longyuan_sword':d.line([(7,16),(6,13)],fill='#B99A57',width=2);d.line([(17,24),(20,25)],fill='#B99A57',width=2)
 if n=='peach_sword':d.line([(17,13),(19,15)],fill='#71392F',width=2);d.line([(20,10),(22,12)],fill='#71392F',width=2)
 save(im,n,'forms',idea)
# Higher-tier swords: keep every accepted base pixel, add substantial joined guard shapes.
styles=[('sword_silver','银翼护手 · 黑柄',[(2,9),(5,9),(7,12),(7,15),(4,13)] ,[(17,23),(20,23),(23,26),(23,29),(20,28)]),('sword_jade','玉叶护手 · 双瓣',[(2,9),(5,10),(8,14),(6,16),(3,13)],[(16,23),(18,22),(22,25),(23,29),(19,28)]),('qinggang_sword','回钩剑格 · 青钢肩',[(2,8),(5,8),(5,11),(8,14),(6,16),(2,12)],[(16,23),(18,21),(21,25),(25,25),(25,28),(20,28)]),('yitian_sword','展翼剑格 · 紫银饰',[(1,7),(4,8),(8,13),(7,16),(4,13)],[(16,23),(19,22),(23,26),(26,30),(22,29)]),('supreme_sword','金色仪仗格 · 朱玉',[(1,9),(5,9),(8,12),(8,16),(5,15),(3,12)],[(16,22),(20,22),(23,25),(25,25),(25,29),(21,29),(18,26)])]
for n,idea,a,b in styles:
 base=Image.open(old/'textures'/f'{n}.png').convert('RGBA');im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im);s=next(s for s in spec['swords'] if s[0]==n);met=s[2].split()
 for shape in [a,b]:poly(d,shape,met[0]);d.line(shape[:3],fill='#'+met[4],width=2)
 im.alpha_composite(base)
 # Jewel stays on hilt; extra silhouette stays outside blade.
 if n in ['sword_jade','supreme_sword']:
  d=ImageDraw.Draw(im);d.rectangle((8,18,10,20),fill='#396D59' if n=='sword_jade' else '#A94336');d.point((8,18),fill='#E5C981')
 save(im,n,'advanced-swords',idea)
 checks.append({'id':n,'base_silhouette_retained':all(not base.getpixel((x,y))[3] or im.getpixel((x,y))[3] for y in range(32) for x in range(32)),'added_pixels':sum(im.getpixel((x,y))[3]>0 and not base.getpixel((x,y))[3] for y in range(32) for x in range(32))})
# Existing five bows, including low-tier hunter: restrained rank-relative decoration.
for n,idea,shape in [('lie_gong','铜箍弓臂 · 反曲短角','horn'),('luoyan_bow','外翻雁羽 · 银白弓梢','feather'),('tianlang_bow','狼牙反曲 · 蓝灰骨饰','fang'),('sunbow','日轮金翼 · 铜金弓臂','sun'),('zhuque_bow','双层火羽 · 朱金弓梢','flame')]:
 s=next(s for s in spec['bows'] if s[0]==n);pal=s[2].split();acc=s[3].split()
 for frame in range(4):
  suffix='' if not frame else f'_pulling_{frame-1}';base=Image.open(old/'textures'/(n+suffix+'.png')).convert('RGBA').resize((32,32),Image.Resampling.NEAREST)
  im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
  # Limb positions measured per draw stage, no decoration on string/arrow.
  for yy in [6,18]:
   xs=[x for x in range(32) if base.getpixel((x,yy))[:3] in [tuple(bytes.fromhex(z)) for z in pal] and base.getpixel((x,yy))[3]]
   if not xs:continue
   xx=min(xs)
   points={'horn':[(1,2),(-3,2),(-4,0),(-4,-3),(-2,-3),(-2,-1),(1,0)],'feather':[(1,2),(-3,1),(-6,-4),(-3,-3),(1,0)],'fang':[(1,2),(-4,1),(-6,-3),(-5,-5),(-2,-1),(1,0)],'sun':[(1,2),(-3,2),(-5,0),(-5,-3),(-3,-5),(-2,-2),(1,0)],'flame':[(1,2),(-3,1),(-6,-2),(-6,-5),(-3,-3),(-2,-5),(-1,-2),(2,0)]}[shape]
   pts=[(max(0,xx+dx),max(0,yy+dy)) for dx,dy in points];poly(d,pts,pal[0]);d.line(pts[:3],fill='#'+acc[1],width=2);d.line(pts[-3:],fill='#'+acc[2],width=1)
  im.alpha_composite(base);save(im,'shenbi_bow' if n=='lie_gong' else n,'advanced-bows',idea,suffix)
  assert all(not base.getpixel((x,y))[3] or im.getpixel((x,y))==base.getpixel((x,y)) for y in range(32) for x in range(32))
  checks.append({'id':('shenbi_bow' if n=='lie_gong' else n)+suffix,'all_accepted_pixels_unchanged':True,'added_pixels':sum(im.getpixel((x,y))[3]>0 and not base.getpixel((x,y))[3] for y in range(32) for x in range(32))})
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22);small=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',16)
for group in ['forms','advanced-swords','advanced-bows']:
 rows=[m for m in manifest if m['group']==group];c=Image.new('RGB',(1400,360),'#252F37');d=ImageDraw.Draw(c)
 for i,m in enumerate(rows):
  x=i*280;d.rectangle((x+8,8,x+271,350),fill='#354149');im=Image.open(T/(m['id']+'.png'));im=im.resize((256,256),Image.Resampling.NEAREST);c.paste(im,(x+12,9),im);d.text((x+16,275),m['name'],font=font,fill='#EDDCB3');d.text((x+16,311),m['idea'],font=small,fill='#C5D4D8')
 c.save(O/(group+'.png'))
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items())
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(O/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));(O/'runtime-before-sha256.json').write_text(json.dumps(protected,indent=2))
with zipfile.ZipFile(O/'existing-weapons-review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in T.glob('*.png'):z.write(p,'textures/'+p.name)
 z.write(Path(__file__),'create.py')
(O/'index.html').write_text('<meta charset="utf-8"><title>现有武器审稿</title><style>body{background:#252f37;color:#eddbb7;font:20px sans-serif;margin:32px}img{width:100%;image-rendering:pixelated}</style><h1>现有武器：五种剑形／五剑／五弓</h1><p>全部对应现有物品。审稿PNG，未覆盖精修原图；神臂弓采用原版弓骨架加铜箍的方案。弓包含四个拉弓阶段。</p>'+''.join('<img src="'+g+'.png">' for g in ['forms','advanced-swords','advanced-bows']))
print('15 existing IDs; 30 review sprites; runtime PNGs unchanged')
