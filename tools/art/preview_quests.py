"""Clickable native-image/QuestLink preview of the exact generated book, not a game screenshot."""
import copy
import json
import os
from pathlib import Path
import sys
from quest_routes import GROUPS
from quest_story import DOC, OUT, ROOT, encode


def preview_data(output):
    chapters=json.loads((DOC/"book.json").read_text())
    for c in chapters:
        assert encode(c)==(OUT/"chapters"/(c["file"]+".snbt")).read_text(), "Stale quest preview: "+c["file"]
    chapters=copy.deepcopy(chapters)
    group_order={n:i for i,(n,_) in enumerate(GROUPS)}
    chapters.sort(key=lambda c:(group_order[c["group"]],c["order"]))
    for c in chapters:
        for decoration in c.get("images",[]):
            resource=ROOT/"src/main/resources/assets"/decoration["image"].replace(":","/",1)
            decoration["url"]=os.path.relpath(resource,output.parent)
        for q in c["quests"]:
            q["image"]=""
            icon=q["icon"].split('"')[1]
            if icon.startswith("dynasty:"):
                for kind in ("item","block"):
                    resource=ROOT/f"src/main/resources/assets/dynasty/textures/{kind}/{icon.split(':')[1]}.png"
                    if resource.exists():
                        q["image"]=os.path.relpath(resource,output.parent);break
    return chapters


