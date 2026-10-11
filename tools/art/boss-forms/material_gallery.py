"""Publish the two material revisions, keeping full-size evidence and real game receipts."""
import json,hashlib,html
from PIL import Image
from materials import p
D=p.D
INFO={
'xianzhen_duantoujiang':dict(name='刑枷悬首',cause='脸部原有大黑块和亮铁框互相干扰；手、甲与刑具的分区接近，刀面缺少切削方向。',paint='重画额部、斜眼窝、紧咬口部与下颌，压低盔框；刑木沿横梁连续排纹，端面单独绘制。刑铁、内侧连接、皮绑和指组分开；刀背压暗、刃口连续，握持段独立包覆。',reference='Goety Necromancer：骨色主体与深色包围的明度关系，用在悬首和指组；Goety stripped_haunted_log：长轴纹路与端面分工，用在现有刑木，未沿用其像素和配色。',motion='完整检查 idle / walk / hurt / roar / spin / throw / death。吼击24 tick、旋转26 tick、抛掷20 tick的既有姿态已实机取样。转身时背面自然遮住脸，正向蓄势和恢复时悬首仍可辨认。',limit='原模型没有独立下颚；本轮口部仅为贴图，不声称可以张嘴。抛掷仍沿用已有技能，未增加飞头或新刀种。'),
'rebel_general':dict(name='兵煞残甲',cause='上层护甲与下层巨手重复使用箱体描边，外甲和内部梁同亮；小块黄眼缺少周围面甲支持。',paint='用盔口暗面、折叠面甲和额部建立观察方向；上层甲保留跨前侧面的暗朱旧漆，下层巨手突出护腕和接触磨损。内部梁比外甲更深，普通支撑收敛；长兵刃区分刀背、刃面、刃口与握持段。',reference='Cataclysm Ignis 原始PNG：主甲色区、暗连接和兵刃之间的主次，落实到既有红色身份、破甲臂和长兵刃；未复制纹章或角色外观。',motion='完整检查 idle / walk / hurt / attack / cast / death。普攻12 tick接触前后的持刀侧、甲臂和恢复已实机取样。保留全部动作文件。',limit='cast 为保留的资源片段，其抬甲阶段会遮住部分盔口；当前通用生产控制器未将它绑定具体法术，页面作为资源回放单列，未改技能或臆称完成法术同步。非空主手装备组合未逐项测试。')}

def fig(path,title):
 return f'<figure><a href="{html.escape(path)}" target="_blank"><img loading="lazy" src="{html.escape(path)}" alt="{html.escape(title)}"></a><figcaption>{html.escape(title)}</figcaption></figure>'

def group(title,items):
 return '<details><summary>'+title+'</summary><div class="grid">'+''.join(fig(*x) for x in items)+'</div></details>'

native=D/'native/material-1'
assert (native/'PASS.txt').exists()
receipts={id:[] for id in p.TARGETS}
for f in sorted(native.glob('*-state.json')):
 r=json.loads(f.read_text())
 for rel,digest in r['loadedResourceSha256'].items():
  assert hashlib.sha256((p.R/'src/main/resources'/rel).read_bytes()).hexdigest()==digest,(f,rel)
 image=next(native.glob(f.stem[:2]+'-'+r['entity']+'-*.png'))
 receipts[r['entity']].append(dict(label=r['stage'],age=r['age'],receipt=str(f.relative_to(D)),image=str(image.relative_to(D))))
assert [len(receipts[id]) for id in p.TARGETS]==[10,8]
assert 'BUILD SUCCESSFUL' in (D/'build-result.log').read_text()
assert json.loads((D/'idempotence.json').read_text())['repeatExport']=='byte-identical'
result={'scope':'PNG and authoritative painting source only; geometry/UV/rig/animation bytes unchanged',
 'baseCommit':'69600980','build':'PASS','native':'18 production-rendered states; actual PNG/geo/animation hashes verified',
 'offlinePlayback':'13 full clips, 40 samples per clip, fixed camera, all face UVs sampled from actual PNG',
 'externalPixelsUsed':False,'localGeometryAdaptationRequired':False,
 'models':{id:{**INFO[id],'nativeStates':receipts[id],'textureSha256':hashlib.sha256((p.A/'textures/entity/boss_forms'/(id+'.png')).read_bytes()).hexdigest()} for id in p.TARGETS},
 'limits':['Native acceptance uses a disposable controlled flat world, not natural encounter or multiplayer balance testing.', 'Software previews use unlit or neutral diffuse light; images under native/ are game screenshots.']}
