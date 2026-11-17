"""Record selected body support studies. Never writes production or master lists."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[4]
O = Path(__file__).resolve().parent
B = R/'docs/art/bestiary-v43'
A = R/'build/creature-reference-1000/AlexModGuy__AlexsMobs/src/main/java/com/github/alexthe666/alexsmobs'
M = R/'build/creature-reference-1000/BobMowzie__MowziesMobs-Public/src/main/java/com/bobmowzie/mowziesmobs'
N = R/'build/bestiary-v43/references/native-damage-1.20.1/net/minecraft'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p): return dict(path=str(p),sha256=sha(p))
def put(n,d): (O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

baseline_path=B/'suanni-death-intent-review-20261110/review.json'
baseline=json.loads(baseline_path.read_text())
for p,h in baseline['production_hashes'].items(): assert sha(p)==h, 'Current measured asset changed.'
legacy_path=R/'docs/art/creature-mc-v35/reference-ledger.json'
legacy=json.loads(legacy_path.read_text())
prior=B/'suanni-death-reference-scope-20261110'
prior_scope=json.loads((prior/'applicability.json').read_text())

def sources(name, model_scope, entity_scope):
 return [dict(ev(A/f'client/model/Model{name}.java'),read_scope=model_scope),
         dict(ev(A/f'entity/Entity{name}.java'),read_scope=entity_scope),
         dict(ev(O/f'sources/Render{name}.java'),read_scope='固定上游提交下载，完整renderer文件已读；层类未另行全读')]

studies=[
 dict(identity='AlexsMobs:Crocodile',
  sources=sources('Crocodile','模型构造/父子层级1–160、完整animate160–193、完整setupAnim194–284、render/getparts尾部；无专用死亡分支',
   '继承TamableAnimal；88–105、145–169、213–362选定低伏/抓咬/DEATHROLL与动画推进；501–518坐姿；动画列表只有LUNGE/DEATHROLL；未读完整繁殖AI'),
  finding='DEATHROLL是活体在水中抓住乘客目标后的攻击，非死亡。低伏来自陆地坐姿baskingProgress十步升降；身体下移同时四肢反向位置补偿，前后肢外展与手足反旋；尾部和颈部左右偏转。',
  head_jaw='头部晒背上仰、jaw反向张开；setup末尾jaw.rotateAngleX=-head.rotateAngleX覆盖先前局部颚角，不能把早先jaw关键帧或局部角直接认作最终世界嘴部姿态。没有头颚求地面约束。',
  support='body源Y+3、四肢局部Y-3先抵消躯干平移，但肢体旋转仍改变端点；它是手工姿态补偿，不是斜坡IK或头部自动接地。',
  state_limit='新构造random.nextInt(1)只产生0；源码虽有baskingType1镜像分支，不能算自然随机第二机制。NBT可保存/读取BaskingStyle。',
  renderer='0.9等比缩放，无getFlipDegrees/setupRotations覆盖；王冠层重画同骨架，不是第二个身体机制。',
  reload='坐姿、样式、晒背/游泳计时、眩晕标志存NBT，进度字段不是此类显式保存内容；非死亡连续性证明。',
  qualification='RELATED_LIVE_LOW_POSTURE_ONLY; DEATHROLL_EXCLUDED_FROM_DEATH_REFERENCE_CREDIT'),
 dict(identity='AlexsMobs:KomodoDragon',
  sources=sources('KomodoDragon','全236行模型；局部低伏/坐姿、角力、步态/头颈反向摆动、幼体渲染',
   '声明继承TamableAnimal；180–279保存/坐姿进度/角力状态；全类检索无tickDeath/die；非整段角力AI研究'),
  finding='坐姿5tick进度：躯干俯仰，后肢外展、前肢与局部高度协同，头部反向俯仰；角力是另一活体层，不能改称死亡。',
  head_jaw='head只有吻部整体和tongue，没有独立jaw骨骼。因此不能作为“已实现头颚落地”的直接案例。',
  support='肩/髋分组接四肢，低姿态的body、四肢各自偏移且叠步态；无世界地面采样器，未定量证明贴地。',
  renderer='无整体scale和死亡翻转覆盖；鞍/女仆层复用同模型加膨胀并再次setupAnim，不按层算不同机制，物件不制作。',
  reload='保存KomodoCommand/Saddle/JostlingCooldown/SpitTime；sitProgress从命令/坐姿重建，不声称保存完整瞬时姿态。',
  qualification='RELATED_LIVE_SITTING_ONLY; NO_ARTICULATED_JAW_OR_CUSTOM_DEATH'),
 dict(identity='AlexsMobs:Elephant',
  sources=sources('Elephant','1–147身体/腿/头/象鼻构造；147–155动画入口reset；325–394完整setupAnim与末尾方法；未声称七段攻击全部重读',
   '声明继承TamableAnimal；262–299坐/立进度互斥；597–608动画枚举；647–663及681–706选定坐立保存读取；748–764坐立同步方法；无tickDeath/die覆盖'),
  finding='坐下时body大幅下降，四腿分向折叠并局部平移，头部反向抬升、两节象鼻折叠；坐姿5tick、立姿0.5步长到5，实体禁止坐与立同时持续。',
  head_jaw='没有独立jaw，头/鼻局部抬升为避免整体降体后埋入；不是要求兽首砸地的同一策略。',
  support='四腿同属body支链而头/鼻分层；大幅body下降必须由各子链协调。最终setup还叠耳、头鼻idle、腿walk、body bob与faceTarget，不能只看坐姿角度。',
  renderer='成年长牙分支1.1等比缩放；无getFlipDegrees/setupRotations覆盖；物件层不是新身体。',
  reload='坐立标志存取；所读保存段不保存坐立插值进度。不把离线坐姿或历史静态图当实机死亡。',
  qualification='RELATED_LIVE_FOLDING_SUPPORT_ONLY; NO_JAW_OR_CUSTOM_DEATH')
]
for s in studies:
 assert legacy[s['identity']]['accepted']
 name=s['identity'].split(':')[1]
 card=R/f'build/creature-reference-1000/cards/AlexsMobs-Model{name}.png'
 s.update(revision='09755dade2cfbdf14839e026d3af446f9d3ff843',historical_static_approval_retained=True,
          viewed_static_card=ev(card),visual_scope='实际查看了灰模绑定姿态45度/侧面图；不是带贴图动画或游戏截图',
          new_death_policy_credit=0,new_accepted_reference_credit=0)
put('quadruped-studies.json', studies)

put('shared-death-chain.json', {
 'sources':[dict(ev(N/'world/entity/LivingEntity.java'),scope='540–558死亡计时，沿用既有可核原版源档'),
            dict(ev(N/'client/renderer/entity/LivingEntityRenderer.java'),scope='170–231完整所选setupRotations与getFlipDegrees'),
            ev(O/'vanilla-inheritance.json')],
 'method':'TamableAnimal→Animal→AgeableMob→PathfinderMob→Mob→LivingEntity。逐层检查声明和死亡覆盖；TamableAnimal.die188–197读到先super.die再死亡通知，没有新死亡时长。三目标全类检索未自定义tickDeath/die；三renderer无死亡翻转覆盖。',
 'timer':'按这些声明链，LivingEntity deathTime>=20在服务器移除。渲染f=sqrt((deathTime+partial-1)/20*1.6)夹至1，再乘默认90度侧翻；不是兽首追地求解。',
 'dedup':'三物种共享同一原版死亡机制，仅作为一条已存在的框架链，不新增三项death信用。此前原生死亡框架收据继续有效。',
 'limit':'本次研究声明继承链，不声称全整合包Mixin/全局事件/原版运行结果已复验；未运行任何Java/游戏。'
})

foliaath={
 'identity':'MowziesMobs-Public:Foliaath', 'revision':'7aa17309337cbd4102efc418cba12a4983b1540c',
 'sources':[dict(ev(M/'client/model/entity/ModelFoliaath.java'),scope='父链167–210检索、210–335完整独立render/default层、384–末尾完整死亡分支'),
            dict(ev(M/'server/entity/foliaath/EntityFoliaath.java'),scope='50tick死亡常量、130–164及226–279死亡控制器/触发、338–359保存读取'),
            dict(ev(M/'client/render/entity/RenderFoliaath.java'),scope='全文件'),
            dict(ev(M/'client/model/tools/ControlledAnimation.java'),scope='75–145进度增减、185–225正弦/幂进度；非全文')],
 'shared_parent_reuse':ev(prior/'frostmaw-death-study.json'),
 'body':'stem1Joint→stem1Base→stem2→stem3→stem4→headBase，上下口部各有两级骨骼。固定根茎不侧翻，死亡先反曲/张口，再链式头茎失重、两步反弹，叶/舌跟随。与四肢撑地不是同一机制。',
 'phases_ticks':[4,10,5,2,2,27], 'clip_ticks':50, 'server_removal_threshold_ticks':30,
 'phase_reading':'0–4反曲，4–14保持，14–19坍塌，19–21及21–23两步回弹，23–50保持；共享Mowzie父类duration-20使服务器30tick移除，不能称50tick都可见。',
 'additive_caveat':'同一关键帧多次rotate(stem1Base/stem2等)会累加，不能把末条当覆盖值；MMModelAnimator相对变换/正弦插值已在上批完整读取，不重复计数。',
 'controllers':'deathFlail前12tick增加至上限5，之后下降；stopDance增加到10，压掉活体摆动；死亡强制activateTarget30。activate渐变仍影响renderToBuffer的整体scale/translate，不能忽略后仅测headBase本地角度。',
 'renderer':'getFlipDegrees0；模型的地叶与头茎分开render，头茎受activeProgress缩放和1.4*(1-activeProgress)平移。不是原版整体90度侧翻。',
 'reload':'所选自定义NBT仅canDespawn；共享父spawn动画tick同步不是世界重载死亡恢复认证。',
 'transfer':'借鉴根部保持、头茎链放松后小幅回弹与停止活体摆动；不移植植物形态或关键帧，也不替代狻猊最终几何接地计算。',
 'qualification':'ONE_RELATED_DEATH_POLICY_SOURCE_STUDIED; NOT_HEAD_GROUND_CERTIFIED',
 'dedup':'共享Mowzie父类与插值器不再计数，四条茎、两口部、叶舌和阶段不拆为独立实现；旧静态同identity认可保留。',
 'new_accepted_reference_credit':0
}
assert legacy[foliaath['identity']]['accepted']
assert sum(foliaath['phases_ticks'])==50 and foliaath['server_removal_threshold_ticks']==50-20
put('foliaath-death-study.json',foliaath)

put('applicability.json', {
 'target':'dynasty:zhenmu_suanni_tonghou', 'scope_authority_reused':ev(prior/'applicability.json'),
 'historical_per_creature_required':100, 'current_new_fix_required':1000,
 'historical_static_accepted_preserved':1000,
 'historical_target100s_preserved':prior_scope['historical_target100s_preserved'],
 'this_batch_static_identities_mapped': [{'identity':s['identity'],'decision':'旧静态范围继续有效；活体低姿态可借鉴，不是独立死亡头颚接地参考'} for s in studies]+[{'identity':foliaath['identity'],'decision':'旧静态认可保留；新增完整选定死亡头茎控制研究候选，未独立验收'}],
 'related_custom_death_policy_studies_accumulated':5, 'new_custom_death_policy_study_this_batch':1,
 'related_non_death_posture_studies_this_batch':3,
 'mapped_accepted_for_current_fix':0, 'mapped_register_shortfall':1000,
 'global_applicable_accepted_total':None, 'global_final_gap':None,
 'count_limit':'登记缺口不等于旧参考失效或实际必须另找1000。全历史语义映射未结束；相关研究候选不自动升格为独立验收信用。',
 'new_accepted_reference_credit':0, 'production_before_gate':False,
 'unresolved':['完整旧库的真实适用映射与语义/继承去重','独立接受与实际头颚接地证明','符合隔离要求的原生自然死亡验证']
})
put('progress.json', {
 'status':'CONTINUING_SOURCE_RESEARCH_NOT_PRODUCTION_READY',
 'done':['鳄/蜥/象真实绑定姿态图查看','三条活体低姿态→实体进度→Renderer叠加阅读','三物种共享20tick/90度原版死亡链核实并去重','食人花50tick动画/30tick移除与头茎坍塌、叠加渲染完整选定流程'],
 'retained_previous_custom_death_studies':4,'new_custom_death_policy_candidates':1,'new_low_posture_studies':3,
 'new_accepted_credit':0,'production_modified':False,'game_or_java_started':False,
 'no_dense_resampling':True,'main_checklist_modified':False,'original_task_retained':True,
 'next_concrete':'继续核本地BetterAnimalsPlus鳄/犰狳等是否有不同的死亡/低姿态控制；如果同样仅原版侧翻则排除独立死亡信用。优先寻找明确头部父链高度补偿或最终模型接触约束的实现，不按物种数量补数。'
})
for p,h in baseline['production_hashes'].items(): assert sha(p)==h
put('handoff-metadata.json', {n:ev(O/n) for n in ['quadruped-studies.json','shared-death-chain.json','foliaath-death-study.json','applicability.json','progress.json','vanilla-inheritance.json','source-byte-verification.json','renderer-source-download.json','README.md','record.py']})
print(json.dumps(ev(O/'handoff-metadata.json'),ensure_ascii=False))
