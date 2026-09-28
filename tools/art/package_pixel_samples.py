"""Package only three approval samples. Keep shipped artwork unchanged until approval."""
import json,shutil,subprocess,zipfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/journey-polish-v4'
SOURCE=Path('/Users/a15356015027/.codex/generated_images/01a0b3cd-a8f4-7620-8174-d631c852f383')
ROWS=[('wanjun_ring','万钧戒','exec-f476bb76-01b6-4271-b1a5-413c28c375cf.png'),
      ('lingwen_pendant','灵文佩','exec-c3393e1d-786f-4088-b585-be375bcca240.png'),
      ('jinwu_quiver','金乌箭囊','exec-1c4bccd4-e435-4d73-920b-af7fdaa7a455.png')]
PROMPT="Use case: style-transfer. Edit target: attached Dynasty accessory {key}. Restyle ONLY into crisp hand-authored Minecraft mod inventory pixel art, matching sophisticated but genuinely low-resolution modpack trinkets. Preserve recognizable object type and main colors/silhouette (ring / jade amulet / quiver respectively). Coarse deliberate square pixel clusters on a 32x32 logical grid, 12-20 colors, bold dark outline, 3-tone hard shading, no realistic engraved microdetail, no gradients or glossy photographic rendering. Single complete isolated icon, fills 85% of square canvas, genuine transparent alpha background, no checkerboard, no lettering. This is an approval sample, not an elaborate illustration."
def main():
    for folder in ('before','samples','sources'): (DOC/folder).mkdir(parents=True,exist_ok=True)
    payload={'pack.mcmeta':json.dumps({'pack':{'pack_format':15,'description':'王朝 · 3件像素风试样（关闭即可恢复）'}},ensure_ascii=False).encode()}
    manifest=[];cards=[]
    for key,name,filename in ROWS:
        original=ROOT/f'src/main/resources/assets/dynasty/textures/item/{key}.png'
        shutil.copy2(original,DOC/'before'/f'{key}.png')
        shutil.copy2(SOURCE/filename,DOC/'sources'/f'{key}.png')
        sample=DOC/'samples'/f'{key}.png'
        subprocess.run(['magick',str(SOURCE/filename),'-filter','point','-resize','64x64','PNG32:'+str(sample)],check=True)
        payload[f'assets/dynasty/textures/item/{key}.png']=sample.read_bytes()
        manifest.append(dict(id=key,name=name,mode='built-in image_gen',prompt=PROMPT.format(key=key),source='sources/'+key+'.png',sample='samples/'+key+'.png',sha256=hashlib.sha256(sample.read_bytes()).hexdigest()))
        cards.append(f'<article><h2>{name}</h2><div class="pair"><figure><img src="before/{key}.png"><figcaption>当前版本</figcaption></figure><figure><img src="samples/{key}.png"><figcaption>像素试样 · 64px</figcaption></figure></div><p>实际小图 <img class="small" src="before/{key}.png"> → <img class="small" src="samples/{key}.png"></p></article>')
    (DOC/'assets.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (DOC/'promptset.md').write_text('# 3 accessory style-transfer samples\n\nMode: built-in image_gen.\n\n'+PROMPT+'\n\nOnly nearest-neighbour resizing for game packaging. Original generations retained in sources/.\n')
    pack=ROOT/'modpack/resourcepacks/dynasty-three-pixel-samples.zip';pack.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in payload.items():z.writestr(n,data)
    (DOC/'gallery.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>王朝 · 三件像素试样</title><style>
body{background:#151b20;color:#f0eadc;font:16px/1.6 system-ui;margin:36px auto;max-width:1100px;padding:0 20px}h1{color:#d1b47c}main{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}article{background:#242d34;border:1px solid #4b565e;border-radius:10px;padding:16px}.pair{display:flex;gap:8px}figure{margin:0;width:50%;text-align:center}img{width:100%;image-rendering:pixelated;background:repeating-conic-gradient(#37424b 0% 25%,#2a343b 0% 50%) 0/16px 16px}.small{width:32px;vertical-align:middle}a{color:#98d4d4}@media(max-width:800px){main{grid-template-columns:1fr}}</style>
<h1>三件饰品 · 像素风试样</h1><p>只试这三件，不批量替换。原图仍是默认版本；在游戏「选项 → 资源包」开启 <b>dynasty-three-pixel-samples</b> 可比较，关闭立即恢复。64px试样由图像生成工具制作并以最近邻缩放。</p><main>'''+''.join(cards)+'''</main><h2>这一轮内容</h2><p>每章新增两条支路，共32个任务；淬炼节点列出逐级成本；六种弓统一方向与正反面贴图；新增 FTB Ultimine 与 WorldEdit。</p><p><a href="建筑搭建交接.md">我想进游戏搭建筑：操作与交接说明</a> · <a href="../../quests-remaster/gallery.html">任务总览</a></p></html>''')
    print(pack);print(DOC/'gallery.html')
if __name__=='__main__':main()