HTML=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>王朝 · 山河行纪 / 流派任务图鉴</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0c1719;color:#e5e3d6;font:14px system-ui,-apple-system,sans-serif}header{padding:24px 28px;border-bottom:1px solid #33463f;background:linear-gradient(90deg,#17312c,#0e1c21)}h1{font-family:serif;font-size:27px;font-weight:500;letter-spacing:3px;color:#e3c78e;margin:0 0 7px}p{line-height:1.8;margin:7px 0}header p{color:#b3c5bd}.note{font-size:12px;color:#a0b5ad}main{display:grid;grid-template-columns:224px minmax(440px,1fr) 310px;min-height:calc(100vh - 132px)}nav{padding:16px 10px;border-right:1px solid #304940}details{margin-bottom:12px}summary{padding:8px;color:#dcc690;cursor:pointer}button{font:inherit;border:0;cursor:pointer;color:#c6d7ce;background:transparent;text-align:left;border-radius:5px;padding:10px 12px}nav button{width:100%;font-size:13px}button.active,button:hover{background:#244239;color:#f6dda7}.stage{padding:20px;min-width:0}.stage h2{font:21px serif;color:#e8ce98;margin:0 0 7px}#goal{min-height:48px;font-size:13px;color:#b8c7bd}.toolbar{display:flex;gap:10px;margin:10px 0}.toolbar button{border:1px solid #385548;padding:7px 12px}svg{display:block;width:100%;height:660px;background:radial-gradient(ellipse,#1c2d2b,#0b181d);border:1px solid #355047;border-radius:9px}aside{padding:24px 20px;border-left:1px solid #304940;background:#122422}aside h2{font:23px serif;color:#ead1a2;line-height:1.5}.line{line-height:1.8;margin:8px 0;overflow-wrap:anywhere}.heading{font-weight:600;color:#92d2be;margin-top:20px}.description-link{color:#8edcd8;display:block;width:100%;text-decoration:underline;padding-left:0}.node{cursor:pointer;outline:none}.node .outline{fill:#244237;stroke:#95b89e;stroke-width:1.7}.node:hover .outline,.node:focus .outline,.node.selected .outline{stroke:#ffe1a3;stroke-width:3;fill:#365a46}.node.link .outline{stroke-dasharray:4 3;fill:#152e35;stroke:#8ebcca}.node.milestone .outline{fill:#544629;stroke:#edcd87}.node image{image-rendering:pixelated;pointer-events:none}.caption{fill:#c6d6c8;font-size:10.5px;pointer-events:none;paint-order:stroke;stroke:#10251f;stroke-width:3px}.legend{display:flex;flex-wrap:wrap;gap:15px;padding:12px 0;font-size:12px;color:#a9c5ba}.map-image.link{cursor:pointer}.map-image.link:hover{filter:brightness(1.5)}#stats strong{color:#ecce8e}@media(max-width:1150px){main{grid-template-columns:180px 1fr}aside{grid-column:1/-1;border-top:1px solid #304940}svg{height:620px}}@media(max-width:680px){main{display:block}nav{max-height:260px;overflow:auto}.stage{padding:12px}svg{height:550px}}
</style>
<header><h1>王朝 · 山河行纪</h1><p id="stats"></p><p class="note">生成任务配置的可点击预览，不是游戏截图。实色节点是真实任务；虚线入口引用原有任务，不重复给奖励。</p></header>
<main><nav id="nav"></nav><section class="stage"><h2 id="chapter"></h2><p id="goal"></p><div class="toolbar"><button onclick="show(0)">山河总览</button><button onclick="goBack()">← 上个页面</button><button onclick="show(chapters.findIndex(c=>c.file==='dynasty_boss_guides'))">Boss 攻略</button></div><svg id="map" role="img" aria-label="王朝任务布局"></svg><div class="legend"><span>◇ 核心节点</span><span>□ 阅读 / 图鉴</span><span>↗ 虚线：已有任务快捷入口</span><span>六边形：永久加槽</span></div></section><aside id="detail"></aside></main>
<script>
const chapters=__DATA__,groups=__GROUPS__,all=new Map(chapters.flatMap(c=>c.quests.map(q=>[q.id,q])));let current=-1,history=[];
const clean=s=>s.replace(/[&§][0-9a-fklmnor]/gi,''),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function jump(id){const chapter=chapters.findIndex(c=>c.id===id);if(chapter>=0){show(chapter);return;}const i=chapters.findIndex(c=>c.quests.some(q=>q.id===id));if(i>=0){show(i);detail(all.get(id));}}
function goBack(){if(!history.length)return;const i=history.pop();show(i,false);}
function line(s){if(s.startsWith('{"')){const c=JSON.parse(s);if(c.clickEvent?.action==='change_page')return '<button class="description-link" onclick="jump(\''+c.clickEvent.value+'\')">'+esc(c.text)+'</button>';}return '<div class="line '+(s.includes('&l')?'heading':'')+'">'+esc(clean(s))+'</div>';}
function detail(q){document.querySelectorAll('.node').forEach(n=>n.classList.toggle('selected',n.dataset.id===q.id));document.getElementById('detail').innerHTML='<p class="note">'+(q.kind==='checkmark'?'阅读 / 导航 · 不检测操作':q.kind==='advancement'?'成就检测 · 服务器实际授予':q.kind==='kill'?'击杀检测 · 不限制指定武器':q.kind==='dimension'?'维度检测 · 实际进入':'持有物品检测 · 不消耗物品')+'</p><h2>'+esc(clean(q.title))+'</h2><p class="note">'+esc(clean(q.subtitle))+'</p>'+q.description.map(line).join('')+'<p class="note">固定任务 ID：'+q.id+'</p>';}
function outline(shape,r){if(shape==='circle')return '<circle class="outline" r="'+r+'"/>';const n=shape==='hexagon'?6:shape==='gear'?8:4,offset=shape==='square'?Math.PI/4:0;let pts=[];for(let j=0;j<n;j++){const a=j*Math.PI*2/n+offset;pts.push(Math.cos(a)*r+','+Math.sin(a)*r);}return '<polygon class="outline" points="'+pts.join(' ')+'"/>';}
function show(i,remember=true){if(i<0)return;if(remember&&current>=0&&current!==i)history.push(current);current=i;const c=chapters[i];document.querySelectorAll('nav button').forEach(n=>n.classList.toggle('active',Number(n.dataset.index)===i));document.getElementById('chapter').textContent=clean(c.title);document.getElementById('goal').textContent=c.goal;const nodes=[...c.quests,...(c.quest_links||[]).map(l=>({...all.get(l.linked_quest),...l,link:true}))],map=document.getElementById('map'),xs=nodes.map(q=>q.x*48),ys=nodes.map(q=>q.y*48);for(const im of c.images||[]){xs.push((im.x-im.width/2)*48,(im.x+im.width/2)*48);ys.push((im.y-im.height/2)*48,(im.y+im.height/2)*48);}map.setAttribute('viewBox',[Math.min(...xs)-25,Math.min(...ys)-25,Math.max(...xs)-Math.min(...xs)+50,Math.max(...ys)-Math.min(...ys)+50].join(' '));let html='';for(const im of [...(c.images||[])].sort((a,b)=>a.order-b.order)){html+='<image class="map-image '+(im.click?'link':'')+'" href="'+esc(im.url)+'" x="'+(im.x-im.width/2)*48+'" y="'+(im.y-im.height/2)*48+'" width="'+im.width*48+'" height="'+im.height*48+'" opacity="'+im.alpha/255+'" '+(im.click?'onclick="jump(\''+im.click.slice(1)+'\')"':'')+'/>';}
const lookup=new Map(c.quests.map(q=>[q.id,q]));for(const q of c.quests)for(const id of q.deps){const p=lookup.get(id);if(p)html+='<path d="M'+p.x*48+','+p.y*48+' L'+q.x*48+','+q.y*48+'" fill="none" stroke="#839e7b" stroke-width="1.8" opacity=".58"/>';}
for(const q of nodes){const r=20*(q.size||1),milestone=q.rewards?.includes('dynasty unlock_curio');html+='<g class="node '+(q.link?'link ':'')+(milestone?'milestone':'')+'" tabindex="0" role="button" data-id="'+q.id+'" '+(q.link?'data-target="'+q.linked_quest+'"':'')+' aria-label="'+esc(clean(q.title))+'" transform="translate('+q.x*48+','+q.y*48+')"><title>'+esc(clean(q.title))+'</title>'+outline(q.shape,r)+(q.image?'<image href="'+esc(q.image)+'" x="-14" y="-14" width="28" height="28"/>':'<text text-anchor="middle" y="5" fill="#e5d9a3">'+(q.link?'↗':'◆')+'</text>')+(q.link?'<text x="13" y="-13" fill="#b4def2" font-size="12">↗</text>':'')+'<text class="caption" text-anchor="middle" y="'+(r+15)+'">'+esc(clean(q.title).slice(0,10))+'</text></g>';}
map.innerHTML=html;map.querySelectorAll('.node').forEach(n=>{const activate=()=>n.dataset.target?jump(n.dataset.target):detail(all.get(n.dataset.id));n.onclick=activate;n.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate();}};});detail(c.quests[0]);}
document.getElementById('nav').innerHTML=groups.map(([id,g],gi)=>'<details '+(gi<3?'open':'')+'><summary>'+esc(clean(g))+'</summary>'+chapters.map((c,i)=>c.group===id?'<button data-index="'+i+'" onclick="show('+i+')">'+esc(clean(c.title).split(' · ')[0])+'</button>':'').join('')+'</details>').join('');
document.getElementById('stats').innerHTML='<strong>8</strong> 章主线 · <strong>4</strong> 条战斗流派 · <strong>9</strong> 类饰品 · '+chapters.reduce((n,c)=>n+c.quests.length,0)+' 任务 · '+chapters.reduce((n,c)=>n+(c.quest_links||[]).length,0)+' 图鉴快捷入口 · 488 条旧任务进度保留';show(0);
</script></html>'''


def main():
    output=Path(sys.argv[1]).resolve()
    chapters=preview_data(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(HTML.replace("__DATA__",json.dumps(chapters,ensure_ascii=False).replace("<","\\u003c"))
                     .replace("__GROUPS__",json.dumps(GROUPS,ensure_ascii=False)))
    print(output)


if __name__=="__main__": main()
