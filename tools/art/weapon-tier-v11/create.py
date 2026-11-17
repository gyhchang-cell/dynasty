from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import io,json,zipfile,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/art/weapon-tier-v11';T=O/'textures';T.mkdir(exist_ok=True);A=R/'src/main/resources/assets/dynasty'
jar=zipfile.ZipFile('/Users/a15356015027/Public/.minecraft/versions/1.20.1/1.20.1.jar')
def vanilla(n):return Image.open(io.BytesIO(jar.read('assets/minecraft/textures/item/'+n+'.png'))).convert('RGBA')
def rgba(h):return tuple(bytes.fromhex(h))+(255,)
wood=[(73,54,21),(137,103,39),(104,78,30),(40,30,11)]
checks=[]
for n,colors,orn in [('lie_gong',['493615','A47A36','745326','281E0B'],'leather'),('luoyan_bow',['45515B','BFCBCC','7C969F','28343D'],'feather'),('tianlang_bow',['303B55','A1B6C9','5C718D','1D273D'],'fang')]:
 for stage in range(4):
  src=vanilla('bow' if not stage else f'bow_pulling_{stage-1}');im=src.copy()
  for y in range(16):
   for x in range(16):
    col=src.getpixel((x,y))
    if col[3] and col[:3] in wood:im.putpixel((x,y),rgba(colors[wood.index(col[:3])]))
  # Local winding on existing grip, plus two sparse outer limb details.
  for y in [5,7]:
   for x in range(2,7):
    if src.getpixel((x,y))[:3] in wood:im.putpixel((x,y),rgba('AD8054' if n=='lie_gong' else 'A6A7B8'))
  for y in [3,9]:
   xs=[x for x in range(16) if src.getpixel((x,y))[:3] in wood]
   if not xs or orn=='leather':continue
   x=min(xs)
   shape=[(-1,0),(-2,-1),(-2,-2)] if orn=='feather' else [(-1,0),(-2,0),(-3,-1),(-3,-2)]
   for dx,dy in shape:
    q=(x+dx,y+dy)
    if 0<=q[0]<16 and 0<=q[1]<16 and not src.getpixel(q)[3]:im.putpixel(q,rgba('DEE4CF' if orn=='feather' else 'C7D8E0'))
  assert all(not src.getpixel((x,y))[3] or im.getpixel((x,y))[3] for y in range(16) for x in range(16))
  assert all(src.getpixel((x,y))!= (68,68,68,255) or im.getpixel((x,y))==(68,68,68,255) for y in range(16) for x in range(16))
  dest=n+('' if not stage else f'_pulling_{stage-1}');im.save(T/f'{dest}.png');checks.append({'id':dest,'original_bow_body':True,'original_string_pixels':True})
# Approved long angled stone-Ge pixel design, now mapped to actual shi_ge ID.
source=json.loads((R/'docs/art/weapons-nine-v4/pixel-sources.json').read_text());grid=source['tool_grids']['stone_ge'];pal={k:tuple(v) for k,v in source['tool_palette'].items()}
im=Image.new('RGBA',(16,16))
for y,row in enumerate(grid):
 for x,c in enumerate(row):im.putpixel((x,y),pal[c])
im.save(T/'shi_ge.png')
# Jade pick: vanilla handle and recognisable pick structure; inset gold collar.
im=vanilla('iron_pickaxe');metal={ (68,68,68):'3F6651',(255,255,255):'EBF3C8',(24,24,24):'243B31',(190,190,190):'83AC81',(216,216,216):'BCD19F',(107,107,107):'5C8267',(150,150,150):'98B389'}
for y in range(16):
 for x in range(16):
  col=im.getpixel((x,y))
  if col[3] and col[:3] in metal:im.putpixel((x,y),rgba(metal[col[:3]]))
for q in [(9,5),(10,6)]:
 if im.getpixel(q)[3]:im.putpixel(q,rgba('C6A663'))
im.save(T/'pickaxe_jade.png')
# Split-lug battle axe: a broad crescent edge, rivet and long native stepped shaft.
grid=['................','......oooo......','.....ohmmmo.....','....ohmmmso.....','....ohmmsso.....','.....omsso......','......osoboo....','.......olbmo....','.......lwdo.....','......lwdo......','.....lwdo.......','....lwdo........','...lwdo.........','..lwdo..........','.lwdo...........','..do............']
im=Image.new('RGBA',(16,16))
for y,row in enumerate(grid):
 for x,c in enumerate(row):im.putpixel((x,y),pal[c])
