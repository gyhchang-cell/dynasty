"""Review actual native frames; no surrogate model render or copied third-party art."""
from pathlib import Path
import json,shutil,html,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/swords-menu-army-v28';D.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'tools/art/steve-fighters-v25'));from weapons import DESIGNS
N=R/'docs/art/steve-fighters-v25/native';new=N/'fighters-v25-swords-v28b';old=N/'fighters-v25-sword-v27'
def crop(p):
 im=Image.open(p).convert('RGB');w,h=im.size;return im.crop((round(w*.25),round(h*.22),round(w*.70),round(h*.88)))
def jpg(p,d,w=1400):
 im=Image.open(p).convert('RGB');im.thumbnail((w,2000));im.save(D/d,quality=94)
sections=[]
for i,(id,design) in enumerate(DESIGNS.items()):
 cards=[]
 for view,j in [('front',0),('45',1),('side',2),('back',3),('action',4)]:
  file=f'{i*5+j:02}-{id}-{view}.png';source=new/file
  if not source.exists() and view=='action':source=min((new/'frames'/id).glob('*.png'),key=lambda p:abs(int(p.stem)-16))
  im=crop(source);im.save(D/f'{id}-{view}.jpg',quality=95)
  if view=='45':
   a=crop(old/file);a=a.resize(im.size);pair=Image.new('RGB',(im.width*2,im.height));pair.paste(a);pair.paste(im,(im.width,0));pair.save(D/f'{id}-compare.jpg',quality=95)
  cards.append(f'<figure><img loading="lazy" src="{id}-{view}.jpg"><figcaption>{view}</figcaption></figure>')
 frames=[];ticks=[]
 for p in sorted((new/'frames'/id).glob('*.png')):
  im=crop(p);im.thumbnail((620,680));frames.append(im);ticks.append(int(p.stem))
 durations=[max(50,(b-a)*50) for a,b in zip(ticks,ticks[1:])]+[150]
 frames[0].save(D/f'{id}-motion.webp',save_all=True,append_images=frames[1:],duration=durations,loop=0,quality=90)
 # Pixel-close inspection of the actual native screenshot, not a repainted sword.
 im=Image.open(new/f'{i*5+1:02}-{id}-45.png');w,h=im.size;im=im.crop((int(w*.32),int(h*.48),int(w*.48),int(h*.64)));im=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST);im.save(D/f'{id}-detail.png')
 tex=R/f'src/main/resources/assets/dynasty/textures/entity/steve_fighters/{id}.png';shutil.copy2(tex,D/f'{id}-texture.png')
 sections.append(f'<section><h2>{html.escape(design[0])} · {id}</h2><p>左：修改前；右：修改后。同机位、同光照。人物身体与战斗逻辑保持。</p><img src="{id}-compare.jpg"><div class="grid">'+''.join(cards)+f'</div><div class="pair"><figure><img src="{id}-motion.webp"><figcaption>完整采样动作序列 · 0–64 tick，AI关闭</figcaption></figure><figure><img class="pixel" src="{id}-detail.png"><figcaption>真实截图剑部最近邻放大</figcaption></figure></div><a href="{id}-texture.png">实际256×256像素图集</a></section>')
jpg(N/'fighters-v25-ui-title-v28/title-960x540-scale2.png','title.jpg',1920)
jpg(N/'fighters-v25-ui-title-v28/title-320x240-scale3.png','title-small.jpg')
for state in ['empty','roster','formation','encounters']:jpg(N/f'fighters-v25-ui-army-v28/army-{state}-320x240.png',f'army-{state}.jpg')
shutil.copy2(R/'build/sword-ui-v28/swords-final.jpg',D/'overview.jpg')
refs=json.loads((D/'references.json').read_text());ledger=''.join(f'<li><a href="{html.escape(x["sourceImage"] if isinstance(x["sourceImage"],str) else str(x["sourceImage"]))}">{html.escape(x["design"])}</a></li>'for x in refs['swords'])
(D/'index.html').write_text('''<!doctype html><html lang="zh"><meta charset="utf-8"><title>Dynasty · 武器、主菜单、虎符</title><style>body{margin:0;background:#101c22;color:#e5e9df;font:17px/1.7 system-ui}main{max-width:1400px;margin:auto;padding:32px}h1,h2{color:#e6c791}section{padding:28px 0;border-top:1px solid #39505a}img{max-width:100%;height:auto}figure{margin:0}a{color:#92cbd3}.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}.pixel{image-rendering:pixelated}figcaption{color:#aabfc2}li{break-inside:avoid}ol{columns:3}@media(max-width:700px){.grid,.pair{grid-template-columns:1fr}ol{columns:1}}</style><main><h1>像素刀剑 · 清晰菜单 · 简化虎符</h1><p>这里全部成品画面来自隔离的真实Forge客户端。没有修改用户存档、声音或屏幕亮度。武器使用实际PNG逐面贴图，保留原前倾握持，修正刃面朝向。</p><img src="overview.jpg"><section><h2>主菜单</h2><p>保留龙宫背景；去掉“王朝”大标题；采用OFL授权Cinzel Decorative字体；主入口、次入口和辅助项分层。</p><img src="title.jpg"><details><summary>最小窗口检查</summary><img src="title-small.jpg"></details></section><section><h2>虎符</h2><p>兵册每页六人 → 选中后执行操作；军阵与关卡独立。招募、编队、修整、出收阵、转向、五种阵型、三份预设与六关仍映射原服务端操作。</p><div class="pair">'''+''.join(f'<figure><img src="army-{s}.jpg"><figcaption>{n}</figcaption></figure>'for s,n in [('empty','空兵册'),('roster','选兵员与当前操作'),('formation','军阵与预设'),('encounters','关卡')])+'''</div></section><section><h2>验证范围</h2><p>构建通过；9位剑手36张静态视图、9组同步动作采样序列通过；主菜单5种尺寸和入口导航通过；虎符3种尺寸15张视图、分页、选中、预设切换和按钮边界通过。虎符截图使用客户端兵册数据夹具，尚未验证真实联机招募/编队往返；自然AI实战仍待验证。</p></section>'''+''.join(sections)+f'<section><h2>实际参考记录</h2><p>{html.escape(refs["scope"])}</p><p>菜单选取Infinity Evolved、Mage Quest、ATM9、ATM10、Sky Adventures的实际截图学习主次和留白，不声称是客观排名前五。</p><a href="references.json">完整记录与来源</a><details><summary>100件刀剑设计</summary><ol>{ledger}</ol></details></section></main>')
print('Review page created',D/'index.html')
