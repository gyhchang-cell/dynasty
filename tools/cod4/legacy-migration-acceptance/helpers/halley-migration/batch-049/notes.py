# -*- coding: utf-8 -*-

add('pal-1.9.0-support-for-apoli-legacy-source-revocation',
whole('SimpleAbilityTracker.java')+whole('AbilitySource.java')+whole('PlayerAbility.java')+whole('VanillaAbilities.java')+whole('VanillaAbilityTracker.java')+whole('ServerPlayerEntityMixin.java')+whole('PlayerAbilityView.java')+whole('PalInternals.java')+whole('Pal.java'),
'Apoli047 PlayerAbilityPower.onAdded撤销旧apoli:power_source，然后其后续serverTick恢复当前powerType来源；PAL原生NBT及copyFrom hook为依赖边界。',
'玩家已注册ability trackers；来源ID列表ability_sources；playerabilitylib:abilities[{ability_id,...}]；当前gamemode、其他来源、enable callbacks。',
'来源集合恢复和逐来源撤销；失去最后来源立即更新实际原生能力；PAL自身只在copyFrom alive为true时序列化复制。独立建议0。',
'AbilitySource.grantTo/revokeFrom直接调用对应tracker.addSource/removeSource。SimpleAbilityTracker.load逐个注册表lookup来源并addSource，不先clear现有集合；未知来源仅warn，不保留原样。来源registerSource以Identifier驻留同一实例，显式冲突priority抛错；来源不能因NBT中出现而自动创建。addSource即使enable callback拒绝仍保留来源，只有集合首次非空时尝试enable；refresh再按各来源callback求shouldBeEnabled。removeSource只移除指定来源，其他模组来源不清空，但最后来源移除立即updateState(false)/sync。VanillaAbilityTracker把状态写到真实PlayerAbilities，并按gamemode融合；ALLOW_FLYING setter会flying &= allowFlying，因此生存玩家失去最后飞行来源可同时停止飞行。PAL服务端mixin原生writer输出各tracker，reader未知ability只warn；copyAbilitiesAfterRespawn仅alive分支写旧/读新，不能称PAL自身无条件死亡复制。refreshAll排除易变FLYING，并可合并一次原生sendAbilitiesUpdate；Apoli自己的CCA power重建和后续tick授权是另外生命周期，不能误认为与旧source撤销原子完成。',
'为047旧来源迁移提供完整依赖证据：以source身份精确撤销，永久资格与派生飞行状态分开，刷新应可重入；若需要无缝切换须明确解决先撤销后授权的间隔及未知来源隔离，不直接照搬。',
'固定tag1.9.0与Apoli声明版本对应，但没有发布jar构建重现、mixin执行顺序或游戏验证。原生gamemode和其他mod callback可改变实际结果，不能保证飞行连续。通用PAL不作为独立玩法迁移候选。PalInternals.loadConfig完整方法仅作上下文，没有运行。',
'严格为047 PlayerAbilityPower候选的外部支持，PAL NBT/注册/Clone/refresh均不得再各计信用；与046共享CCA链也不能包装为新候选。')
