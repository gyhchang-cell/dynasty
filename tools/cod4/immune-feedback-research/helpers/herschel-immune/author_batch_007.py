"""Write only the seventh helper batch; all referenced bodies read before authoring."""
from pathlib import Path
p=Path(__file__).with_name('build_batch_006.py');s=p.read_text()
head=s[:s.index("add('iron-shadow-slash")].replace('006','007').replace('001–005','001–006')
body=r'''
add('iron-poison-marked-once-native-long-cast-interruption-refusal',
 'PoisonMobEffect.applyEffectTick HEAD的实际Mixin对ServerPlayer记tickCount；MagicData.popMarkedPoison以当前tick-标记<=1认定一次毒伤并立刻清零。原生onLivingIncomingDamage仅在casting/canBeInterrupted/remaining>0、伤害不在LONG_CAST_IGNORE且pop返回false时cancelCast。canBeInterrupted要求LONG并未戴CONCENTRATION_AMULET；标签datagen含燃烧/凋零/摔落等及可选NeoForge毒伤。',
 '控制拒绝需区分来源标签、装备与一次性事件标记；仅用时间邻近匹配会把第一次相关incoming当毒伤，不是DamageSource对象级关联。免打断不等于免伤。',
 '静态无运行；Poison applyEffectTick标记在HEAD，不证明本次确产生伤害；标签门短路时不pop，可能留下窗口。默认timestamp=0，pop只检查差<=1未排负值。仅服务端玩家有标记，Boss/普通Mob不套用同一语义。Mixin资源未新取/未运行，Java链已固定。',
 '原生PoisonMobEffect.applyEffectTick→MobEffectMixin.markPoisoned→MagicData.timestamp→原生LivingIncomingDamageEvent→ServerPlayerEvents.onLivingIncomingDamage→popMarkedPoison拒绝中断或Utils.serverSideCancelCast→既有OnCastFinished明确cancelled回执',
 ev(I,'MagicData','popMarkedPoison'),ev(I,'MobEffectMixin','__complete_file__'),ev(I,'MagicData','markPoisoned'),ev(I,'ServerPlayerEvents','onLivingIncomingDamage'),ev(I,'AbstractSpell','canBeInterrupted'),ev(I,'DamageTypeTagGenerator','addTags'),ev(I,'Utils','serverSideCancelCast','boolean triggerCooldown'),ev(I,'CancelCastPacket','cancelCast'),ev(I,'AbstractSpell','onServerCastComplete'),
 dedup='001 incoming全文的冰墓/火戒分支与005反制取消回执为共享支持；新决策是LONG_CAST_IGNORE/护符/一次性毒伤标记拒绝中断，不把既有packet或每种来源再计。')
entityMixin='src/main/java/com/hollingsworth/arsnouveau/common/mixin/EntityMixin'
add('ars-soaked-native-positive-fire-tick-denial-versus-fire-damage-immunity',
 '已注册ConjureWater.onResolveEntity立即clearFire，再在Living且durationMultiplier>0时赋SOAKED。EntityMixin原生setRemainingFireTicks HEAD仅当Living且isWet（SOAKED或Bubble乘客）且新ticks>0时clearFire并cancel；原生isInWaterOrRain RETURN也把湿目标置true。不是LivingIncomingDamage取消，对直接火伤并未在此拒绝。',
 '具体点燃状态写入门可明确表示拒绝点燃，不能把“未着火”泛化成火伤免疫；控制状态来源和伤害来源需分别记录。',
 '只读Java未验证Mixin运行/资源启用。SoakedEffect有applyEffectTick清火，但未覆写shouldApplyEffectTickThisTick，故不据该方法存在声称持续tick必调用；真正已找到的是原生fire-ticks写入门和立即clearFire。保护只在状态/乘骑存在时判定，无另加持久免疫。',
 'APIRegistry注册EffectConjureWater→SpellResolver/EffectConjureWater.onResolveEntity→IPotionEffect.applyPotion→注册SOAKED；原生Entity.setRemainingFireTicks→EntityMixin.isWet取消正ticks；原生isInWaterOrRain读取同门',
 ev(A,entityMixin,'ars_nouveau$setSecondsOnFire'),ev(A,entityMixin,'isWet'),ev(A,entityMixin,'ars_nouveau$isInWaterOrRain'),ev(A,'EffectConjureWater','onResolveEntity'),ev(A,'IPotionEffect','__complete_file__'),ev(A,'SoakedEffect','__complete_file__'),span(A,'ModPotions',51,51,'SOAKED_registration'),span(A,'APIRegistry',94,94,'ConjureWater_registration'),ev(A,'SpellResolver','onResolveEffect'),ev(A,'SpellResolver','resolveAllEffects'),
 dedup='与Iron fireward incoming取消伤害不同：这里明确只拒绝原生点燃状态写入，并改变wet查询；与Bubble乘骑捕获同门共享但不是重复乘骑解除/redirect。')
add('ars-soaked-observer-effect-sync-with-local-player-exclusion-and-lossy-amplifier',
 'PotionEffectTagProvider实际TO_SYNC仅加入SOAKED。onPotionAdd服务端在Wixie时长修正后发entity int/effect registry ID/duration；Remove与Expired共用-1发同包。PotionSyncPacket客户端查当前mc.level整数ID且Living、并排除本地proxy player；正时长addEffect构造固定amplifier0且不显粒子/图标，其他值remove。Networking确注册S2C。',
 '面向旁观者的控制状态反馈要区分本地玩家已有原生同步与远端副本；接收实体及状态注册表校验有用，但有状态包不代表原伤害接纳，丢失amplifier不能当全量状态一致。',
 '无TCP/实机。只有事件通知，不把事件名Added猜成最终原生接受点；包不带UUID/维度/代际/序号，目标未跟踪时无缓存重试，后来进入视距的初始状态未在此补发。tag datagen已读且有实际登记，不声称已运行生成资源。',
 'ConjureWater实际SOAKED生产→MobEffectEvent.Added/Remove/Expired→EventHandler→Networking.sendToNearbyClient按区块tracking→注册PotionSyncPacket→当前世界实体查找/本地玩家排除→add/removeEffect→Soaked/native wet门',
 ev(A,'PotionSyncPacket','onClientReceived'),ev(A,'PotionSyncPacket','__complete_file__'),ev(A,'EventHandler','onPotionAdd'),ev(A,'EventHandler','onPotionRemove'),ev(A,'EventHandler','onPotionExpire'),ev(A,'EventHandler','syncPotionRemoval'),ev(A,'PotionEffectTagProvider','addTags'),span(A,'ModDatagen',42,42,'PotionEffectTagProvider_registration'),ev(A,'EffectConjureWater','onResolveEntity'),ev(A,'Networking','register'),ev(A,'Networking','handle'),ev(A,'Networking','handleClient'),ev(A,'Networking','sendToNearbyClient','BlockPos pos'),
 dedup='不是泛型codec计数：实际SOAKED远端状态副本策略、LocalPlayer排除和增删负时长约定合1；与上一条原生点燃拒绝为独立客户端归属/生命周期点。')
add('spellengine-stashed-combat-charge-consumed-on-attempt-with-deferred-effect-replacement',
 'SpellStashHelper.link由服务器starting注册，针对真实STASH_EFFECT配置把触发器绑到StatusEffect；SpellDelivery实际给目标addStatusEffect。原生combat→fireTriggers先useStashes，复制activeEffects，以本次调用Map按实例累计剩余amp，通过触发门后performImpacts却忽略bool，TRANSFER无arrow也照后续消费；非零consume写Diff，最后统一applyChanges。delayConsume将delay=1，排到world tick TAIL的immediateTasks，届时按effect type重查当前instance但用旧计算newAmplifier，未核验是否同一代效果。',
 '控制反馈消耗预算要定义尝试还是接纳；延迟扣层不能用旧预算覆盖后来刷新的同类型状态。每次调用局部预算不等于同tick全局封顶。',
 '只有静态框架原生链，未装载具体外部STASH法术配置/未运行；不声称任一Boss实际用了此机制。既有evaluateTrigger cap仍可限制一部分重入，所以不能把delay直接称无限触发。WorldScheduler delay=0在下次TAIL处理不是保证完整下一tick。',
 'SpellEngineMod.init→SpellStashHelper.init→serverStarting link→StatusEffectSpellStash；SpellDelivery STASH_EFFECT→效果持有；原生LivingEntityHealthImpacting→CombatEvents→SpellTriggers.init/onDamageIncoming/fireTriggers→useStashes→StatusEffectUtil.applyChanges→WorldScheduler/ServerWorldMixin TAIL→processRemoval',
 ev(S,'SpellStashHelper','useStashes'),ev(S,'SpellStashHelper','init'),ev(S,'SpellStashHelper','link'),ev(S,'SpellStash','__complete_file__'),ev(S,'StatusEffectSpellStash','__complete_file__'),ev(S,'SpellEngineMod','init'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'LivingEntityHealthImpacting','damage_ApplyDamage_entity'),ev(S,'SpellTriggers','init'),ev(S,'SpellTriggers','onDamageIncoming'),ev(S,'SpellTriggers','fireTriggers'),ev(S,'SpellTriggers','evaluateTrigger'),ev(S,'StatusEffectUtil','__complete_file__'),ev(S,'WorldScheduler','__complete_file__'),ev(S,'ServerWorldMixin','__complete_file__'),
 dedup='004 cap/chance算法全文仅支持。此处为实际存储法术效果栈、尝试后消费、延迟重查同type覆盖边界，独立于一般被动触发配额；全部同链消费包装1条，不拆每种trigger。')
add('spellengine-teleport-minimum-displacement-explicit-fizzle-before-cost-callback',
 'performImpact TELEPORT解析FORWARD安全候选或BEHIND_TARGET坐标。配置minimum_distance>0且实体/起点存在时，目标为空或直线位移未达平方阈值会在目标实体当前位置发专门fizzle particles/model/sound并return false，没走depart/teleport/arrive。fizzle粒子调用includeSourceEntity=false，仅把payload sourceEntityId写0（sourceType仍ENTITY）；最终sender仍显式向tracked ServerPlayer本人及tracking集合发送，不能把该参数名误读成排除本人。声音另走world.playSound(null,目标坐标)。成功路径却调用void teleport后直接success=true。deliver完成回调传delivered||forceSuccess；performSpell completion仅success后ReleaseFx/SpellCost.consume。',
 '这是有明确拒绝生产点的语义反馈，能区分“目的地/距离失败”和泛型hurt失败；反馈锚在实际被传送实体，原因和完成回调应一起核查。',
 '静态未运行；BEHIND_TARGET自目标更早return false不发fizzle，minimum_distance=0缺dest也无此提示。不能宣称所有失败均免CD/消耗：AREA分支forceSuccess=true、其他impact可成功，且imposeAttemptCooldown已在delivery前执行。void teleport返回不证明最终原生位置接受。',
 'performSpell→SpellDelivery.resolveAndDeliver/deliver DIRECT→SpellImpacts.performImpacts/performImpact TELEPORT→min-distance fizzle false→聚合/DeliveryCompletion→success门的ReleaseFx+cost；模型/粒子/SoundHelper为既有反馈消费者支持',
 ev(S,'SpellImpacts','performImpact'),ev(S,'SpellDelivery','resolveAndDeliver'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'SpellImpacts','performImpacts','boolean additionalTargetLookup'),ev(S,'SpellExecution','performSpell'),ev(S,'SpellCooldowns','imposeAttemptCooldown'),ev(S,'TargetHelper','findTeleportDestination'),ev(S,'TargetHelper','isSafeWithClearance'),ev(S,'TargetHelper','isSafeTeleportDestination'),ev(S,'ParticleHelper','sendBatches','Entity trackedEntity, List<ParticleGroup> effects, boolean includeSourceEntity'),ev(S,'ParticleHelper','sendBatches','@Nullable Entity trackedEntity'),ev(S,'ModelEffectHelper','spawn','LivingEntity contextEntity'),ev(S,'SoundHelper','playSound','Entity entity'),ev(S,'SoundHelper','playSoundEvent','float volume'),
 dedup='004/005共享performImpact完整体不代表新计相同分支：本条仅新增minimum_distance显式fizzle/回调边界；与003Iron被取消传送仍先发FX为不同原生否决策略。不按FX种类或FORWARD/BEHIND拆数。')
add('ars-sensitive-glow-target-color-receipt-gates-existing-status-and-native-team-precedence',
 '已注册EffectLight实际对非自身或Sensitive目标applyConfigPotion(GLOWING)，仅hasEffect(GLOWING)&&Sensitive才发PacketUpdateGlowColor（仍会为已有glowing发，不证明本次添加接纳）。S2C以整数entityID/color发区块tracking；接收把非0颜色写目标client persistentData，0删除。EntityMixin.getTeamColor只在原生颜色=16777215且isCurrentlyGlowing时读取，负值用本地ticks rainbow，否则用原色。',
 '具体状态反馈应依实际目标有该状态再生产，但已有状态不能证明本次成功；原生队伍颜色优先、0清除哨兵与颜色取值域需区分，避免目标着色错归。',
 '不是拒控文字实现/未运行；缺UUID、维度、目标未加载重试与初始跟踪补色。该NBT只在client包中写，搜索glow_color未见效果移除时自动清；重新发0才显式删。Mixin启用资源本地缺，无运行承诺。原始RGB黑0会走删除而非黑色，不能声称所有颜色等价可见。',
 'APIRegistry注册EffectLight→SpellResolver→EffectLight.onResolveEntity→IPotionEffect→hasEffect→Networking S2C注册/区块tracking→PacketUpdateGlowColor.onClientReceived→Entity.getTeamColor RETURN mixin取target persistentData',
 ev(A,'PacketUpdateGlowColor','onClientReceived'),ev(A,'PacketUpdateGlowColor','__complete_file__'),ev(A,'EffectLight','onResolveEntity'),ev(A,'IPotionEffect','__complete_file__'),ev(A,entityMixin,'ars_nouveau$getTeamColor'),ev(A,'Networking','register'),ev(A,'Networking','sendToNearbyClient','BlockPos pos'),span(A,'APIRegistry',55,55,'EffectLight_registration'),ev(A,'APIRegistry','registerSpell'),ev(A,'SpellResolver','onResolveEffect'),ev(A,'SpellResolver','resolveAllEffects'),
 dedup='独立实际目标颜色回执/原生team优先策略，不拆几何/modelFX模板；与旧hud颜色常量不同。不是按药水或颜色数量凑参考，主岗可按与战斗文字的实际相关性降支持。')
add('spellengine-passive-delay-target-snapshot-world-change-support',
 'fireTriggers的passive.fire_delay>0在触发当场选targetResult并排到旧player.world的scheduler；闭包执行时改用player.getWorld且仍用捕获的targetResult，不在此重新找目标。performSpell先检查spectator/法术source/attempt，短路可能拒绝后续；delivery.delay>0又另有caster/target removed检查，二者不是同一时序。',
 '延迟反馈若把旧目标快照与当前新世界混用，应验证世界和代际；仅静态可见风险，不推定已跨维攻击成功。',
 '本条没有新增具体Boss拒绝门/明确反馈生产，支持0。与既有004触发器和005目标生命周期背景合并；不将scheduler通用设施计信用。',
 '原生CombatEvent→SpellTriggers.fireTriggers选目标→WorldScheduler→旧world TAIL运行闭包→当前player.world performSpell/attempt→SpellDelivery.resolveAndDeliver',
 ev(S,'SpellTriggers','fireTriggers'),ev(S,'SpellTriggers','init'),ev(S,'SpellExecution','performSpell'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'WorldScheduler','__complete_file__'),ev(S,'ServerWorldMixin','__complete_file__'),status='support_only_not_effective',dedup='通用延迟目标生命周期只支持0；不与既有触发配额或具体feedback TTL重复计。')
add('iron-gust-direct-motion-before-status-acceptance-and-single-pulse-support',
 'GustSpell真实生成GustCollider并主动gust.tick。AbstractConeProjectile服务端dealDamageActive只执行一轮、碰撞实体Set去重后置false；GustCollider仅owner非空/目标Living/范围/非友伤时直接加速度并hurtMarked，再addAIRBORNE忽略结果。getOwner在tickCount>=1直接null；尾部实体外观存留到>8tick。Airborne碰墙速度满足阈值先发fall声再hurt，忽略bool且return false。',
 '控制位移写入在状态之前，不能以状态拒绝证明没被推动；音效也不是伤害成功回执。',
 '同001 Ars Snare/Gravity直接motion旁路家族，支持0；不是新免疫门。没有实机计时，不能据getOwner阈值假定第一次原生tick必有owner。说明主动tick/计数门不代表已验证实际移动。',
 '注册GUST→GustSpell.onCast主动tick→AbstractConeProjectile单轮碰撞Set→GustCollider.onHitEntity motion→AIRBORNE；原生effect tick碰墙声/伤害',
 ev(I,'GustCollider','onHitEntity'),ev(I,'GustSpell','onCast'),ev(I,'AbstractConeProjectile','tick'),ev(I,'AbstractConeProjectile','getSubEntityCollisions'),ev(I,'GustCollider','getOwner'),ev(I,'GustCollider','tick'),ev(I,'AirborneEffect','applyEffectTick'),ev(I,'AirborneEffect','shouldApplyEffectTickThisTick'),span(I,'MobEffectRegistry',42,42,'AIRBORNE_registration'),span(I,'SpellRegistry',123,123,'GUST_registration'),status='support_only_not_effective',dedup='直接motion与status成功分离已计家族；新脉冲门不是单独拒控/反馈策略，支持0不补数量。')
add('iron-scapegoat-taunt-selector-not-hit-rejection-support',
 'ScapegoatSpell生成诱饵后Utils.performTaunt在近球体选目标，tauntPredicate混合Enemy XOR/taunter Enemy和allied/Neutral愤怒；最终只对Mob先发愤怒粒子再setTarget。没有读取setTarget接纳结果，临时诱饵自身15秒倒计时归零清退。',
 '目标改变意图与目标接受分开；这种清仇恨/嘲讽无实际伤害拒绝不扩成免疫样本。',
 '依006主审对真实隐身清仇恨的范围决定，本条同样支持0。没有修改守卫或转移其旧账信用。',
 'SCAPEGOAT注册→ScapegoatSpell.onCast→Utils.tauntPredicate/performTaunt→Mob.setTarget；ScapegoatEntity.tick→poofAndDiscard',
 ev(I,'Utils','performTaunt','List<Entity> targets'),ev(I,'Utils','performTaunt','Predicate<Entity> selector'),ev(I,'Utils','tauntPredicate'),ev(I,'ScapegoatSpell','onCast'),ev(I,'ScapegoatEntity','__complete_file__'),ev(I,'ScapegoatEntity','poofAndDiscard'),span(I,'SpellRegistry',135,135,'SCAPEGOAT_registration'),status='support_only_not_effective',dedup='与006-02隐身/其他纯仇恨控制一致降支持0；不计为Boss免伤回执。')
add('iron-sacrifice-owner-recheck-and-direct-killed-removal-support',
 'Sacrifice预选仅自有IMagicSummon，onCast重取TargetEntityCastData并再次UUID比summoner，随后先范围爆破再remove(KILLED)，不走目标hurt。实际DeadKingBoss.sacrificialMarkHandler为ominous召唤物随机加Mark；Mark在LivingDeathEvent服务器回调爆破并remove。爆破目标伤害applyDamage返回未读，声光/摄像震动无条件。',
 '直接移除与伤害拒绝不同，预选成功文字不是最终接纳；存在先爆破后移除的实际源不应伪称已处理全部免疫。',
 '已有Ars Disintegration直接remove绕hurt家族，支持0；无客户端/AI/死亡事件顺序运行验证。没有测试重入或声明必然double explosion，也未制作/改变camera。',
 '注册SACRIFICE→checkPreCastConditions→onCast所属复核→doSacrificeExplosion→remove；SetSummonOwnerEvent→DeadKingBoss.sacrificialMarkHandler→Mark→LivingDeathEvent→onLivingDeath',
 ev(I,'SacrificeSpell','onCast'),ev(I,'SacrificeSpell','checkPreCastConditions'),ev(I,'SacrificeSpell','doSacrificeExplosion'),ev(I,'SacrificialMarkEffect','onLivingDeath'),ev(I,'DeadKingBoss','sacrificialMarkHandler'),span(I,'SpellRegistry',98,98,'SACRIFICE_registration'),span(I,'MobEffectRegistry',76,76,'SACRIFICIAL_MARK_registration'),status='support_only_not_effective',dedup='同直接remove绕hurt家族支持0，不凭来源武器/标记死亡变体再计；旧预选回执包也不重新计。')
rows[4]['decision_focus']={'lines':[640,655],'counting_rule':'The complete performImpact containing method is shared support with 004/005; the proposed independent site is only the minimum_distance fizzle decision, not another count for that entire method. Pending primary review; zero helper credit.'}
supplements=[]
'''
tail=s[s.index('assert len(rows)<=30'):].replace('006','007').replace("('001','002','003','004','005')","('001','002','003','004','005','006')")
tail=tail.replace('既有005注册网页全文观察支持0、原始资源TLS失败未重试。','既有005/006注册来源及TLS失败记录保留，未重试；真实隐身/通用AOE/直接移除同族主动降支持0。')
Path(__file__).with_name('build_batch_007.py').write_text(head+body+tail)
Path(__file__).with_name('verify_batch_007.py').write_text(Path(__file__).with_name('verify_batch_006.py').read_text().replace('006','007'))
