"""Offline evidence gallery; links stay relative for the delivery ZIP."""
from refine import *
NAMES={'nine_heaven_general':'九霄天将 · 雷鼓刑钟','dragon_king':'东海龙王','dragon_emperor':'龙帝'}
import html
cards=[]
notes={
 'nine_heaven_general':'以实际看过的 Ignited Revenant 作者展示研究“核心与外围结构的主次”；以 Ignis 展示研究攻击部位的辨识度。原创中空刑钟、两侧雷鼓和连通雷环形成身体，中央观察印为视觉中心。没有人体腰腿；沿用地面导航，视觉上低悬滑行，并未新增飞行能力。',
 'dragon_king':'实际查看愚者 0.2.2 / Twilight Forest 4.3.2508 的 Naga 头与躯段、Hydra 原始像素图：借鉴背腹分区和克制的定向鳞片，不复制像素。保留原盘尾、水龙骨架及所有动画，用海青鳞、浅腹板、骨角、鼻口与眼窝恢复身份。实际显示放大1.35倍，受击宽高同步。',
 'dragon_emperor':'同样研究实际安装版本 Naga/Hydra 的头部、腹面、鳞与干净大面的关系。原四足龙、弯颈、九段尾与全部几何保持；独立UV重绘鳞、玉面、青铜甲与骨爪。完整回放发现原步态/爪击低点穿地，新增root最小落地位移，不改旧旋转轨迹、技能或动画长度。'}
for i,id in enumerate(IDS):
 o=D/id
 parts=[f'<section id="{id}"><h2>{NAMES[id]} <small>dynasty:{id}</small></h2><p>{notes[id]}</p>']
 for name in ['compare-front','compare-45','compare-right']:
  parts.append(f'<figure><img loading="lazy" src="{id}/{name}.png"><figcaption>相同机位、取景、光照的前后对照；软件逐面PNG采样。</figcaption></figure>')
 parts.append('<div class="grid">')
 for name in ['front-unlit','45-lit','right-lit','left-lit','back-lit','gray-model','silhouette','gray','dim','scene']:
  parts.append(f'<figure><img loading="lazy" src="{id}/{name}.png"><figcaption>{name} · 软件预览</figcaption></figure>')
 parts.append('</div><details><summary>原始PNG、4倍最近邻、UV编号与方向</summary><div class="grid">')
 for name in ['texture','texture-4x','uv-overlay-4x','uv-direction','uv-side']:
  parts.append(f'<figure><a href="{id}/{name}.png"><img class="pixel" loading="lazy" src="{id}/{name}.png"></a><figcaption>{name}（点击原尺寸）</figcaption></figure>')
 parts.append('</div></details><details><summary>全部六段完整动作 / 关键阶段</summary>')
 for clip in ['idle','walk','attack','cast','hurt','death']:
  parts.append(f'<h3>{clip}</h3><div class="grid"><img loading="lazy" src="{id}/{clip}.webp"><a href="{id}/{clip}-phases.png"><img loading="lazy" src="{id}/{clip}-phases.png"></a></div>')
 parts.append('<p>cast 是已有资源动作，生产控制器没有对应施法状态；没有以QA触发器冒充服务器技能验收。attack 为原0.3秒挥击动画，实机对应标准swing，截图标签不证明伤害接触判定。</p></details><details><summary>正常观察距离</summary><div class="grid">')
 for d in [10,18,28]:parts.append(f'<img loading="lazy" src="{id}/distance-{d}m.png">')
 parts.append('</div></details><h3>原生Forge / 普通日光 / 无粒子</h3><div class="grid">')
 for j,label in enumerate(['front','45','side','back','walk','attack-tell','attack-contact','attack-recovery','hurt','death']):
  file=f'native/checklist-v9-final-clean/{i*10+j:02d}-{id}-{label}.png'
  parts.append(f'<figure><a href="{file}"><img loading="lazy" src="{file}"></a><figcaption>{label} · 游戏截图 · <a href="native/checklist-v9-final-clean/{i*10+j:02d}-state.json">加载哈希与骨骼状态</a></figcaption></figure>')
 parts.append(f'</div><a href="blockbench/{id}.bbmodel">可编辑Blockbench源文件</a></section>');cards+=parts
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Dynasty — 清单遗留Boss V9</title><style>body{margin:0;background:#ecece7;color:#243038;font:17px/1.7 system-ui,sans-serif}main{max-width:1350px;padding:30px;margin:auto}h1,h2{line-height:1.3}h2 small{display:block;font-size:15px;font-weight:400}section{margin:55px 0;border-top:2px solid #bbc2bc;padding-top:20px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:20px}figure{margin:15px 0}img{width:100%;height:auto}img.pixel{image-rendering:pixelated;max-width:1024px}figcaption{font-size:14px;color:#4c595b}a{color:#235d69}summary{cursor:pointer;font-weight:600;padding:16px;background:#dde3dd}details{margin:20px 0}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #bbc2bc;text-align:left}@media(max-width:600px){.grid{display:block}main{padding:15px}}</style><main>
<h1>清单遗留Boss资源 · V9</h1><p>本页区分软件预览与原生游戏截图。前八只已认可Boss与锤链资源保持字节一致。本轮补九霄天将、东海龙王、龙帝，注册ID、身份、掉落与战斗逻辑沿用。没有改变最终Boss镇渊帝君。</p>
<p><a href="#nine_heaven_general">九霄天将</a> · <a href="#dragon_king">东海龙王</a> · <a href="#dragon_emperor">龙帝</a> · <a href="README.md">范围、验证与待验清单</a> · <a href="validation.json">离线验证</a> · <a href="native/checklist-v9-final-clean/PASS.txt">最终原生验证</a></p>
<p>完成：UV/PNG加载、完整资源动作预览、受击尺寸同步、构建与30个原生状态。待验：自然刷新、复杂地形寻路、联机、技能施法可视状态与实际伤害接触；这些没有被静态截图替代。</p>
<h2>真正查看过的作者画面</h2><div class="grid"><figure><img loading="lazy" src="https://media.forgecdn.net/attachments/510/175/2022-10-30_21.png"><figcaption>Ignited Revenant：中央主体与外围防护；作者环境展示并非中性日光。不复制资产。</figcaption></figure><figure><img loading="lazy" src="https://media.forgecdn.net/attachments/510/182/2022-10-30_21.png"><figcaption>Ignis：大型武器/防护明确战斗身份；不把其光影当PNG材质。<a href="https://www.curseforge.com/minecraft/mc-mods/lendercataclysm/gallery">作者画廊</a></figcaption></figure></div>
'''+''.join(cards)+'</main></html>'
(D/'index.html').write_text(page)
print('Gallery written')
