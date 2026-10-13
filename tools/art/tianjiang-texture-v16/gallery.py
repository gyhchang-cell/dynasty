"""Texture-only deliverable, independent native proof and honest comparisons."""
from export import *
import shutil,zipfile,base64
from PIL import ImageDraw,ImageFont
NAT=R/'docs/art/boss-human-v12/native/tianjiang-texture-v16-final-12m'
def run():
 assert (NAT/'PASS.txt').exists()
 shutil.copytree(NAT,D/'native',dirs_exist_ok=True)
 current=hashes();old=json.loads((D/'before-hashes.json').read_text())
 stages={}
 for i in range(14):
  rec=json.loads((D/'native'/f'{i:02d}-state.json').read_text())
  assert all(current['src/main/resources/'+k]==v for k,v in rec['loadedResourceSha256'].items())
  stages[rec['stage']]={'renderer':rec['renderer'],'texture':rec['texture'],'clip':rec['clip'],'age':rec['age']}
  assert rec['dimensions']==json.loads((PREV/'native'/f'{i:02d}-state.json').read_text())['dimensions']
 cfg=json.loads((R/'build/boss-eight-native/tianjiang-texture-v16-final-12m/launch.json').read_text())
 assert '-Ddynasty.bossEightQa.cameraDistance=12' in cfg['jvmArgs']
 assert '-Ddynasty.bossEightQa.cameraPitch=-7' in cfg['jvmArgs']
 report={'productionLoadHashes':current,'stages':stages,'camera':'12m, FOV70, eye1.62m, pitch -7, normal day, no shaders','scope':'14 stages in silent hidden disposable Forge world; not natural encounter/multiplayer balance testing','geometryAnimationUV':'exact production byte equality before/after'}
 (D/'native-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 # Native idle micro-motion is left untouched; exact same pose evidence is
 # supplied by the offline pair, whose only differing input is the PNG.
 font=lambda n:ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',n)
 crop=(700,600,2500,1350)
 for i,name in [(0,'front'),(2,'45')]:
  out=Image.new('RGB',(3600,850),(232,233,228));draw=ImageDraw.Draw(out)
  for j,(folder,label) in enumerate([(PREV/'native','修改前 V15'),(D/'native','仅贴图修改 V16')]):
   rec=json.loads((folder/f'{i:02d}-state.json').read_text())
   expected=old if j==0 else current
   assert all(expected['src/main/resources/'+k]==v for k,v in rec['loadedResourceSha256'].items())
   im=Image.open(folder/f'{i:02d}-{ID}-{name}-off.png')
   out.paste(im.crop(crop),(j*1800,60));draw.text((j*1800+16,12),label+' / '+name+' / 原生日光 / 关闭气场',font=font(28),fill=(37,42,43))
  draw.text((16,811),'同机位、同FOV、相同裁切；未单独放大角色。既有待机微动保留；离线对照使用完全相同姿态。',font=font(23),fill=(37,42,43));out.save(D/f'native-{name}-comparison.png')
 # Update only the embedded PNG of the existing editable model.
 bb=json.loads((PREV/'blockbench'/f'{ID}.bbmodel').read_text())
 bb['textures'][0]['source']='data:image/png;base64,'+base64.b64encode(TARGETS[2].read_bytes()).decode()
 (D/'blockbench').mkdir(exist_ok=True);(D/'blockbench'/f'{ID}.bbmodel').write_text(json.dumps(bb,ensure_ascii=False,indent=2)+'\n')
 refs={'source':'https://www.curseforge.com/minecraft/mc-mods/lendercataclysm','localStudyVersion':'Cataclysm 3.27 Forge 1.20.1 (existing study installation, not a claim about latest release)','actuallyViewed':[
  {'character':'Scylla','files':['assets/cataclysm/textures/entity/scylla/scylla.png','docs/art/boss-human-v12/reference-native/power-reference-round1/cataclysm_scylla-front.png'],'observation':'Cold segmented armour tones, recessed internal areas and selectively brighter gold edging. Applied to helmet/cheek framing and broad steel panels; no colours or motifs sampled.'},
  {'character':'Maledictus','files':['assets/cataclysm/textures/entity/maledictus/maledictus_armor.png','docs/art/boss-human-v12/reference-native/power-reference-round1/cataclysm_maledictus-front.png'],'observation':'Metal and dark fabric use different tone organization, sparse ornamental contrast. Applied to painted shoulder folds, cloth and worn antique-gold bands; no ghost wings or emissive assets used.'}],
 'externalAssetsInProduction':False,'productionInput':'Approved original Dynasty geometry and UV; exclusively hand-arranged V16 pixel clusters'}
 (D/'reference-notes.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
 with zipfile.ZipFile(D/'texture-only-assets.zip','w',zipfile.ZIP_DEFLATED) as z:
  z.write(TARGETS[2],str(TARGETS[2].relative_to(R/'src/main/resources')))
 def figure(file,label):return f'<figure><a href="{file}.png"><img src="{file}.png" loading="lazy"></a><figcaption>{label}</figcaption></figure>'
 detail=''.join(figure(n+'-comparison',label) for n,label in [('head','头部：压眉、眼窝与护颊铁面；古金冠沿、玉点'),('chest','胸甲：同一大甲面的深浅折面；沿用原创雷纹'),('shoulder','肩部：甲面转折与有限磨损；深蓝衣褶分开'),('weapon','大戟：连续钢面与切削刃、克制缺损；皮革握柄')])
 views=''.join(figure(n+'-'+mode,n+' / '+('PNG原色' if mode=='unlit' else '基础软件光照')) for n in ['front','45'] for mode in ['unlit','lit'])
 clips=''.join(f'<figure><a href="{n}.webp"><img src="{n}.webp" loading="lazy"></a><figcaption>{n} 原有完整动作 / 时间轴未改</figcaption></figure>' for n in ['idle','walk','attack','cast','hurt','death'])
 page=f'''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>九霄天将 · 仅贴图精修 V16</title>
<style>body{{background:#e9ece8;color:#25343c;margin:0;font:17px/1.65 system-ui}}main{{max-width:1500px;padding:28px;margin:auto}}h1{{font-size:28px}}h2{{font-size:23px;margin-top:34px}}img{{max-width:100%;height:auto}}figure{{margin:0 0 22px}}figcaption{{padding:8px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px}}a{{color:#195b70}}p{{max-width:1150px}}.pixel{{image-rendering:pixelated}}</style><main>
<h1>九霄天将：模型锁定，只精修贴图</h1>
<p>生产资源只改一张 PNG。模型、比例、骨架、装备位置、兵器、碰撞、动画和全部 UV 均保留；geo.json 与 animation.json 相比 V15 逐字节一致。仍是原来的 128×128 图集，没有增加分辨率，也没有新增几何结构。</p>
<h2>修改前后：真实图集</h2>{figure('texture-comparison','原始128×128，四倍最近邻；相同UV，全部原创绘制。')}
<p><a href="before.png">修改前原始 PNG</a> · <a href="after.png">修改后原始 PNG</a> · <a href="after-4x.png">修改后4倍最近邻</a> · <a href="texture-only-assets.zip">仅PNG运行资源包</a> · <a href="blockbench/{ID}.bbmodel">原模型内嵌新贴图的可编辑源文件</a></p>
<h2>同形体、同姿态、同机位对照</h2>{figure('front-comparison','正面 / 原色贴图软件预览')}{figure('45-comparison','45度 / 基础漫反射软件预览')}
<h2>头部、胸甲、肩部与武器近景</h2>{detail}
<p>冷铁通过大甲面、转折与少量亮边区分内外；古金改为暗金底、古金面与克制亮点。深蓝布料按折叠方向画低对比像素簇；腰带与戟柄使用暗皮革。玉点使用深底与少量浅像素，均为非发光 PNG。雷纹沿用角色已有标识，未新增家族、阵营或剧情设定。</p>
<h2>正面与45度独立预览</h2><div class="grid">{views}</div>
<h2>实际游戏加载验证</h2>{figure('native-front-comparison','真实游戏，前后相同普通日光机位与裁切；待机微动保持。')}{figure('native-45-comparison','真实游戏45度，玩家与石砖参照；气场关闭。')}
<p>构建通过，PNG在源资源、处理资源和JAR中逐字节一致。静音隐藏的独立Forge世界完成14项受控检查，各帧核对实际加载的模型、动画与PNG哈希；保留原有移动、攻击接触、恢复、受伤与死亡。未操作用户存档。该验证确认加载与美术表现，不冒充自然遭遇或多人平衡验收。</p>
<p><a href="native/00-{ID}-front-off.png">实机正面完整截图</a> · <a href="native/02-{ID}-45-off.png">实机45度完整截图</a> · <a href="native/10-{ID}-attack-contact.png">原攻击接触帧</a> · <a href="native-validation.json">实际加载核对</a> · <a href="validation.json">模型/UV未变与导出检查</a></p>
<h2>UV、材质与距离检查</h2><div class="grid">{figure('uv-direction','带方向与编号的临时UV检查，未进入运行PNG')}{figure('gray','灰度下的主次与材质关系')}{figure('dim','软件暗光检查')}{figure('player-scale','正常玩家、石砖、木材的比例参照')}{figure('distance-8','8米软件透视，正常观察视高')}{figure('distance-16','16米软件透视，正常观察视高')}</div>
<h2>既有动作回放</h2><div class="grid">{clips}</div>
<h2>实际参考与改动原因</h2><p>实际查看了灾变现有研究安装中 Scylla 的原始图集和游戏正面，以及 Maledictus 的盔甲图集和游戏正面：借鉴的是甲面深浅分区、内层留暗、古金边框有主次、布与铁不共用一种表面处理。分别落实在天将眉压与护颊、胸肩钢面、低对比深蓝衣褶和旧金饰边。没有复制颜色、纹样、贴图、模型或动画，也没有将鬼翼、粒子与宣传光效算作PNG层次。<a href="https://www.curseforge.com/minecraft/mc-mods/lendercataclysm">灾变作者发布页</a> · <a href="reference-notes.json">实际查看的资源和借鉴部位</a>。</p>
<p>根因是旧绘制中金属大面近乎平填、布与铁过于接近、脸部与冠沿主次不足。已重新组织这些表面；图集分辨率、UV和预览采样没有问题，均保留。自检时又修正了月牙戟上段过暗的问题，使钢面跨相邻块连续。权威绘制源为 tools/art/tianjiang-texture-v16/paint.py；现有 V15 完整导出也调用这个源，下次导出不会恢复旧贴图。</p></main></html>'''
 (D/'index.html').write_text(page)
 print('Texture-only gallery, before/after native proof and unchanged editable model ready.')
if __name__=='__main__':run()
