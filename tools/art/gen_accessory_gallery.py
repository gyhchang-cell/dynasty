"""Publish real sprites and optional Minecraft captures, never simulated game evidence."""
import html
import json
import shutil
from pathlib import Path
from gen_trinkets7 import ITEMS,TRINKETS
from gen_codex_all import use_line
from gen_curios import SLOT_NAMES
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/school-accessories-v2'
SCHOOLS={'sword':('游龙剑舞','近战直接增伤，搭配攻速。'), 'guard':('玄武守御','护甲韧性也能成为进攻收益。'),
         'archer':('逐星射艺','专门提高箭矢伤害，不改弹道。'), 'talisman':('道门律令','强化敕令笔、雷符杖、太乙剑、太乙拂尘与混元杖。')}
def main():
    sections=[]
    for school,(title,intro) in SCHOOLS.items():
        cards=[]
        for k,v in ITEMS.items():
            if v['school']!=school:continue
            stats=use_line(TRINKETS[k],(0,0,0),0,True)
            if v['zh_effect']:stats.insert(0,v['zh_effect'])
            old=ITEMS.get(v['recipe'][0].split(':')[-1])
            upgrade='由 '+old['zh']+' 升级' if old else '基础件'
            cards.append(f'<article><img src="after/{k}.png" alt="{v["zh"]}"><small>{SLOT_NAMES[v["slot"]]} / {upgrade}</small><h3>{v["zh"]}</h3><p>{"<br>".join(map(html.escape,stats))}</p></article>')
        sections.append(f'<h2>{title}</h2><p>{intro}</p><div class="grid">{"".join(cards)}</div>')
    old=[]
    for row in json.loads((DOC/'remasters.json').read_text()):
        k=row['id'];old.append(f'<article><div class="compare"><figure><img src="before/{k}.png"><figcaption>旧版 32px</figcaption></figure><figure><img src="after/{k}.png"><figcaption>重制 128px</figcaption></figure></div><h3>{row["zh"]}</h3></article>')
    captures=[]
    out=DOC/'runtime';out.mkdir(parents=True,exist_ok=True)
    for key in ['school-accessory-tooltips','book-new-accessory']:
        src=ROOT/f'build/school-accessories-v2/book-qa/results/{key}.png'
        if src.exists():
            shutil.copy2(src,out/src.name);captures.append(f'<figure><img class="wide" src="runtime/{key}.png"><figcaption>独立 Minecraft 客户端实际截图</figcaption></figure>')
    for k in ITEMS:
        src=ROOT/f'build/runtime-render-qa/results/item-{k}.png'
        if src.exists():shutil.copy2(src,out/src.name)
    rows=[('01 安家','铁镐、水桶：为采矿与返程准备工具'),('02 工坊','精钢、锻造台：建立兵器升级工位'),
          ('03 平叛','金创膏：首战前的应急治疗'),('04 天朝','延寿丹：跨维度探索的持续恢复'),
          ('05 幽冥','复战祭坛：利用首杀信物继续获取材料'),('06 九霄','御风符：45秒缓降与机动准备'),
          ('07 龙宫','末影箱：跨维度保管稀有战利品'),('08 问鼎','金苹果：终战应急补给')]
    doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>王朝 · 四脉佩章</title><style>
body{margin:0;background:#10201f;color:#eee6cf;font:16px/1.75 system-ui}main{max-width:1160px;margin:auto;padding:42px 24px}h1{font-size:48px;letter-spacing:.12em;margin:4px 0}h2{margin-top:52px;color:#e3c987}h3{margin:10px 0 6px}p,small{color:#b9c9c2}a{color:#91d7c6}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}article{padding:18px;border:1px solid #34504a;background:#182d29;border-radius:12px}article img{width:100%;height:200px;object-fit:contain;image-rendering:pixelated}article p{font-size:14px;min-height:70px;margin:0}article small{display:block;font-size:12px}.compare{display:grid;grid-template-columns:1fr 1fr;gap:8px}.compare img{height:150px}.compare figure{margin:0}.compare figcaption{font-size:12px;text-align:center;color:#9db8ac}.old{grid-template-columns:repeat(3,1fr)}.wide{max-width:100%;border:1px solid #34504a}figure{margin:16px 0}table{border-collapse:collapse;width:100%}td{border-bottom:1px solid #34504a;padding:10px}.notice{border-left:3px solid #ddbd77;padding:15px;background:#213830}@media(max-width:800px){.grid,.old{grid-template-columns:repeat(2,1fr)}h1{font-size:36px}}</style><main>
<small>DYNASTY / SCHOOL ACCESSORIES 02 / 2026-09-24</small><h1>四脉佩章</h1><p>16 件新饰品 · 8 条材料升级链 · 12 件旧贴图重制 · 主线 59 → 69 节点</p>
<p class="notice">佩戴后被动生效，属性逐行显示。相同饰品重复佩戴不重复结算；不同饰品的本批增伤相加。基础件可消耗材料升级为同槽位的进阶件。饰品任务独立排列，不是主线或兵器进化的门槛。</p>
'''
    doc+=''.join(sections)+'<h2>旧饰品 · 前后对比</h2><p>以下是实际替换进资源包的素材，不是概念图；已重制的其他美术保持不变。</p><div class="grid old">'+''.join(old)+'</div>'
    doc+='<h2>每章多一步实际准备</h2><table>'+''.join('<tr><td>'+a+'</td><td>'+b+'</td></tr>' for a,b in rows)+'</table><p><a href="../../quests-remaster/gallery.html">查看完整任务配置预览</a>（不是游戏截图）</p>'
    doc+='<h2>游戏内验证</h2>'+''.join(captures)
    doc+='<p>图标已通过独立 Minecraft 渲染器加载；上述图标本身为贴图预览。服务器测试覆盖伤害类型隔离、穿戴/卸下、韧性转伤害上限与真实配方注册。</p>'
    doc+='<p><a href="assets.json">新饰品素材与完整提示词</a> · <a href="remasters.json">旧贴图重制与完整提示词</a> · <a href="DELIVERY.md">交付与验证记录</a></p></main></html>'
    (DOC/'gallery.html').write_text(doc)
    print(DOC/'gallery.html')
if __name__=='__main__':main()
