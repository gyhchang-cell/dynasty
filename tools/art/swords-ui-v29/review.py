"""V29: native before/after frames and explicit isolated-runtime provenance."""
from pathlib import Path
import json,sys,html,shutil
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/swords-ui-v29';D.mkdir(parents=True,exist_ok=True)
N=R/'docs/art/steve-fighters-v25/native';W=Path('/Users/a15356015027/.codex/worktrees/boss-eight-art/dynasty');WN=W/'docs/art/steve-fighters-v25/native'
sys.path.insert(0,str(R/'tools/art/steve-fighters-v25'));from weapons import DESIGNS
old=N/'fighters-v25-swords-v28b';new=N/'fighters-v25-swords-v29'
def cropped(p):
 im=Image.open(p).convert('RGB');w,h=im.size;return im.crop((int(w*.12),int(h*.02),int(w*.77),int(h*.94)))
def copyimage(p,name):
 im=Image.open(p).convert('RGB');im.save(D/name,quality=94)
sections=[]
for i,(id,design) in enumerate(DESIGNS.items()):
 cards=[]
 for j,v in enumerate(['front','45','side','back']):
  f=f'{i*5+j:02}-{id}-{v}.png';im=cropped(new/f);im.save(D/f'{id}-{v}.jpg',quality=95)
  if v=='45':
   a=cropped(old/f);pair=Image.new('RGB',(im.width*2,im.height));pair.paste(a);pair.paste(im,(im.width,0));pair.save(D/f'{id}-compare.jpg',quality=95)
  cards.append(f'<figure><img loading="lazy" src="{id}-{v}.jpg"><figcaption>{v}</figcaption></figure>')
 frames=[];ticks=[]
 for p in sorted((new/'frames'/id).glob('*.png')):
  im=cropped(p);im.thumbnail((780,680));frames.append(im);ticks.append(int(p.stem))
 durations=[max(50,(b-a)*50)for a,b in zip(ticks,ticks[1:])]+[150]
 frames[0].save(D/f'{id}-motion.webp',save_all=True,append_images=frames[1:],duration=durations,loop=0,quality=92)
 shutil.copy2(R/f'src/main/resources/assets/dynasty/textures/entity/steve_fighters/{id}.png',D/f'{id}-texture.png')
 sections.append(f'<section><h2>{design[0]} · {id}</h2><p>左 V28 / 右 V29。相同游戏机位与光照；身体、握点与动作时序保留。普通人形参照位于旁侧。</p><img loading="lazy" src="{id}-compare.jpg"><div class="grid">'+''.join(cards)+f'</div><details><summary>0–64 tick 动作采样回放与实际贴图</summary><img loading="lazy" src="{id}-motion.webp"><p>AI关闭的同步动作夹具，不等于自然战斗验收。</p><a href="{id}-texture.png">256×256运行PNG</a></details></section>')
for stem in ['title-960x540-scale2','title-320x240-scale3','settings-320x240-scale3']:
 copyimage(WN/'fighters-v25-ui-title-v29c'/f'{stem}.png',stem+'.jpg')
for state in ['roster','formation','recruit','empty','encounters']:
 copyimage(WN/'fighters-v25-ui-army-v29b'/f'army-{state}-320x240.png','army-'+state+'.jpg')
ledger=json.loads((R/'build/swords-ui-v29/reference-ledger.json').read_text())
assert len(ledger)==100 and len({x['name']for x in ledger})==100 and not any('error'in x for x in ledger)
for x in ledger:x['review']='已查看角色持剑/配剑画面；仅研究长度、刃背关系、握持和视觉主次，不提取美术资产。'
refs={'scope':'100个不同持剑角色的画面研究，含官方作品转载、游戏截图及同人画面；不声称全是官方图，也不把100人等同100种独立剑型。排除了误识别角色和明显生成图。','characters':ledger,'ui':[{'source':'愚者 The Fool 0.2.2 本地 FancyMenu 启用布局及 button_dark.png','method':'四个主入口，背景优先；没有复制其按钮图片。'},{'source':'https://developer.apple.com/design/human-interface-guidelines/buttons','method':'胶囊轮廓、主次层级；Minecraft逻辑像素绘制，不引入玻璃/PBR。'}],'application':['制式剑、佩刀和盾剑：刃长18–24模型单位，对应32单位身体的56–75%；不把全部职业都改成巨剑。','刺客、斥候、死士：12–13单位短锋，保留短刃身份但消除手掌小玩具感。','有限冷灰刃面、暗脊、金属护手与缠柄保持像素硬边；只延长武器几何并重新分配真实UV。']}
(D/'references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2))
links=''.join(f'<li><a href="{html.escape(x["url"])}">{html.escape(x["name"])}</a></li>'for x in ledger)
(D/'index.html').write_text('''<!doctype html><html lang="zh"><meta charset="utf-8"><title>Dynasty V29 · 长锋与四入口</title><style>body{margin:0;background:#101c22;color:#e4e9df;font:17px/1.7 system-ui}main{max-width:1440px;margin:auto;padding:32px}section{padding:28px 0;border-top:1px solid #37515a}h1,h2{color:#dfc593}img{max-width:100%;height:auto}figure{margin:0}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}a{color:#9ed0d7}ol{columns:3}li{break-inside:avoid}@media(max-width:800px){.grid,.pair{grid-template-columns:1fr}ol{columns:1}}</style><main><h1>长锋 · 四入口 · 付费募兵</h1><p>本轮重点：加长刀剑、减少主菜单入口、柔化按钮形状、把购买士兵与兵册操作分开。</p><section><h2>主菜单只保留四个入口</h2><img src="title-960x540-scale2.jpg"><p>单人、多人、设置、退出。Mod、语言、无障碍和Realms移到设置页；原回调与限制保留。龙宫背景及英文标题不变。</p><div class="pair"><img src="title-320x240-scale3.jpg"><img src="settings-320x240-scale3.jpg"></div></section><section><h2>兵册与付费募兵</h2><p>购买发生在募兵台：刀卫12银、弩卫16银、盾卫20银。展示生命、用途、总价、购后余额及36人容量；不足余额禁用确认。每次购买1人，部署上限仍为9人。</p><div class="pair">'''+''.join(f'<figure><img src="army-{s}.jpg"><figcaption>{n}</figcaption></figure>'for s,n in [('recruit','募兵台'),('roster','兵员详情'),('formation','军阵'),('encounters','关卡'),('empty','空兵册')])+'''</div></section><section><h2>验证与限制</h2><p>刀剑画面来自共享工作区当时的真实Forge客户端；最终UI来自独立美术分支的真实Forge客户端。独立分支排除了并行物品改动：共享整包后来因storm_charm 1274×1234纹理图集超限而启动失败，不能把本页截图当作最新共享整包启动通过。</p><p>共享服务端测试执行335项，41项失败；未宣称整套游戏逻辑通过。菜单与募兵客户端夹具分别验证排版和入口，游戏截图不是概念预览。自然AI战斗和完整多人联机仍待验证。详见验证记录。</p><a href="verification.json">验证记录</a> · <a href="prompt-cleanup.json">提示词精确清理记录</a></section>'''+''.join(sections)+f'<section><h2>实际查看的100位持剑角色</h2><p>{refs["scope"]}</p><p>从长刃占比、刀背与切削边、少量护手特征学习，不移植他人剑形与贴图。游戏内剑仍使用Minecraft式长方体及硬边像素。</p><a href="references.json">来源和落地记录</a><details><summary>展开100条来源</summary><ol>{links}</ol></details></section></main>')
print(D/'index.html')
