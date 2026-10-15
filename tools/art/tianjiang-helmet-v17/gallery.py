"""Local head/helmet review with separate software and native evidence."""
from export import *
import shutil,zipfile
from PIL import ImageFont
NAT=R/'docs/art/boss-human-v12/native/tianjiang-helmet-v17-final-12m'
PREV=R/'docs/art/tianjiang-texture-v16'
def run():
 assert (NAT/'PASS.txt').exists();shutil.copytree(NAT,D/'native',dirs_exist_ok=True)
 current=hashes();oldhash=json.loads((D/'before-hashes.json').read_text());records=[]
 for i in range(14):
  rec=json.loads((NAT/f'{i:02d}-state.json').read_text());prev=json.loads((PREV/'native'/f'{i:02d}-state.json').read_text())
  assert all(current['src/main/resources/'+k]==val for k,val in rec['loadedResourceSha256'].items())
  assert rec['dimensions']==prev['dimensions'];records.append({'stage':rec['stage'],'clip':rec['clip'],'age':rec['age'],'renderer':rec['renderer']})
 report={'sourceAndActualLoadedAssetsMatch':True,'colliderUnchanged':True,'camera':'12m, FOV70, player eye1.62, pitch -7, ordinary daylight, no shaders','stages':records,'scope':'14 controlled native stages; offline full animation separately; not natural fight or multiplayer testing'}
 (D/'native-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',28)
 for i,name in [(0,'front'),(2,'45')]:
  board=Image.new('RGB',(3600,850),(232,233,228));d=ImageDraw.Draw(board)
  for j,folder in enumerate([PREV/'native',D/'native']):
   pic=Image.open(folder/f'{i:02d}-{ID}-{name}-off.png');board.paste(pic.crop((700,600,2500,1350)),(j*1800,60))
   d.text((j*1800+16,12),('修改前V16' if j==0 else '头脸精修V17')+' / 同机位普通日光 / 关闭气场',font=font,fill=(37,42,43))
  d.text((16,810),'实机截图相同裁切，不单独缩放角色。既有待机微动保留；软件对照使用完全相同姿态。',font=font,fill=(37,42,43));board.save(D/f'native-{name}-comparison.png')
 refs={'actuallyViewed':[
  {'mod':'Cataclysm','version':'3.27 existing native study; local jar also inspected separately:3.16','characters':['Scylla','Maledictus'],'evidence':'Existing native front/45 screenshots and enlarged head crops; original PNG atlases','source':'https://www.curseforge.com/minecraft/mc-mods/lendercataclysm','method':'Eye aperture lies behind distinct brow/cheek planes; sparse high-value metal directs attention. Applied as six original shallow brow/cheek/forehead/bridge pieces, not copied head silhouettes.'},
  {'mod':'Goety / Goety Revelation','version':'Goety2.5.36.1 / Revelation2.2.7 local jars; ApostleModel source snapshot 75a80b2 is a separate later version','characters':['Apostle','Apollyon'],'evidence':'Original64x128 atlases enlarged, ApostleModel source, Apollyon author overworld/nether images (350x181, shader-lit, unsuitable for judging base colour)','source':'https://www.curseforge.com/minecraft/mc-mods/goety-revelation/gallery','method':'Restricted eye line and head-versus-dark-cloth separation; no big cartoon flesh mouth. Used the attention hierarchy, not their pale skin/red eyes/halo. Apollyon belongs to the addon, not a separately assumed base-Goety boss.'},
  {'mod':'Iron’s Spells ’n Spellbooks','version':'Local1.20.1-3.4.0.11; author gallery images date2023, exact pictured build not stated','characters':['Pyromancer','Cryomancer','Necromancer','Archevoker','Priest'],'evidence':'Original entity/armour atlases; pyromancer/cryomancer/cleric hood geo; author Pyromancer and Necromancer actual screenshots. Did not view all characters in-game.','source':'https://www.curseforge.com/minecraft/mc-mods/irons-spells-n-spellbooks/gallery','method':'Pyromancer hat shadows small facial opening; Cryomancer inflated hood wraps a dark aperture; Necromancer uses a few eye/mouth clusters. Applied actual helmet overlap around a quieter mask. No wizard hat, villager nose or borrowed face.'}],
 'limits':'The small Apollyon gallery pictures do not support pixel-level claims; raw local atlases and source supply those checks. No claim to reviewing every boss, every phase, or every mod asset.',
 'externalAssetsCopiedIntoProduction':False}
 (D/'reference-notes.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
 with zipfile.ZipFile(D/'helmet-assets.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in TARGETS:z.write(p,str(p.relative_to(R/'src/main/resources')))
 def fig(n,label,ext='png'):return f'<figure><a href="{n}.{ext}"><img loading="lazy" src="{n}.{ext}"></a><figcaption>{label}</figcaption></figure>'
 clips=''.join(fig(n,n+' · 原有完整时间轴','webp') for n in ['idle','walk','attack','cast','hurt','death'])
 page=f'''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>九霄天将 · 头脸与浅层盔甲 V17</title>
<style>body{{background:#e9ece8;color:#25343c;margin:0;font:17px/1.7 system-ui}}main{{max-width:1550px;margin:auto;padding:28px}}h1{{font-size:29px}}h2{{font-size:23px;margin-top:34px}}figure{{margin:0 0 24px}}img{{max-width:100%;height:auto}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px}}a{{color:#195b70}}p{{max-width:1180px}}figcaption{{padding:8px 0}}</style><main>
<h1>九霄天将：改头脸，不改身体</h1>
<p>这次修正的是醒目的肉色鼻口、平盒子头盔与柱状帽顶。面部改为冷铁战斗面甲，窄眼缝位于压低的古金眉甲后；两片浅护颊、额甲和短鼻梁形成实际内外层。旧柱状冠件收为短纵向盔脊。不是重做全身。</p>
{fig('head-comparison','左：V16。右：V17。相同相机、相同原色采样、相同头部姿态；无发光。')}
<p>仅头骨上附加6块薄盔甲，沿用原骨骼；调整原有小盔脊。头部本体仍为原8×8×8比例，身体、持戟、装备布局、碰撞和全部动作时间轴不变。新增面放入128×128图集空区，旧UV没有挪动，头部以外的有效像素逐像素保持。</p>
<h2>45度与侧面：真实建模起伏</h2><div class="grid">{fig('head45-close','基础漫反射软件预览；不是游戏截图')}{fig('helmet-side-close','浅护颊与盔脊的侧面')}{fig('head-front-close','原色正面：眼、眉、面甲的主次')}{fig('head-gray-close','灰度检查，真实几何起伏')}</div>
<h2>原身体与大戟</h2>{fig('45-comparison','同机位45度对照，未扩大头部或改变全身比例')}{fig('player-scale','软件预览，玩家、石砖与木材同场比例')}
<h2>普通日光实机</h2>{fig('native-front-comparison','独立静音Forge测试世界，气场关闭')}{fig('native-45-comparison','前后相同机位与裁切，保留既有待机微动')}
<p>构建通过。14项受控实机检查完成，实际加载的模型、动画和PNG哈希与源资源/JAR一致。离线逐条检查6段动作，每段121个采样点通过地面与渲染边界检查。没有运行自然战斗或多人联机验收；没有操作用户存档。</p>
<p><a href="native/00-{ID}-front-off.png">完整实机正面</a> · <a href="native/10-{ID}-attack-contact.png">实机攻击接触</a> · <a href="native/13-{ID}-death.png">实机倒地</a> · <a href="validation.json">范围/UV/导出核对</a> · <a href="native-validation.json">实机加载核对</a></p>
<h2>实际PNG与可编辑源</h2>{fig('texture-comparison','相同128×128图集，四倍最近邻；仅头盔与脸部区域改变')}
<p><a href="before.png">修改前PNG</a> · <a href="after.png">修改后PNG</a> · <a href="after-4x.png">最近邻放大PNG</a> · <a href="blockbench/{ID}.bbmodel">Blockbench模型与内嵌贴图/原动作</a> · <a href="helmet-assets.zip">运行资源包</a></p>
<h2>完整动作</h2><div class="grid">{clips}</div>
<h2>实际看过的参考与落实</h2>
<p><a href="https://www.curseforge.com/minecraft/mc-mods/lendercataclysm">灾变 Scylla、Maledictus</a>：看过实际游戏正面、45度、头部裁切和原图集；落实“盔口留暗、眉颊在外”的层次，没有借用触角、长角或面具造型。</p>
<p><a href="https://www.curseforge.com/minecraft/mc-mods/goety-revelation/gallery">Goety使徒、Revelation亚博伦</a>：看过原图集、使徒模型源和亚博伦作者展示；学习小范围眼线与深浅主次。亚博伦是附属内容。展示图小且有光影，未当作PNG金属效果依据。</p>
<p><a href="https://www.curseforge.com/minecraft/mc-mods/irons-spells-n-spellbooks/gallery">铁魔法术士</a>：看过火焰术士、死灵术士作者画面，以及冰霜术士等的原图集和兜帽几何；借鉴外围遮挡与窄面部窗口。没有复制巫师帽、村民鼻子或别人的五官。<a href="reference-notes.json">版本、实际查看范围与限制</a>。</p>
<p>自检第一稿仍有下垂眉甲与金色胡须感，已再修。现版把眼窝收窄、眉尖压向中心、下半脸改为低对比铁面，并降低原帽顶。权威生成源为 tools/art/tianjiang-helmet-v17/export.py；V15/V16旧导出入口均转到此源，重复导出资源一致。</p></main></html>'''
 (D/'index.html').write_text(page);print('Helmet gallery and native parity ready.')
if __name__=='__main__':run()
