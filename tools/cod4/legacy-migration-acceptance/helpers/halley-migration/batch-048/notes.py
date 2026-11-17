# -*- coding: utf-8 -*-

add('cca-5.3.0-support-for-origins-apoli-copy-and-component-envelope',
whole('RespawnCopyStrategy.java')+whole('PlayerComponent.java')+whole('PlayerCopyCallback.java')+whole('CardinalComponentsEntity.java')+whole('CardinalEntityInternals.java')+whole('StaticEntityComponentPlugin.java')+whole('MixinServerPlayerEntity.java')+whole('MixinEntity.java')+whole('AbstractComponentContainer.java')+pick('ComponentsInternals.java','logDeserializationWarnings'),
'Origins046/Apoli047注册CHARACTER/ALWAYS_COPY后，玩家原生copyFrom RETURN触发CCA PlayerCopyCallback；实体原生writeNbt/readNbt调用容器持久化。',
'原实体component keys；lossless、keepInventory或spectator、original.switchingCharacter；各组件自己的NBT writer/reader。',
'按组件策略选择复制；旧componentId列表可读，当前compound envelope写出。此处只有依赖支持，独立建议0。',
'CHARACTER仅检查sameCharacter，不要求lossless；普通死亡未标记切换角色时与ALWAYS_COPY同样复制。回调取original.switchingCharacter的反值，并在原生copyFrom RETURN执行。INVENTORY检查lossless||keepInventory；默认非PlayerComponent为LOSSLESS_ONLY，PlayerComponent委托自身shouldCopyForRespawn。目标为CopyableComponent时走copyFrom，否则新建NBT执行from.writeToNbt/to.readFromNbt。因此只序列化组件writer中的字段，框架本身不提供永久字段白名单。StaticEntityComponentPlugin.after只登记依赖并交给builder，respawnStrategy登记到策略map。AbstractComponentContainer.fromTag先读旧LIST格式componentId，未知key或当前实体缺组件跳过；当前COMPOUND格式仅对本容器已注册key读取，随后remove已消费key，剩余只传logDeserializationWarnings。logger只是警告。toTag重新建立已注册组件的非空map，未发现把未知component payload保存入组件实例的隔离仓。旧list new Identifier未捕获非法ID异常。',
'补足046/047的外部Clone边界：永久历史应由具体组件writer明确筛选，不能把CHARACTER名称误当作只保留永久字段。读取未知数据应另留原样payload；不可把日志记录等同于保留。',
'这是匹配声明版本tag5.3.0的固定源码阅读，未运行mixin/native copyFrom或ASM生成顺序；after依赖如何最终排序不在本批完整审查内。没有断言任意模组都不会额外保留未知字段。不会把通用CCA实现作为新的Minecraft玩法迁移信用。',
'046/047已计候选的同链依赖；与038及其他CCA支持家族也重合。所有方法/策略/旧list分支均支持证据，不新增候选，不按策略拆条。')