(D/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
s='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dynasty · 刑枷与残甲材质精修 v6</title><style>
:root{color-scheme:light}body{margin:0;background:#f1f1ec;color:#273335;font:17px/1.7 system-ui}header,main{max-width:1400px;margin:auto;padding:24px}header{padding-top:48px}h1{margin:.2em 0}small,.note{color:#546362}nav{display:flex;gap:16px;flex-wrap:wrap}a{color:#256164}section{background:#fff;padding:28px;margin:28px 0;border:1px solid #d5dcd6;border-radius:10px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}figure{margin:14px 0}img{display:block;width:100%;height:auto;image-rendering:pixelated}figcaption{font-size:14px;color:#51615f}button{font:inherit;padding:7px 16px;margin:8px 8px 8px 0;background:#e2ebe6;border:1px solid #b8c9c1;border-radius:6px;cursor:pointer}button[aria-pressed=true]{background:#315c56;color:white}summary{cursor:pointer;padding:13px 0;font-weight:600}code{font-size:13px}details{border-top:1px solid #dde3dd;margin-top:20px}.native img{image-rendering:auto}.raw{width:256px;height:256px;max-width:none}.zoom{overflow:auto} @media(max-width:760px){.grid{grid-template-columns:1fr}section{padding:16px}header,main{padding:16px}}
</style><header><small>DYNASTY · FORGE 1.20.1 · 材质精修 v6</small><h1>悬首、刀锋与残甲的主次</h1><p>刑枷悬首与兵煞残甲：保留已认可的形体，重画实际贴图。</p><nav><a href="#xianzhen_duantoujiang">刑枷悬首</a><a href="#rebel_general">兵煞残甲</a><a href="#verification">验证与参考</a></nav><p class="note">构建通过 · 18个实机状态 · 13段完整离线回放 · 点击图片打开原尺寸</p></header><main>'''
for id in p.TARGETS:
 m=INFO[id];s+=f'<section id="{id}"><h2>{m["name"]}</h2><code>dynasty:{id}</code><p>{m["cause"]}</p><p>{m["paint"]}</p><small>实际参考：{m["reference"]}</small><h3>同相机、同姿态、同比例对照</h3><p class="note">左：本轮前的v5；右：本轮v6。软件逐面采样真实PNG，无粒子或发光。仅替换贴图，画面取景保持一致。</p><div class="modes">'
 for mode,label in [('lit','基础光照'),('unlit','PNG原色'),('gray','灰度主次')]:
  s+=f'<button aria-pressed="{str(mode=="lit").lower()}" data-target="{id}-compare" data-src="{id}/comparison-{mode}.png">{label}</button>'
 s+=f'</div><a href="{id}/comparison-lit.png" target="_blank"><img id="{id}-compare" src="{id}/comparison-lit.png" alt="同条件前后对照"></a>'
 for region,name in [('face','面部'),('weapon','武器'),('yoke' if id.startswith('xianzhen') else 'armor','刑枷连接' if id.startswith('xianzhen') else '上下甲面')]:
  s+=group(name+'近景 · 左旧右新',[(id+f'/detail-{region}-{angle}-{mode}.png',f'{name} / {angle} / {mode} / 同条件') for angle in ['front','45'] for mode in ['unlit','lit','gray']])
 s+='<h3>实机 · 普通光照、玩家与石砖参照</h3><div class="grid native">'+''.join(fig(r['image'],r['label']+' / Minecraft实机') for r in receipts[id][:2])+'</div>'
 s+=group('实机侧背、移动、蓄势、接触与恢复',[(r['image'],f'{r["label"]} / {r["age"]} tick / Minecraft实机') for r in receipts[id][2:]])
 s+='<h3>完整原动作回放</h3><p>'+m['motion']+'</p><p class="note">以下为软件逐面贴图回放。每段从0至结束，固定相机和尺度；点击展开逐帧表可以检查全部40帧。</p>'
 clips=json.loads((D/id/'motion-review.json').read_text())
 for clip,record in clips.items():
  s+=f'<details><summary>{clip} · {record["durationSeconds"]}秒 · 完整回放'+('（资源片段，未绑定具体法术）' if id=='rebel_general' and clip=='cast' else '')+'</summary><div class="grid">'+fig(id+'/'+clip+'-full.webp','完整循环 / 软件预览')+fig(id+'/'+clip+'-phases.png','开始、蓄势、主要动作、接触、恢复取样')+f'</div><p><a href="{id}/{clip}-filmstrip.png" target="_blank">查看全部40帧（原尺寸）</a></p></details>'
 s+=group('正面、侧面、背面与弱光',[(id+'/'+f+'.png',f+' / 软件逐面PNG') for f in ['front-unlit','side-unlit','back-unlit','three-quarter-unlit','front-gray','three-quarter-gray','dim']])
 s+=f'<details><summary>原始PNG、4倍最近邻与UV方向</summary><p>256×256图集、既有16 texel/block标尺保留。UV未调整；检查图仅在预览中使用。</p><div class="zoom"><a href="{id}/texture.png"><img class="raw" src="{id}/texture.png" alt="256x256原始PNG"></a></div><div class="grid">'+''.join(fig(id+'/'+f+'.png',label) for f,label in [('texture-4x','4倍最近邻'),('uv-overlay-4x','UV叠加编号'),('uv-direction','编号与方向'),('uv-direction-side','侧面方向')])+'</div></details>'
 s+=group('玩家视高与观察距离',[(id+'/'+f+'.png',label) for f,label in [('scene','1.8m玩家、1m石砖和木材 / 软件参照'),('distance-10m','10米 / 软件透视'),('distance-18m','18米 / 软件透视'),('distance-28m','28米 / 软件透视')]])
 s+=f'<p class="note">现有结构与验证边界：{m["limit"]}</p></section>'
s+='''<section id="verification"><h2>验证与实际参考</h2><p>运行绑定和UV未发现本轮需要修复的错面、共享岛或尺寸错误。根因主要在绘制方式：外框、主体和连接的处理过于接近，缺少部位职责。预览使用逐面最近邻PNG采样；原色视图不叠加材质乘色。</p><p>两张PNG、两份bbmodel内嵌贴图及权威绘制源已更新。重复导出字节一致；几何、UV、骨架和全部动画文件逐字节保持。其余6只与锤链资源保持。未新增局部几何。</p><p>13段完整资源动画已检查；18个实机状态核对当前PNG、模型和动画哈希。实机来自隔离测试世界中的正式注册实体、Renderer和控制器。自然遭遇、多人同步与非空主手装备组合未在本轮追加验证。</p><p><a href="results.json">结果与实机记录</a> · <a href="offline-validation.json">离线资源检查</a> · <a href="idempotence.json">重复导出</a> · <a href="build-result.log">构建记录</a></p><details><summary>实际看过的原始素材与借鉴部位</summary><p><a href="https://raw.githubusercontent.com/Polarice3/Goety-2/75a80b2d5a195b3b93efc12f14049b3ad5ada7d9/src/main/resources/assets/goety/textures/entity/necromancer/necromancer.png">Goety Necromancer 原PNG</a>：最近邻放大检查骨色与深色包围的关系，用于悬首与指组的明度层级。<a href="https://raw.githubusercontent.com/Polarice3/Goety-2/75a80b2d5a195b3b93efc12f14049b3ad5ada7d9/src/main/resources/assets/goety/textures/block/stripped_haunted_log.png">Goety stripped_haunted_log 原PNG</a>：查看沿轴纹路，刑木按自身朝向和受力点重新绘制。源码快照对应Goety 2.5.58.4 / Minecraft 1.20.1。</p><p><a href="https://raw.githubusercontent.com/lender544/new1.20.1/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/resources/assets/cataclysm/textures/entity/ignis/ignis_idle_0.png">Cataclysm Ignis 原PNG</a>：最近邻查看甲面色区、暗连接和兵器分工，落实到兵煞残甲的上层残漆、下层接触甲面和刀刃。沿用上轮看过的<a href="https://media.forgecdn.net/attachments/510/182/2022-10-30_21.png">Ignis作者展示</a>主次观察，宣传光照不作为基础贴图反射依据。</p><p>仅研究材质组织，没有复制外部像素、纹章、UV、模型或动画。本轮未声称研究未核实的整合包角色。</p></details></section></main><script>
document.querySelectorAll('[data-target]').forEach(button=>button.addEventListener('click',()=>{let img=document.getElementById(button.dataset.target);img.src=button.dataset.src;img.parentElement.href=button.dataset.src;button.parentElement.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)))}));
</script></html>'''
(D/'index.html').write_text(s)
sheet=Image.new('RGB',(1800,1520))
for i,id in enumerate(p.TARGETS):sheet.paste(Image.open(D/id/'comparison-lit.png'),(0,i*760))
sheet.save(D/'two-comparisons.png')
print('Gallery ready: 18 current hashed native receipts, 13 complete clips')
