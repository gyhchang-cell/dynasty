"""Actual shipped sprites and native-client captures, no simulated gameplay images."""
import html
import json
import shutil
from pathlib import Path
from gen_trinkets7 import ITEMS
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/accessory-refining-v3'
def main():
    new={r['id'] for r in json.loads((DOC/'assets.json').read_text())}
    sections=[]
    for school,title in [('sword','游龙剑舞'),('guard','玄武守御'),('archer','逐星射艺'),('talisman','道门律令')]:
        chains=[]
        for key in new:
            if ITEMS[key]['school']!=school:continue
            chain=[key]
            while ITEMS[chain[0]]['recipe'][0].split(':')[-1] in ITEMS:
                chain.insert(0,ITEMS[chain[0]]['recipe'][0].split(':')[-1])
            cards=[]
            for ident in chain:
                v=ITEMS[ident];src='after/'+ident+'.png' if ident in new else '../school-accessories-v2/after/'+ident+'.png'
                cards.append(f'<article><img src="{src}" alt="{v["zh"]}"><h3>{v["zh"]}</h3><p>{html.escape(v["zh_effect"])}</p></article>')
            chains.append('<div class="chain">'+'<span class="arrow">→</span>'.join(cards)+'</div>')
        sections.append('<h2>'+title+'</h2>'+''.join(chains))
    captures=[]
    (DOC/'runtime').mkdir(exist_ok=True)
    for key in ['book-refining','book-third-tier']:
        p=ROOT/f'build/school-accessories-v2/book-qa/results/{key}.png'
        if p.exists():
            shutil.copy2(p,DOC/'runtime'/p.name)
            captures.append(f'<figure><img class="wide" src="runtime/{p.name}"><figcaption>独立 Minecraft + Patchouli 客户端实际截图</figcaption></figure>')
    for ident in new:
        p=ROOT/f'build/runtime-render-qa/results/item-{ident}.png'
        if p.exists():shutil.copy2(p,DOC/'runtime'/p.name)
    body='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>王朝 · 百炼佩章</title><style>
body{margin:0;background:#111e23;color:#e5e3d4;font:17px/1.7 system-ui}main{max-width:1080px;margin:auto;padding:48px 24px}h1{font-size:54px;margin:12px 0}h2{color:#e8c681;margin-top:54px}.chain{display:flex;align-items:center;gap:14px;margin:18px 0}article{flex:1;text-align:center;background:#203138;padding:22px 12px;border:1px solid #40565c;border-radius:16px}article img{width:128px;height:128px}article h3{margin:8px 0}article p{font-size:14px;color:#bbd8ce}.arrow{color:#e8c681;font-size:26px}.notice{border-left:3px solid #d8b77b;padding:16px 24px;background:#213239}a{color:#9ad8e3}.wide{width:100%}figure{margin:24px 0}small,figcaption{color:#9eafb4}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:12px;border-bottom:1px solid #3a5058}@media(max-width:600px){article img{width:82px;height:82px}.chain{gap:5px}article{padding:12px 4px}h1{font-size:38px}}</style><main>
<small>DYNASTY / ACCESSORY REFINEMENT 03 / 2026-09-24</small><h1>百炼佩章</h1><p>本轮 8 件新品 · 8 条三阶路线 · 24 件可淬炼饰品 · 新增 28 个流派任务</p>
<p class="notice">锻造台进化：兵器图纸 + 上一阶饰品 + 对应材料。保留强化、附魔和名称。铁砧淬炼：饰品 + 指定材料，取出才消耗材料与经验。佩戴后增伤，同名饰品只取最高淬炼；不需要主动按键。</p>
<h2>同一件，也能持续变强</h2><p>淬炼额外伤害 = 4% × √等级。+1 为 4%，+25 为 20%，+100 为 40%。单级收益递减，没有固定毕业等级。材料数量与经验成本增长后分别封顶 64 份、39 级，避免铁砧“过于昂贵”阻断后期成长。</p>
<table><tr><th>当前淬炼等级</th><th>下一次材料</th></tr><tr><td>0–9</td><td>玉</td></tr><tr><td>10–24</td><td>龙晶</td></tr><tr><td>25–49</td><td>玄天玉</td></tr><tr><td>50+</td><td>天将令</td></tr></table>
<p>每个流派有两条饰品进化连线，以及独立的「铁砧 → +1 → +5 → +15 → +30」淬炼任务线。任务检测真实等级；+30 是里程碑，不是上限。流派章节各 35 个节点，整本 35 章 / 664 节点，主线仍为 69 节点。</p>
'''
    body+=''.join(sections)+'<h2>书中可直接查配方</h2>'+''.join(captures)
    body+='<p>上方饰品是实际资源贴图；每件独立生成后机械裁切、缩放。不是概念图。<a href="assets.json">原图与完整提示词</a> · <a href="DELIVERY.md">验证与交付说明</a> · <a href="../../quests-remaster/gallery.html">完整任务配置预览</a></p></main></html>'
    (DOC/'gallery.html').write_text(body)
    print(DOC/'gallery.html')
if __name__=='__main__':main()
