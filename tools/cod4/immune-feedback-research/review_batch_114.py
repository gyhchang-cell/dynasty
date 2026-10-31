"""Three manually inspected Occultism native policies; shared wrappers/constants grant no credit."""
from ledger import B, O, record, verify
import json

r = 'klikli-dev/occultism'
p = 'src/main/java/com/klikli_dev/occultism/'
def f(s, a, z): return p+s, a, z
def w(s): return f(s, 1, len((B/'sources'/r.replace('/', '__')/(p+s)).read_text().splitlines()))

shared = [f('Occultism.java', 90, 150), w('util/FamiliarUtil.java'),
          f('common/entity/familiar/FamiliarEntity.java', 80, 131),
          f('common/entity/familiar/FamiliarEntity.java', 183, 257),
          f('common/entity/familiar/FamiliarEntity.java', 264, 342),
          f('common/capability/FamiliarSettingsData.java', 53, 134),
          f('common/capability/FamiliarSettingsData.java', 264, 289),
          w('registry/OccultismDataStorage.java'), f('registry/OccultismEffects.java', 38, 70)]
ids = []
k = 'occultism-native-equipped-or-owned-upgraded-familiar-final-effect-rejection'
record(k, r, shared + [f('handlers/FamiliarEventHandler.java', 62, 63),
    f('handlers/FamiliarEventHandler.java', 153, 192),
    f('common/entity/familiar/BlacksmithFamiliarEntity.java', 92, 134),
    f('common/entity/familiar/BlacksmithFamiliarEntity.java', 269, 408),
    f('registry/OccultismEntities.java', 354, 358), f('registry/OccultismEntities.java', 534, 535)],
    '真实Effect Applicable事件经静态EventBusSubscriber进入familiarEffectsImmunity；最终DO_NOT_APPLY以效果匹配、玩家attachment启用标记、实际升级使魔查询联合决定。FamiliarUtil先装备后附近，装备扫描Curios及手持TOOLS/盔甲，附近扫描owner的10格AABB并检查存活与归属。黑匠原生注册UpgradeGoal/IesniumUpgradeGoal，消耗铁/艾司金属并给同主人目标升级，SynchedEntityData升级位供最终判定。',
    '计1：外部使魔存在与归属/装备升级共同决定最终状态拒绝；九个效果/使魔组合是同一策略的常量变体，不拆9条。装备分支仅type+predicate，未重验owner/alive；附近分支验证两者。启用查询和hasFamiliar是两次查询，拒绝分支没有文本/粒子/音效回执。DO_NOT_APPLY是明确拒绝，不是从hurt=false猜出。',
    'Boss入口必须先识别确实被策略拒绝的控制；反馈不能仅凭拥有能力、已有状态或伤害没变化产生。判定使用的目标/归属应来自服务端，不将普通阴阳体质扩成Boss灰字。',
    '所列最终事件、查询全方法、升级goal全类和真实事件/实体注册已读；未声称完整仪式获取、Curios库或平台最终事件仲裁全文已读。其他监听器优先级可能改变最终结果，静态不证明全包实际拒绝或画面。',
    'native_owned_equipped_capability_effect_refusal')
ids.append(k)

