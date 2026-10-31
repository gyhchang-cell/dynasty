# -*- coding: utf-8 -*-
"""Own static evidence rendering. Does not execute any upstream program."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
T=Path(__file__).resolve().parent
notes={48: '''
add('cca-5.3.0-support-for-origins-apoli-copy-and-component-envelope',
whole('RespawnCopyStrategy.java')+whole('PlayerComponent.java')+whole('PlayerCopyCallback.java')+whole('CardinalComponentsEntity.java')+whole('CardinalEntityInternals.java')+whole('StaticEntityComponentPlugin.java')+whole('MixinServerPlayerEntity.java')+whole('MixinEntity.java')+whole('AbstractComponentContainer.java')+pick('ComponentsInternals.java','logDeserializationWarnings'),
'Origins046/Apoli047注册CHARACTER/ALWAYS_COPY后，玩家原生copyFrom RETURN触发CCA PlayerCopyCallback；实体原生writeNbt/readNbt调用容器持久化。',
'原实体component keys；lossless、keepInventory或spectator、original.switchingCharacter；各组件自己的NBT writer/reader。',
'按组件策略选择复制；旧componentId列表可读，当前compound envelope写出。此处只有依赖支持，独立建议0。',
'CHARACTER仅检查sameCharacter，不要求lossless；普通死亡未标记切换角色时与ALWAYS_COPY同样复制。回调取original.switchingCharacter的反值，并在原生copyFrom RETURN执行。INVENTORY检查lossless||keepInventory；默认非PlayerComponent为LOSSLESS_ONLY，PlayerComponent委托自身shouldCopyForRespawn。目标为CopyableComponent时走copyFrom，否则新建NBT执行from.writeToNbt/to.readFromNbt。因此只序列化组件writer中的字段，框架本身不提供永久字段白名单。StaticEntityComponentPlugin.after只登记依赖并交给builder，respawnStrategy登记到策略map。AbstractComponentContainer.fromTag先读旧LIST格式componentId，未知key或当前实体缺组件跳过；当前COMPOUND格式仅对本容器已注册key读取，随后remove已消费key，剩余只传logDeserializationWarnings。logger只是警告。toTag重新建立已注册组件的非空map，未发现把未知component payload保存入组件实例的隔离仓。旧list new Identifier未捕获非法ID异常。',
'补足046/047的外部Clone边界：永久历史应由具体组件writer明确筛选，不能把CHARACTER名称误当作只保留永久字段。读取未知数据应另留原样payload；不可把日志记录等同于保留。',
'这是匹配声明版本tag5.3.0的固定源码阅读，未运行mixin/native copyFrom或ASM生成顺序；after依赖如何最终排序不在本批完整审查内。没有断言任意模组都不会额外保留未知字段。不会把通用CCA实现作为新的Minecraft玩法迁移信用。',
'046/047已计候选的同链依赖；与038及其他CCA支持家族也重合。所有方法/策略/旧list分支均支持证据，不新增候选，不按策略拆条。')
''',49: '''
add('pal-1.9.0-support-for-apoli-legacy-source-revocation',
whole('SimpleAbilityTracker.java')+whole('AbilitySource.java')+whole('PlayerAbility.java')+whole('VanillaAbilities.java')+whole('VanillaAbilityTracker.java')+whole('ServerPlayerEntityMixin.java')+whole('PlayerAbilityView.java')+whole('PalInternals.java')+whole('Pal.java'),
'Apoli047 PlayerAbilityPower.onAdded撤销旧apoli:power_source，然后其后续serverTick恢复当前powerType来源；PAL原生NBT及copyFrom hook为依赖边界。',
'玩家已注册ability trackers；来源ID列表ability_sources；playerabilitylib:abilities[{ability_id,...}]；当前gamemode、其他来源、enable callbacks。',
'来源集合恢复和逐来源撤销；失去最后来源立即更新实际原生能力；PAL自身只在copyFrom alive为true时序列化复制。独立建议0。',
'AbilitySource.grantTo/revokeFrom直接调用对应tracker.addSource/removeSource。SimpleAbilityTracker.load逐个注册表lookup来源并addSource，不先clear现有集合；未知来源仅warn，不保留原样。来源registerSource以Identifier驻留同一实例，显式冲突priority抛错；来源不能因NBT中出现而自动创建。addSource即使enable callback拒绝仍保留来源，只有集合首次非空时尝试enable；refresh再按各来源callback求shouldBeEnabled。removeSource只移除指定来源，其他模组来源不清空，但最后来源移除立即updateState(false)/sync。VanillaAbilityTracker把状态写到真实PlayerAbilities，并按gamemode融合；ALLOW_FLYING setter会flying &= allowFlying，因此生存玩家失去最后飞行来源可同时停止飞行。PAL服务端mixin原生writer输出各tracker，reader未知ability只warn；copyAbilitiesAfterRespawn仅alive分支写旧/读新，不能称PAL自身无条件死亡复制。refreshAll排除易变FLYING，并可合并一次原生sendAbilitiesUpdate；Apoli自己的CCA power重建和后续tick授权是另外生命周期，不能误认为与旧source撤销原子完成。',
'为047旧来源迁移提供完整依赖证据：以source身份精确撤销，永久资格与派生飞行状态分开，刷新应可重入；若需要无缝切换须明确解决先撤销后授权的间隔及未知来源隔离，不直接照搬。',
'固定tag1.9.0与Apoli声明版本对应，但没有发布jar构建重现、mixin执行顺序或游戏验证。原生gamemode和其他mod callback可改变实际结果，不能保证飞行连续。通用PAL不作为独立玩法迁移候选。PalInternals.loadConfig完整方法仅作上下文，没有运行。',
'严格为047 PlayerAbilityPower候选的外部支持，PAL NBT/注册/Clone/refresh均不得再各计信用；与046共享CCA链也不能包装为新候选。')
'''}
for n in (48,49):
 b='batch-%03d'%n;base=T/b
 (base/'notes.py').write_text('# -*- coding: utf-8 -*-\n'+notes[n])
 review=(T/'batch-047/review.py').read_text().replace('batch-047',b)
 review=review.replace("status='helper_reviewed_pending_coordinator'","status='dependency_support_only_not_new_credit'")
 review=review.replace("'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\\n' for x in rows))","'dependency-support.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\\n' for x in rows))")
 review=review.replace("'reviewed_chains':len(rows)","'reviewed_chains':0,'support_chain_count':len(rows)")
 review=review.replace("'records':rows","'records':[],'support_records':rows")
 review=review.replace("print('Hand-reviewed families',len(rows),'helper credit 0; document rendering only')","print('Support-only chains',len(rows),'new suggestions 0, credit 0')")
 (base/'review.py').write_text(review)
 audit=(T/'batch-047/record-document-integrity.py').read_text().replace('batch-047',b).replace("rows=batch['records']","rows=batch['support_records'];assert batch['records']==[]")
 audit=audit.replace("'reviewed_chains':len(rows)","'reviewed_chains':0,'support_chains':len(rows)")
 (base/'record-document-integrity.py').write_text(audit)
print('048/049 support-only notes and renderer prepared')
