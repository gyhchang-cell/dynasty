"""Mechanical pixel-grid/color adaptation of imagegen assets, with provenance and backup.
Only touches project block textures and docs; never reads/writes a world or live instance.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/vanilla-v9'
TEX=ROOT/'src/main/resources/assets/dynasty/textures/block'

def main():
    records=json.loads((DOC/'generation.json').read_text())
    records.append({'id':'palace_bricks','name':'宫廷砖（已确认样稿）','path':str(ROOT/'docs/art/vanilla-v8-sample/palace_bricks-sample.png'),'prompt':'Reuse user-approved 16x16, 7-color sample unchanged.'})
    result=[]
    for r in sorted(records,key=lambda r:r['id']):
        id=r['id']; source=DOC/'sources'/f'{id}.png';before=DOC/'before'/f'{id}.png';out=DOC/'block'/f'{id}.png'
        for p in (source,before,out):p.parent.mkdir(parents=True,exist_ok=True)
        if not source.exists():shutil.copy2(r['path'],source)
        if not before.exists() and (TEX/f'{id}.png').exists():shutil.copy2(TEX/f'{id}.png',before)
        if id=='palace_bricks':shutil.copy2(source,out)
        else:subprocess.run(['magick',str(source),'-filter','point','-resize','16x16!','-alpha','off','+dither','-colors','10','PNG24:'+str(out)],check=True)
        dims=subprocess.check_output(['magick','identify','-format','%w %h %k',str(out)],text=True).split()
        assert dims[:2]==['16','16'] and int(dims[2])<=10,(id,dims)
        shutil.copy2(out,TEX/f'{id}.png')
        result.append({**r,'colors':int(dims[2]),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'target':str((TEX/f'{id}.png').relative_to(ROOT))})
    (DOC/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    cards=''.join(f'<article><h3>{r["name"]}</h3><div class="pair"><figure><img src="before/{r["id"]}.png"><figcaption>之前</figcaption></figure><figure><img src="block/{r["id"]}.png"><figcaption>16×16 · {r["colors"]}色</figcaption></figure></div><div class="wall" style="background-image:url(block/{r["id"]}.png)"></div><small>{r["id"]}</small></article>' for r in result)
    (DOC/'gallery.html').write_text('''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>王朝 · 16像素方块工坊</title>
<style>body{margin:32px auto;max-width:1280px;padding:24px;background:#202925;color:#eef3e9;font:16px/1.7 system-ui}h1{font-size:30px}a{color:#b4e1b7}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:20px}article{padding:16px;background:#303a34;border:1px solid #526052;border-radius:8px}.pair{display:flex;gap:12px}figure{margin:0;width:50%}img{width:100%;aspect-ratio:1;image-rendering:pixelated}figcaption{font-size:13px;color:#b7c8bc}.wall{height:128px;margin:16px 0;background-size:64px 64px;image-rendering:pixelated}table{border-collapse:collapse;width:100%;margin:24px 0}td,th{text-align:left;padding:10px;border-bottom:1px solid #566057}small{color:#abc0ad}</style>
<h1>王朝 · 16像素方块工坊</h1><p>34 张方块材质统一为真正的 16×16、每张不超过 10 色。宫廷砖沿用已确认的 7 色样稿。只修改 Dynasty 方块；护甲、饰品、原版方块、存档及建筑没有改动。</p>
<p>这是素材与程序模型预览，不是游戏截图。本轮尚未同步到正在运行的实例。</p>
<h2>四种新交互方块</h2><table><tr><th>方块与形状</th><th>右键消耗 → 作用</th></tr>
<tr><td>制革架 · 薄架与双脚</td><td>腐肉×8＋骨粉×2 → 皮革×2</td></tr><tr><td>药浴盆 · 低矮空心盆</td><td>小麦×4＋糖×2＋海带×2 → 解毒、5秒生命恢复I</td></tr><tr><td>琢玉台 · 四脚矮桌</td><td>紫水晶碎片×4＋石英×4 → 玉×1</td></tr><tr><td>御火盆 · 四脚空心铜盆</td><td>木炭×2＋烈焰粉×1 → 2分钟抗火I</td></tr></table>
<p>新增四种和原有四种工坊统一为可朝向摆放、模型与实际碰撞一致。材料放背包，潜行右键查看说明；缺材料不扣除。药浴和御火冷却30秒，其余新加工冷却1秒。</p>
<p><a href="models.html">查看八种工坊模型</a> · <a href="release-notes.md">验证与交付说明</a> · <a href="generation.json">完整 imagegen 提示词</a> · <a href="../vanilla-v8-references/curated-100-gallery.html">100 个模组参考审阅</a></p><section class="grid">'''+cards+'</section></html>')
    subprocess.run(['magick','montage',*[str(DOC/'block'/f'{r["id"]}.png') for r in result],'-set','label','%t','-font','/System/Library/Fonts/Supplemental/Arial.ttf','-pointsize','12','-background','#28312b','-fill','white','-filter','point','-geometry','128x128+8+8','-tile','6x',str(DOC/'contact.png')],check=True)
    print(f'Installed {len(result)} block textures in project only; 16x16 / <=10 colors. Backups: {DOC}/before')

if __name__=='__main__':main()
