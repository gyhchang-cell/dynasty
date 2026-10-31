# -*- coding: utf-8 -*-
add('anthropophagy-paid-tethered-death-progress-copy-with-nonretained-protection-receipt',
pick('event/CopyCannibalLevelEvent.java','copyFromPlayer')+whole('component/entity/CannibalLevelComponent.java')+whole('component/entity/TetheredComponent.java')+whole('init/ModEntityComponents.java')+whole('item/TetheredHeartItem.java')+whole('item/KnifeItem.java')+whole('mixin/LivingEntityMixin.java')+whole('mixin/PlayerEntityMixin.java')+whole('Anthropophagy.java'),
'吃TetheredHeart建立持久tethered资格；玩家NBT组件读回；ServerPlayerEvents.COPY_FROM死亡分支检查旧tethered，复制cannibalLevel并重建属性。',
'CannibalLevel int、Tethered bool；old/new ServerPlayerEntity与alive；装备和现有UUID属性modifier。',
'普通lossless注册策略复制两组件；真实死亡时仅有旧tethered资格才手工复制等级，新玩家tethered没有在该事件复制。等级与有代价保护资格属于一条生命周期，不能拆两个信用。',
'两个CCA组件分别只读写一个标量，缺失归0/false；readFromNbt直接赋值，无版本、旧别名或范围限幅。注册两者均LOSSLESS_ONLY，而非ALWAYS_COPY。手工CopyCannibalLevelEvent只有!alive且old.TETHERED真时，将old等级赋给new.CANNIBAL_LEVEL，立即updateAttributes并sync；未赋new.TETHERED，构造默认false。因此从本地明确复制集合可见一次死亡后保留等级而不续同一保护标记，不能称无条件永久保留整个组件包。TetheredHeart.finishUsing在未tethered时置true、非creative扣1、增加使用统计和消息，随后super；usageTick半程会阻止已tethered重复使用。Knife sneaking使用先自伤攻击，再将已有tethered置false并掉普通PIGLUTTON_HEART；死亡dropEquipment也在tethered时掉普通心，不是原TETHERED_HEART。正常吃flesh在未tethered时加等级到MAX120，吃其他food减至至少0；tethered锁住这两种变化。恢复等级被canEquip阈值和jumpBoost直接消费，updateAttributes在server移除六个固定UUID旧modifier后按等级添加PersistentModifier，并把不允许装备copyAndEmpty后drop。readFromNbt本身不调用updateAttributes，不能把死亡重建和磁盘加载混为同一触发；原生属性另行持久化可能影响重登结果。',
'学习审定永久数值、可消费保护回执与派生属性的分层复制：Clone只列明允许保留的进度，不把一次性保护、状态或整个ForgeData续过去。研究现存死亡意图后才能决定永久任务历史白名单，不能直接复制上游收费保护机制。',
'版本为MC1.20.6-r1/CCA6.0.0；未展开匹配CCA6外部实现，不能拿048的5.3.0补证当作本版本执行证明。原生event与CCA复制的实际时序、多模组覆盖、NBT/属性重登一致性未测试。上游条件式丢等级是设计观察，不得变成本任务新增死亡惩罚。read/set不限制非法负值或大于120；updateAttributes会掉不合规装备且不核drop成功，不应在迁移时盲目调用有此副作用的rebuild。Food/Heart/Knife若无server guard不能声称仅server变更。',
'同一等级+付费tether保护回执+死亡复制一链，六属性和两个组件支持方法不拆计。与TAN037/其他保留历史门槛主题相近但具体状态/选择和可消费receipt不同，Kepler最终核查是否已包含同源/移植家族；credit0、pending。')
add('excluded-anthropophagy-piglutton-persisted-combat-behavior-is-not-permanent-player-progress',
pick('entity/PigluttonEntity.java','readCustomDataFromNbt')+whole('entity/PigluttonEntity.java'),
'Piglutton原生实体持久化及tick行为；不是玩家Clone永久进度恢复。',
'CanAttack/DamageTaken/FleeDistance/OverhealAmount/StalkTicks/FleeingTicks。',
'实体重载恢复战斗/逃离计时，缺FleeDistance用6；不提交独立迁移建议。',
'完整writer/reader保存敌对生物行为参数。reader仅FleeDistance有contains缺值6，其他按类型默认；mobTick递减fleeingTicks，在400计时降至160时discard，startFleeing直接160下一tick159不会同分支discard；modifyAppliedDamage累积伤害超过20触发普通逃离，runAwayAndDespawn设400并扩大距离64。属于明确临时战斗AI状态在实体自身持久化，不是玩家历史或受保护物品恢复。',
'作为反例说明NBT持久化不等于可复制到玩家死亡后的永久进度；临时逃跑/伤害累计不纳入本项目Clone白名单。',
'完整AI目标子类未展开，无法把所有读回字段到行为消费者当作迁移候选。本批只保留整类来源以说明排除，不按字段/默认分支增加数量。',
'排除当前player-progress迁移对象语义不足；临时AI实体存储不包装成永久Clone实现，独立候选0。')
