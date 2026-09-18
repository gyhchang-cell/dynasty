"""从生成的任务配置导出可点击布局预览（不是游戏截图）。"""
import base64
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
STRING = r'"(?:\\.|[^"\\])*"'


def string(text, field):
    found = re.search(r'\b' + field + r': (' + STRING + ')', text)
    return json.loads(found[1]) if found else ""


def main():
    chapters = []
    for path in sorted((ROOT / "modpack/config/ftbquests/quests/chapters").glob("*.snbt")):
        raw = path.read_text()
        quests = []
        for block in raw.split("\t\t{\n")[1:]:
            desc = re.search(r'description: \[(.*?)\]', block, re.S)
            icon = re.search(r'icon: \{ id: "([^"]+)"', block)
            image = ""
            if icon and icon[1].startswith("dynasty:"):
                tex = ROOT / ("src/main/resources/assets/dynasty/textures/item/" + icon[1].split(":")[1] + ".png")
                if tex.exists():
                    image = "data:image/png;base64," + base64.b64encode(tex.read_bytes()).decode()
            deps = re.search(r'dependencies: \[(.*?)\]', block)
            quests.append({"id": string(block, "id"), "title": string(block, "title"),
                           "subtitle": string(block, "subtitle"), "image": image,
                           "description": json.loads("[" + desc[1] + "]") if desc else [],
                           "x": float(re.search(r'\bx: (-?[\d.]+)d', block)[1]),
                           "y": float(re.search(r'\by: (-?[\d.]+)d', block)[1]),
                           "milestone": "dynasty unlock_curio " in block,
                           "deps": re.findall(STRING, deps[1]) if deps else []})
            quests[-1]["deps"] = [json.loads(s) for s in quests[-1]["deps"]]
        title = re.search(r'^\ttitle: (' + STRING + ')', raw, re.M)
        chapters.append({"name": json.loads(title[1]), "quests": quests,
                         "group": string(raw, "group"),
                         "order": int(re.search(r'order_index: (\d+)', raw)[1])})
    chapters.sort(key=lambda c: (c["group"], c["order"]))
    html = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>王朝 · 任务布局预览</title>
<style>*{box-sizing:border-box}body{margin:0;background:#101719;color:#eee6d1;font:15px system-ui,-apple-system,sans-serif}header{padding:25px 30px;border-bottom:1px solid #34453e}h1{font-size:25px;margin:0 0 8px;color:#e6c889}p{line-height:1.8}header p{margin:0;color:#aebcb4}main{display:grid;grid-template-columns:205px 1fr 310px;min-height:80vh}nav{padding:20px 10px;border-right:1px solid #34453e}button{width:100%;text-align:left;color:#c7d3cb;border:0;border-radius:5px;padding:12px 10px;background:none;cursor:pointer;font:inherit}button.active,button:hover{background:#263c33;color:#f8d695}.stage{padding:22px;min-width:0}.stage h2{font-size:18px}svg{width:100%;height:650px;background:radial-gradient(ellipse,#1c2c27,#121c1a);border:1px solid #34453e;border-radius:8px}aside{padding:25px 20px;background:#18231f;border-left:1px solid #34453e}aside h2{color:#e6c889;font-size:20px}aside .line{line-height:1.8;margin:9px 0}aside .heading{color:#83ceba;font-weight:700;margin-top:23px}.milestone{color:#e7b5ff}.note{font-size:12px;color:#acb9b0}.node{cursor:pointer}.node:hover circle,.selected circle{stroke:#fff;stroke-width:3}.node image{image-rendering:pixelated;pointer-events:none}.caption{fill:#c1cabf;font-size:11px;pointer-events:none}.legend{display:flex;gap:20px;color:#b3c4ba;font-size:13px;margin-top:12px}@media(max-width:1000px){main{grid-template-columns:170px 1fr}aside{grid-column:1/-1}svg{height:550px}}</style>
<header><h1>王朝 · 山河行纪</h1><p>12 章 · 438 条任务 · 119 件分类饰品 · 五项永久加槽里程碑</p><p class="note">根据实际任务坐标与说明生成的交互预览，不是游戏截图。物品图标沿用现有贴图，尚未重绘。</p></header>
<main><nav id="nav"></nav><section class="stage"><h2 id="chapter"></h2><svg id="map" role="img" aria-label="任务关系图"></svg><div class="legend"><span>绿色：普通任务</span><span class="milestone">金色：永久 +1 万能槽</span><span>点击节点查看说明</span></div></section><aside id="detail"></aside></main>
<script>const chapters=__DATA__;const clean=s=>s.replace(/[&§][0-9a-fklmnor]/gi,'');const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));let selected;
function detail(q){selected=q.id;document.querySelectorAll('.node').forEach(n=>n.classList.toggle('selected',n.dataset.id===q.id));document.getElementById('detail').innerHTML='<p class="note">任务详情</p><h2>'+esc(clean(q.title))+'</h2><p class="milestone">'+esc(clean(q.subtitle))+'</p>'+q.description.map(s=>'<div class="line '+(s.includes('&l')?'heading':'')+'">'+esc(clean(s))+'</div>').join('')+'<p class="note">'+q.id+'</p>';}
function show(i){const c=chapters[i];document.querySelectorAll('nav button').forEach((n,j)=>n.classList.toggle('active',i===j));document.getElementById('chapter').textContent=c.name+' · '+c.quests.length+' 项';const map=document.getElementById('map'), xs=c.quests.map(q=>q.x*48),ys=c.quests.map(q=>q.y*48);map.setAttribute('viewBox',[Math.min(...xs)-55,Math.min(...ys)-55,Math.max(...xs)-Math.min(...xs)+110,Math.max(...ys)-Math.min(...ys)+110].join(' '));let html='';const lookup=new Map(c.quests.map(q=>[q.id,q]));for(const q of c.quests){for(const id of q.deps){const p=lookup.get(id);if(p)html+='<line x1="'+p.x*48+'" y1="'+p.y*48+'" x2="'+q.x*48+'" y2="'+q.y*48+'" stroke="#496555" stroke-width="1.5" opacity=".7"/>';}}for(const q of c.quests){html+='<g class="node" tabindex="0" role="button" data-id="'+q.id+'" aria-label="'+esc(clean(q.title))+'" transform="translate('+q.x*48+','+q.y*48+')"><title>'+esc(clean(q.title))+'</title><circle r="'+(q.milestone?23:19)+'" fill="'+(q.milestone?'#473a23':'#243c30')+'" stroke="'+(q.milestone?'#edc46f':'#71937d')+'" stroke-width="2"/>'+(q.image?'<image href="'+q.image+'" x="-13" y="-13" width="26" height="26"/>':'<text text-anchor="middle" y="5" fill="#d6e0d3">'+(q.milestone?'✦':'◆')+'</text>')+'<text class="caption" text-anchor="middle" y="36">'+esc(clean(q.title).slice(0,9))+'</text></g>';}map.innerHTML=html;map.querySelectorAll('.node').forEach(n=>{n.onclick=()=>detail(lookup.get(n.dataset.id));n.onkeydown=e=>{if(e.key==='Enter')detail(lookup.get(n.dataset.id));};});detail(c.quests.find(q=>q.milestone)||c.quests[0]);}
document.getElementById('nav').innerHTML=chapters.map((c,i)=>'<button onclick="show('+i+')">'+esc(c.name)+'</button>').join('');show(chapters.findIndex(c=>c.name.includes('朝堂')));</script></html>'''
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html.replace("__DATA__", json.dumps(chapters, ensure_ascii=False).replace("<", "\\u003c")))
    print(output)


if __name__ == "__main__":
    main()
