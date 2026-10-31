"""Manual semantic follow-up; original source is data, never executed."""
from reference_evidence import Evidence,row
import json
E=Evidence(14);R='Electroblob77__Wizardry'
r=lambda f,m=None,**kw:E.ref(R,f,m,**kw)
P='pending_primary_semantic_review';S='support_only_not_effective'
ray=[r('SpellRay','cast',signature='EntityPlayer caster'),r('SpellRay','shootSpell'),r('Paralysis','onEntityHit'),r('Paralysis','onMiss'),r('Paralysis','onBlockHit'),r('Spells',span=[441,441])]
rows=[]
rows.append(row(14,1,'wizardry-paralysis-native-ai-disable-last-tick-release-versus-critical-hurt-early-removal',P,
 [r('Paralysis','onLivingUpdateEvent'),r('Paralysis','onLivingHurtEvent'),*ray,r('WizardryPotions',span=[151,157]),r('PotionMagicEffect','performEffect'),r('WizardryClientEventHandler','onMouseEvent'),r('WizardryClientEventHandler','onInputUpdateEvent')],
 '原生LivingUpdate只在EntityLiving且paralysis仍活动时setNoAI(timeLeft>1)，最后一tick强制false，不保存此前NoAI。原生LivingHurt若health-event.amount<=critical_health就直接removePotionEffect，不在该handler恢复NoAI；若此前AI已置true且效果被提前移除，后续本地LivingUpdate分支不再进入，不能依赖最后一tick补偿。注册的paralysis是匿名PotionMagicEffectParticles，仅覆写spawnCustomParticle，父performEffect空；本地没有对应removeAttributes重置AI。Player不走Mob的NoAI门，客户端MouseEvent在focus且effect时cancel并把yaw/pitch及prev值设0，InputUpdate清forward/strafe/jump/sneak。仅静态阅读，未触碰屏幕或相机。',
 '控制拒绝/解除必须覆盖实际AI生产与提前移除，不能把效果消失视为AI一定恢复；归还状态应保留原先值而非一律false。玩家输入与Mob AI不可混做一种权威控制。',
 '区别已计SlowTime orphan扫描恢复和Possession完整释放：这里正常尾tick释放与受伤早移除存在显式分叉，来源与生命周期失配独立供审。把鼠标/按键/NoAI三消费者合并同一paralysis生命周期，不拆数；主岗可以对通用状态恢复家族再合并。',
 ['这是外部项目静态缺口，未在原生AI运行复现，不报告为王朝已证实缺陷。', '原生Potion remove及其它第三方listener可能影响最终表现，未运行。', 'LivingHurt的amount不等于最终HP损失，不能说发生此分支就已真实掉到临界值。', '原生Player输入包/反作弊强制移动不在此链，不声称对玩家服务端所有运动都不可突破。']))
rows.append(row(14,2,'wizardry-paralysis-shock-damage-refusal-does-not-short-circuit-effect-attempt-support',S,
 [*ray,r('MagicDamage','isEntityImmune'),r('ItemArtefact','onPotionApplicableEvent'),r('PotionMagicEffectParticles'),r('PotionMagicEffect')],
 'onEntityHit先在client发BEAM/LIGHTNING，再按MagicDamage SHOCK映射决定服务器resist文字或尝试shock伤害；随后无论immune/hurt bool都在server尝试addPotionEffect(paralysis)。duration对Player用modifiers.get(player_effect_duration_multiplier)，不是getProperty。本地ItemArtefact Applicable只否决frost/wither，不覆盖paralysis。onEntityHit总false，父shootSpell继续onMiss，后者画原range BEAM/LIGHTNING且true；故有抵抗文字仍可能有施效尝试/满程预测粒子，不能推出原生最终addEffect接纳。',
 '元素免伤、状态接纳和实际控制分开记录原因；拒伤文字不能给仍在发生的控制尝试背书，预测射线也不能代表服务器认可控制。',
 '主账wizardry-elemental-policy-explicit-resist-versus-event-rejection已涵盖元素映射/Spell resist家族，本条只补完整麻痹决策上下文支持0，不用新spell名字重复计数。', ['原生isPotionApplicable与第三方拦截没读，不声称所有SHOCK免疫实体最终都被麻痹。', '仅记录duration读取表达式，不猜默认倍率或宣称配置有bug。']))
