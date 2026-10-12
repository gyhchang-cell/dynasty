"""Compose honest native/grey proof and the two actually viewed reference frames."""
from create import *
import shutil, html, zipfile
from PIL import ImageFont
P=D/ID;NAT=R/'docs/art/boss-human-v12/native/tianjiang-steve-v15-delivery-12m'
REF=R/'docs/art/boss-human-v12/reference-native/power-reference-round1'
font=lambda n:ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',n)
def title(im,s,xy,n=26):ImageDraw.Draw(im).text(xy,s,font=font(n),fill=(38,46,48))
def run():
 assert (NAT/'PASS.txt').exists()
 native=D/'native';shutil.copytree(NAT,native,dirs_exist_ok=True)
 # One shared crop, no individual actor resizing; reference wings remain intact.
 crop=(700,600,2500,1350)
 board=Image.new('RGB',(5400,920),(232,233,228))
 items=[(REF/'cataclysm_scylla-45.png','Scylla / 大武器与紧凑身体'),(native/f'02-{ID}-45-off.png','九霄天将 / Steve六块比例＋大戟'),(REF/'cataclysm_maledictus-45.png','Maledictus / 主体与大翼架')]
 for i,(p,label) in enumerate(items):
  title(board,label,(i*1800+20,15),30);board.paste(Image.open(p).convert('RGB').crop(crop),(i*1800,90))
 title(board,'实际游戏截图 · 12m / FOV70 / 1.62m视高 / 45° / 日间无光影 · 完全相同裁切，无单独放大',(20,845),26)
 title(board,'参考归灾变作者所有；灾变自带翼效、粒子及天空色保留。天将独立气场关闭；未复制外部模型、贴图或动画。',(20,882),24)
 board.save(D/'reference-comparison.png')
 for i,label in [(0,'front'),(2,'45'),(4,'side'),(6,'back')]:
  p=native/f'{i:02d}-{ID}-{label}-off.png';raw=Image.open(p).convert('RGB')
  out=Image.new('RGB',(1800,850),(232,233,228));title(out,'九霄天将 / 原生游戏 / '+label+' / 1.8m玩家 / 气场关闭',(16,12),28)
  out.paste(raw.crop(crop),(0,60));title(out,'12m普通视高与日光；只裁去空白，角色和玩家未单独缩放。完整原始截图可在下方打开。',(16,810),22);out.save(D/f'native-{label}.png')
 # Native animation proof comes from actual registered swing; no QA animation triggers.
 proof={}
 for i in range(14):
  rec=json.loads((native/f'{i:02d}-state.json').read_text());assert all(hashes()[str(Path('src/main/resources')/k)]==v for k,v in rec['loadedResourceSha256'].items())
  proof[rec['stage']]={'clip':rec['clip'],'age':rec['age'],'texture':rec['texture'],'mainHand':rec['equipment']['main']}
 launch=json.loads((R/'build/boss-eight-native/tianjiang-steve-v15-delivery-12m/launch.json').read_text())
 assert '-Ddynasty.bossEightQa.cameraDistance=12' in launch['jvmArgs'] and '-Ddynasty.bossEightQa.cameraPitch=-7' in launch['jvmArgs']
 report={'registeredId':'dynasty:'+ID,'sourceResourceHashes':hashes(),'actualLoadedStages':proof,'camera':{'distance':12,'fov':70,'eyeHeight':1.62,'pitch':-7},'scope':'Quiet independent Forge world; normal user save untouched; controlled art/animation validation, not natural-fight or multiplayer acceptance','cast':'Complete offline replay; existing production routing preserved; not a new server skill'}
 (D/'native-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 # Copy the actual loadable triplet beside the editable source, easy to inspect.
 for p in TARGETS:shutil.copy2(p,P/p.name)
 with zipfile.ZipFile(D/'tianjiang-assets.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in TARGETS:z.write(p,str(p.relative_to(R/'src/main/resources')))
 views=''.join(f'<figure><a href="native-{n}.png"><img src="native-{n}.png"></a><figcaption>{n}：<a href="native/{i:02d}-{ID}-{n}-off.png">完整原图 / 关闭气场</a> · <a href="native/{i+1:02d}-{ID}-{n}-on.png">开启气场</a></figcaption></figure>' for i,n in [(0,'front'),(2,'45'),(4,'side'),(6,'back')])
 motion=''.join(f'<figure><a href="{ID}/{c}.webp"><img src="{ID}/{c}.webp"></a><figcaption>{c} 完整离线回放 · <a href="{ID}/{c}-phases.png">六阶段图</a></figcaption></figure>' for c in ['idle','walk','attack','cast','hurt','death'])
 texture=''.join(f'<figure><a href="{ID}/{f}.png"><img src="{ID}/{f}.png"></a><figcaption>{label}</figcaption></figure>' for f,label in [('texture-4x','128×128原创图集，4倍最近邻'),('uv-overlay-4x','逐面UV编号叠加'),('uv-direction','方向检查纹理，仅用于离线审查'),('close-face','脸部原色近景'),('close-weapon','握持、戟刃原色近景'),('body-silhouette','隐藏饰件和兵器的六块Steve主体'),('player-scale','离线玩家、石砖、木材比例'),('gray','灰度材质关系')])
 page=f'''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>九霄天将 V15 · Steve主体与原创大戟</title>
<style>body{{margin:0;background:#e9ece8;color:#25343c;font:17px/1.65 system-ui}}main{{max-width:1480px;margin:auto;padding:28px}}h1{{font-size:28px}}h2{{font-size:22px;margin-top:36px}}img{{max-width:100%;height:auto}}figure{{margin:0 0 20px}}figcaption{{padding:8px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px}}a{{color:#195b70}}.texture img{{image-rendering:pixelated}}p{{max-width:1100px}}</style><main>
<h1>九霄天将：保留Steve六块主体，少量饰件，明显的大戟</h1>
<p>本轮只修改九霄天将。六块尺寸关系完整保留：头8×8×8、身体8×12×4、手臂与腿4×12×4，统一放大1.35倍。裸主体高2.7格，含小冠饰约3格；双腿仅略分开。额外身体几何共4块：两片浅腿甲、小冠沿、小冠脊。护甲、袖口、腰带、靴面主要画在原来的六块表面。</p>
<figure><a href="overview.png"><img src="overview.png"></a><figcaption>同尺度离线对照：裸Steve主体 → 加4块小饰件和原创大戟 → 实际PNG贴图。软件预览。</figcaption></figure>
<h2>实际游戏画面</h2><p>Forge独立静音隐藏窗口测试，原版日光、石砖和玩家参照。14项原生检查通过；每一项核对实际加载的模型、贴图和动画SHA-256。没有进入或关闭用户的愚者存档。此处是受控美术测试，不冒充自然战斗平衡验收。</p><div class="grid">{views}</div>
<h2>与你给出的两只参考对照</h2><figure><a href="reference-comparison.png"><img src="reference-comparison.png"></a><figcaption>共同12m机位、FOV70、1.62m视高、45°和相同裁切。灾变的原生效果与天空色保留；本页不把其反射或粒子当作贴图效果。<a href="https://www.curseforge.com/minecraft/mc-mods/lendercataclysm">灾变作者发布页</a></figcaption></figure>
<p>从Scylla画面学习“紧凑主体与明显的大武器”；从Maledictus画面学习“身体与特色外围结构分主次”。落实在天将上的是完整Steve主体和单一的大戟轮廓。图中的参考用于比例与视觉关系研究，未声称它们源码骨架等同Steve，也未复制触手、翼架或资产。</p>
<h2>自检与修正</h2><p>上一稿改变了肩胸、手臂和腿脚太多。本稿去掉那些结构，身体回到六个经典Cuboid。自检中修正了像张嘴的面部色块、像数字的胸纹、戟面共面闪烁、死亡穿地以及攻击接触帧“举戟不挥戟”的反向旋转。同机位对照后，又将贴着头部的兵器稍向外展，刀头做成有真实开口的阶梯月牙形；这次增量只在兵器，不扩张身体。修改后重新导出并实机复验。没有增加新实体、装备、伤害、范围或碰撞调整。</p><figure><a href="before-after.png"><img src="before-after.png"></a><figcaption>V14与V15：相同机位和世界尺度的灰模对照。</figcaption></figure>
<h2>完整动作</h2><p>六条名称与时长沿用现有运行绑定。攻击接触仍在3 tick，整条6 tick；实机捕获了蓄势、接触和恢复。施法完整离线回放，生产技能路由保留。</p><div class="grid">{motion}</div>
<p>实际攻击：<a href="native/09-{ID}-attack-tell.png">蓄势</a> · <a href="native/10-{ID}-attack-contact.png">接触</a> · <a href="native/11-{ID}-attack-recovery.png">恢复</a> · <a href="native/13-{ID}-death.png">死亡</a>。死亡红色是游戏自带受伤覆盖层。</p>
<h2>纹理、UV与六块主体检查</h2><div class="grid texture">{texture}</div>
<p><a href="{ID}/texture.png">原始128×128 PNG</a> · <a href="{ID}/{ID}.geo.json">实际geo.json</a> · <a href="{ID}/{ID}.animation.json">实际animation.json</a> · <a href="blockbench/{ID}.bbmodel">可编辑bbmodel（内嵌原创图集与6条动作）</a> · <a href="tianjiang-assets.zip">运行资源三件套</a> · <a href="validation.json">离线检查</a> · <a href="native-validation.json">实机加载核对</a></p>
<p>权威生成源：tools/art/tianjiang-steve-v15/create.py。再次导出三件资源逐字节相同；导出前检查所有权哈希，遇到人工或并行修改会停止。旧V10/V11/V12导出也会因资源哈希改变而拒绝覆盖。</p></main></html>'''
 (D/'index.html').write_text(page)
 print('Gallery, native validation, original editable source and actual asset triplet ready.')
if __name__=='__main__':run()
