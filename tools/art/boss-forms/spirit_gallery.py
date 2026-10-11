"""Review page for the three improvements, using actual exported and native images."""
import json,hashlib,html
from pathlib import Path
from spirits import p
D=p.D
INFO={
'eunuch_mastermind':dict(name='帷幕面灵',cause='扇骨、金边和袖口与面具争抢注意力，原面部有笑脸感。',paint='收敛扇沿与袖口；深眼窝、克制的目光与下垂面纹突出面具。布幕沿折叠方向分层，长指区分根部、指节与末端。',motion='面具独立观察，长袖和指体轻微蓄势；近战从原有接触开始回弹，再收拢。',reference='Goety Necromancer / Wraith 原始贴图的暗布、骨色与小面积重点组织。',limit='仍沿用原有面具、鼻和颊几何。cast 未由当前通用控制器绑定具体法术，本轮未声称法术同步全部完成。'),
'rebel_general':dict(name='兵煞残甲',cause='甲片上重复的亮边、铆点和残旗盖过了残盔；刀面缺少连续刃口。',paint='残盔改为暗眼槽中的小面积琥珀观察口；旧铁保留干净大面，只在搭接与破甲手受力面集中接缝和磨损。原刃口连续区分，胸内兵煞降为辅助。',motion='残盔朝向与持械预备姿态加强；第12 tick前蓄力，接触后巨臂配重回稳，完整动作仍24 tick。',reference='Ignis 的兵器/护甲主次及原始PNG色区；Ender Golem 作者展示中的头与重臂分工。',limit='自然创建实体主手为空时展示原有几何长兵刃；非空主手仍走既有物品挂点。本轮未改变装备逻辑，非空装备组合未追加逐项测试。'),
'xianzhen_duantoujiang':dict(name='刑枷悬首',cause='悬首与钢甲明度接近，红橙眼像通用装饰；吼击时旧滚转让脸转离玩家。',paint='苍灰面部、深眼窝和口腔分区突出悬首；木枷、暗链、铁甲分材质。普通肩甲去掉均匀亮点，刃口与手部接触磨损成为次级威胁。',motion='头与链作为整体绕原锚点摆动；吼击减少侧翻，24 tick仍朝前，巨臂随后恢复。旋转与抛掷保留既有技能时间。',reference='Goety Necromancer 骨色与暗衣层次；保留本作木枷长轴木纹，未复制外部资产。',limit='悬首没有独立下颚，本轮口部是表面设计，不声称具备张嘴结构；抛掷技能沿用原血池机制，未新增飞头。')}
def fig(path,title):
 return f'<figure><a href="{path}" target="_blank"><img loading="lazy" src="{path}" alt="{title}"></a><figcaption>{title}</figcaption></figure>'
receipts={}
for id in p.TARGETS:
 batch='spirits-2' if id==p.TARGETS[0] else 'spirits-1'
 states=[]
 assert (D/'native'/batch/'PASS.txt').exists()
 for f in sorted((D/'native'/batch).glob('*-state.json')):
  record=json.loads(f.read_text())
  if record['entity']!=id:continue
  for rel,hash in record['loadedResourceSha256'].items():assert hashlib.sha256((p.R/'src/main/resources'/rel).read_bytes()).hexdigest()==hash
  states.append({'label':record['stage'],'age':record['age'],'receipt':str(f.relative_to(D)),'image':str(next(f.parent.glob(f.name[:2]+'-'+id+'-*.png')).relative_to(D))})
 receipts[id]=states
