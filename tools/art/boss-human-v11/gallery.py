"""Review actual PNG surfaces separately from real production atmosphere captures."""
from create import *
import html
NATIVE='human-v11-verified'
notes={
 IDS[0]:'保留钢甲天将与长枪，扩肩厚胸、叠领腰护、两段短披挂、双令旗；屈肘扭身迎战。独立淡金白青符线与低速尘，关闭特效仍保留统帅剪影。',
 IDS[1]:'保留人脸冠角白须与三叉戟，增加分层王袍、水纹袖缘、阶梯鳍披、潮轮与龙珠；沉稳俯視。青蓝潮尘、水符和少量水滴独立绘制。',
 IDS[2]:'保留帝冠赤袍黑须与玉印，增加厚肩、礼领、腰衣、分片龙纹背屏与浮空玉圭；冷静微扭身。背后暗金符印和赤金上升尘；没有新增剑技能。'
}
def run():
 cards=[]
 for i,id in enumerate(IDS):
  cards.append(f'<section id="{id}"><h2>{NAMES[id]} <small>dynasty:{id}</small></h2><p>{notes[id]}</p>')
  cards.append('<h3>现有V10 → 增强V11 / 同机位、同世界尺度、无特效</h3>')
  for f in ['compare-front','compare-45','compare-side']:cards.append(f'<a href="{id}/{f}.png"><img loading="lazy" src="{id}/{f}.png"></a>')
  cards.append('<h3>正 / 45度 / 侧 / 背 · 原色与基础光照</h3><div class="grid">')
  for f in ['front-unlit','front-lit','45-lit','side-lit','back-lit','silhouette','scene','gray-model']:
   cards.append(f'<figure><a href="{id}/{f}.png"><img loading="lazy" src="{id}/{f}.png"></a><figcaption>{f} · 逐面真实PNG软件预览</figcaption></figure>')
  cards.append('</div><h3>开启 / 关闭气场 · 普通Forge日光游戏截图</h3><p>相机位置、70度FOV、1.62格视高、玩家位置与光照相同。待机和粒子按各次实际捕获时刻显示，不是将软件特效叠到截图上。点击查看原始2800×1800图。</p>')
  for view in ['front','45','side','back']:cards.append(f'<a href="{id}/fx-{view}-compare.png"><img loading="lazy" src="{id}/fx-{view}-compare.png"></a>')
  cards.append('<details><summary>所有原生截图、资源哈希、实际粒子发射记录</summary><div class="grid">')
  labels=[v+'-'+fx for v in ['front','45','side','back'] for fx in ['off','on']]+['walk','attack-tell','attack-contact','attack-recovery','hurt','death']
  for j,label in enumerate(labels):
   stem=f'{i*14+j:02d}-{id}-{label}';src=f'native/{NATIVE}/{stem}.png';state=f'native/{NATIVE}/{i*14+j:02d}-state.json'
   cards.append(f'<figure><a href="{src}"><img loading="lazy" src="{src}"></a><figcaption>{label} · 游戏截图 · <a href="{state}">资源/姿态/粒子记录</a></figcaption></figure>')
  cards.append('</div></details><details><summary>实际PNG、4倍最近邻、UV方向与近景</summary><div class="grid">')
  for f in ['texture','texture-4x','uv-overlay-4x','uv-direction','close-face','close-torso','close-hand','gray','dim']:
   cards.append(f'<figure><a href="{id}/{f}.png"><img class="pixel" loading="lazy" src="{id}/{f}.png"></a><figcaption>{f} · 软件检查</figcaption></figure>')
  cards.append('</div></details><details><summary>六段完整模型动作 / 仅资源回放</summary>')
  for clip in ['idle','walk','attack','cast','hurt','death']:
   cards.append(f'<h4>{clip}</h4><div class="grid"><img loading="lazy" src="{id}/{clip}.webp"><a href="{id}/{clip}-phases.png"><img loading="lazy" src="{id}/{clip}-phases.png"></a></div>')
  cards.append(f'<p>六段动作保留原名、时长和循环属性；只补姿态与背饰/衣摆轻动。cast资源回放不等于服务器技能同步。<a href="blockbench/{id}.bbmodel">可编辑bbmodel</a></p></details></section>')
 header='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Dynasty 人形Boss增强 V11</title><style>body{margin:0;background:#ecece7;color:#273238;font:17px/1.7 system-ui}main{max-width:1600px;padding:28px;margin:auto}img{width:100%;height:auto}.pixel{image-rendering:pixelated}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:22px}figure{margin:12px 0}small,figcaption{font-size:14px}small{display:block}section{margin-top:48px;border-top:2px solid #aabbb9;padding-top:20px}summary{cursor:pointer;background:#dae1dc;padding:14px}details{margin:20px 0}a{color:#235d69}@media(max-width:600px){.grid{display:block}main{padding:14px}}</style><main><h1>三位人形Boss · 在现有基础上增强 V11</h1><p>九霄天将、东海龙王、龙帝。保留V10主体与分段骨架，重新分配肩胸体量，补各自的背后识别结构和独立客户端气场。身高约3格，玩家1.8格；几何层和特效层分别验收。</p><p><a href="#nine_heaven_general">九霄天将</a> · <a href="#dragon_king">东海龙王</a> · <a href="#dragon_emperor">龙帝</a> · <a href="validation.json">离线检查</a> · <a href="build-report.json">构建与原生检查</a> · <a href="README.md">改动与验证边界</a></p><img src="overview.png" alt="同世界尺度软件总览"><p>软件总览不含粒子，实际气场见下方游戏截图。未采用强光影、低机位或额外资源包。普通日光下单独核对面部、武器、肩胸与背饰。</p>'''
 footer='''<section><h2>本轮实际复查</h2><p>先看到原版背后空、直臂和服制节奏弱；第一轮增加三种背饰并调整待机，龙王长板再收为阶梯鳍缘。原生第一轮发现玩家取景裁切及白天气场过弱，改回普通70度FOV、同深度玩家参照，增强细符线而非整身发光。另一次原生检查发现上一只Boss的延迟遗骸容器遮挡下一只；保留正式死亡掉落逻辑，只清理一次性测试世界的遗骸，并逐帧检查场景空气无遮挡。</p><p>自然战斗/复杂地形/联机、真实装备握持，以及服务器技能到cast动作同步仍待验证；视觉出击峰值不冒充伤害判定。本轮无新伤害、声音、弱点或战斗系统。</p></section></main></html>'''
 header=header.replace('<img src="overview.png"', '<h2>原生游戏同场景比例 · 关闭气场</h2><a href="native-overview.png"><img src="native-overview.png"></a><p>三张使用同样裁切；完整2800×1800原图在下方每只的截图列表。玩家与Boss在同一深度，没有单独缩放人物。</p><h2>软件检查总览</h2><img src="overview.png"')
 (D/'index.html').write_text(header+''.join(cards)+footer)
if __name__=='__main__':run()
