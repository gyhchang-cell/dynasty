"""Compose QA sheets from native pixels. Does not create/modify source artwork."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import hashlib,json
from PIL import Image,ImageDraw,ImageFont

DOC=Path(__file__).resolve().parent
TEX=DOC/'candidate/assets/dynasty/textures/block'
PREVIEW=DOC/'previews';PREVIEW.mkdir(exist_ok=True)
JAR=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar')
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
font=ImageFont.truetype(FONT,16);small=ImageFont.truetype(FONT,12)
def enlarge(im,n):return im.resize((im.width*n,im.height*n),Image.Resampling.NEAREST)

with ZipFile(JAR) as z:
    refs={}
    provenance=[]
    for name in ['stone','stone_bricks','deepslate_bricks','tuff','copper_block','chiseled_stone_bricks']:
        path=f'assets/minecraft/textures/block/{name}.png';data=z.read(path)
        refs[name]=Image.open(BytesIO(data)).convert('RGB')
        provenance.append({'source_jar':str(JAR),'path':path,'sha256':hashlib.sha256(data).hexdigest(),
                           'use':'local comparison only; no pixels copied into candidate textures or pack'})
(DOC/'reference-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')

canvas=Image.new('RGB',(1040,890),'#ecebe5');d=ImageDraw.Draw(canvas)
d.text((20,16),'LOCAL VANILLA COMPARISON | Minecraft 1.20.1 | REVIEW, not in-game',font=font,fill='#29342c')
items=list(refs.items())+[(n,Image.open(TEX/(n+'.png')).convert('RGB')) for n in ['marble_block','jade_ore','dragon_crystal_ore']]
items += [('palace_bricks / PRESERVED',Image.open(DOC/'before/assets/dynasty/textures/block/palace_bricks.png').convert('RGB'))]
for i,(name,im) in enumerate(items):
    x=20+(i%5)*204;y=60+(i//5)*205
    d.text((x,y),name,font=small,fill='#29342c')
    canvas.paste(enlarge(im,8),(x,y+29));canvas.paste(im,(x+151,y+30))
    d.text((x,y+164),'Vanilla reference' if i<6 else ('Approved / unchanged' if i==9 else 'Original candidate'),font=small,fill='#59625a')

d.text((20,486),'4x native mixed wall: vanilla stone bricks + marble candidate + preserved palace bricks',font=font,fill='#29342c')
wall=Image.new('RGB',(16*12,16*4))
chosen=[refs['stone_bricks'],Image.open(TEX/'marble_block.png'),items[-1][1]]
for y in range(4):
    for x in range(12):wall.paste(chosen[x//4],(16*x,16*y))
canvas.paste(enlarge(wall,4),(20,523))
d.text((20,804),'Reference pixels belong to Minecraft; they are displayed only for scale/color comparison.',font=small,fill='#59625a')
d.text((20,828),'All Dynasty candidate pixels are explicitly authored on 16x16 grids; no reference pattern tracing.',font=small,fill='#59625a')
canvas.save(PREVIEW/'vanilla-context.png')

names=['jade_mending_forge_top','jade_mending_forge_front','jade_mending_forge_side',
       'jade_mending_forge_bottom','jade_mending_forge_top_active','jade_mending_forge_front_active']
canvas=Image.new('RGB',(970,640),'#ecebe5');d=ImageDraw.Draw(canvas)
d.text((20,15),'FORGE SURFACE ATLASES | Original 1x + nearest 8x + 3x3 repeat | actual model in separate QA',font=font,fill='#29342c')
for i,name in enumerate(names):
    x=20+(i%3)*318;y=62+(i//3)*280
    im=Image.open(TEX/(name+'.png')).convert('RGB')
    d.text((x,y),name.replace('jade_mending_forge_',''),font=font,fill='#29342c')
    canvas.paste(enlarge(im,8),(x,y+34));canvas.paste(im,(x+142,y+34))
    tile=Image.new('RGB',(48,48))
    for u in range(3):
        for v in range(3):tile.paste(im,(16*u,16*v))
    canvas.paste(enlarge(tile,3),(x+158,y+65))
    d.text((x,y+224),f'{len(im.getcolors(256))} colors / UV atlas, not a whole cube face',font=small,fill='#59625a')
canvas.save(PREVIEW/'forge-surface-atlases.png')

native=Image.new('RGB',(340,140),'#ecebe5');d=ImageDraw.Draw(native)
for i,tid in enumerate(['marble_block','jade_ore','dragon_crystal_ore','jade_mending_forge_front']):
    y=10+i*32
    oldname='jade_mending_forge' if 'forge' in tid else tid
    native.paste(Image.open(DOC/'before/assets/dynasty/textures/block'/(oldname+'.png')),(8,y))
    native.paste(Image.open(TEX/(tid+'.png')),(36,y))
    d.text((65,y),tid,font=small,fill='#29342c')
native.save(PREVIEW/'native-1x.png')

sections=[('首组三项：原尺寸／最近邻／3×3铺贴','first-three-comparison.png'),
          ('修补炉：同一模型，原图／候选待机／候选工作','forge-model-comparison.png'),
          ('原版石砖等对照及混合墙面','vanilla-context.png'),
          ('同标准追加龙晶矿候选','ore-followup-comparison.png'),
          ('功能面的原始16×16图集','forge-surface-atlases.png'),
          ('汉白玉共用材质：药浴盆的间接外观影响','herbal-shared-material.png'),
          ('六个方向与实际UV检查','forge-six-face-comparison.png')]
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dynasty 原生16像素候选评审</title><style>body{max-width:1160px;margin:32px auto;padding:0 20px;background:#f0eee5;color:#29342c;font:16px/1.7 system-ui}h1{font-size:28px}h2{font-size:21px;margin-top:40px}img{max-width:100%;height:auto;image-rendering:pixelated}a{color:#346449}code{background:#dedfd4;padding:2px 5px}.note{padding:16px;border-left:4px solid #577c5e;background:#e3e6d9}figure{margin:20px 0}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #b9c3b4}</style>
<h1>Dynasty · 原生 16×16 候选评审</h1><p class="note">状态：仅供评审，尚未接入项目源资源，也未安装到实例。当前34张专属方块PNG都已有v9完成记录；本次不是补空白资源，而是针对有证据的风格／功能面问题提供独立改进候选。</p>
<p>首样：汉白玉、玉矿、玉髓修补炉。追加：龙晶矿。汉白玉同时被药浴盆复用，未来启用候选也会改变盆体石面，已附间接影响对比。保留用户确认的宫廷砖、饰品、展示架。没有修改源资源、龙口遗迹、祭坛建模、建筑、存档、Java或公共注册。</p>
<p>所有候选均由明确的16格像素表和整数色簇绘制。没有高分辨率缩图、随机噪声、平滑渐变、抗锯齿或第三方图案复制。修补炉几何及UV不变；只增加面与已有状态的引用分工。</p>
<p><a href="INVENTORY.md">45个方块ID清单</a> · <a href="README.md">交付说明</a> · <a href="candidate-manifest.json">准确路径与哈希</a> · <a href="verification.json">静态检查结果</a> · <a href="dynasty-native16-v10-REVIEW-ONLY.zip">评审用资源包（不会自动安装）</a></p>
<h2>1× 原尺寸：左为旧图，右为候选</h2><img style="width:340px" src="previews/native-1x.png" alt="真实16×16尺寸对比">
'''
for title,path in sections:html+=f'<h2>{title}</h2><figure><img src="previews/{path}" alt="{title}"></figure>'
html+='''<p class="note">以上均为静态或离线模型预览，不是游戏截图。修补炉正面玉槽与顶部小段亮色随已有lit状态切换；原代码已有工作时10级方块光照，本轮没有新增自发光着色器或动画。材料仍放背包，所有面均能右键，图案不代表新增实体投料槽。</p></html>'''
(DOC/'review.html').write_text(html)
print('Review pages, native-size/tiling/vanilla/UV sheets written. Source textures unchanged.')