rows.append(row(14,3,'wizardry-anchoring-telekinesis-full-chain-already-effective-duplicate-support',S,
 [r('GreaterTelekinesis','onEntityHit'),r('GreaterTelekinesis','onMiss'),r('ItemArtefact','isArtefactActive'),r('SpellRay','shootSpell'),r('EntityUtils','undoGravity')],
 '复核完整onEntityHit：Player互移开关关闭或target anchoring活动则服务端给caster resist并false，发生在持有/投掷前；否则控制Living/LevitatingBlock/TNT，steal block owner后，sneak加look速度，非sneak补重力并按holdpoint误差*.8加速度；MP有原生velocity包，client有beam/flash/sparkle。没有新Boss门。',
 '复用已有有效研究，拒绝重复条目；直接运动生产者应在改变owner/速度前做策略判定。',
 '明确主账wizardry-anchoring-final-displacement-refusal-and-resist-text已全文收录本文件1..164及Whirlwind，重复0，不能因本轮多读shootSpell而重新申请。', ['不新增、修改或重新验收既有研究信用。']))
rows.append(row(14,4,'wizardry-blackhole-anchored-control-denial-still-allows-contact-damage-support',S,
 [r('EntityBlackHole','onUpdate'),r('EntityBlackHole','EntityBlackHole'),r('EntityScaledConstruct','setSizeMultiplier'),r('EntityMagicConstruct','isValidTarget'),r('AllyDesignationSystem','isValidTarget'),r('EntityUtils','undoGravity'),r('EntityUtils','getEntitiesWithinRadius'),r('SpellConstructRanged','cast',signature='EntityPlayer caster'),r('SpellConstruct','spawnConstruct'),r('Spells',span=[379,379]),r('WizardryEntities',span=[142,142])],
 'BlackHole server枚举有效Living或启用吸块时的FallingBlock。Player互移关闭/anchoring仅跳过吸引分支，距离<=2仍尝试2*damageMultiplier魔法伤害；hurt返回忽略。可移动目标先undoGravity，逐轴按朝中心且当前速度在+/-1内加减.075，非向量长度clamp；MP另velocity包。整体radius=2*height*sizeMultiplier，而setSizeMultiplier已按倍率缩height，不能把它概括为纯一次blast缩放。黑洞整体portal/ambient/vanish时机按寿命与tick，不是每个目标拒控回执。',
 '拒控与拒伤可不同，免控不能自动把接触伤害省略；表现依构造物寿命产生也不证明命中被目标接纳。',
 '与主账anchoring既有同一Player饰品/开关拒控策略合并支持0；Iron黑洞已计常规吸引/到期失验另家族，本条也不按坐标轴/数值换皮新增。', ['完整onUpdate内吸块分支已读，但BlockUtils权限/破坏消费者未完整扩链，不声称此批包含完整世界破坏机制。', '没有Boss显式拒控门，也没有真实网络或计时验收。']))
rows.append(row(14,5,'wizardry-ice-spike-native-hurt-gates-frost-attempt-template-support',S,
 [r('EntityIceSpike','onUpdate'),r('IceSpikes','spawnConstruct'),r('IceSpikes','addConstructExtras'),r('SpellConstruct','spawnConstruct'),r('SpellConstructRanged','cast',signature='EntityPlayer caster'),r('Spells',span=[408,408]),r('WizardryEntities',span=[166,166])],
 '原生IceSpike tick先按lifetime差值移动伸缩，等于30播extend声，再server枚举相交Living且isValidTarget，只有attackEntityFrom true才尝试frost；不检查Potion接纳结果。最后super.onUpdate才做过期despawn，故不能把parent寿命门说成挡住所有本tick先行碰撞。IceSpikes声明permanent但addConstructExtras把lifetime重写30+rand(15)，把它当延迟使用；spawn对super每次返回值忽略，外围最终true不证明全部期望尖刺均已生成。',
 '实际hurt、效果尝试、伸缩声与施法成功是不同证据；失败hurt不执行效果尝试，但声仍由时间独立触发。',
 '和013箭/MPS原生hurt gate副作用相同家族，仅补状态尝试消费者，支持0；不按尖刺数量/朝向/元素常量扩信用。', ['facing setter几何已全文读，不扩成独立研究条；native move碰撞与Potion最终接纳未验。']))
print(json.dumps(E.finish(rows),ensure_ascii=False))
