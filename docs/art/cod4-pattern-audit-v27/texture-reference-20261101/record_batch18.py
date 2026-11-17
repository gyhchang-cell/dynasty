"""Actual archery source observations; animation/state files are not new weapons."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-18-candidates.json').read_text())['rows']
groups=[
 (612,615,'archery-dark-open-frame-red-hub',612,'黑色粗弓臂、暗红连接片与少数正红亮块，弓弦保持一条细黑阶梯线，内孔仍大。'),
 (619,622,'archery-stepped-bone-endplates',619,'骨灰弓臂两端用大锯齿/凸片，灰中握把和更暗细弦分开；只用少数骨白明暗宽块。'),
 (626,637,'archery-segmented-ember-limbs',626,'凤凰弓的橙黄亮块沿弓臂分段，灰握点与深暗弦留对比；经典版更平直，配色/旧版不另计。'),
 (638,645,'archery-forked-ice-crossbow',638,'浅蓝叉形弩臂、深蓝外缘与少数白色转折，深色内孔很大；箭、烟花和两类彩弹只是同弩载荷状态。'),
 (647,650,'archery-wide-limb-stud-tips',647,'青黑较宽弓臂，木褐握把，两个端头各只一个绿白方亮点；细黑弦不与亮端争主次。'),
 (651,658,'archery-layered-ice-limbs',651,'冰蓝弓臂在clear图，棕握把/黑弦和箭轴在solid图；实际四个model JSON均同时引用layer0/1，是同一把弓的两层。'),
 (659,662,'archery-leaf-limbs-red-binding',659,'深浅绿大叶片式弓臂、中央少量红色绑点和细暗弦，末端只伸少量短枝；大亮绿片不铺满内孔。'),
 (663,666,'archery-violet-limbs-gold-hub',663,'暗紫大段弓臂配少量浅紫面，金黄只集中握点；后拉图的三根棕箭轴可分别读出，不是三把新弓。'),
 (667,673,'archery-cool-plates-gray-string',667,'蓝灰/浅紫大板片弓臂、灰绿细弦，special图更换青色箭头；满蓄special两帧只改箭尖折角，mcmeta开启插值。'),
 (674,677,'archery-segmented-ember-limbs',626,'天境扩展资源包里的凤凰弓仍是同一橙黄分段弓臂和灰握点；资源包覆写不作为新增弓族。'),
 (678,679,'archery-gold-frame-bluegreen-islands',678,'128px整图实际只有少数金褐框件、蓝灰竖岛及青色幽影长条；已打开完整x4图。item父级为builtin/entity且不直接声明texture，不能把小岛当库存平面弓。'),
 (681,684,'archery-wide-limb-stud-tips',647,'棕黑弓臂、中央橙褐绑带、端部青黑座各一点绿，弦为灰白阶梯；保守与647的端点亮块组织合并，不声称纯换色。'),
 (685,691,'archery-violet-curled-limb-bright-state',685,'暗紫卷折臂与中央红方点有大块层次；后续状态加橙红弦/箭，full图黄红亮块占据大片内孔，作为过亮反例保留，不当当前制作范本。'),
 (692,695,'archery-dark-metal-gold-fittings',692,'暗棕紫弓身、灰握点和几个金黄横扣，弦为浅米白，读材质不靠全边描亮；已命中旧参考索引，后续单列历史排重。'),
 (696,701,'archery-hooked-brass-crossbow',696,'18px弩以金褐宽折面、两端弯钩与灰弦组织，箭/烟花为同弩载荷；保留18px原尺寸不压16。'),
]
arrows={
611:'暗箭杆配宽金褐铲状箭头，黑色尾羽有大缺口；只作箭头/羽尾分区观察，不适用学院身份。',
616:'暗红杆上几段粉红亮块，箭尾和头部用较大粉红角；不能据此断言游戏发光/追踪。',
617:'木褐箭杆、白灰箭头与青绿宽羽尾，三材有明确色区；不是新的学院翎纹。',
618:'浅灰骨杆、黑灰尖头与白色尾端，用极少色阶；基础箭形不充新纹样。',
623:'木杆/白头/绿尾周围另画几颗亮绿点，这些是源PNG中实际像素，不等同运行时粒子。',
624:'木杆、宽骨白箭头与蓝色三角尾羽分区；仍是通用箭形材料观察。',
625:'深灰箭头、棕杆与较大的棕灰羽尾，羽区以几块硬边面表示，不借密噪点。',
646:'蓝紫细杆配较宽蓝头与浅蓝尾点，杆与尖颜色接近；通用元素箭不加案例。',
680:'棕杆配宽紫箭头与金黄短尾，亮色只集中两端；元素换色不建立学院或帝王身份。',
}
representatives=set()
for r in rows:
 n=int(r['reference_id'].split('-')[1])
 if n in arrows:
  r.update(semantic_family='EXCLUDE_GENERIC_PROJECTILE_CONTEXT',scope='pattern_context',distinct_family_proposed_credit=0,
   observation_zh=arrows[n])
 else:
  lo,hi,family,rep,note=next(g for g in groups if g[0]<=n<=g[1])
  credit=1 if n==rep and rep not in representatives else 0
  representatives.add(rep)
  context=''
  path=r['path']
  if 'pulling' in path:context='这是同族后拉/满蓄源状态，形变与箭轴变化不拆新武器。'
  if 'classic_' in path:context+='内置经典皮肤只保留版本观察，不新增装备。'
  if n in [687,691]:context+='该16px icon未在本次18个JSON声明链中找到直接引用，实际选用分支未核；不推定未使用。'
  r.update(semantic_family=family,family_representative=f'VIS-{rep:03}',scope='equipment_material',
   distinct_family_proposed_credit=credit,observation_zh=note+context)
 r.update(status='VISUALLY_REVIEWED_SOURCE_CONTEXT_ONLY',
  limitation='同族状态、层、载荷和经典覆写合并；材料/轮廓观察不等于当前逐星/风翎身份设计、完整UV或游戏验收。历史语义排重仍需继续。',
  applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0)
 if n in [678,679]:r['inspected_detail_view']='build/art-reference-20261101/batch18-binding/cursed-full-atlases.png'
 if n==673:r['inspected_detail_view']='build/art-reference-20261101/batch18-binding/storm-source-frames.png'
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),
 proposed_distinct_design_families=sum(r['distinct_family_proposed_credit'] for r in rows),
 coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='Eight source sheets plus full128px atlases and both storm frames opened. Thirteen conservative material/composition families, not91 independent bows; all reference gates remain unmet.',rows=rows)
(D/'review-batch-18.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
review=dict(recorded_at=out['recorded_at'],source_sheets_actually_opened=8,
 supplemental_sheets_actually_opened=['build/art-reference-20261101/batch18-binding/cursed-full-atlases.png','build/art-reference-20261101/batch18-binding/storm-source-frames.png'],
 model_jsons_read=18,source_animation_tiles_opened=2,new_design_credit=0,production_changes=0,
 findings_zh=[
 '暮色冰弓4个model均是solid layer0与clear layer1；8PNG为4状态2层，不能判单层缺图或算8把弓。',
 '风暴弓普通/enchanted特殊predicate声明与三段拉弓分开，满蓄special含2源帧且interpolate=true；未验代码条件注册或游戏中插值。',
 '灾变弓128px PNG是分散UV图集；item JSON走builtin/entity、无textures字段。此处不读Java，不声称已绑定实际renderer或完整体块。',
 '启示录base_bow直接继承item/generated，有左右手display变换；声明链引用24px源图和pull阈值0.361/0.5/3.5。两张16px icon未在这个JSON链引用，不能据同名猜GUI自动使用。',
 '普通/经典/扩展凤凰弓按同装备合并；深棕绿端猎弓与青黑绿端末影弓保守并材料族。',
 '旧索引中dark_netherite_bow已存在，排重不以PNG换包/另一个来源路径算新。'],
 limits='原图/声明链核看，不是运行时谓词、渲染器、shader、资源包优先级或目标身份验收。')
(D/'batch18-resource-manual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
