"""Package generated armor sheets and biome-specific travel-site data; never touches saves."""
import json,shutil,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/build-feedback-v5'
RES=ROOT/'src/main/resources'
SOURCE=Path('/Users/a15356015027/.codex/generated_images/01a0b3cd-a8f4-7620-8174-d631c852f383')
SETS=[('general','将军','exec-13cd6776-73bb-4e9b-92fb-e0b0b00789e5.png'),('jade','玉甲','exec-f85d7d6e-2226-4851-8894-d8e601d84da0.png'),('sky','天界','exec-9d1ab3dd-0d9c-4754-b334-005f8959b5be.png')]
SITES=[('post_house','官道驿站',0,['minecraft:plains','minecraft:sunflower_plains']),('herbal_retreat','林间药庐',1,['minecraft:forest','minecraft:birch_forest','minecraft:flower_forest']),('desert_caravan','沙海商旅院',2,['minecraft:desert'])]
def write(rel,data):
    p=RES/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    for d in ('sources','before','armor'): (DOC/d).mkdir(parents=True,exist_ok=True)
    manifest=[];cards=[]
    for key,name,filename in SETS:
        source=DOC/'sources'/f'{key}.png'
        if not source.exists():shutil.copy2(SOURCE/filename,source)
        w,h=map(int,subprocess.check_output(['magick','identify','-format','%w %h',str(source)]).split())
        # Visual inspection: the chestplates cross the mathematical 50% seam. The
        # 580/1254 gutter is genuinely transparent in all three original sheets.
        split=round(w*580/1254);half=h//2
        cells=[(0,0,split,half),(split,0,w-split,half),(0,half,split,h-half),(split,half,w-split,h-half)]
        for slot,(x,y,cw,ch) in zip(('helmet','chestplate','leggings','boots'),cells):
            item=f'{key}_{slot}';dest=RES/f'assets/dynasty/textures/item/{item}.png';backup=DOC/'before'/f'{item}.png'
            if not backup.exists():shutil.copy2(dest,backup)
            out=DOC/'armor'/f'{item}.png'
            subprocess.run(['magick',str(source),'-crop',f'{cw}x{ch}+{x}+{y}','+repage','-trim','+repage','-filter','Lanczos','-resize','116x116','-background','none','-gravity','center','-extent','128x128','PNG32:'+str(out)],check=True)
            shutil.copy2(out,dest)
            manifest.append(dict(id=item,source=str(source.relative_to(DOC)),output=str(out.relative_to(DOC)),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),mode='built-in image_gen; crop, trim and resize only'))
            cards.append(f'<figure><img src="armor/{item}.png"><figcaption>{name} · {slot}</figcaption></figure>')
    (DOC/'armor-assets.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (DOC/'gallery.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>王朝 · 建筑反馈第五轮</title><style>body{background:#172127;color:#f0eadc;font:16px/1.6 system-ui;max-width:1100px;margin:40px auto;padding:20px}h1,h2{color:#e0bf79}section{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}figure{margin:0;padding:16px;background:#29373f;border-radius:8px}img{width:100%;image-rendering:pixelated;background:repeating-conic-gradient(#37424b 0% 25%,#2a343b 0% 50%) 0/16px 16px}a{color:#93ded9}</style><h1>王朝 · 建筑反馈第五轮</h1><p>三套盔甲的物品栏图标，共12张。采用图像生成工具生成，再做裁切和尺寸适配；这里不是穿戴模型预览。</p><section>'''+''.join(cards)+'''</section><h2>建筑与机关</h2><p>导入玩家书院、城门改动；帝陵增加地面入口；观星台台基增加可进入的书库工坊；音乐遗迹与封印室补全封闭后室，解开机关生成公共奖励箱。</p><p>新建筑：平原官道驿站、森林药庐、沙海商旅院。新增建筑探访与后续备料任务。</p><p><a href="player-build-delta.json">玩家建筑差异记录</a> · <a href="../../quests-remaster/gallery.html">任务总览</a> · <a href="release-notes.md">验证与更新说明</a></p><p>本页是资源预览，不代表运行中的旧存档已自动更新。</p></html>''')
    gallery=DOC/'gallery.html'
    gallery.write_text(gallery.read_text().replace('</html>', '<h2>手持侧面离屏检查</h2><p>太乙拂尘：正面、斜侧面、近侧面、背面。来自实际 JSON 模型与贴图的隐藏 OpenGL 渲染，不是游戏实拍。</p><img style="max-width:960px" src="mesh-qa/whisk-contact.png"><p><a href="退出游戏后安装本轮更新.command">退出游戏后安装本轮更新</a></p></html>'))
    for key,name,style,biomes in SITES:
        write(f'data/dynasty/worldgen/structure/{key}.json',dict(type='dynasty:travel_site',style=style,biomes=biomes,step='surface_structures',terrain_adaptation='beard_thin',spawn_overrides={}))
        write(f'data/dynasty/worldgen/structure_set/{key}.json',dict(structures=[dict(structure='dynasty:'+key,weight=1)],placement=dict(type='minecraft:random_spread',spacing=42,separation=20,salt=928250+style)))
        write(f'data/dynasty/advancements/visit_{key}.json',dict(criteria={'visit':dict(trigger='minecraft:location',conditions={'player':[{'condition':'minecraft:location_check','predicate':{'dimension':'minecraft:overworld','structure':'dynasty:'+key}}]})}))
    changes={
        'block.dynasty.ruin_shell':'封印石砖',
        'dynasty.puzzle.msg.solved_claim':'[机关] 封印已解除，奖励在中央机关上方的箱子里；后室有附魔台、书架和锻造台。',
        'dynasty.puzzle.msg.chest_blocked':'[机关] 奖励已保存。请清空中央机关上方一格，再右键机关生成宝箱。',
        'dynasty.puzzle.msg.already_claimed':'[机关] 本室奖励箱已生成，不会重复补货。',
        'dynasty.puzzle.clue.lamp':'目标：四灯全亮。每次切换自身与顺时针下一盏；点击中央机关会提示下一步该点哪一盏。',
    }
    english={'block.dynasty.ruin_shell':'Sealed Masonry','dynasty.puzzle.msg.solved_claim':'Seal opened! Rewards are in the chest above the controller. An enchanting workshop awaits beyond the gate.','dynasty.puzzle.msg.chest_blocked':'Clear the block above the controller, then click it to place your saved reward chest.','dynasty.puzzle.msg.already_claimed':'This room has already created its reward chest. It will not refill.'}
    for key,name,_,_ in SITES:
        changes['structure.dynasty.'+key]=name;changes['structure.dynasty.'+key+'.name']=name
        english['structure.dynasty.'+key]=key.replace('_',' ').title();english['structure.dynasty.'+key+'.name']=key.replace('_',' ').title()
    for locale,updates in [('zh_cn',changes),('en_us',english)]:
        path=RES/f'assets/dynasty/lang/{locale}.json';data=json.loads(path.read_text());data.update(updates);write(str(path.relative_to(RES)),data)
    print('12 armor icons; 3 registered structure resources; 3 visit advancements; localization packaged.')
if __name__=='__main__':main()
