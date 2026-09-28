#!/usr/bin/env python3
"""Package already-generated RGBA artwork and document the actual project assets.

No image API calls and no procedural painting: Java only crops/resizes the saved
source sprites using the existing Minecraft item integration pipeline.
"""
import html
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/art/schools-remaster-v1"
RES = ROOT / "src/main/resources/assets/dynasty"
SCHOOLS = {
    "guard": ("玄武守御", "接住正面来袭，再以一记反击打出优势。", "#cfb079"),
    "sword": ("游龙剑舞", "追踪同一个目标，掌握三击收势的节奏。", "#9de1d8"),
    "archer": ("逐星射艺", "满弦留下标记，第二箭精确追击。", "#92baff"),
    "talisman": ("道门律令", "择地施令，站定凝神，再把握进攻时机。", "#d7b1ed"),
}


def main():
    assets = json.loads((DOC / "final-assets.json").read_text())
    expected = {i["id"] for i in json.loads((ROOT / "docs/content/schools-v1-contract.json").read_text())["items"]}
    assert {a["id"] for a in assets} == expected | {"imperial-dawn", *(f"zhuxing_bow_pulling_{i}" for i in range(3))}
    classes = ROOT / "build/school-art"
    classes.mkdir(parents=True, exist_ok=True)
    subprocess.run(["javac", "-d", str(classes), str(ROOT / "tools/art/PackRemasterAssets.java")], check=True)
    for asset in assets:
        source = DOC / asset["project_source"]
        assert source.is_file(), source
        if asset["id"] == "imperial-dawn":
            target = RES / "textures/gui/title/imperial-dawn.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        else:
            subprocess.run(["java", "-cp", str(classes), "PackRemasterAssets", "item", str(source),
                            str(RES / f'textures/item/{asset["id"]}.png')], check=True)
    gallery()


def gallery():
    contract = json.loads((ROOT / "docs/content/schools-v1-contract.json").read_text())
    cards = []
    slots = {"body":"身体", "bracelet":"手镯", "belt":"腰带", "necklace":"项链",
             "ring":"戒指", "charm":"护符", "back":"背部"}
    for school, (title, sub, color) in SCHOOLS.items():
        rows = []
        for item in (i for i in contract["items"] if i["school"] == school):
            key = item["id"]
            sprite = f"../../../src/main/resources/assets/dynasty/textures/item/{key}.png"
            kind = "流派兵器" if item["kind"] == "weapon" else "Curios · " + slots[item["slot"]]
            rows.append(f'<article><a href="source/{key}.png" title="查看美术原图"><img class="sprite" src="{sprite}" alt="{html.escape(item["zh"])}"></a>'
                        f'<div class="sample">物品格预览 <img src="{sprite}" alt="{html.escape(item["zh"])}格子大小"></div>'
                        f'<small>{kind}</small><h3>{html.escape(item["zh"])}</h3><p>{html.escape(item["zh_effect"])}</p></article>')
        cards.append(f'<section style="--accent:{color}"><h2>{title}</h2><p class="lead">{sub}</p><div class="cards">'+''.join(rows)+'</div></section>')
    stages = ''.join(f'<img src="../../../src/main/resources/assets/dynasty/textures/item/zhuxing_bow_pulling_{i}.png" alt="拉弓阶段{i+1}">' for i in range(3))
    actual = DOC / "title-menu.png"
    hero = ('<img class="hero" src="title-menu.png" alt="Minecraft客户端实际主菜单截图"><p class="caption">实际 Minecraft 开发客户端主菜单截图；未进入用户存档。</p>'
            if actual.is_file() else '<img class="hero" src="source/imperial-dawn.png" alt="王朝原创封面美术"><p class="caption">原创封面美术，非游戏世界截图。</p>')
    (DOC / "gallery.html").write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>王朝 · 四脉新章</title><style>
*{box-sizing:border-box}body{margin:0;background:#09171b;color:#ecdfc4;font:16px/1.8 system-ui,sans-serif}main{max-width:1280px;margin:auto;padding:38px 32px 70px}h1{font-size:48px;margin:0}h2{font-size:30px;color:var(--accent);margin:0}h3{font-size:24px;margin:8px 0}small,.caption{color:#a2b8b7}.eyebrow{letter-spacing:5px;color:#cfb079}.lead{color:#b6ceca}.hero{width:100%;border:1px solid #5a5b45;border-radius:5px}.caption{font-size:13px}section{margin:48px 0}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}article{padding:24px;border:1px solid #34484a;border-top:3px solid var(--accent);background:#12252b;border-radius:5px}article p{font-size:15px}a{color:#b0d9e1}.sprite{width:100%;height:220px;object-fit:contain;image-rendering:pixelated;background:radial-gradient(ellipse,#33484f,#112228)}.sample{display:flex;align-items:center;gap:12px;font-size:12px;color:#a2b8b7;margin:14px 0}.sample img{width:48px;height:48px;image-rendering:pixelated;background:#8a8a8a;border:3px ridge #ddd}.stages{display:flex;gap:22px}.stages img{width:27%;max-width:180px;image-rendering:pixelated}.note{border-left:3px solid #cfb079;padding:12px 18px;background:#12252b}@media(max-width:800px){.cards{grid-template-columns:1fr}main{padding:25px 18px}h1{font-size:36px}}
</style><main><div class="eyebrow">DYNASTY / 四脉新章</div><h1>同一段王朝路，四种战斗方式</h1><p class="lead">4 件新武器 · 8 件新饰品 · 独立招式试炼 · 主线顺序不变</p>'''+hero+
        '<p class="note">装备图展示实际打包的 128×128 透明贴图，最长边占 120 像素。不是用一张画替代整套图标；点图可看各自的生成原图。下面的物品格是网页大小预览，不是游戏截图。</p>'+
        ''.join(cards)+'<section><h2>逐星弓 · 三段拉弓</h2><p>专属弓身、弦与搭弦的箭，拉开后不切回原版木弓贴图。</p><div class="stages">'+stages+'</div></section>'+
        ('<section><h2>青龙偃月刀 · 竖直俯冲</h2><p>攻击龙单独调整头颈姿态，长身竖直、尾巴在上，龙嘴沿法阵中心落下。保留原来1.5倍攻击体型和12格额外起始高度，装饰龙不变。</p><img class="hero" style="max-width:760px" src="dragon-dive.png" alt="青龙竖直俯冲的游戏渲染器离屏截图"><p class="caption">实际 Minecraft 渲染器离屏帧，非玩家存档中的战斗截图。后羿弓另已移除准心前法阵，脚下结界、虚影和箭上法阵保留。</p></section>' if (DOC / 'dragon-dive.png').is_file() else '')+
        '<p><a href="../../quests-remaster/gallery.html">查看任务书布局预览</a> · <a href="final-assets.json">美术来源与完整提示词</a></p></main></html>', encoding="utf-8")
    print("Saved", DOC / "gallery.html")


if __name__ == "__main__":
    main()
