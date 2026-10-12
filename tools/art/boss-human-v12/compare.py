"""Compose captured native frames, with identical crops/scales and explicit effect boundaries."""
from create import *
from PIL import ImageFont
F='/System/Library/Fonts/STHeiti Medium.ttc'
def font(n):return ImageFont.truetype(F,n)
def title(im,text,x,y,n=30):ImageDraw.Draw(im).text((x,y),text,font=font(n),fill=(36,43,47))
def raw(path):return Image.open(path).convert('RGB')
REF=D/'reference-native/power-reference-round1';OWN=D/'reference-native/power-own-complete';FX=OWN;NAT=D/'native/human-v12-complete'
# All three pairs share this exact crop. It removes empty sky, not relative world scale.
CROP=(650,400,2350,1350)
pairs=[('ignis',IDS[0],'Ignis：厚甲、兵器和防护构成战斗三角'),('scylla',IDS[1],'Scylla：武器前置，头部和海族身份形成方向'),('maledictus',IDS[2],'Maledictus：主体/外围结构与非对称战备')]
for effects,suffix in [(False,'off'),(True,'on')]:
 if effects and not (FX/'PASS.txt').exists():continue
 board=Image.new('RGB',(3400,3370),(232,233,228));title(board,'灾变 3.27 / Dynasty V12 · 原生游戏对照',30,22,42)
 title(board,'相机均12m / FOV70 / 视高1.62m / 45° / 同裁切，无人物单独缩放；日间，无光影资源包',30,80,27)
 title(board,'左：灾变自带发光/翼效/天空效果保留。右：Dynasty独立气场'+('开启' if effects else '关闭')+'。静态受控展示，不冒充自然战斗。',30,120,26)
 for i,(ref,id,note) in enumerate(pairs):
  y=180+i*1030;title(board,note,30,y,32);title(board,NAMES[id]+' / 保留既有约3格人形主体',1730,y,32)
  board.paste(raw(REF/f'cataclysm_{ref}-45.png').crop(CROP),(0,y+65));board.paste(raw(OWN/f'dynasty_{id}-45-{suffix}.png').crop(CROP),(1700,y+65))
 title(board,'灾变美术归原作者所有，仅作画面对照。左右模型与材质均为各自运行资源；未复制任何灾变资产到Dynasty。',30,3300,26)
 board.save(D/f'comparison-cataclysm-v12-{suffix}.png')
# Eight actually viewed references. Leviathan gets an explicitly labelled full-body camera.
refs=['ender_guardian','netherite_monstrosity','ignis','the_harbinger','the_leviathan','ancient_remnant','maledictus','scylla'];names=['末影守卫','下界合金巨兽','焰魔 Ignis','先驱者 Harbinger','利维坦 Leviathan','远古遗魂 Ancient Remnant','咒翼 Maledictus','斯库拉 Scylla']
board=Image.new('RGB',(3200,1520),(232,233,228));title(board,'灾变3.27 · 实际查看的八只主Boss · 静音独立Forge世界',24,15,34)
for i,(id,name) in enumerate(zip(refs,names)):
 x=i%4*800;y=70+i//4*690
 p=(D/'reference-native/reference-leviathan-full' if id=='the_leviathan' else REF)/f'cataclysm_{id}-45.png'
 board.paste(raw(p).resize((800,514),Image.Resampling.NEAREST),(x,y));title(board,name,x+12,y+525,25);title(board,('32m全身构造补图，不作同尺度比较' if id=='the_leviathan' else '12m / 1.62m视高 / FOV70 / 45°'),x+12,y+562,22)
 title(board,'NoAI待机；自带发光/粒子和天空色仍在',x+12,y+599,20)
board.save(D/'reference-eight.png')
# Same-camera, same-production-resource native before/after; keep full player proportions.
for i,id in enumerate(IDS):
 for view,j in [('front',0),('45',2),('side',4)]:
  stem=f'{i*14+j:02d}-{id}-{view}-off.png';old=R/'docs/art/boss-human-v11/native/human-v11-verified'/stem;new=NAT/stem
  out=Image.new('RGB',(2800,1080),(232,233,228))
  for k,(p,label) in enumerate([(old,'V11'),(new,'V12')]):
   title(out,NAMES[id]+' / '+label+' / 相同6m机位 / 独立气场关闭',k*1400+12,12,27);out.paste(raw(p).resize((1400,900),Image.Resampling.NEAREST),(k*1400,60))
  title(out,'完整原生图等比例缩小，未单独缩放角色；控制回放中保留原有技能次级效果；最终夹具排除环境背景事件。',20,1000,26);out.save(D/id/f'native-before-after-{view}.png')
 for view,j in [('front',0),('45',2),('side',4),('back',6)]:
  out=Image.new('RGB',(2800,1050),(232,233,228))
  for k,fx in enumerate(['off','on']):
   title(out,NAMES[id]+' / '+view+' / 独立气场'+('关闭' if k==0 else '开启'),k*1400+15,12,28);out.paste(raw(NAT/f'{i*14+j+k:02d}-{id}-{view}-{fx}.png').resize((1400,900),Image.Resampling.NEAREST),(k*1400,55))
  title(out,'同机位/比例/日光；各次捕获有独立待机相位。on/off针对BossHumanAura，原有技能特效未改。',15,995,24);out.save(D/id/f'fx-{view}-compare.png')
# Native player/Boss reference from clean 12m fixtures; one shared crop for all.
over=Image.new('RGB',(2550,1090),(232,233,228))
for i,id in enumerate(IDS):
 title(over,NAMES[id]+' / 原生关闭气场',i*850+16,12,27);over.paste(raw(OWN/f'dynasty_{id}-45-off.png').crop(CROP).resize((850,475),Image.Resampling.NEAREST),(i*850,70));over.paste(raw(NAT/f'{i*14+10:02d}-{id}-attack-contact.png').resize((850,546),Image.Resampling.NEAREST),(i*850,545))
over.save(D/'native-overview.png')
print('Native comparisons preserve crop/scale, references credited; no foreign model/texture import.')

# The complete eight-reference + three-own contact sheet, without actor-specific enlargement.
board=Image.new('RGB',(3200,2300),(232,233,228));board.paste(raw(D/'reference-eight.png'),(0,0))
title(board,'Dynasty V12 · 同12m机位 / 三位既有人形首领 / 自身气场开启',24,1530,34)
for i,id in enumerate(IDS):
 x=i*800;p=OWN/f'dynasty_{id}-45-on.png';board.paste(raw(p).resize((800,514),Image.Resampling.NEAREST),(x,1600));title(board,NAMES[id],x+12,2130,26);title(board,'约3格主体；武器/背部结构保持世界尺度',x+12,2170,20)
title(board,'同FOV、视高、基础日光',2420,1660,26);title(board,'未放大我们的角色',2420,1710,26);title(board,'外部模型/PNG未复制',2420,1760,26);title(board,'利维坦32m补图明确标注',2420,1810,23);title(board,'自然战斗演出不在静态验收内',2420,1860,23)
board.save(D/'comparison-eight-v12.png')
