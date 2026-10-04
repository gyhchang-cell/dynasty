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
old=ROOT/'docs/art/native16-rework-v11/candidate/assets/dynasty/textures/item/bronze_mirror.png'
src=ROOT/'src/main/resources/assets/dynasty/textures/item/bronze_mirror.png'
model=ROOT/'src/main/resources/assets/dynasty/models/item/bronze_mirror.json'
back=DOC/'before';back.mkdir(exist_ok=True)
records=[]
for p,label in [(src,'source-32.png'),(old,'v11-16.png'),(model,'bronze_mirror.json')]:
    target=back/label
    if not target.exists():shutil.copy2(p,target)
    assert target.read_bytes()==p.read_bytes()
    records.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'backup':str(target.relative_to(DOC))})

# Six copper shades, six grey-green mirror shades. No glow or transparent edge pixels.
C={'a':'403629','b':'635034','c':'8b663b','d':'b18548','e':'d4ac64','f':'ead08c',
   'g':'344e46','h':'4b695b','i':'678977','j':'89a68d','k':'b2c5a3','l':'d2dac0'}
C={k:'#'+v for k,v in C.items()}
im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
def line(a,b,c):d.line((*a,*b),fill=C[c])
def rect(box,c):d.rectangle(box,fill=C[c])
def poly(points,c):d.polygon(points,fill=C[c])
# Short solid handle, positioned behind the disc.
rect((13,24,18,29),'a');rect((14,25,17,29),'c');line((14,26),(14,28),'e')
rect((15,28,16,30),'b');line((15,28),(16,28),'d')
# Deliberate raster silhouette: circle, no perspective ellipse or rendered bevel.
spans={2:(12,18),3:(9,21),4:(7,23),5:(6,24),6:(5,25),7:(4,26),
       8:(3,27),9:(3,27),10:(3,27),11:(2,28),12:(2,28),13:(2,28),
       14:(2,28),15:(2,28),16:(2,28),17:(2,28),18:(3,27),19:(3,27),
       20:(3,27),21:(4,26),22:(5,25),23:(6,24),24:(7,23),25:(9,21),26:(12,18)}
for y,(left,right) in spans.items():
    line((left,y),(right,y),'a')
    if 3<=y<=25:line((left+1,y),(right-1,y),'c')
poly([(10,4),(20,4),(24,7),(26,11),(26,17),(23,22),(19,24),(10,23),(5,19),(4,11),(7,7)],'d')
poly([(10,4),(19,4),(22,5),(22,6),(10,6),(7,9),(6,14),(4,16),(4,11),(6,7)],'e')
line((10,4),(18,4),'f');line((7,6),(9,6),'f');line((5,9),(5,12),'f')
poly([(25,9),(27,11),(27,17),(25,21),(22,24),(19,25),(12,25),(9,24),(9,23),(19,23),(23,20),(25,16)],'b')
line((11,24),(18,24),'d');line((23,20),(23,21),'d')
# Inner cast recess, with broken highlight rather than a white ring.
inner=[(12,6),(19,6),(22,8),(24,11),(24,18),(21,21),(18,23),(12,23),(8,20),(6,17),(6,12),(8,9)]
poly(inner,'b')
line((10,7),(12,6),'c');line((8,9),(9,8),'c')
line((10,22),(12,23),'e');line((13,23),(18,23),'e');line((20,21),(22,19),'d')
# Mirror inset: five broad connected planes; no noisy pixels or realistic reflections.
glass=[(12,7),(18,7),(21,9),(23,12),(23,17),(21,20),(18,22),(12,22),(9,20),(7,17),(7,12),(9,9)]
poly(glass,'i')
poly([(16,7),(18,7),(21,9),(23,12),(23,17),(21,20),(18,22),(12,22),(9,20),(10,17),(13,15)],'h')
poly([(22,12),(23,12),(23,17),(21,20),(18,22),(12,22),(11,21),(17,21),(20,18),(21,15)],'g')
poly([(12,8),(16,8),(16,10),(14,10),(14,12),(12,12),(12,14),(10,14),(10,16),(8,16),(8,12),(10,9)],'j')
poly([(12,8),(15,8),(15,9),(13,9),(13,11),(11,11),(11,13),(9,13),(10,10)],'k')
line((12,8),(14,8),'l');line((10,10),(10,11),'k')
poly([(16,12),(18,10),(20,11),(20,13),(18,13),(18,15),(16,15),(16,17),(14,17),(14,15)],'i')
line((17,12),(18,11),'j')
# Two short engraved copper accents, restricted to the broad rim.
line((16,4),(18,4),'f');line((19,5),(20,5),'c')
line((4,16),(4,18),'b');line((5,17),(5,18),'e')
line((25,12),(25,14),'c');line((25,15),(25,16),'e')
line((14,25),(17,25),'e')
im.save(OUT/'bronze_mirror.png')