assert [len(receipts[id]) for id in p.TARGETS]==[7,8,10]
result={'scope':'improvement; approved geometry, UV, skeleton hierarchy, dimensions, collision and skills unchanged','baseCommit':'05932437','build':'PASS','native':'25 selected production-rendered states PASS; 7 curtain states recaptured after chunk warmup','idempotence':'byte-identical repeat export, bbmodel embedded PNG equals runtime PNG','externalPixelsUsed':False,'models':{id:{**INFO[id],'nativeStates':receipts[id]} for id in p.TARGETS},'limits':['Controlled offline flat-world native renderer/controller acceptance; not a natural encounter or multiplayer balance test.','No local geometry adaptation was required for this focal pass; no new jaw or chain entity introduced.']}
(D/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
s='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dynasty · 三只怨灵改善 v5</title><style>body{margin:0;background:#f0f1ec;color:#263233;font:17px/1.7 system-ui}header,main{max-width:1320px;margin:auto;padding:24px}header{padding-top:48px}h1{margin:.2em 0}small,.note{color:#546564}nav{display:flex;gap:12px;flex-wrap:wrap}a{color:#285f62}section{background:#fff;padding:26px;margin:28px 0;border:1px solid #d6ddd7;border-radius:12px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}figure{margin:12px 0}img{display:block;width:100%;height:auto;image-rendering:pixelated}figcaption{font-size:14px;color:#526361}button{font:inherit;padding:7px 16px;margin:8px 8px 8px 0;background:#e2ebe6;border:1px solid #bccac3;border-radius:6px;cursor:pointer}summary{cursor:pointer;padding:12px 0}code{font-size:13px}details{border-top:1px solid #dde3dd;margin-top:18px}.native img{image-rendering:auto}@media(max-width:720px){.grid{grid-template-columns:1fr}section{padding:16px}header,main{padding:16px}}</style><header><small>DYNASTY / FORGE 1.20.1 / 美术改善 v5</small><h1>形态保留，意志与威胁更清楚</h1><p>帷幕面灵 · 兵煞残甲 · 刑枷悬首。只改善实际贴图与已有骨骼姿态，保持模型、UV、体型和技能。</p><nav>'''
s+=''.join(f'<a href="#{id}">{INFO[id]["name"]}</a>' for id in p.TARGETS)
s+='</nav><p class="note">构建通过 · 25个实机状态核对加载哈希 · 可点击任意图片查看原尺寸</p></header><main>'
for id in p.TARGETS:
 m=INFO[id];s+=f'<section id="{id}"><h2>{m["name"]}</h2><code>dynasty:{id}</code><p>{m["cause"]}</p><p>{m["paint"]}</p><p>{m["motion"]}</p><small>实际参考：{m["reference"]}</small><h3>同相机、同比例前后对照 · 软件预览</h3>'
 for mode,label in [('unlit','PNG原色'),('lit','基础光照'),('gray','灰度主次')]:
  s+=f'''<button onclick="const i=document.getElementById('{id}-compare');i.src='{id}/comparison-{mode}.png';i.parentNode.href=i.src">{label}</button>'''
 s+=f'<a href="{id}/comparison-lit.png" target="_blank"><img id="{id}-compare" src="{id}/comparison-lit.png" alt="修改前后"></a>'
 s+='<h3>实机画面 · 普通光照、无额外粒子、玩家比例</h3><div class="grid native">'
 s+=''.join(fig(r['image'],r['label']+' · 实机') for r in receipts[id][:4])+'</div>'
 s+='<details><summary>实机移动、预备、接触和恢复</summary><div class="grid native">'+''.join(fig(r['image'],f'{r["label"]} · {r["age"]} tick') for r in receipts[id][4:])+'</div></details>'
 s+='<h3>完整代表动作 · 软件逐面贴图</h3><div class="grid">'+fig(id+'/action.webp','固定镜头完整动作')+fig(id+'/states.png','待机、观察/预备、接触、恢复')+'</div>'
 for title,files in [('原色近景、正侧背与灰度',[(x+'.png',x) for x in ['front-unlit','side-unlit','back-unlit','three-quarter-unlit','front-gray','three-quarter-gray']]),('原始PNG与UV检查',[('texture.png','256×256原始PNG'),('texture-4x.png','4倍最近邻'),('uv-overlay-4x.png','UV叠加编号'),('uv-direction.png','方向检查'),('uv-direction-side.png','侧面方向检查')]),('玩家、石砖木材与观察距离',[('scene.png','1.8m玩家 / 1m石砖木材'),('distance-10m.png','10m'),('distance-18m.png','18m'),('distance-28m.png','28m')])]:
  s+=f'<details><summary>{title}</summary><div class="grid">'+''.join(fig(id+'/'+file,label) for file,label in files)+'</div></details>'
 s+=f'<p class="note">验证边界：{m["limit"]}</p></section>'
s+='''<section><h2>验证记录</h2><p>实际PNG、动画与3份可编辑bbmodel已更新。完整geo.json、UV、父子骨骼、动作名称与总时长逐项一致；其他5只及锤链资源未变。循环、地面穿插采样和重复导出通过。</p><p>第一轮25项实机检查通过；首次面灵截图的背景区块未完全显示，延长首帧等待后重拍7项，全部通过。页面采用重拍后的面灵和第一轮另外两只。自然遭遇、多人同步、非空主手装备组合未追加测试。</p><p><a href="results.json">结果与25项实机记录</a> · <a href="offline-validation.json">离线检查</a> · <a href="build-result.log">构建记录</a></p><details><summary>实际查看的素材来源</summary><p><a href="https://raw.githubusercontent.com/Polarice3/Goety-2/75a80b2d5a195b3b93efc12f14049b3ad5ada7d9/src/main/resources/assets/goety/textures/entity/necromancer/necromancer.png">Goety Necromancer 原PNG</a> · <a href="https://raw.githubusercontent.com/Polarice3/Goety-2/75a80b2d5a195b3b93efc12f14049b3ad5ada7d9/src/main/resources/assets/goety/textures/entity/wraith/wraith.png">Goety Wraith 原PNG</a>：本轮查看最近邻放大，学习深色衣料与骨色局部的明度分配。Goety 2.5.58.4 / MC1.20.1。</p><p><a href="https://raw.githubusercontent.com/lender544/new1.20.1/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/resources/assets/cataclysm/textures/entity/ignis/ignis_idle_0.png">Ignis 原PNG</a>：本轮查看色区；<a href="https://media.forgecdn.net/attachments/510/182/2022-10-30_21.png">Ignis作者展示</a>与<a href="https://media.forgecdn.net/attachments/411/941/2021-12-02_10.png">Ender Golem作者展示</a>沿用上一轮已查看的主次观察。宣传光照不作为PNG反射依据。仅学习方法，没有复制像素、UV或模型。</p></details></section></main></html>'''
(D/'index.html').write_text(s)
# A compact before/after entry image; detailed originals remain in individual sections.
from PIL import Image
sheet=Image.new('RGB',(1800,2280))
for i,id in enumerate(p.TARGETS):sheet.paste(Image.open(D/id/'comparison-lit.png'),(0,i*760))
sheet.save(D/'three-comparisons.png')
print('Gallery ready; 25 current hashed native receipts')
