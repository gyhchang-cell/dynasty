"""Review gallery: native evidence first, labelled original-PNG checks and full resource playback."""
from create import *
NATIVE='human-v12-complete'
notes={IDS[0]:'九霄天将：借鉴Ignis/末影守卫的肩胸与兵器主次。加厚已有肩胸、盔颊与手甲，收胸甲描线；锐化原枪尖端并转到前方战备，左手抬起。未增盾、改枪种或重做骨架。',IDS[1]:'东海龙王：借鉴Scylla的前方攻击方向、利维坦的观察与危险器官主次。保留人脸龙冠白须；加厚已有肩披、恢复须髯层次、收拢背鳍衔接；海青王袍与金甲、玉、织纹分开。',IDS[2]:'龙帝：借鉴Maledictus的非对称战备、Harbinger的中心/外围主次。保留人脸帝冕黑须与左手玉印；加厚肩胸、抬掌印、修须根遮挡，礼屏降对比，王袍叠领与袖体分层。'}
css='body{margin:0;background:#ecece7;color:#273238;font:17px/1.7 system-ui}main{max-width:1700px;padding:28px;margin:auto}img{width:100%;height:auto}.pixel{image-rendering:pixelated}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px}figure{margin:12px 0}small,figcaption{font-size:14px}small{display:block}section{margin-top:36px;border-top:2px solid #aabbb9;padding-top:20px}summary{cursor:pointer;background:#dae1dc;padding:14px}details{margin:20px 0}a{color:#235d69}@media(max-width:600px){.grid{display:block}main{padding:14px}}'
h=[f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Dynasty × 灾变 · Boss力量精修 V12</title><style>{css}</style><main><h1>Dynasty × 灾变：力量与身份复查 V12</h1><p>八轮实际修正，保留三位人形Boss、原骨架、脚部、约3格体型和战斗时间轴。下面使用真实Forge截图，未单独放大我们的角色来制造同级感。</p><p><a href="README.md">具体差距与改动</a> · <a href="validation.json">UV/骨架/动作检查</a> · <a href="build-report.json">构建与原生验收</a></p>']
h+=['<h2>同相机、同裁切的游戏对照</h2><p><a href="comparison-eight-v12.png">灾变八只与Dynasty三只合在一张图</a></p><p>灾变3.27的原美术资产保持；仅在个人临时开发环境映射代码名称以运行，未复制到Dynasty。双方12m、70度FOV、1.62m视高、45度、日间，无额外资源包或光影。灾变自身发光、翼效及天空色变化保留，不能当作纯PNG效果。<a href="https://www.curseforge.com/minecraft/mc-mods/lendercataclysm/gallery">灾变作者展示</a></p>']
for suffix,label in [('on','双方保留自身气场'),('off','Dynasty关闭独立气场，检查本体')]:h.append(f'<h3>{label}</h3><a href="comparison-cataclysm-v12-{suffix}.png"><img src="comparison-cataclysm-v12-{suffix}.png"></a>')
h+=['<details><summary>实际看过的灾变八大Boss与完整参考图</summary><a href="reference-eight.png"><img loading="lazy" src="reference-eight.png"></a><p>前7/8图为12m；利维坦触肢在12m裁切，因此另拍32m全身构造，明确不作同尺度比较。NoAI待机，不声称完整打过八场战斗。</p><div class="grid">']
for id in ['ender_guardian','netherite_monstrosity','ignis','the_harbinger','the_leviathan','ancient_remnant','maledictus','scylla']:
 for view in ['front','45']:
  folder='reference-leviathan-full' if id=='the_leviathan' else 'power-reference-round1';src=f'reference-native/{folder}/cataclysm_{id}-{view}'
  h.append(f'<figure><a href="{src}.png"><img loading="lazy" src="{src}.png"></a><figcaption>{id} / {view} / <a href="{src}.json">实际机位记录</a></figcaption></figure>')
h+=['</div></details><h2>我们的正常玩家比例与代表攻击</h2><a href="native-overview.png"><img loading="lazy" src="native-overview.png"></a>']
for i,id in enumerate(IDS):
 h.append(f'<section id="{id}"><h2>{NAMES[id]} <small>dynasty:{id}</small></h2><p>{notes[id]}</p><h3>V11 → V12 / 同机位原生前后对照</h3>')
 for f in ['native-before-after-front','native-before-after-45','native-before-after-side']:h.append(f'<a href="{id}/{f}.png"><img loading="lazy" src="{id}/{f}.png"></a>')
 h.append('<details><summary>原色、普通基础光照、正侧背与剪影</summary><div class="grid">')
 for f in ['front-unlit','front-lit','45-lit','side-lit','back-lit','silhouette','scene','gray-model','compare-front','compare-45','compare-side','gray','dim','distance-8m','distance-16m']:
  h.append(f'<figure><a href="{id}/{f}.png"><img loading="lazy" src="{id}/{f}.png"></a><figcaption>{f} · 真实PNG逐面采样的软件检查，非游戏截图</figcaption></figure>')
 h.append('</div></details><details><summary>独立气场开/关 · 同日光Forge截图</summary>')
 for view in ['front','45','side','back']:h.append(f'<a href="{id}/fx-{view}-compare.png"><img loading="lazy" src="{id}/fx-{view}-compare.png"></a>')
 h.append('<p>off仅关闭BossHumanAura，原有技能次级效果不改；临时测试世界排除scenic_21等环境背景事件，使用控制夹具，不冒充自然遭遇。</p></details><details><summary>42状态中的本角色原图与姿态/哈希记录</summary><div class="grid">')
 labels=[v+'-'+fx for v in ['front','45','side','back'] for fx in ['off','on']]+['walk','attack-tell','attack-contact','attack-recovery','hurt','death']
 for j,label in enumerate(labels):
  src=f'native/{NATIVE}/{i*14+j:02d}-{id}-{label}.png';state=f'native/{NATIVE}/{i*14+j:02d}-state.json';h.append(f'<figure><a href="{src}"><img loading="lazy" src="{src}"></a><figcaption>{label} · 游戏截图 · <a href="{state}">加载与骨骼记录</a></figcaption></figure>')
 h.append('</div></details><details><summary>实际PNG、4倍最近邻、UV方向、面部与手部近景</summary><div class="grid">')
 for f in ['texture','texture-4x','uv-overlay-4x','uv-direction','close-face','close-torso','close-hand']:h.append(f'<figure><a href="{id}/{f}.png"><img class="pixel" loading="lazy" src="{id}/{f}.png"></a><figcaption>{f} · 软件检查</figcaption></figure>')
 h.append('</div></details><details><summary>六段完整模型资源回放</summary>')
 for clip in ['idle','walk','attack','cast','hurt','death']:h.append(f'<h4>{clip}</h4><div class="grid"><img loading="lazy" src="{id}/{clip}.webp"><a href="{id}/{clip}-phases.png"><img loading="lazy" src="{id}/{clip}-phases.png"></a></div>')
 h.append(f'<p>名字、时长、循环和接触时序保留；cast资源回放不等于服务器技能同步。<a href="blockbench/{id}.bbmodel">可编辑bbmodel</a></p></details></section>')
h+=['<section><h2>复查边界</h2><p>建模本体和生产PNG有实际改动，未更换三者主题、脚部、骨架、碰撞、伤害或任务。前七次资源与失败点保留在iterations目录。构建、真实加载和控制动作分别记录；自然战斗编排、复杂地形、联机、真实装备交互与服务器cast同步待验证，不能因静态并排好看便宣称完整战斗演出等同灾变。没有改变系统声音、亮度或用户愚者存档。</p></section></main></html>']
(D/'index.html').write_text(''.join(h))
print('Gallery written; reference effects and natural-fight limits explicit.')