alpha=set(im.getchannel('A').getdata());colors=len({p[:3] for p in im.getdata() if p[3]})
assert im.size==(32,32) and alpha=={0,255} and colors<=12
assert all(v==0 for v in im.getchannel('A').crop((0,0,32,1)).getdata())
assert model.read_bytes()==(back/'bronze_mirror.json').read_bytes()
md=json.loads(model.read_text());assert md['parent']=='item/generated' and md['textures']['layer0']=='dynasty:item/bronze_mirror'

# Side by side at equal display size. Asset above is drawn at 32; resizing below is QA only.
font='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
f=ImageFont.truetype(font,23);s=ImageFont.truetype(font,16);t=ImageFont.truetype(font,13)
sheet=Image.new('RGB',(980,620),'#eeeae0');p=ImageDraw.Draw(sheet)
p.text((28,20),'铜镜 · 细节样张',font=f,fill='#29392f')
p.text((28,56),'保持 MC 像素轮廓，增加铜框厚度与镜面层次；只做这一件供确认。',font=s,fill='#65715f')
for x,image,title,desc in [(28,Image.open(old).convert('RGBA'),'上一版 · 16×16','10 色 / 16 倍最近邻'),(362,im,'新样张 · 原生 32×32','12 色 / 8 倍最近邻')]:
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
        'reason_for_32':'Existing source item is 32x32; user requested slightly more detailed accessory sample. Extra pixels describe cast rim and broad mirror planes; no block resolution change.',
        'colors':colors,'alpha':sorted(alpha),'model':'item/generated','layer0':'dynasty:item/bronze_mirror',
        'candidate':'candidate/assets/dynasty/textures/item/bronze_mirror.png',
        'target_if_later_approved':'src/main/resources/assets/dynasty/textures/item/bronze_mirror.png',
        'candidate_sha256':hashlib.sha256((OUT/'bronze_mirror.png').read_bytes()).hexdigest(),
        'baseline':records,'source_and_previous_unchanged':True,'installed':False,'in_game_test':False,
        'batch_authorization':'Pending. User explicitly requested this sample first; do not start bulk work until approval arrives.'}
(DOC/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(DOC/'README.md').write_text('''# 铜镜 32×32 单件细节样张

本轮只做 `dynasty:bronze_mirror` 一件。用户要求比 v11 稍细致，先看样张，确认后再开始剩余饰品和方块。

新 PNG 原生 32×32、12 个可见颜色、透明度仅 0/255。现有铜镜源资源本来就是 32×32，沿用实际 `item/generated` / `dynasty:item/bronze_mirror` 关系，无需改模型。额外像素用于铜框的断续亮边、内沿和镜面大色簇；不是把 16 图直接放大，也没有高分辨率生成后缩小。

- `comparison.png`：上一版与新样张的等大最近邻预览，附各自原尺寸及16/32/64px显示检查。
- `candidate/assets/dynasty/textures/item/bronze_mirror.png`：可用 PNG，未安装。
- `before/`：当前源 PNG、v11 PNG 与源模型的备份。
- `manifest.json`：尺寸、色数、哈希、准确引用和待确认状态。

像素绘制脚本只写本目录。未修改源文件、之前成品、公共注册、并行任务或游戏实例。尚未游戏内实测。

后续约定：等待用户对本样张风格的同意后，再重新核对项目文档、实际资源和此前任务完成记录，只处理剩余未完成或仍不合适的内容；保留之前已做好的饰品和方块。方块继续原生16×16，不因这一个饰品样张升到32×32。
''')
print(json.dumps({'png':str(OUT/'bronze_mirror.png'),'colors':colors,'alpha':sorted(alpha),'status':'ONE_SAMPLE_ONLY'},ensure_ascii=False))
