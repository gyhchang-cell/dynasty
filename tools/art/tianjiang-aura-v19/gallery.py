"""Package actual silent Forge captures, matched comparisons and bounded reference evidence."""
from export import *
from PIL import ImageDraw,ImageFont
import shutil,html,zipfile
N=R/'docs/art/boss-human-v12/native/tianjiang-aura-v19-delivery'
OLD=R/'docs/art/tianjiang-aura-v18/native'
REF=R/'docs/art/boss-human-v12/reference-native/power-reference-round1'
FONT=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',25)
CROP=(560,340,2210,1480)
def shot(folder,num):return next(folder.glob(f'{num:02d}-{ID}-*.png'))
def panel(paths,labels,name,crop=CROP):
 board=Image.new('RGB',((crop[2]-crop[0])*len(paths),crop[3]-crop[1]+70),'#e9ece8');d=ImageDraw.Draw(board)
 for i,(p,label) in enumerate(zip(paths,labels)):
  x=i*(crop[2]-crop[0]);im=Image.open(p).crop(crop);board.paste(im,(x,54));d.text((x+15,12),label,font=FONT,fill='#263a40')
 board.save(D/f'{name}.png')
def figure(name,caption,ext='png'):
 return f'<figure><a href="{name}.{ext}"><img loading="lazy" src="{name}.{ext}" alt="{html.escape(caption)}"></a><figcaption>{caption}</figcaption></figure>'