im.save(T/'pojun_axe.png')
rows=[('sword_bronze','青铜剑',1,'铁剑＋青铜＋图纸'),('sword_silver','官银剑',2,'玉笛之后，银锭＋图纸'),('sword_jade','玉剑',2,'官银剑＋玉＋图纸'),('lie_gong','猎弓',0,'木棍＋线，开局弓'),('luoyan_bow','落雁弓',2,'神臂弓＋精钢＋官银'),('tianlang_bow','天狼弓',3,'落雁弓＋龙晶＋精钢'),('shi_ge','石戈',0,'木矛＋圆石，开局'),('pickaxe_jade','玉镐',2,'玉材料阶段的采掘工具'),('pojun_axe','破军战斧',3,'巨阙＋龙晶＋叛将首级')]
levels=[('基础','#9EA6AB'),('进阶','#76C77B'),('精工','#59BDEC'),('名将','#BB78E4'),('帝兵','#F2BD4C')]
f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20);small=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',15)
c=Image.new('RGB',(1200,1040),'#30383E');d=ImageDraw.Draw(c)
for i,(n,label,tier,why) in enumerate(rows):
 assert (A/f'models/item/{n}.json').exists();x=i%3*400;y=i//3*325
 d.rectangle((x+8,y+8,x+390,y+315),fill='#465058');old=Image.open(A/f'textures/item/{n}.png').convert('RGBA');im=Image.open(T/f'{n}.png').convert('RGBA')
 for j,pic in enumerate([old,im]):
  size=128;pic=pic.resize((size,size),Image.Resampling.NEAREST);px=x+35+j*190;py=y+45;c.paste(pic,(px,py),pic)
  if j:d.rectangle((px-5,py-5,px+132,py+132),outline=levels[tier][1],width=3)
  d.text((px,y+185),'现有' if not j else '新稿 · '+levels[tier][0],font=small,fill='#E7E4D5')
 d.text((x+22,y+222),label,font=f,fill='#F0E6CB');d.text((x+22,y+259),why,font=small,fill='#CBD6DA')
d.text((22,985),'品质框为界面分档示意，不包含在PNG中；本批为审稿，未部署。',font=f,fill='#E8D9B4');c.save(O/'comparison.png')
# Endgame colour examples use accepted/current textures, not repainted originals.
c=Image.new('RGB',(1050,240),'#30383e');d=ImageDraw.Draw(c)
for i,(n,label,tier) in enumerate([('tie_jian','基础·铁剑',0),('sword_bronze','进阶·青铜',1),('sword_jade','精工·玉剑',2),('longyuan_sword','名将·龙渊',3),('tianzi_sword','帝兵·天子',4)]):
 x=i*210;im=Image.open(A/f'textures/item/{n}.png').convert('RGBA').resize((128,128),Image.Resampling.NEAREST);c.paste(im,(x+40,20),im);d.rectangle((x+35,15,x+172,152),outline=levels[tier][1],width=3);d.text((x+25,175),label,font=f,fill=levels[tier][1])
c.save(O/'quality-frames.png')
(O/'quality-plan.json').write_text(json.dumps({'status':'UI review only, not installed','basis':'quest progression + actual crafting prerequisites, no item Rarity mutation','tiers':levels,'items':[dict(id=n,name=label,tier=tier,reason=why) for n,label,tier,why in rows],'endgame_examples':{'longyuan_sword':3,'tianzi_sword':4},'note':'Changing vanilla Rarity affects InfusionTraits maxCapacity; future implementation must be client-only and not modify Rarity.'},ensure_ascii=False,indent=2))
(O/'bow-checks.json').write_text(json.dumps(checks,indent=2));(O/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
with zipfile.ZipFile(O/'nine-item-review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in T.glob('*.png'):z.write(p,'textures/'+p.name)
 z.write(O/'quality-plan.json','quality-plan.json');z.write(__file__,'create.py');z.write(Path(__file__).with_name('swords.py'),'swords.py')
(O/'index.html').write_text('<meta charset="utf-8"><title>武器工具与品质框审稿</title><style>body{background:#30383e;color:#e7e8de;font:20px/1.6 sans-serif;margin:30px}img{max-width:100%;image-rendering:pixelated}</style><h1>三剑、三弓、三工具</h1><p>保留已定稿的特色剑。品质依据任务材料路线、解锁阶段和实际门槛，框为界面方案，未写进物品贴图，也未修改原版Rarity或战斗属性。尚未部署与游戏验收。</p><img src="quality-frames.png"><img src="comparison.png"><p>石戈沿用此前认可的长柄斜头设计，对应实际shi_ge物品。弓全部保留原版主体和弦线，包含三段拉弓。</p><a href="nine-item-review.zip">下载18张PNG及品质方案</a>')
print('9 existing items, 18 PNGs; 12 bow frame checks; quality UI preview only')
