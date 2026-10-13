"""Single-Boss v8 foot-support delivery with matched-scale and native evidence."""
from proportions import *
import html,shutil
native=D/'native/rebel-foot-v8-1';assert (native/'PASS.txt').exists()
records=[]
for f in sorted(native.glob('*-state.json')):
 r=json.loads(f.read_text());assert r['entity']==ID
 for rel,digest in r['loadedResourceSha256'].items():assert hashlib.sha256((R/'src/main/resources'/rel).read_bytes()).hexdigest()==digest
 image=next(native.glob(f.stem[:2]+'-'+ID+'-*.png'));records.append({'stage':r['stage'],'age':r['age'],'image':str(image.relative_to(D)),'receipt':str(f.relative_to(D))})
assert len(records)==8
old=D/'native-before';old.mkdir(exist_ok=True)
for f in ['00-rebel_general-front.png','02-rebel_general-side.png']:shutil.copy2(R/'docs/art/boss-proportions-v7/native/rebel-proportion-1'/f,old/f)
report=json.loads((D/'validation.json').read_text());report.update(nativeStates=records,native='8 production-rendered states with current hashes',build='PASS',baseCommit='2f64b213',scope='Shrink existing feet and support links only; approved v7 upper-body geometry and forward stance, blade, rig, UV, PNG and gameplay preserved',limits=['Controlled test world, not natural encounter or multiplayer acceptance.','Existing cast clip remains a resource-only review; production controller does not assign it to a specific spell.'])
(D/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def fig(path,title):return f'<figure><a href="{path}" target="_blank"><img loading="lazy" src="{path}" alt="{html.escape(title)}"></a><figcaption>{html.escape(title)}</figcaption></figure>'
s='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>兵煞残甲 · 脚部比例 v8</title><style>body{background:#eeefea;color:#283536;font:17px/1.7 system-ui;margin:0}main{max-width:1480px;margin:auto;padding:28px}h1{margin:.3em 0}section{background:#fff;border:1px solid #d5ddd7;border-radius:10px;padding:24px;margin:24px 0}a{color:#285d62}img{display:block;width:100%;height:auto;image-rendering:pixelated}figure{margin:16px 0}figcaption,small{color:#556562}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}summary{cursor:pointer;padding:16px 0;font-weight:600}details{border-top:1px solid #d5ddd7}.native img{image-rendering:auto}table{border-collapse:collapse;width:100%}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}@media(max-width:700px){.grid{grid-template-columns:1fr}main,section{padding:16px}}</style><main><small>DYNASTY / FORGE 1.20.1 / 兵煞残甲 v8</small><h1>缩脚、减厚，保留巨臂与前压体量</h1><p>上一版脚掌仍像厚底座，邻接腿甲也偏重。本轮只收紧原有腿脚块体，保留已认可的上躯壳、巨臂、头部、刀与12°前倾姿态。</p><section><h2>同相机、同尺度前后对照</h2><p>左：v7；右：v8。双方使用相同玩家和1米石砖参照，未分别缩放画面。</p>'''
s+=fig('comparison-45.png','45° / 软件逐面真实PNG预览')+fig('comparison-front.png','正面 / 软件逐面真实PNG预览')+fig('comparison-side.png','侧面 / 软件逐面真实PNG预览')
s+='<details><summary>背面与纯黑剪影</summary>'+fig('comparison-back.png','背面 / 同尺度')+'<div class="grid">'+fig(ID+'/before-silhouette.png','调整前剪影')+fig(ID+'/after-silhouette.png','调整后剪影')+'</div></details><table><tr><th>部位</th><th>本轮调整</th></tr><tr><td>上躯壳</td><td>沿用v7，几何与位置未改</td></tr><tr><td>头盔主体</td><td>沿用v7，几何与位置未改</td></tr><tr><td>脚掌</td><td>12×5×16 → 10×3×11（宽×厚×长）；厚度−40%，前后长度−31%，体积−66%</td></tr><tr><td>上身重心</td><td>沿用v7前压12°，未再次变更</td></tr><tr><td>刀</td><td>全部刀部尺寸、位置、形状、UV与PNG保持v7</td></tr></table></section>'
s+='<details><summary>腿脚近景与完整同机位动作对照</summary>'+''.join(fig('feet-comparison-'+n+'.png','腿甲—脚踝—脚掌 / '+n+' / 软件同尺度') for n in ['front','45','side'])+fig('comparison-walk-full.webp','完整移动前后对照 / 左v7、右v8 / 软件')+fig('comparison-attack-full.webp','完整攻击前后对照 / 左v7、右v8 / 软件')+'</details>'
s+='<section class="native"><h2>真实Minecraft截图</h2><p>正式实体与Renderer，普通光照，无额外粒子。下列旧/新截图采用同一套测试场景与相机。</p><div class="grid">'
for tag in ['00-rebel_general-front.png','02-rebel_general-side.png']:
 s+=fig('native-before/'+tag,'调整前 v7 / 实机')+fig('native/rebel-foot-v8-1/'+tag,'调整后 v8 / 实机')
s+='</div><details><summary>45°、背面、移动、蓄势、接触、恢复</summary><div class="grid">'+''.join(fig(r['image'],f'{r["stage"]} / {r["age"]} tick / 实机') for i,r in enumerate(records) if i not in [0,2])+'</div></details></section>'
s+='<section><h2>六段完整原动作</h2><p>保留原动作名称、时长、攻击12 tick接触与全部旋转通道。只有死亡动画原有的根骨位移值根据收紧后的支撑重新贴地，时间键未变。下列WebP为完整离线回放，固定镜头。</p>'
for clip,record in json.loads((D/ID/'motion-review.json').read_text()).items():
 s+='<details><summary>'+clip+f' / {record["durationSeconds"]}秒</summary><div class="grid">'+fig(ID+'/'+clip+'-full.webp','完整离线回放')+fig(ID+'/'+clip+'-phases.png','分阶段取样')+f'</div><a href="{ID}/{clip}-filmstrip.png">全部40帧</a></details>'
s+='<details><summary>原色、灰度、UV与玩家观察距离</summary><div class="grid">'+''.join(fig(ID+'/'+f+'.png',f+' / 软件检查') for f in ['front-unlit','45-unlit','front-gray','45-gray','texture-4x','uv-direction','uv-side','distance-10m','distance-18m','distance-28m'])+'</div></details></section>'
s+='''<section><h2>验证</h2><p>构建通过；8个实机状态核对当前资源哈希；重复导出字节一致。骨骼名称、父子关系和方块数量保持，未新增Boss。贴图与UV保持v6字节/数据一致，刀的尺寸与局部形状一致。已核对所有非support骨骼数据与v7完全一致。其他角色、碰撞、技能和伤害未改。</p><p>自然遭遇与多人战斗未追加测试；cast仍是未绑定具体生产法术的既有资源片段。</p><p><a href="results.json">结果与实机记录</a> · <a href="validation.json">几何、刀与动画检查</a> · <a href="idempotence.json">重复导出检查</a> · <a href="build-result.log">构建记录</a></p></section></main></html>'''
(D/'index.html').write_text(s)
print('v8 gallery ready, 8 hashed native states')
