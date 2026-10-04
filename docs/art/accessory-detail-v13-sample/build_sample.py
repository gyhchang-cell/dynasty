"""One original 32x32 copper mirror sample; integer pixels only, no source installation.
The existing project item is already specified at 32x32. This redraw uses that space
for a stepped copper rim and broad mirror planes, not supersampling or filters.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil
DOC=Path(__file__).resolve().parent
ROOT=DOC.parents[2]
OUT=DOC/'candidate/assets/dynasty/textures/item'
OUT.mkdir(parents=True,exist_ok=True)
old=ROOT/'docs/art/accessory-detail-v12-sample/candidate/assets/dynasty/textures/item/bronze_mirror.png'
src=ROOT/'src/main/resources/assets/dynasty/textures/item/bronze_mirror.png'
model=ROOT/'src/main/resources/assets/dynasty/models/item/bronze_mirror.json'
back=DOC/'before';back.mkdir(exist_ok=True)
records=[]
for p,label in [(src,'source-32.png'),(old,'v12-32.png'),(model,'bronze_mirror.json')]:
    target=back/label
    if not target.exists():shutil.copy2(p,target)
    assert target.read_bytes()==p.read_bytes()
    records.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'backup':str(target.relative_to(DOC))})

# A new native 32px pattern, keeping the mirror subject and readable circular face.
# Seven warm copper colors, five grey-green glass colors, two dark red cord colors.
C={'a':'3e342b','b':'61503c','c':'88623d','d':'af8148','e':'cfa665','f':'e6c580','m':'f3dda4',
   'g':'345b55','h':'57887b','i':'84b09a','j':'b4d1b3','k':'e0e5c6',
   'r':'683c32','s':'a16443'}
C={k:'#'+v for k,v in C.items()}
im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
def line(a,b,c):d.line((*a,*b),fill=C[c])
def rect(box,c):d.rectangle(box,fill=C[c])
def poly(points,c):d.polygon(points,fill=C[c])
# Stepped bronze short handle with a two-color binding, set behind the body.
poly([(12,23),(18,23),(18,26),(17,27),(17,29),(16,30),(14,30),(13,29),(13,27),(12,26)],'a')
rect((14,25,16,29),'d');line((14,25),(14,28),'f');line((16,25),(16,29),'c')
rect((13,27,17,28),'r');line((13,27),(16,27),'s');line((14,29),(15,29),'e')
# The body outline is raster-authored, not a perspective sphere.
spans={2:(12,18),3:(9,21),4:(7,23),5:(6,24),6:(5,25),7:(4,26),
       8:(3,27),9:(3,27),10:(2,28),11:(2,28),12:(2,28),13:(2,28),
       14:(2,28),15:(2,28),16:(2,28),17:(2,28),18:(3,27),19:(3,27),
       20:(4,26),21:(4,26),22:(5,25),23:(6,24),24:(8,22),25:(11,19)}
for y,(left,right) in spans.items():
    line((left,y),(right,y),'a')
    if 3<=y<=24:line((left+1,y),(right-1,y),'c')
poly([(10,4),(20,4),(24,7),(26,10),(27,13),(26,18),(24,21),(21,23),(18,24),(11,23),(7,21),(4,17),(4,10),(7,6)],'d')
poly([(10,4),(20,4),(23,6),(23,7),(10,6),(7,9),(6,12),(5,18),(4,16),(4,10),(7,6)],'e')
line((10,4),(18,4),'f');line((8,5),(10,5),'m');line((6,7),(7,7),'f')
line((4,10),(4,14),'f');line((5,9),(5,10),'m')
# Retain copper body color on the lower right, with a narrow dark back edge.
poly([(25,8),(27,10),(27,17),(25,21),(22,23),(19,24),(11,24),(9,23),(19,22),(23,19),(25,15)],'b')
line((10,23),(19,23),'d');line((22,21),(24,19),'d');line((26,12),(26,16),'d')
# Three copper ridges organize the frame. Engraving is confined to two short sectors.
poly([(12,6),(19,6),(22,8),(24,11),(24,17),(22,20),(19,22),(12,22),(9,20),(7,17),(7,12),(9,9)],'b')
line((11,7),(18,7),'f');line((9,9),(10,8),'e');line((8,11),(8,12),'e')
line((10,20),(12,22),'e');line((12,22),(18,22),'f');line((20,21),(22,19),'e')
# Two original step-shaped shallow carvings, not someone else's emblem.
for pts,col in [([(7,16),(5,16),(5,18),(7,18),(7,20),(9,20)],'c'),
                ([(6,16),(6,17),(8,17),(8,19)],'f'),
                ([(22,6),(22,8),(24,8),(24,10)],'b'),
                ([(22,7),(23,7),(23,9)],'f')]:
    for u,v in zip(pts,pts[1:]):line(u,v,col)
# Mirror plate: smooth material expressed by connected stepped shapes, no blur.
glass=[(12,8),(18,8),(21,10),(23,12),(23,16),(21,19),(18,21),(12,21),(10,19),(8,17),(8,12),(10,10)]
poly(glass,'h')
poly([(12,8),(18,8),(21,10),(22,12),(21,14),(19,14),(19,16),(17,16),(17,18),(15,18),(14,20),(11,19),(9,17),(9,12),(10,10)],'i')
poly([(12,8),(17,8),(18,9),(16,11),(14,11),(14,13),(12,13),(12,15),(10,15),(9,16),(9,12),(10,10)],'j')
poly([(12,8),(16,8),(16,9),(13,9),(13,11),(11,11),(11,13),(10,13),(10,11)],'k')
poly([(23,13),(23,16),(21,19),(18,21),(12,21),(11,20),(16,20),(19,18),(21,15)],'g')
poly([(18,12),(20,10),(21,11),(20,13),(18,15),(16,17),(15,17),(16,15)],'j')
line((18,13),(19,12),'k')
# Small interruption in the reflection and a quiet lower plane keep it from a solid blob.
poly([(12,17),(14,15),(15,15),(14,17),(13,18),(12,18)],'h')
line((17,19),(19,17),'i')
# A tiny top inset and base clasp distinguish the accessory from a plain coin.
rect((13,3,17,6),'b');line((13,3),(17,3),'f');line((13,4),(13,5),'e')
rect((14,4,16,5),'g');line((14,4),(15,4),'j');line((14,5),(15,5),'h')
rect((13,23,17,24),'c');line((13,23),(17,23),'e');line((14,24),(16,24),'d')
im.save(OUT/'bronze_mirror.png')

alpha=set(im.getchannel('A').getdata());colors=len({p[:3] for p in im.getdata() if p[3]})
assert im.size==(32,32) and alpha=={0,255} and colors<=14
assert all(v==0 for v in im.getchannel('A').crop((0,0,32,1)).getdata())
assert model.read_bytes()==(back/'bronze_mirror.json').read_bytes()
md=json.loads(model.read_text());assert md['parent']=='item/generated' and md['textures']['layer0']=='dynasty:item/bronze_mirror'

# Side by side at equal display size. Asset above is drawn at 32; resizing below is QA only.
font='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
f=ImageFont.truetype(font,23);s=ImageFont.truetype(font,16);t=ImageFont.truetype(font,13)
sheet=Image.new('RGB',(980,620),'#eeeae0');p=ImageDraw.Draw(sheet)
p.text((28,20),'铜镜 · 再精修一版',font=f,fill='#29392f')
p.text((28,56),'细化铸铜边饰、嵌玉顶扣与镜面分区，仍按 32×32 原生像素绘制。',font=s,fill='#65715f')
for x,image,title,desc in [(28,Image.open(old).convert('RGBA'),'上一张 · 32×32','12 色 / 8 倍最近邻'),(362,im,'精修稿 · 32×32','14 色 / 8 倍最近邻')]:
    p.text((x,104),title,font=f,fill='#29392f')
    for yy in range(16):
        for xx in range(16):p.rectangle((x+xx*16,149+yy*16,x+xx*16+15,149+yy*16+15),fill=('#d8ded0','#c7cfbd')[(xx+yy)%2])
    enlarged=image.resize((256,256),Image.Resampling.NEAREST);sheet.paste(enlarged,(x,149),enlarged)
    p.text((x,421),desc,font=t,fill='#65715f')
    sheet.paste(image,(x+6,466),image);p.text((x+52,470),'1× 原尺寸',font=t,fill='#65715f')
x=694;p.text((x,104),'新稿小图检查',font=f,fill='#29392f')
for j,size in enumerate([16,32,64]):
    y=157+j*83;bg='#393f3b' if j%2==0 else '#a5aba0'
    p.rectangle((x,y,x+72,y+72),fill=bg)
    pic=im.resize((size,size),Image.Resampling.NEAREST);sheet.paste(pic,(x+(72-size)//2,y+(72-size)//2),pic)
    p.text((x+91,y+23),f'{size}px 显示',font=t,fill='#65715f')
p.line((28,534,952,534),fill='#c0cabb')
p.text((28,552),'新增图按 32×32 网格直接绘制；0 / 255 透明，无模糊、半透明毛边或发光特效。',font=t,fill='#65715f')
p.text((28,582),'源文件与上一版均保留。样稿未接入，尚未游戏内实测。',font=t,fill='#65715f')
sheet.save(DOC/'comparison.png')
report={'id':'dynasty:bronze_mirror','status':'single_sample_waiting_for_user_style_confirmation','size':[32,32],
        'reason_for_32':'Existing source item is 32x32; user requested slightly more detailed accessory sample. Refined copper sectors, top jade clasp, mirror planes and handle binding; resolution remains 32 and block resolution unchanged.',
        'colors':colors,'alpha':sorted(alpha),'model':'item/generated','layer0':'dynasty:item/bronze_mirror',
        'candidate':'candidate/assets/dynasty/textures/item/bronze_mirror.png',
        'target_if_later_approved':'src/main/resources/assets/dynasty/textures/item/bronze_mirror.png',
        'candidate_sha256':hashlib.sha256((OUT/'bronze_mirror.png').read_bytes()).hexdigest(),
        'baseline':records,'source_and_previous_unchanged':True,'installed':False,'in_game_test':False,
        'batch_authorization':'Pending. User explicitly requested this sample first; do not start bulk work until approval arrives.'}
(DOC/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(DOC/'README.md').write_text('''# 铜镜 32×32 单件细节样张

本轮只做 `dynasty:bronze_mirror` 一件。用户要求在 v12 基础上再精修，先看样张，确认后再开始剩余饰品和方块。

新 PNG 原生 32×32、14 个可见颜色、透明度仅 0/255。现有铜镜源资源本来就是 32×32，沿用实际 `item/generated` / `dynasty:item/bronze_mirror` 关系，无需改模型。本次像素用于铸铜边饰、嵌玉顶扣、短柄缠绳与更清楚的镜面分区；不是把旧图直接放大，也没有高分辨率生成后缩小。

- `comparison.png`：上一版与新样张的等大最近邻预览，附各自原尺寸及16/32/64px显示检查。
- `candidate/assets/dynasty/textures/item/bronze_mirror.png`：可用 PNG，未安装。
- `before/`：当前源 PNG、v12 PNG 与源模型的备份。
- `manifest.json`：尺寸、色数、哈希、准确引用和待确认状态。

像素绘制脚本只写本目录。未修改源文件、之前成品、公共注册、并行任务或游戏实例。尚未游戏内实测。

后续约定：等待用户对本样张风格的同意后，再重新核对项目文档、实际资源和此前任务完成记录，只处理剩余未完成或仍不合适的内容；保留之前已做好的饰品和方块。方块继续原生16×16，不因这一个饰品样张升到32×32。
''')
print(json.dumps({'png':str(OUT/'bronze_mirror.png'),'colors':colors,'alpha':sorted(alpha),'status':'ONE_SAMPLE_ONLY'},ensure_ascii=False))
