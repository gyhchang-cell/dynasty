"""Verified native review for original V20 glyphs; no external art is exported to runtime."""
from pathlib import Path
import json,hashlib,shutil,zipfile
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/tianjiang-runes-v20'
N=R/'docs/art/boss-human-v12/native/tianjiang-runes-v20-final';OLD=R/'docs/art/tianjiang-aura-v19/native'
ID='nine_heaven_general';CROP=(560,340,2210,1480)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',26)
def shot(n,i):return next(n.glob(f'{i:02d}-{ID}-*.png'))
def board(paths,labels,name,crop=CROP):
 w,h=crop[2]-crop[0],crop[3]-crop[1];out=Image.new('RGB',(w*len(paths),h+60),'#e9ece8');draw=ImageDraw.Draw(out)
 for i,(p,label) in enumerate(zip(paths,labels)):
  out.paste(Image.open(p).crop(crop),(w*i,55));draw.text((w*i+14,12),label,font=font,fill='#243842')
 out.save(D/f'{name}.png')
def figure(name,caption,ext='png'):return f'<figure><a href="{name}.{ext}"><img loading="lazy" src="{name}.{ext}"></a><figcaption>{caption}</figcaption></figure>'
def main():
 assert (N/'PASS.txt').exists()
 locks=json.loads((R/'docs/art/tianjiang-aura-v19/asset-validation.json').read_text())['lockedAcceptedAssets']
 for p,h in locks.items():assert hashlib.sha256((R/'src/main/resources/assets/dynasty'/p).read_bytes()).hexdigest()==h
 states=[];manifest=json.loads((N/'runtime-manifest.json').read_text())
 assert hashlib.sha256((R/'build/libs/dynasty-1.4.0.jar').read_bytes()).hexdigest()==manifest['productionJarSha256']
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:
  assert 'com/dynasty/client/TianjiangRuneField.class' in z.namelist()
  for i in range(19):
   state=json.loads((N/f'{i:02d}-state.json').read_text())
   for k,h in state['loadedResourceSha256'].items():assert h==hashlib.sha256(z.read(k)).hexdigest()==hashlib.sha256((R/'src/main/resources'/k).read_bytes()).hexdigest()
   if state['stage'].endswith('-off') or state['stage']=='death':assert state['materialGlowAlpha']==0
   if state['stage']=='minimal-on':assert state['auraParticleEmissionRequests']==0
   states.append({k:state[k] for k in ['stage','age','environment','materialGlowAlpha','auraParticleEmissionRequests']})
 native=D/'native';native.mkdir(exist_ok=True)
 for p in N.iterdir():
  if p.is_file():shutil.copy2(p,native/p.name)
 for i,view in [(0,'front'),(2,'45'),(4,'side'),(6,'back')]:
  Image.open(shot(N,i+1)).crop(CROP).save(D/f'{view}.png')
  board([shot(OLD,i+1),shot(N,i+1)],['V19 · 旧线条符号','V20 · 折角符印＋漂浮晶片'],view+'-comparison')
 board([shot(N,0),shot(N,1)],['关闭气场 · 原模型','开启气场 · 新符文'], 'on-off')
 board([shot(N,9),shot(N,10),shot(N,11)],['蓄势','接触','恢复'],'attack')
 board([shot(N,14),shot(N,15)],['普通夜间 · 关闭','普通夜间 · 开启'],'night')
 board([shot(N,17),shot(N,18)],['最少粒子 · 简化符印','减少粒子 · 降低密度'],'settings')
 board([shot(OLD,1),shot(N,1)],['V19符号近景','V20符印近景'],'rune-detail',crop=(1440,580,2100,1250))
 frames=[Image.open(p).crop(CROP).convert('RGB') for p in sorted((N/'sequence').glob('*.png'))];assert len(frames)==24
 frames[0].save(D/'runes-motion.webp',save_all=True,append_images=frames[1:],duration=200,loop=0,lossless=True)
 (D/'frames').mkdir(exist_ok=True)
 for i,f in enumerate(frames):f.save(D/'frames'/f'{i:02d}.webp',lossless=True)
 contact=Image.new('RGB',(1800,830),'#e9ece8')
 for i,j in enumerate([0,4,8,12,16,20]):contact.paste(frames[j].resize((600,415),Image.Resampling.NEAREST),((i%3)*600,(i//3)*415))
 contact.save(D/'motion-samples.png')
 refs={'goety':{'source':'https://www.curseforge.com/minecraft/mc-mods/goety/gallery','viewedLocalVersion':'goety-2.5.49.3','texturesInspected':['entity/cultist/apostle_aura.png','entity/cultist/apostle_summon_circle.png','entity/cultist/summon_apostle_ring.png','entity/summon_circle.png'],'observation':'apostle_aura是成组分支折线，使用重复但错开的符号组织；不是反复画一个汉字。32px召唤图案用几何轮廓和少量笔画构成识别。纹理单独查看不能证明全部实机运动。','application':'四组原创断笔、折角、支钩组合；12枚大符印＋24枚小符文错开布置。未复制PNG或原符号。'},
 'apollyon':{'source':'https://www.curseforge.com/minecraft/mc-mods/goety-revelation/gallery','image':'https://media.forgecdn.net/attachments/1149/859/apollyon-nether-png.png','observation':'350×181官方图仅能确认中心角色与外围紫色结构，不足以逐像素研究符文，未将细节结论归给这张图。'},
 'anime':{'source':'https://overlord-anime.com/_season2/story/?ep=26','image':'https://overlord-anime.com/_season2/assets/story/26_5.jpg','viewed':'Overlord III 第12话官方第5张静帧','observation':'主体后方有大环带、密集小符号和不同尺度圆形图案，强蓝白光把场景统一；手和人物仍是明确中心。静帧不用于推断旋转速度。','application':'主符印/环绕碎符/晶片光屑按尺度分层，避免把所有符号排在一个平面。保留天将青白与古金配色，不照搬动漫花纹或宣传光照。'},
 'notUsed':'第一季11/12话页面看过的其他静帧没有足够清楚的符文，不拿它们证明符文研究。外部参考文件未进入运行资源。'}
 (D/'reference-notes.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
 report={'approvedV17AssetsUnchanged':locks,'nativeStates':states,'nativeFrames':24,'runtimeJarSha256':manifest['productionJarSha256'],
 'changes':{'oldRepeatedGlyphRemoved':True,'originalGlyphFamilies':4,'majorSigns':12,'orbitingSmallSigns':24,'facetedLightShards':36,'renderedMotes':84,'previousRenderedMotes':42,'emissionsPer4TicksIdle':10,'dustPer4TicksAttack':14,'additionalAttackSparkMaximum':1,'sharedEmissionBudget':16},
 'productionScope':'Only TianjiangAura.java and new client-only TianjiangRuneField.java; no new entities, hitboxes, damage, sounds, body assets or other bosses.',
 'inspection':'Round1 solid yellow looked like metal signage; round2 made branched broken signs with cool faces, dark sides and warmer narrow cores. 19 native controlled states and source/JAR resource checks passed.',
 'pending':['User visual acceptance before applying to other bosses','Natural combat and multiplayer performance','Third-party shaders']}
 (D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>天将 · 悬浮符印 V20</title><style>body{margin:0;background:#e9ece8;color:#243842;font:17px/1.75 system-ui}main{max-width:1600px;margin:auto;padding:28px}h1{font-size:32px}h2{margin-top:36px}img{max-width:100%;height:auto}figure{margin:0 0 25px}figcaption{padding:8px 0}a{color:#176479}p{max-width:1250px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:24px}button,input{font:inherit;padding:8px}</style><main>
<h1>九霄天将 · 悬浮符印与晶片 V20</h1><p>移除旧版“王字式”符号。四组原创折角符印，带断笔、分支和错落的小印记；冷色表面、暗侧面与暖亮芯形成厚度感。模型、头部、武器和动作保持原样。本版仅改天将，其他Boss等待你验收后再做。</p>'''+figure('runes-motion','4.8秒无声实机采样：大符印缓慢偏转，小符文环绕，晶片与光屑上升。','webp')+'''<button id="toggle">暂停</button> <input id="frame" type="range" min="0" max="23" value="0"><span id="time">0.0秒</span>
<h2>同机位前后对照</h2>'''+figure('45-comparison','左旧版、右新版；同8米、FOV70、相同裁切和普通日光，不借相机缩放增加体量。')+figure('front-comparison','正面：主符印围绕身体后方，碎符环带与光屑分层。')+'''<div class="grid">'''+figure('rune-detail','符文局部实际画面：移除可读汉字式符号。')+figure('on-off','关闭后原模型保持一致。')+figure('side-comparison','侧面：符印有偏转和侧面厚度，不是贴在镜头前的字。')+figure('back-comparison','背面：符印层与肩后气流的关系。')+'''</div><h2>增加了多少</h2><p>普通粒子设置下：6枚旧符号改为12枚主符印＋24枚环绕小符文；增加36片有明暗面的漂浮晶片；细光屑轨迹42条增至84条。实际小粒子发射从待机每4tick 7枚提高到10枚，挥击时14枚光屑及至多1枚电光，仍受原有全局16枚预算限制。它们都是客户端视觉效果，没有新实体、碰撞或伤害。</p>
<p>减少/最少粒子设置会降低符印、晶片与光屑数量，远距离也会简化。数量增加并不等于发出同样多的服务器实体。</p>'''+figure('attack','原有攻击蓄势、接触、恢复；大戟导流继续跟随真实动作。')+figure('night','普通夜间开关对照，不用后期提亮截图。')+figure('settings','粒子设置降级；最少设置不发射额外粒子，仍保留少量简化符印。')+'''<h2>实际参考与返工</h2><p><a href="https://www.curseforge.com/minecraft/mc-mods/goety/gallery">诡厄巫法</a>：读取了本地2.5.49.3的使徒气场与召唤图案，实际查看折线分组、连贯密度和形状组织。没有复制原图或直接改色。</p>
<p><a href="https://overlord-anime.com/_season2/story/?ep=26">Overlord III 第12话官方静帧</a>：实际查看第5张法阵画面，学习大环带、小符号与中央人物的尺度关系。仅作静帧研究，没有声称看过完整特效动画。<a href="https://overlord-anime.com/_season2/assets/story/26_5.jpg">查看参考原图</a>。</p>
<p>第一轮已经增加符文，但整圈金黄偏像金属挂件；第二轮增加断笔和分支，改为冷面、暗侧、暖芯，保留厚度而减轻“字牌”感。</p>
<h2>检查与验收范围</h2><p>构建通过（跳过通用测试）；19个受控实机状态通过，24帧待机连续采样。基础模型、贴图、动画与认可版本逐字节相同。没有修改其他Boss，也没有改战斗机制。自然战斗、多人负载和第三方光影仍待验证。</p>
<p><a href="reference-notes.json">参考记录</a> · <a href="validation.json">验证记录</a> · <a href="native/PASS.txt">实机状态记录</a> · <a href="../tianjiang-aura-v19/index.html">上一版</a></p></main><script>const im=document.querySelector('img[src="runes-motion.webp"]'),slider=document.getElementById('frame'),button=document.getElementById('toggle');function frame(){im.src='frames/'+String(slider.value).padStart(2,'0')+'.webp';document.getElementById('time').textContent=(slider.value*.2).toFixed(1)+'秒';button.textContent='播放'}slider.oninput=frame;button.onclick=()=>{if(im.getAttribute('src')==='runes-motion.webp')frame();else{im.src='runes-motion.webp';button.textContent='暂停'}};</script></html>'''
 (D/'index.html').write_text(page)
 print('V20 native review ready; body assets locked; other bosses untouched.')
if __name__=='__main__':main()
