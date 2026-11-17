"""Package and verify this bounded review, without touching production assets."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, html, json
from PIL import Image

D=Path(__file__).resolve().parent
R=D.parents[3]
j=json.loads((D/'receipt.json').read_text())
samples=json.loads((D/'joint-samples.json').read_text())
contexts=[]
for root,filename,observations in [
 ('build/creature-reference-1000/Polarice3__Goety-2',
  'src/main/java/com/Polarice3/Goety/client/render/model/ArmoredIllagerModel.java',[
   'Arms remain single 4x12x4 cubes under body; compound root/body transforms are applied by translateToHand.',
   'Attack/spell/bow/crossbow states choose distinct arm poses instead of adding elbow/hand geometry for every pose.',
   'resetPose precedes pose assignment. Geometry includes crossed-arm alternative; raw declared cubes are not the visible per-frame set.'
  ]),
 ('build/bestiary-v43/references/Infamous-Misadventures__Dungeons-Mobs',
  'src/main/java/com/infamous/dungeons_mobs/client/models/illager/IllagerBipedModel.java',[
   'Starts from HumanoidModel.createMesh, retains single-cube arms/legs and layers a jacket over body.',
   'prepareMobModel maps MAIN/OFF_HAND through getMainArm before selecting BLOCK/BOW/CROSSBOW poses.',
   'setupAnim hides crossed-arm alternative or separate arms; jacket is hidden when chest/leg equipment occupies it. Runtime visibility is not mesh-budget deletion.'
  ])]:
 rootp=R/root; meta=json.loads((rootp/'source.json').read_text());p=rootp/filename
 contexts.append({'repo':meta['repo'],'commit':meta['sha'],'branch':meta['branch'],
  'source_url':f"https://github.com/{meta['repo']}/blob/{meta['sha']}/{filename}",
  'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
  'read_scope':'Entire model Java file read in this batch; source context only. No actual atlas or complete renderer reconstruction.',
  'observations':observations,'new_gate_credit':0,
  'dedup_boundary':'Existing cached family; not counted as a new creature or a distinct reference for each state.'})
(D/'reference-contexts.json').write_text(json.dumps({'contexts':contexts,'accepted_new_credit':0,
 'application':'Basis for future gated body/pose design; no source or external artwork copied into Dynasty.'},ensure_ascii=False,indent=2)+'\n')

checks=[]
def check(name,condition):
 checks.append({'check':name,'pass':bool(condition)})
check('all captured production/source inputs still byte equal',all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in j['input_sha256'].items()))
check('two actors / six explicit comparison candidates',len(j['entities'])==2 and len(j['baselines'])==6)
check('all declared face partitions conserve totals',all(sum(e['quad_partition'].values())==e['all_embedded_quads'] for e in j['entities']))
check('reference contexts add zero gate credit',all(c['new_gate_credit']==0 for c in contexts))
check('all clip sample records accounted for',len(samples)==sum(c['samples'] for e in j['entities'] for c in e['clips']))
animations=[]
for e in j['entities']:
 check(e['id']+' no skeleton-name/parent/cycle errors',not e['skeleton_errors'] and not e['duplicate_bone_names'])
 check(e['id']+' all clip references valid',all(not c['missing_bones'] for c in e['clips']))
 for name in ('idle','wander','flee','special'):
  p=D/f"{e['id']}-{name}.webp"
  with Image.open(p) as im:
   animations.append({'file':p.name,'frames':im.n_frames,'size':list(im.size)})
   check(p.name+' animated',im.n_frames>1)
  with Image.open(D/f"{e['id']}-{name}-frames.png") as im:
   check(e['id']+name+' fixed camera filmstrip',im.size==(2000,1200))
assert all(c['pass'] for c in checks),checks
verification={'recorded_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,
 'status':'PASS_LOCAL_EVIDENCE_INTEGRITY_ONLY','pose_samples':len(samples),
 'animations':animations,'game_java_native_bake':False,'reference_credit':0}
(D/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')

rows=''.join(f"<tr><td>{e['id']}</td><td>{e['quad_partition']['anatomy']}</td><td>{e['quad_partition']['garment']+e['quad_partition']['headwear']}</td><td>{e['quad_partition']['back_attachment']}</td><td>{e['quad_partition']['held_attachment']}</td><td>{e['body_and_worn_quads']}</td><td>{e['all_embedded_quads']}</td></tr>" for e in j['entities'])
base=''.join(f"<tr><td>{b['id']}</td><td>{b['all_embedded_quads']}</td><td>{b['held_embedded_quads']}</td><td>{b['carried_embedded_quads']}</td><td>{b['body_and_worn_quads']}</td></tr>" for b in j['baselines'])
motion=''
for e in j['entities']:
 ident=e['id'];motion+=f'<h2>{ident}：现有身体与关节</h2>'
 for name,label in [('idle','待机'),('wander','行走'),('flee','逃跑'),('special','现有特殊动作')]:
  motion+=f'<details><summary>{label} · 完整离线线框回放</summary><img src="{ident}-{name}.webp" alt="{ident} {name} 身体线框动作"><p><a href="{ident}-{name}-frames.png">同尺度四阶段展开图</a></p></details>'
refs=''.join('<li><a href="'+html.escape(c['source_url'])+'">'+html.escape(c['repo'])+'</a> · '+html.escape(c['commit'][:12])+': <ul>'+''.join('<li>'+html.escape(o)+'</li>' for o in c['observations'])+'</ul></li>' for c in contexts)
doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>两个人物身体与关节核查 · 2026-11-02</title>
<style>body{margin:40px auto;max-width:1160px;padding:0 22px;background:#eeeae0;color:#29373c;font:17px/1.7 system-ui,sans-serif}h1,h2{line-height:1.3}table{border-collapse:collapse;width:100%;background:#faf8f2}td,th{padding:10px;text-align:left;border-bottom:1px solid #c7cbc4}img{max-width:100%;height:auto}details{margin:16px 0;padding:12px;background:#faf8f2}a{color:#2e6876}.notice{padding:18px;border-left:4px solid #ad7840;background:#f6f1e5}code{font-size:.9em}</style>
<h1>身体预算与动态关节：本批可复核结果</h1>
<p class="notice">只读现有资源，未修改任何身体、动作、贴图、挂件或Java。没有启动游戏；以下均为离线诊断，不是新模型成品，也不是实机验收。</p>
<p>这批新增的是<strong>按职责分项计数、对照双方挂件口径、38段动作的2,322次姿态采样</strong>，不把旧192/180面计数再包装成新修复。所有原嵌入物仍在运行资源内，拆分只是账目分类。</p>
<h2>两个现有角色：面数分区</h2><table><tr><th>ID</th><th>解剖身体</th><th>服制/头饰</th><th>背负物</th><th>手持物</th><th>身体+服制</th><th>完整模型</th></tr>'''+rows+'''</table>
<p>每只解剖身体19个Cuboid，共114个声明四边面；腕、膝等空骨骼不增加几何面。是否把头饰列入附件不会改变完整模型总预算。</p>
<h2>基础怪必须使用相同口径</h2><table><tr><th>候选</th><th>完整模型</th><th>内嵌手持</th><th>背负配件</th><th>身体+服制</th></tr>'''+base+'''</table>
<p>卒伍刀手156面里有60面内嵌武器，扣去后的同口径是96面；不能把骗子156面身体服制与刀手156面完整模型对比后宣布达标。采药客138面与长枪兵同口径相等，也不等于它获得了唯一、同职业的预算基准。原要求还包含同屏20只性能实测，仍未验。</p>
<h2>关节与动作判断</h2><ul>
<li>两只未发现重名骨骼、缺父骨、父子环或38段动作引用缺失骨骼。检查涵盖每段动作起止与中间采样，不是只看0 tick。</li>
<li>肩部有直接轨道，右肘在attack/special中动作；前臂、腕、手跟随父级。没有独立手腕轨道不能推断为手不动。</li>
<li>共享表面点的变换差最大约3.6×10⁻¹⁵模型单位；这只验证特定接缝点的变换连续性，不能证明整块表面无穿插。</li>
<li>逃跑数学样本中脚底最低约-0.356、最高约+0.694模型单位（名义约-0.022／+0.043格）。需实际根变换、地面与原生播放复核，不能直接定性为游戏穿地或悬浮。</li>
<li>骗子special使用抬臂/伸臂的模板动作，源码在未识破时持续选择special；是否读成“假装受伤”尚待身份动作验收。未擅自修改状态或动作时间。</li>
<li>身体现在是分段19块构造，不是标准Steve六主体块；这是与后续人形方向的差异，不是本轮授权重做已认可资产。</li>
</ul>'''+motion+'''<h2>实际补读的制作方法</h2><p>两份既有缓存模型源码完整补读，只作为关节／姿态实现上下文。未查看本轮对应原始图集，不计新“模型+贴图”参考；既有家族不按动作状态重复计数，新增1000门槛信用为0。</p><ul>'''+refs+'''</ul>
<h2>具体资源与未验范围</h2><p>读取的两只实体资源为 <code>geo/secondary/{swindler,herb_picker}.geo.json</code> 与对应 <code>animations/secondary/*.animation.json</code>；仍由 ExpansionClient Geo 渲染链加载，未切换到 SteveFighterRenderer。具体22个输入路径与SHA256见收据。</p>
<p>尚未验证：GeckoLib控制器混合、原生插值/根变换、实际遮挡/穿插/触地、完整持物、替换挂件、同屏20只性能和游戏身份动作效果。适用1000条语义不同参考未达，不新增修复、不删清单。</p>
<p><a href="receipt.json">完整收据及输入哈希</a> · <a href="joint-samples.json">逐姿态样本</a> · <a href="reference-contexts.json">固定来源和观察</a> · <a href="verification.json">本地证据完整性检查</a> · <a href="review_body_joints.py">复核脚本</a></p></html>'''
(D/'index.html').write_text(doc)
print(json.dumps({'checks_passed':len(checks),'pose_samples':len(samples),'animated_previews':len(animations),
 'input_files_byte_equal':len(j['input_sha256']),'production_changes':0,'new_reference_credit':0},ensure_ascii=False))
