"""Visible sample comparisons, per-face evidence, and honest native scope."""
from create import *
import html
refs=[
 {'name':'Human Companions · 骑士与弓手','page':'https://www.curseforge.com/minecraft/mc-mods/human-companions','image':'https://media.forgecdn.net/attachments/423/810/models.png','study':'实际查看作者双人物图。借鉴皮肤、脸部与衣甲分区；天将改用分段肢体、厚甲和独立持械。没有复制像素。'},
 {'name':'MCA Reborn · Genetics and Clothing','page':'https://www.curseforge.com/minecraft/mc-mods/minecraft-comes-alive-reborn/gallery','image':'https://media.forgecdn.net/attachments/441/18/2022-03-16_20.png','study':'实际查看Carlos人物图。借鉴脸与衣袍的明度关系、连贯滚边；龙帝改用原创帝冠、分片袍摆和宽肩。'},
 {'name':'Electroblob’s Wizardry · 冰系巫师','page':'https://github.com/Electroblob77/Wizardry/wiki/Wizard','image':'https://media.forgecdn.net/attachments/202/398/2017-01-16_20.png','study':'实际查看Wiki中的塔内冰系巫师。借鉴人脸、白须和衣袍的层次；龙王保留人类下颌、冠角与海青仪袍，未使用动物嘴。'},
 {'name':'Iron’s Spells · Pyromancer Enemy','page':'https://www.curseforge.com/minecraft/mc-mods/irons-spells-n-spellbooks/gallery','image':'https://media.forgecdn.net/attachments/653/528/2023-04-27_19.png','study':'实际查看红树林屋内火焰法师。借鉴深袍与腰带的主次；不把屋内阴影当作PNG明暗，也不复制尖帽、纹样。'}
]
(D/'references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
cards=[]
for i,id in enumerate(IDS):
 cards.append(f'<section id="{id}"><h2>{NAMES[id]} <small>dynasty:{id}</small></h2>')
 for f in ['compare-front','compare-45','compare-side']:cards.append(f'<figure><img loading="lazy" src="{id}/{f}.png"><figcaption>同机位、同尺度、相同基础光照；软件逐面PNG预览。</figcaption></figure>')
 cards.append('<div class="grid">')
 for f in ['front-unlit','45-lit','side-lit','back-lit','gray-model','silhouette','gray','dim','scene','close-face','close-torso','close-hand']:cards.append(f'<figure><a href="{id}/{f}.png"><img loading="lazy" src="{id}/{f}.png"></a><figcaption>{f} · 软件预览</figcaption></figure>')
 cards.append('</div><details><summary>原始PNG / 4倍最近邻 / UV方向</summary><div class="grid">')
 for f in ['texture','texture-4x','uv-overlay-4x','uv-direction']:cards.append(f'<figure><a href="{id}/{f}.png"><img class="pixel" loading="lazy" src="{id}/{f}.png"></a><figcaption>{f}</figcaption></figure>')
 cards.append('</div></details><details><summary>六段完整资源动作与阶段表</summary>')
 for clip in ['idle','walk','attack','cast','hurt','death']:cards.append(f'<h3>{clip}</h3><div class="grid"><img loading="lazy" src="{id}/{clip}.webp"><a href="{id}/{clip}-phases.png"><img loading="lazy" src="{id}/{clip}-phases.png"></a></div>')
 cards.append('<p>cast为完整资源回放；现有生产控制器没有服务器施法状态绑定。标准近战使用真实swing；画面“contact”表示视觉出击峰值，不等于伤害判定已验收。</p></details><h3>普通原生Forge光照 / 玩家视高1.62m</h3><div class="grid">')
 for j,label in enumerate(['front','45','side','back','walk','attack-tell','attack-contact','attack-recovery','hurt','death']):
  file=f'native/human-v10-final/{i*10+j:02d}-{id}-{label}.png'
  cards.append(f'<figure><a href="{file}"><img loading="lazy" src="{file}"></a><figcaption>{label} · 游戏截图 · <a href="native/human-v10-final/{i*10+j:02d}-state.json">实际资源哈希/姿态</a></figcaption></figure>')
 cards.append(f'</div><p><a href="blockbench/{id}.bbmodel">可编辑bbmodel（含贴图、全部动作）</a></p></section>')
refcards=''.join(f'<figure><img loading="lazy" src="{r["image"]}"><figcaption><a href="{r["page"]}">{r["name"]}</a>：{r["study"]}</figcaption></figure>' for r in refs)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Dynasty 三位人形Boss V10</title><style>body{margin:0;background:#ecece7;color:#273238;font:17px/1.7 system-ui}main{max-width:1400px;padding:30px;margin:auto}img{width:100%;height:auto}img.pixel{image-rendering:pixelated}figure{margin:15px 0}figcaption,small{font-size:14px}small{display:block}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:24px}section{margin-top:55px;border-top:2px solid #aabbb9;padding-top:20px}summary{cursor:pointer;background:#dae1dc;padding:14px}details{margin:20px 0}a{color:#235d69}table{width:100%;border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #bbc5bd;text-align:left}@media(max-width:600px){.grid{display:block}main{padding:15px}}</style><main>
<h1>九霄天将 / 东海龙王 / 龙帝 · 人形Boss V10</h1><p>2026-10-12用户明确要求这三只采用人形。与已认可八只非人形Boss分开处理；注册ID、身份、掉落、核心技能不更换。原色、基础光照、游戏截图分别标注。</p>
<p><a href="#nine_heaven_general">天将</a> · <a href="#dragon_king">龙王</a> · <a href="#dragon_emperor">龙帝</a> · <a href="validation.json">离线验证</a> · <a href="native/human-v10-final/PASS.txt">原生验证</a> · <a href="README.md">改动与验证边界</a></p><img src="overview.png" alt="相同世界尺度的人形Boss和玩家">
<h2>与真正查看过的样本对照</h2><p>样本用于人形可读性，未作为模型或皮肤底稿。作者画面与我们的普通日光实机图均保留；室内画面、太阳方向和截图机位不完全一致，不能宣称逐像素公平评比。原色图单独检验PNG。</p><div class="grid">'''+refcards+'''</div>
<h2>实际返工记录</h2><table><tr><th>观察到的差距</th><th>改动</th><th>证据</th></tr><tr><td>第一轮眼形过大，甲面仍像空白盒子</td><td>收紧眼白/眉眼，连续胸甲带和布袍身份纹；保留干净大面</td><td>面部/躯干近景、灰度、实机正面</td></tr><tr><td>抬手前后方向错误，长兵器出击时刃朝向不清</td><td>纠正肩肘旋转、兵器协同；视觉峰值位于原6 tick动作中段</td><td>完整attack/cast回放</td></tr><tr><td>第三轮实机胸腰露天空；短攻击被2 tick过渡吞掉</td><td>加厚已有腰段形成连续衣体；仅三Boss的挥击/受击/死亡过渡为0</td><td>最终原生正侧面、观察真实出击峰值后截帧</td></tr><tr><td>脚部与甲袍抢主次、背雷纹位置偏低</td><td>脚保持7.5×4×10单位；肩胸主导体量，雷纹上移至上躯后方</td><td>玩家比例/侧面/黑剪影</td></tr></table>
<p>我的判断：本版保留样本的人物识别与克制像素语言，额外提供Boss体量、厚甲/袍摆层次、肘膝动作和明确的进攻方向。不能用这一点宣称整体审美客观胜过原作者。自然寻路、联机和服务器施法同步仍待验，未用摆拍替代。</p>
'''+''.join(cards)+'</main></html>'
(D/'index.html').write_text(page)
print('Human gallery written')
