"""Selected death-mechanism study and scope ledger; no production mutations."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[4]
O = Path(__file__).resolve().parent
B = R / 'docs/art/bestiary-v43'
L = R / 'build/creature-reference-1000/lender544__new1.20.1'
M = R / 'build/creature-reference-1000/BobMowzie__MowziesMobs-Public'
C = 'src/main/java/com/github/L_Ender/cataclysm/'
F = 'src/main/java/com/bobmowzie/mowziesmobs/'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p): return {'path': str(p), 'sha256': sha(p)}
def put(n, d): (O/n).write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n')

old_review = B/'suanni-death-intent-review-20261110/review.json'
old = json.loads(old_review.read_text())
for p, h in old['production_hashes'].items():
    assert sha(p) == h, 'Do not reuse measurements after input change.'

reconciliation_path = B/'reference-reconciliation-20261110/receipt.json'
reconciliation = json.loads(reconciliation_path.read_text())
qimen_path = B/'qimen-research-20261030/progress.json'
qimen = json.loads(qimen_path.read_text())
legacy_path = R/'docs/art/creature-mc-v35/reference-ledger.json'
legacy = json.loads(legacy_path.read_text())
assert qimen['human_per_creature_reference_gate'] == 100
assert legacy['new1.20.1:Ender_Golem_']['accepted']
assert legacy['new1.20.1:Netherite_Monstrosity_']['accepted']

scope = {
    'target': 'dynasty:zhenmu_suanni_tonghou',
    'repair': '最终已认可几何下，死亡头颚接地的最小动画/生成顺序修正',
    'authority_evidence': [ev(qimen_path), ev(reconciliation_path)],
    'authority_decision': '本聊天直接人类逐生物100个相似模型+贴图要求仍按原范围保留；用户本轮提供的较新AGENTS对新制作/修复要求适用1000处真实相关、语义不同实现。六工具1000不是body依据。当前修复按较新要求核清，不能靠另一目标旧100或静态1000直接放行。',
    'historical_static_accepted_preserved': 1000,
    'historical_target100s_preserved': reconciliation['actual_cumulative_state']['target_specific_historical_accepted'],
    'suanni_specific_100_acceptance_receipt_found_in_reconciled_target_ledgers': False,
    'current_fix_required': 1000,
    'current_fix_confirmed_mapped_accepted_in_this_review': 0,
    'mapped_register_shortfall': 1000,
    'shortfall_meaning': '这是当前明确映射且已验收登记的缺口，不是宣称全库1000条失效或实际必须再搜1000条；未逐项映射的旧参考可能补入。',
    'all_legacy_applicable_semantic_total': None,
    'all_legacy_final_gap': None,
    'selected_complete_death_policy_studies_accumulated': 4,
    'new_policy_studies_this_batch': 3,
    'new_accepted_reference_credit': 0,
    'no_production_before_gate': True,
    'remaining': ['旧静态/whole记录向当前死亡接地范围的语义映射', '跨类继承/同骨架同机制去重及独立接受', '头颚实际接地证明与软件/原生边界']
}
put('applicability.json', scope)

net_sources = [
    (L/(C+'client/model/entity/Netherite_Monstrosity_Model.java'), '1–85、94–155、264–结尾：构造/主要父链/腿及完整setupAnim，未称全模型所有炮臂几何均重读'),
    (L/(C+'entity/InternalAnimationMonster/IABossMonsters/NewNetherite_Monstrosity/Netherite_Monstrosity_Entity.java'), '385–505：状态同步、停止、死亡、60tick移除、保存读取；530–625：待机门控/头部服务器部件更新'),
    (L/(C+'entity/InternalAnimationMonster/Internal_Animation_Monster.java'), '1–83：同步攻击状态/计时复位/死亡调度'),
    (L/(C+'entity/InternalAnimationMonster/IABossMonsters/IABoss_monster.java'), '65–88及死亡相关方法检索：保存字段与父类继承，未称全部父类AI已读'),
    (L/(C+'client/render/entity/New_Netherite_Monstrosity_Renderer.java'), '全文件：纹理、缩放、死亡不翻转、部件裁剪'),
    (O/'sources/Netherite_Monstrosity_Animation.java', '1249–1401：完整DEATH定义；其他动画未读')
]
net = {
    'identity': 'new1.20.1:Netherite_Monstrosity_',
    'revision': '819937203e22b4fa72fdeccc6c56ad415d65eeef',
    'source_url': 'https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/client/animation/Netherite_Monstrosity_Animation.java',
    'sources_read': [dict(ev(p), scope=s) for p,s in net_sources],
    'upstream_verification': ev(O/'upstream-byte-verification.json'),
    'animation_download': '固定上游提交的原始源码，TLS curl成功下载到研究sources；不进入运行资源。',
    'whole_selected_policy': {
        'entry': 'die先调用父die，再setAttackState(5)；ATTACK_STATE同步更新停止其他显式状态并开始death状态，setAttackState同时复位attackTicks。',
        'life': 'DEATH长度2.5秒/50tick；deathtimer60；内部父类tickDeath经Animation_Monsters.onDeathUpdate先回调再递增deathTime，到60服务器移除。最后约10tick不能凭本源码宣称回默认姿态或继续循环，取决于原版animate非循环末帧采样。',
        'support': 'roots→lowerbody→upperbody→head→jaw，双腿是roots另一分支；上躯与头颚各有局部转动/位置，不能只移动整体。',
        'phases': '0–约21tick先颤动/抬头；约21–28tick屈腿、roots沉降与上躯/手臂调整；约28–40tick头颚下垂、躯干与臂部回弹/落定；余段不再设新关键帧。源码posVec值按原版轴转换，不能直接当作世界Y。',
        'jaw_head': 'head独立位置源值-3后回-2，末段三轴转动；jaw保留不对称张合/偏转，与上躯和root分开组织。并非目标相关的几何接地约束。',
        'interpolation': 'DEATH混用LINEAR与CATMULLROM；不采用狻猊线性采样器去冒充其真实曲线。',
        'overlays': '每帧reset后还有head look、walk、未觉醒sleep与多状态动画；idle显式仅state0且觉醒时激活。不能孤立看DEATH就宣称实际接地。',
        'server_head_part': 'setHeadPart对3/6/8状态有额外位移，未见5死亡分支；可见头动画与受击part位置不是同一套驱动，不迁移这种差异为狻猊新碰撞机制。',
        'reload': '所选实体保存Berserk/Awaken/Magazine，父类保存LifeRemain/Home；所选自定义保存路径未保存death AnimationState/attackTicks，不声称跨重载死亡连续性通过。',
        'transfer': '借鉴有支撑链的整体沉降、头颚局部落定和余段稳定；只用于理解限定修复，不抄角度/位移，也不加炮臂或改狻猊形态。'
    },
    'semantic_dedup': '与EnderGolem共享Animation_Monsters死亡移除底层，但同步状态触发、50/60生命周期和根/头颚/屈腿组织不同；记录一项相关死亡策略候选，不把每个骨骼/通道/文件单算。历史同identity已作静态研究，不重复增加静态数。',
    'acceptance': 'SOURCE_STUDIED_CANDIDATE; NOT_NATIVE_OR_HEAD_FLOOR_CERTIFIED',
    'new_accepted_credit': 0
}
put('netherite-monstrosity-death-study.json', net)

frost_scopes = {
 'client/model/entity/ModelFrostmaw.java': '535–553：默认姿态/地形腿解算后动画；1481–1565完整死亡分支；1565–结尾全部共用叠加；父子连接检索。未称其他攻击分支全读。',
 'server/entity/frostmaw/EntityFrostmaw.java': '死亡常量94tick；274–299地形腿解算门控；760–883完整受伤触发/死亡声回调/保存读取选定方法。',
 'server/entity/MowzieEntity.java': '438–473：死亡计时/服务器移除、延迟掉落和die，未读全实体AI。',
 'server/entity/MowzieLLibraryEntity.java': '全文件：动画推进、致命受伤触发、duration-20、出生数据同步。',
 'client/render/entity/RenderFrostmaw.java': '全文件：死亡flip0、mouth/hand socket读取；不制作水晶物件。',
 'client/model/entity/MowzieEntityModel.java': '全文件：animator.update和animate调用顺序。',
 'client/model/tools/MMModelAnimator.java': '全文件：相对变换、静态段保留、正弦插值和时间区间。',
 'client/model/tools/LegArticulator.java': '全文件：地形腿高平均值影响躯干/头颈与四肢。',
 'server/entity/LegSolver.java': '全文件：地形支撑形状距离、onGround缓变、缓存高度。仅本地SHA，本次未远端核验该文件。',
 'server/entity/LegSolverQuadruped.java': '全文件：四足前后左右采样位点；仅本地SHA，本次未远端核验该文件。'
}
frost = {
 'identity': 'BobMowzie/MowziesMobs-Public:Frostmaw',
 'revision': '7aa17309337cbd4102efc418cba12a4983b1540c',
 'revision_basis': '同仓库历史参考固定提交，另核对八个本地选定源码与该提交字节；不使用父Dynasty git HEAD作为上游提交。',
 'sources_read': [dict(ev(M/(F+p)), scope=s) for p,s in frost_scopes.items()],
 'upstream_verification': ev(O/'frostmaw-byte-verification.json'),
 'whole_selected_policy': {
  'entry': 'MowzieLLibraryEntity.hurt父受伤成功且health<=0发送死亡动画；Frostmaw受伤方法防止以觉醒动画覆盖已进入的death，并可设置active。其他死亡路径不从该分支推定。',
  'life': 'DIE_ANIMATION94tick；父getDeathDuration减20，MowzieEntity.tickDeath在deathTime>=74服务器移除。不是95tick关键帧累加或94tick动画时长全部可见。',
  'phase_durations_ticks': [4,2,5,22,3,12,7,40],
  'phase_cumulative_ticks': [4,6,11,33,36,48,55,95],
  'pose': '先腰/头与腿反向压缩，双臂屈伸；开颚长保持后，48–55tick侧倒，root侧滚并横移，胸与头反向调整，左右臂/腿非对称承接，余段保持。',
  'events': '死亡声条件animationTick5，落地声条件53，与侧倒段相邻；只读调用没有播放声，也不把声帧当几何触地证明。tickDeath先super，计时先后不可省略。',
  'layers': 'setupAnim先reset、地形腿Articulator、再animator；死亡分支之后仍执行活动态look/walk等，而idle明确排除death。未觉醒分支另叠侧卧呼吸；故孤立keyframe不足以证明平地/斜坡接地。',
  'interpolation': 'MMModelAnimator在每段内用sin(t*pi/2)权重插值，不是线性。静态段持有上段变换；relative add有顺序与上下游层影响。',
  'ground_solver': '腿解算取四个世界偏移的支撑VoxelShape高度，按onGround分支逐步变化；Articulator把前后均值转成躯干高度/倾斜并反向补偿neck。此为地形支撑，不是头颚地面约束。',
  'reload': 'spawn数据保存当前动画索引/动画tick用于客户端初始同步；Frostmaw自定义NBT存水晶与active标志。出生同步不等于世界重载恢复完整死亡进度，未作运行证明。',
  'transfer': '借鉴头/胸/支撑肢协调的侧向失衡、落地前后的独立阶段和图层审查；狻猊不改侧卧造型，不复制角度、不追加物件。'
 },
 'semantic_dedup': '一项侧倒死亡策略候选；声事件、眼睑、四肢、两活动态及十个文件不各计一项。与EnderGolem和Netherite并非同一关键帧/状态实现。',
 'historical_static_identity_accepted_in_v35': any('Frostmaw' in k for k in legacy),
 'acceptance': 'SOURCE_STUDIED_CANDIDATE; NOT_NATIVE_OR_HEAD_FLOOR_CERTIFIED',
 'new_accepted_credit': 0
}
assert sum(frost['whole_selected_policy']['phase_durations_ticks']) == 95
put('frostmaw-death-study.json', frost)

wrought = {
 'identity': 'BobMowzie/MowziesMobs-Public:Wroughtnaut',
 'revision': frost['revision'],
 'sources_read': [
  dict(ev(M/(F+'client/model/entity/ModelWroughtnaut.java')), scope='370–440父链、480–632完整默认/步态层与animate入口、1479–1618完整死亡分支；未研究/复制斧体几何。'),
  dict(ev(M/(F+'server/entity/wroughtnaut/EntityWroughtnaut.java')), scope='130tick死亡常量、150–208完整受伤门控和死亡选择、225–307状态/步态计时、560–613保存读取。'),
  dict(ev(M/(F+'client/render/entity/RenderWroughtnaut.java')), scope='全文件，flip0和物件层挂点只读；不制作物件。'),
 ],
 'shared_sources_reused_without_reread': [ev(M/(F+p)) for p in ['server/entity/MowzieLLibraryEntity.java','server/entity/MowzieEntity.java','client/model/entity/MowzieEntityModel.java','client/model/tools/MMModelAnimator.java']],
 'upstream_verification': ev(O/'wroughtnaut-byte-verification.json'),
 'whole_selected_policy': {
  'entry': '原实体hurt经可受伤方向/漏洞门控或无直接实体的绕过无敌来源，再交父hurt；父致命受伤发送死亡动画。只作现有触发分析，不修改狻猊受伤规则。',
  'life': '死亡常量130tick，父getDeathDuration减20，服务器deathTime>=110移除；选定关键帧累计128tick，不能把末段全部算实际可见。',
  'phase_durations_ticks': [5,8,30,10,10,5,13,7,40],
  'phase_cumulative_ticks': [5,13,43,53,63,68,81,88,128],
  'pose': '前5tick腹颈前屈与双臂张开；5–13tick增大waistBendController，13–43保持颤动；43–53解除控制振荡、53–63保持；63–68根部下移后撤且屈腿/脚踝配合，保持至81；81–88根部前翻、再次下移后撤，双臂与小腿非对称；88后保留落定姿态。',
  'controller': '死亡分支末尾腹/颈/肩振荡幅度由waistBendController驱动；该控制器不是额外生物或单独机制。',
  'hierarchy': 'rootBox→waist分别接groin→腿足与stomachJoint→stomach→chestJoint→chest→neck→head；根部翻倒会同时影响腿和头颈，不能把所有补偿视为同一局部Y。',
  'layers': 'animate先setDefaultAngles，默认层对death也施加活动式肩臂和注视；步态幅度来自walkAnim而非输入limbSwingAmount原值。实体非NO_ANIMATION时额外decreaseTimer(2)，故死亡开始残余步态会衰减，不可假设从首帧严格为0。',
  'renderer': 'flip0避免额外原版侧倒。武器只是该身体链现有挂点关系的只读上下文，没有复制或制作。',
  'reload': '自定义NBT保存restPos/active/alwaysActive；共享父spawn动画tick同步不等于死亡重载连续性。',
  'transfer': '学习控制性颤动解除后再失去支撑、屈腿与根部前翻，以及头颈仍受默认层影响的审查方法。狻猊不改人形或跪倒，也不引入该武器。'
 },
 'semantic_dedup': '共享Mowzie死亡父类和插值器已在Frostmaw读取，不再计数；此处前翻双阶段支撑与控制器衰减不同于Frostmaw侧倒，作为一项身体策略候选。骨骼、阶段、文件不拆数。',
 'acceptance': 'SOURCE_STUDIED_CANDIDATE; NOT_NATIVE_OR_HEAD_FLOOR_CERTIFIED',
 'new_accepted_credit': 0
}
assert sum(wrought['whole_selected_policy']['phase_durations_ticks']) == 128
put('wroughtnaut-death-study.json', wrought)

# Prior whole studies are retained by their original selected scope, not counted as new deaths.
prior_scopes = [
 ('suanni-death-intent-review-20261110/review.json', 'EnderGolem', '已读关联分段坍塌，仍一项候选；95tick动画/75tick移除'),
 ('suanni-body-policy-research-20261110/tiger-whole-policy-study.json', 'Tiger', '原选定爪击/跳扑/步态，不能升格成独立死亡接地策略'),
 ('gorilla-smash-body-research-20261110/receipt.json', 'Gorilla', '原选定SMASH，与死亡接地不等价'),
 ('controller-continuity-research-20261110/receipt.json', 'Gecko4.8.4', '控制器相同动画连续性；共享框架不是一只生物参考'),
 ('humanoid-recovery-research-20261110/receipt.json', 'HumanCompanions', '人形候选恢复研究，不对应铜兽头颚落地'),
 ('native-damage-state-research-20261110/receipt.json', 'Native damage/death framework', '原生受伤/死亡框架范围保留，不按实体继承数乘算'),
 ('crossbow-body-state-research-20261110/receipt.json', 'Crossbow body', '选定弩手状态，不是死亡落地'),
]
put('prior-whole-dedup.json', {
 'mode': 'Original receipt identities and selected-scope reconciliation, not fresh full reread of every historical source.',
 'retained': [dict(ev(B/p), identity=i, decision=s, new_credit=0) for p,i,s in prior_scopes],
 'current_dynasty_actor_studies': 'Ink/Lamp/Tide/Rage/Eagle/Suanni当前实现记录是待验对象，不按外部参考数量计；已有收据原样保留。',
 'legacy_static_scope': ev(legacy_path),
 'boundary': '未声称已完成全1345条历史记录的whole机制映射；当前挑选相关完整策略累计4项，独立接收/头颚实测接地资格仍未取得。'
})
put('progress.json', {
 'target': scope['target'], 'status': 'RESEARCH_CONTINUING_NOT_PRODUCTION_READY',
 'done': ['100/1000授权范围核清并保留旧信用', 'EnderGolem原机制与七类旧whole选定范围去重', 'NetheriteMonstrosity死亡完整选定策略', 'Frostmaw死亡完整选定策略及地形/插值叠加', 'Wroughtnaut前翻沉降完整选定策略及共享父类去重'],
 'selected_policy_studies_accumulated': 4, 'new_policy_studies_this_batch': 3,
 'new_accepted_credit': 0, 'mapped_accepted_for_current_fix': 0,
 'global_applicable_total': None, 'global_gap': None,
 'next_concrete': '逐项把旧静态库中的明确相关死亡策略映射到完整实体生命周期/动画/父类/渲染；下一候选检查Mowzie Foliaath的头部/茎部坍塌与当前四项是否语义不同。缺头颚约束证据的候选不当直接接地验收。',
 'production_modified': False, 'game_or_java_started': False,
 'original_task_retained': True, 'main_checklist_modified': False,
 'no_reference_assets_in_runtime': True
})
for p,h in old['production_hashes'].items(): assert sha(p)==h
put('handoff-metadata.json', {n: ev(O/n) for n in ['applicability.json', 'netherite-monstrosity-death-study.json', 'frostmaw-death-study.json', 'wroughtnaut-death-study.json', 'prior-whole-dedup.json', 'progress.json', 'upstream-byte-verification.json', 'frostmaw-byte-verification.json', 'wroughtnaut-byte-verification.json', 'sources/Netherite_Monstrosity_Animation.java', 'README.md', 'record.py']})
print(json.dumps(ev(O/'handoff-metadata.json'), ensure_ascii=False))