k = 'occultism-native-mummy-random-damage-cancellation-assignment-and-conditional-criterion'
record(k, r, shared + [f('handlers/FamiliarEventHandler.java', 62, 63),
    f('handlers/FamiliarEventHandler.java', 203, 247), w('common/data/FamiliarEffects.java'),
    w('common/entity/familiar/MummyFamiliarEntity.java'), w('common/advancement/FamiliarTrigger.java'),
    f('registry/OccultismEntities.java', 367, 371), f('registry/OccultismEntities.java', 538, 539),
    f('datagen/OccultismAdvancementSubProvider.java', 271, 275)],
    'MUMMY实体注册→FamiliarEffects中真实MUMMY_DODGE定义→FamiliarEntity.aiStep每10世界tick距离<8时给主人300tick效果，getFamiliarEffects按升级与主人effect amplifier取min。native LivingIncomingDamage监听依次safeFall/dodge/headlessExtraDamage/fairyDamageConversion；dodge要求已有MUMMY_DODGE、攻击实体非null且不是explosion/bypass，RNG<(amplifier+1)*0.1，然后直接setCanceled(dodge)。只有roll true触发MUMMY_DODGE criterion，FamiliarTrigger仅ServerPlayer进入真实advancement。',
    '计1：原生伤害拒绝以随机结果直接赋值，而非只在true时取消；无独立目标CD，也不消费状态。与已有rapier碰撞回退/voidrobe传送成功条件/救死不同。该入口没有进入dodge前isCanceled保护，内部组合存在将已有取消改回false的语义，但未证明自然来源的safeFall取消与dodge资格必重合。advancement是条件触发，不是世界目标灰字。效果aura入口未检查isAbilityEnabled，enabled字段与effectsLevelMap分开；不凭GUI总开关推断本效果已停。',
    '拒控回执必须绑定最终拒绝结果，不能在尝试roll或能力存在时播成功样提示；多个处理器不得意外用false撤销其他拒绝。Boss节流应独立于是否生成普通效果、成就或伤害iframe。',
    '主查实体原生aiStep效果生产，未把虚拟curio当原生tick；未证明运行时roll结果、最终NeoForge事件仲裁、成就弹窗或TCP画面。共享属性/注册/criterion包装均支持0。',
    'native_random_refusal_assignment_and_actual_receipt_order')
ids.append(k)

k = 'occultism-native-beholder-prehit-target-anchored-replay-with-bounded-eye-lease'
record(k, r, [f('Occultism.java', 90, 150), w('common/entity/familiar/BeholderFamiliarEntity.java'),
    w('common/entity/familiar/ColoredFamiliarEntity.java'), w('util/FamiliarUtil.java'),
    w('network/messages/MessageBeholderAttack.java'), w('network/MessageHandler.java'),
    f('network/Networking.java', 36, 90), f('registry/OccultismEntities.java', 354, 358),
    f('registry/OccultismEntities.java', 534, 535)],
    '实际实体registerGoals接RayGoal，按owner最近受击者/攻击者列表→server发送MessageBeholderAttack到施法者tracking，attackTimer=23；稍后重新以目标numeric ID查询执行hurt且不使用返回值。client收到后shootRay给最多4只眼各取一个目标，prepareShot=20；native tick每眼递减，最后4个tick发dust射线，目标每次由本world实体eyePosition(0)重取。固定包注册playToClient→MessageHandler→实际consumer，颜色由ColoredFamiliarEntity的同步RGB读取。',
    '计1：真实战斗预告的目标跟随/有限眼位租约与服务端延迟命中不同步策略，合并包/插值/尘线/目标ID生命周期为同一反馈链。不是实际免疫回执，视觉已播不证明伤害接受；getOwnerEnemies可重复同一实体，未UUID去重。最多4眼；每次shoot最多150点、步长0.1，碰终点膨胀AABB截断，没做方块遮挡射线。目标丢失时本次shoot返回，不排队重发；倒计时继续。包无UUID/dim/epoch，decode长度无显式上界；目标ID复用/跨world迟包风险仅静态可见。',
    'Boss灰字应由确定拒控的服务端结果产生，有限存活并绑定目标身份/世界；跟踪施法者不等于跟踪被拒控Boss，包路由应明确目标观察者。不能直接复用这种先播预告当成功/免疫回执。',
    '实体及眼部所有关键类全文、RGB父类全文、真实packet/dispatch/发送方法全链已读。粒子使用原版Dust，未读平台dust渲染深度，不能称可见/遮挡通过。无游戏、画面或两TCP测试，普通图形/网络包装0额外。',
    'native_combat_feedback_target_anchor_and_finite_lease')
ids.append(k)

d = json.loads((O/'semantic-dedup.json').read_text())
d['groups'].append({'family': 'batch114-occultism-native-refusal-and-beholder-target-replay',
    'credited_chains': ids,
    'rationale': 'Three distinct native policies: upgraded owned/equipped familiar rejects effect application; mummy roll assigns damage cancellation with criterion only after true; beholder actual prehit target-bound replay with finite eye lease. Nine familiar/effect pairs, wrappers, RGB, criterion helpers and dust draw steps are not separately credited.'})
(O/'semantic-dedup.json').write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n')
verify()