def run_gallery():
 assert (N/'PASS.txt').exists()
 native=D/'native';native.mkdir(exist_ok=True)
 for p in N.iterdir():
  if p.is_file():shutil.copy2(p,native/p.name)
 expected=json.loads((N/'runtime-manifest.json').read_text())['resources'];states=[]
 for i in range(19):
  s=json.loads((N/f'{i:02d}-state.json').read_text())
  for k,h in s['loadedResourceSha256'].items():assert expected[k]==h==hashlib.sha256((R/'src/main/resources'/k).read_bytes()).hexdigest()
  if s['stage'].endswith('-off') or s['stage']=='death':assert s['materialGlowAlpha']==0
  if s['stage']=='minimal-on':assert s['auraParticleEmissionRequests']==0
  states.append({k:s[k] for k in ['stage','clip','age','materialGlowAlpha','replicatedSwing','auraParticleEmissionRequests','environment']})
 for p,h in LOCKS.items():assert hashlib.sha256((A/p).read_bytes()).hexdigest()==h
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as jar:
  for k,h in expected.items():assert hashlib.sha256(jar.read(k)).hexdigest()==h
 for num,view in [(0,'front'),(2,'45'),(4,'side'),(6,'back')]:
  for j,fx in enumerate(['off','on']):Image.open(shot(N,num+j)).crop(CROP).save(D/f'{view}-{fx}.png')
  panel([shot(N,num),shot(N,num+1)],[view+' · 关闭气场',view+' · V19开启气场'],view+'-on-off')
  panel([shot(OLD,num+1),shot(N,num+1)],[view+' · V18较细小',view+' · V19外围与持戟光流'],view+'-before-after')
 frames=[Image.open(p).crop(CROP).convert('RGB') for p in sorted((N/'sequence').glob('*.png'))];assert len(frames)==24
 frames[0].save(D/'aura-motion.webp',save_all=True,append_images=frames[1:],duration=200,loop=0,lossless=True)
 sheet=Image.new('RGB',(1800,830),'#e9ece8');d=ImageDraw.Draw(sheet)
 for i,j in enumerate([0,4,8,12,16,20]):
  im=frames[j].resize((600,415),Image.Resampling.NEAREST);sheet.paste(im,((i%3)*600,(i//3)*415))
 sheet.save(D/'motion-samples.png')
 panel([shot(N,9),shot(N,10),shot(N,11)],['原挥击 · 蓄势','原挥击 · 接触','原挥击 · 恢复'],'attack-phases')
 panel([shot(N,14),shot(N,15)],['普通夜间 · 关闭','普通夜间 · 开启'],'night-comparison')
 panel([shot(N,17),shot(N,18)],['最少粒子 · 无新增实体粒子，保留简化光流','减少粒子 · 简化光流及少量光屑'],'particle-settings')
 Image.open(shot(N,16)).crop(CROP).save(D/'far-on.png')
 # Equal 12m, FOV70, pitch -7, eye 1.62; references apply their own dimension sky effects.
 panel([REF/'cataclysm_scylla-front.png',REF/'cataclysm_maledictus-front.png',shot(N,16)],
       ['灾变 Scylla · 12米正面','灾变 Maledictus · 12米正面','Dynasty 天将 V19 · 12米正面'],'cataclysm-comparison',crop=(540,300,2260,1480))
 refs=json.loads((R/'docs/art/tianjiang-aura-v18/reference-notes.json').read_text())
 refs['observedGameStills']=[
  {'character':'Cataclysm: Scylla / Maledictus','source':'https://www.curseforge.com/minecraft/mc-mods/lendercataclysm','evidence':'既有本机Forge受控参考截图，普通日光，无外部资源包；不是自然战斗录像。','observation':'Scylla的上身与大武器形成紧凑中心；Maledictus半透明翼展开很宽，人物仍有完整的暗色实体轮廓。','application':'青白肩后长气流扩展轮廓；中心留空，金色令纹辅助；戟杆能量跟随现有武器骨骼。'},
  {'character':'Cataclysm: Ancient Remnant / Ender Guardian / Ignis / Netherite Monstrosity / Harbinger / Leviathan','source':'https://www.curseforge.com/minecraft/mc-mods/lendercataclysm','evidence':'本轮查看8只45度参考总览；这6只仅大轮廓比较，未逐帧研究技能。','observation':'多数依靠大实体体量和局部能量中心，不是全身喷粒子。Ignis的剑盾、Harbinger的红色观察中心、Monstrosity的熔岩接缝各有明确位置。','application':'借鉴力量位置，不改已认可的天将身体，不把8只的构造或花纹复制进来。'},
  {'character':'Iron: The Dead King','source':'https://www.curseforge.com/minecraft/mc-mods/irons-spells-n-spellbooks/gallery','image':'https://media.forgecdn.net/attachments/653/896/2023-04-28_17.png','observation':'战斗截图中蓝白束流连接玩家与目标；不能把玩家施法当成亡王常驻气场。','application':'只借鉴效果要有起点终点，不复制攻击行为。'},
  {'character':'Iron: 官方图标题 Fire Boss','source':'https://www.curseforge.com/minecraft/mc-mods/irons-spells-n-spellbooks/gallery','image':'https://media.forgecdn.net/attachments/1132/602/echo_downscale_4-png.png','observation':'头部火核和巨大刃面最醒目，背景强暖光属于宣传环境，不能当作普通Minecraft PNG自身效果。','application':'聚光集中在原胸纹和武器导流，不新增头部火焰或改头盔。'},
  {'character':'Meet Your Fight: Rosalyne','source':'https://www.curseforge.com/minecraft/mc-mods/meet-your-fight/gallery','image':'https://media.forgecdn.net/attachments/648/884/2023-04-17_15.png','observation':'普通日光中身体克制，紫色刃面清晰指向攻击方向，没有大气场。','application':'用刀/戟的局部亮度指向威胁，不能把此图列成大型气场证据。'},
  {'character':'Goety Revelation: Apollyon','source':'https://www.curseforge.com/minecraft/mc-mods/goety-revelation/gallery','image':'https://media.forgecdn.net/attachments/1149/857/apollyon-overworld-png.png','observation':'小幅官方截图可辨中心与周围紫色结构；分辨率不足判断具体粒子纹理，环境疑有额外光影。','application':'仅作中心/外围分层；不声称研究了完整技能或本地2.2.7与网页版本一致。'},
  {'character':'Mowzie’s Mobs: Umvuthi','source':'https://www.curseforge.com/minecraft/mc-mods/mowzies-mobs/gallery','image':'https://media.forgecdn.net/attachments/813/516/2024-02-23_19.png','observation':'金色冠状背景与暗面形成焦点，实体冠饰不等于粒子。','application':'金色断环围住头肩但不遮脸。'},
  {'character':'Bosses of Mass Destruction: Night Lich','source':'https://www.curseforge.com/minecraft/mc-mods/bosses-of-mass-destruction/gallery','image':'https://media.forgecdn.net/attachments/354/968/night-lich-boss.png','observation':'夜色中少量冷色粒子与杖尖强调悬浮中心；图像较暗。','application':'冷暖能量位置分明，天将夜间仍使用真实光照，不后期提亮截图。'}]
 refs['packsCheckedNotCountedAsBossResearch']=[
 {'name':'愚者','url':'https://bbsmc.net/modpack/the-fool','status':'核对页面，未逐一确认定制Boss名称/版本/资源包，不计为已研究全部Boss。'},
 {'name':'落幕曲','url':'https://bbsmc.net/modpack/luomuqu','status':'查看页面，不以封面替代Boss画面。'},
 {'name':'Prominence II','url':'https://www.curseforge.com/minecraft/modpacks/prominence-2-hasturian-era/gallery','status':'已看Mythic Challenges宣传图；右侧角色来源未确认，不计已识别Boss。'},
 {'name':'Project E.N.D / Chocolate Edition','status':'只检索页面所述Boss数量，不计实际看过的参考。'}]
 refs['scope']='实际查看：2个斗罗相关静帧，8只灾变本机参考（其中Scylla/Maledictus重点比较），6个其他模组角色静帧。未完成100动漫+100Boss+100整合包的逐项研究；未声称电影级验收。未播放带声视频。'
 refs['externalAssetsInProduction']=False
 (D/'reference-notes.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
 report={'lockedV17AssetsUnchanged':LOCKS,'runtimeAssetsMatchSourceProcessedAndJar':True,'nativeStages':states,'nativeMotionFrames':24,'motionSeconds':4.8,'visualIteration':'V19 first pass exposed buffer/blend artifacts; fixed batching and alpha blend; broadened currents; follow-up fixed weapon-local binding and cleanup of delayed test loot.', 'scope':'Client visual layers only. No collision/AI/damage/new attack/skill timing change. Native controlled scene, not natural encounter.', 'notValidated':['Natural battle and multiplayer performance','Shader-pack compatibility','Every spell-specific telegraph','Cinematic-quality parity','300 requested references']}
 (D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 game_rows=''.join('<tr><td>'+html.escape(x['character'])+'</td><td>'+html.escape(x['observation'])+'</td><td>'+html.escape(x['application'])+f' <a href="{x["source"]}">来源</a></td></tr>' for x in refs['observedGameStills'])
 page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>九霄天将 · 雷霆气场 V19</title><style>
body{margin:0;background:#e9ece8;color:#23343b;font:17px/1.75 system-ui}main{max-width:1600px;margin:auto;padding:28px}h1{font-size:32px}h2{margin-top:40px;font-size:25px}img{max-width:100%;height:auto}figure{margin:0 0 25px}figcaption{padding:8px 0}a{color:#175971}p{max-width:1250px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:24px}table{border-collapse:collapse;width:100%}td,th{padding:12px;border-bottom:1px solid #bdc9c8;text-align:left;vertical-align:top}small{color:#52666d}details{margin:20px 0}button,input{font:inherit;padding:7px}nav{display:flex;gap:20px;flex-wrap:wrap}</style><main>
<h1>九霄天将 · 雷霆气场 V19</h1><p>已认可的头盔、面部、身体、武器、基础贴图和动画文件保持不变。新增的是实际游戏中的独立光流、令纹、旋转气场和持戟导流；下方全部天将画面来自Forge 1.20.1受控实机，无外部光影、无后期辉光、无声音。</p>
<nav><a href="#compare">同机位前后</a><a href="#motion">动态与动作</a><a href="#reference">参考与差距</a><a href="#checks">检查结果</a></nav>
<h2 id="compare">从细线背饰到大范围气流</h2>'''+figure('45-before-after','左V18、右V19。相同8米距离、FOV70、俯仰-7°及裁切，没有单独放大新版。')+figure('front-on-off','关闭与开启：原始模型没有变化，中心面部与持戟方向保持可读。')+'''<div class="grid">'''+figure('side-on-off','侧面：气流有前后深度，环绕光流穿过身体外围。')+figure('back-on-off','背面：完整断环、肩后长气流、六枚令纹。')+'''</div><h2 id="motion">真实动态 · 可暂停逐帧检查</h2>'''+figure('aura-motion','24张连续实机采样，间隔4tick，约4.8秒；这是待机气场动态，不是完整战斗录像。','webp')+'''<button id="pause">暂停动图</button> <label>采样帧 <input id="frame" type="range" min="0" max="23" value="0"></label><span id="time">0.0 秒</span>
<p>肩后气流左右错相起伏；环绕弧线缓慢转动；光屑持续上升。两条细光流从实际握持点沿戟杆传向玉点，跟随武器本身的动作。挥击时增强，死亡时关闭；没有新增技能预警或伤害区域。</p>'''+figure('attack-phases','原有攻击的蓄势、接触、恢复实机采样：用于检查光流跟随，不冒充连续录像。')+figure('night-comparison','相同夜间机位关闭/开启；无动态光源照亮地面，无曝光修图。')+figure('particle-settings','粒子设置降级：最少设置不发出新增粒子，保留简化光流；减少设置只发少量光屑。')+'''<h2 id="reference">参考结论与目前差距</h2>'''+figure('cataclysm-comparison','Scylla / Maledictus / 天将。同为12米正面、FOV70、眼高1.62、俯仰-7°，同像素裁切；灾变保留自身天空效果，人物光照均为原版日光。版权归各模组作者，仅作研究，不复制资源。')+'''<p><b>参考带来的判断：</b>外围要大，但必须围绕身体与武器组织。Maledictus的大展开让中心看起来更紧凑；Scylla的强武器方向使身体与特征连成整体。天将本轮把肩后气流、古金令环、掌部到戟杆的导流分成三层，光屑只作辅助。</p>
<p><b>仍有差距：</b>天将的外围仍较规则，剪影变化与不同战斗阶段的专用表现少于成熟Boss。当前强化依据既有挥击状态，尚未为每个法术制作独立效果。没有环境光照、电影后期或长镜头战斗演出；这版是明显增强的Minecraft实机气场，不能据此宣布达到电影级。</p>
<table><thead><tr><th>实际查看对象</th><th>画面观察与限制</th><th>落到天将的修改</th></tr></thead><tbody>'''+game_rows+'''</tbody></table>
<p>斗罗静帧参考：<a href="https://www.sohu.com/a/652090875_120704778">千仞雪的后方展开与武器聚光</a>、<a href="https://www.sohu.com/a/713181398_120768750">霍雨浩相关融合技的掌部冷暖汇聚</a>。均为第三方转载静帧，未冒充完整动画研究。</p>
<p><b>研究范围：</b>2个斗罗相关静帧、8只灾变参考、6个其他模组角色画面。未完成“100动漫＋100Boss＋100整合包”逐项研究。愚者、落幕曲页面和其他包宣传图未核实的Boss不计数。<a href="reference-notes.json">完整证据与限制</a>。</p>
<h2 id="checks">检查结果</h2><p>构建通过（跳过通用测试）；19个受控实机状态通过，24帧待机采样。新PNG实际加载哈希与源码资源、打包JAR一致；模型、基础贴图、动画仍与V17完全相同。修复了初版光片混合伪影、武器跟随点以及测试场景延迟掉落物污染。自然遭遇、多人性能、第三方光影兼容性仍待验证。</p>
<p>本轮资源：TianjiangAura.java、独立渲染材质、BossCuboidRenderer中的光效接入、16×32原创光流纹理、128×128局部发光遮罩（胸纹15像素＋武器68像素）。生成源同步更新，旧V18导出入口也会调用新版，避免覆盖回退。</p>
<p><a href="validation.json">实机与资源检查</a> · <a href="native/PASS.txt">19状态记录</a> · <a href="emissive-mask.png">原始光效遮罩</a> · <a href="emissive-mask-4x.png">4倍最近邻</a> · <a href="../tianjiang-helmet-v17/index.html">已认可V17模型</a></p></main>
<script>const motion=document.querySelector('img[src="aura-motion.webp"]'),slider=document.getElementById('frame'),pause=document.getElementById('pause');function frame(){motion.src='frames/'+String(slider.value).padStart(2,'0')+'.webp';document.getElementById('time').textContent=(slider.value*.2).toFixed(1)+' 秒';pause.textContent='播放动图'}slider.oninput=frame;pause.onclick=()=>{if(motion.getAttribute('src')==='aura-motion.webp')frame();else{motion.src='aura-motion.webp';pause.textContent='暂停动图'}};</script></html>'''
 (D/'index.html').write_text(page)
 (D/'frames').mkdir(exist_ok=True)
 for i,im in enumerate(frames):im.save(D/'frames'/f'{i:02d}.webp',lossless=True)
 print('Gallery ready: verified 19 native states and 24 captured frames.')
if __name__=='__main__':run();run_gallery()
