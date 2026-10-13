from create import *
NOTES=[
 '主体改为连成整体的前压铠躯；头嵌入胸肩，左侧长前臂承担防护轮廓，右侧握枪。胸肩、长臂、短承重腿分出主次，背甲延续胸甲而非外挂旗杆。',
 '改为有王者识别的龙化躯体：前伸龙颈与上下颌、后弯承重腿、连续尾根到尾尖。四肢保留操持王兵的能力，身体重心与尾部互相平衡；不再是人脸戴角。',
 '改为宽厚帝王法相：面具嵌在大领甲内，胸壳与下垂外壳连成主体，短承重支撑与不对称施令臂。玉玺保留技能身份，背部连续拱架属于整体法相轮廓。']
REFS=[
 ('末影守卫 / Ender Guardian','ender_guardian','小头嵌入厚胸肩、前臂承担主轮廓；用于天将主体层级。'),
 ('焰魔 / Ignis','ignis','身体、防护肢、主兵器形成战备三角；用于天将握枪与防护侧分工。'),
 ('远古遗魂 / Ancient Remnant','ancient_remnant','头颈向前、后弯腿与尾部构成承重连续线；用于龙王前后重心关系。'),
 ('咒翼灵骸 / Maledictus','maledictus','异化头部与背部大轮廓合成身份，主体并非普通皮肤人物；用于龙帝的非皮肤面具与背后法相关系。')]
def run():
 css='body{font:17px/1.65 system-ui;background:#eceee9;color:#222b30;margin:0 auto;max-width:1500px;padding:25px}img{width:100%;height:auto;display:block}figure{margin:0}a{color:#176079}h1{font-size:28px}h2{font-size:25px;margin-top:35px}nav{display:flex;gap:25px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.card{background:white;padding:18px;border-radius:7px}figcaption{font-size:15px}.status{background:#dde5de;padding:15px}.refs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}@media(max-width:800px){.grid,.refs{grid-template-columns:1fr}}'
 html=['<!doctype html><meta charset="utf-8"><title>Dynasty V13 主结构灰模候选</title><style>'+css+'</style><h1>V13 · 主结构灰模候选</h1>',
 '<p class="status">先验收轮廓，再做正式 UV、像素材质与粒子。全部画面来自实际候选 geo.json 的离线深度缓冲渲染，统一世界单位与相机；均非游戏截图。灰色 PNG 仅用于形体检查。注册、AI、技能、伤害和当前运行美术均未替换。</p>',
 '<nav>'+''.join(f'<a href="#{id}">{name}</a>' for id,name in zip(IDS,NAMES))+'</nav>',
 '<a href="overview.png"><img src="overview.png" alt="三只同尺度灰模与剪影总览"></a><p><a href="body-only-overview.png">三只隐藏武器、独立背饰与冠：主体灰模及剪影总览</a></p>']
 for id,name,note in zip(IDS,NAMES,NOTES):
  b=json.loads((D/id/'bounds.json').read_text())
  html += [f'<section id="{id}"><h2>{name} · dynasty:{id}</h2><p>{note}</p><p>含冠/兵器总高度 {b["height_m"]:.2f}m；参照玩家 1.8m。足底接地，脚厚 {b["foot_top_m"]:.2f}m。图中差异来自实际比例，不是单独放大相机。</p><div class="grid">']
  for file,label in [('compare-front','当前资源 → 结构候选 / 正面同尺度'),('compare-45','当前资源 → 结构候选 / 45°同尺度'),('front-silhouette','正面黑色剪影'),('45-silhouette','45°黑色剪影'),('player-scale','玩家与石砖比例对照'),('45','45°简化灰模'),('front','正面灰模'),('side','侧面灰模'),('back','背面灰模'),('body-only','隐藏武器、独立背饰与冠的主体'),('body-only-silhouette','去配件的主体剪影')]:
   html.append(f'<figure class="card"><a href="{id}/{file}.png"><img src="{id}/{file}.png" loading="lazy" alt="{name} {label}"></a><figcaption>{label} · 点击原图</figcaption></figure>')
  for clip,label in [('idle','待机结构运动样片（完整2秒循环）'),('guard','前压观察结构运动样片（1秒）')]:html.append(f'<figure class="card"><img src="{id}/{clip}.webp" loading="lazy"><figcaption>{label}；不是已接入战斗的正式动画。</figcaption></figure>')
  html += ['</div><p>'+f'<a href="blockbench/{id}.bbmodel">Blockbench 可编辑源</a> · <a href="candidates/{id}/{id}.geo.json">实际候选 geo.json</a> · <a href="candidates/{id}/{id}.animation.json">结构运动 animation.json</a></p></section>']
 html += ['<h2>实际查看的参考与本轮判断</h2><p>以下为此前在隔离测试世界拍摄、这轮重新逐张查看的灾变 3.27 原模组实机画面；普通光照，无光影或替换资源包，静止状态。参考结构方法，不取用外部模型、贴图或动画。游戏图和离线灰模不是材质质量的同条件评分。</p><p><a href="https://www.curseforge.com/minecraft/mc-mods/lendercataclysm/gallery">灾变作者展示页</a></p><div class="refs">']
 for name,id,note in REFS:
  path=f'../boss-human-v12/reference-native/power-reference-round1/cataclysm_{id}-45.png'
  html.append(f'<figure class="card"><a href="{path}"><img src="{path}" loading="lazy"></a><figcaption>{name}：{note} © L_Ender / Cataclysm，图为研究对照。</figcaption></figure>')
 html+=['</div><h2>自检与待验证</h2><p>第一稿过宽、腿过短，仍有积木壮汉感，已返工：收窄主躯宽度、拉长承重阶段，三只分别重画胸甲方向、头部、肢体和背部。随后重算梁段端点，修正非等比调整可能造成的关节与握持偏差。主体不是由旧 anatomy 人形函数生成。</p><p>已检查四视图、黑剪影、去配件主体、编辑源与 geo 的几何一致性、骨骼层级、UV 边界、脚底、待机循环及运动样片。<a href="validation.json">离线检查记录</a>。正式走路/攻击/施法/死亡、装备挂点运行、碰撞适配、Java 构建和游戏验证待灰模验收后完成，本轮不宣称已经达到灾变成品水平。</p>']
 (D/'index.html').write_text('\n'.join(html),encoding='utf-8')
if __name__=='__main__':run()
