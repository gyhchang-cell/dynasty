from pathlib import Path
import json,sys,html,shutil
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];W=Path('/Users/a15356015027/.codex/worktrees/boss-eight-art/dynasty');D=R/'docs/art/swords-army-v30';D.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'tools/art/steve-fighters-v25'));from weapons import DESIGNS
N=W/'docs/art/steve-fighters-v25/native/fighters-v25-swords-v30';B=R/'docs/art/steve-fighters-v25/native/fighters-v25-swords-v29'
if not B.exists():B=W/'docs/art/steve-fighters-v25/native/fighters-v25-swords-v29'
assert(N/'PASS.txt').exists()
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',24)
def crop(p):
 im=Image.open(p).convert('RGB');w,h=im.size;return im.crop((int(w*.14),int(h*.20),int(w*.71),int(h*.90)))
sections=[]
for i,(id,design)in enumerate(DESIGNS.items()):
 dd=D/id;dd.mkdir(exist_ok=True);cards=[]
 for view in ['front','45','side','back']:
  p=next(N.glob(f'*-{id}-{view}.png'));im=crop(p);im.save(dd/f'{view}.jpg',quality=94)
  if view=='45':
   a=crop(next(B.glob(f'*-{id}-{view}.png')));o=Image.new('RGB',(a.width+im.width,im.height+40),'#e6e6dd');o.paste(a);o.paste(im,(a.width,0));d=ImageDraw.Draw(o);d.text((16,im.height+5),'修改前 · V29',font=font,fill='black');d.text((a.width+16,im.height+5),'修改后 · V30',font=font,fill='black');o.save(dd/'comparison.jpg',quality=94)
  cards.append(f'<img loading="lazy" src="{id}/{view}.jpg" alt="{view}">')
 frames=[];ticks=[]
 for p in sorted((N/'frames'/id).glob('*.png')):
  im=crop(p);im.thumbnail((850,650));frames.append(im);ticks.append(int(p.stem))
 if frames:frames[0].save(dd/'motion.webp',save_all=True,append_images=frames[1:],duration=[max(50,(b-a)*50)for a,b in zip(ticks,ticks[1:])]+[150],loop=0,quality=90)
 shutil.copy2(R/f'src/main/resources/assets/dynasty/textures/entity/steve_fighters/{id}.png',dd/'texture.png')
 sections.append(f'<section><h2>{design[0]} · {id}</h2><img src="{id}/comparison.jpg" loading="lazy"><div class="grid">'+''.join(cards)+f'</div><details><summary>动作采样与运行贴图</summary><img src="{id}/motion.webp" loading="lazy"><a href="{id}/texture.png">原始PNG</a></details></section>')
army=W/'docs/art/steve-fighters-v25/native/fighters-v25-army-v30';assert(army/'PASS.txt').exists()
for state in ['beyond36','recruit','formation','roster']:
 Image.open(army/f'army-{state}-320x240.png').convert('RGB').save(D/f'army-{state}.jpg',quality=95)
refs=json.loads((R/'build/swords-army-v30/references.json').read_text())
for r in refs:r.pop('local',None)
(D/'references.json').write_text(json.dumps({'scope':'100件博物馆实物与100件游戏剑图像；实物含佩鞘与仪仗剑，游戏主要99件Elden Ring及1件FF7，并非100个游戏或100种剑制。逐张查看研究，不复制资产。','method':'连续刃面、较厚剑脊、窄刃口、明确尖端、护手握柄分界。对照自有龙帝武器的主体厚度；各兵种保留原握点和攻击时钟。','references':refs},ensure_ascii=False,indent=2))
priest=W/'docs/art/steve-fighters-v25/native/fighters-v25-humans-v30-final3'
extra=''
if(priest/'PASS.txt').exists():
 for v in ['front','45','side','back']:crop(next(priest.glob(f'*-fufa_jijiu-{v}.png'))).save(D/f'priest-{v}.jpg',quality=94)
 paths=sorted((priest/'frames/fufa_jijiu').glob('*.png'));frames=[crop(p)for p in paths];ticks=[int(p.stem)for p in paths]
 for im in frames:im.thumbnail((850,650))
 if frames:frames[0].save(D/'priest-motion.webp',save_all=True,append_images=frames[1:],duration=[max(50,(b-a)*50)for a,b in zip(ticks,ticks[1:])]+[150],loop=0,quality=90)
 extra='<section><h2>符法祭酒 · 必须保留的人类术士</h2><p>六块史蒂夫主体不变，灰眉长须、低道冠、窄法衣、额玉及手持朱符；普通怪没有领域或装饰粒子。沿用术式接触24/28/32 tick，动作由原服务端时钟驱动。</p><div class="grid">'+''.join(f'<img src="priest-{v}.jpg">'for v in ['front','45','side','back'])+'</div><img src="priest-motion.webp"></section>'
if(priest/'PASS.txt').exists():
 id='pijia_panjiang_huwei'
 for v in ['front','45','side','back']:crop(next(priest.glob(f'*-{id}-{v}.png'))).save(D/f'axe-{v}.jpg',quality=94)
 paths=sorted((priest/'frames'/id).glob('*.png'));frames=[crop(p)for p in paths];ticks=[int(p.stem)for p in paths]
 for im in frames:im.thumbnail((850,650))
 frames[0].save(D/'axe-motion.webp',save_all=True,append_images=frames[1:],duration=[max(50,(b-a)*50)for a,b in zip(ticks,ticks[1:])]+[150],loop=0,quality=90)
 extra+='<section><h2>披甲叛将护卫 · 双斧与合夹动作</h2><p>保留已有铁面和主体，补齐原设定的副手短斧；斧眼、刃面及斧刃分开。双斧前倾，减少竖直遮脸；双方手臂使用原16/22 tick接触时钟，不改服务器攻击。</p><div class="grid">'+''.join(f'<img src="axe-{v}.jpg">'for v in ['front','45','side','back'])+'</div><img src="axe-motion.webp"></section>'
(D/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Dynasty V30 刀剑、兵册与术士</title><style>body{background:#142127;color:#e5e9dc;font:17px/1.7 system-ui;margin:30px auto;max-width:1450px;padding:0 20px}img{max-width:100%}section{border-top:1px solid #657678;padding:22px 0}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}a{color:#b5d9d6}summary{cursor:pointer}</style><h1>有厚度的刀剑 · 可扩展兵册</h1><p>截图来自静音隔离Forge客户端，使用实际模型和PNG。前后机位与尺度相同。动作是关闭AI的服务器技能时钟采样，不冒充自然战斗或双人验证。</p><section><h2>不再固定36名 / 9名</h2><p>兵册和阵位按页显示；服务器不再设置固定招募或部署人数上限。仍逐名付费、校验所有权及地形。43人军籍、三份大阵预设、12人实际部署及旧请求拒绝专项已通过。页面上的36和9仅是每批同步/展示条数。</p><div class="grid"><img src="army-beyond36.jpg"><img src="army-recruit.jpg"></div><p>全套测试曾被无关WoodKite测试异常中断；随后隔离虎符专项通过。完整联机、自然战斗与大军压测待验。未改用户正式存档。</p></section>'''+''.join(sections)+extra+'''<section><h2>参考与验证</h2><p>参考的是刃脊、护手和材质组织，不复制颜色或剑形。游戏参考主要来自两款游戏，不能称为100款游戏。</p><a href="references.json">200件参考来源</a> · <a href="verification.json">验证记录</a> · <a href="prompt-cleanup.json">提示词清理记录</a></section>''')
print(D/'index.html')
