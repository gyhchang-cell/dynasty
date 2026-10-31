add('excluded-playerrevive-nbt-client-sync-and-inmemory-combat-clone-without-durable-recovery-wiring',
 pick('/cap/Bleeding.java','serializeNBT deserializeNBT')+whole('/cap/Bleeding.java')+whole('/server/PlayerReviveServer.java')+whole('/server/ReviveEventServer.java')+whole('/api/CombatTrackerClone.java')+
 whole('/packet/ReviveUpdatePacket.java')+whole('/mixin/PlayerMixin.java')+whole('/mixin/ServerPlayerMixin.java')+pick('/PlayerRevive.java','PlayerRevive init registerCaps serverStarting'),
 '仅作为排除证据。官方CreativeMD/PlayerRevive固定86d09e722287a4cb5b7655c902dabd8eebc6959f、branch1.20、mod2.0.31。完整阅读NBT发送接收、能力挂接、出血/重生死亡消费者和combat tracker快照，未找到持久恢复或玩家Clone调用。',
 'Bleeding.serializeNBT仅timeLeft/progress/bleeding/consumed，downedTime/lastSource/trackerClone/revivingPlayers未写；IBleeding extends INBTSerializable只是接口。PlayerReviveServer.startBleeding另根PersistentData写playerrevive:bleeding=true，resetPlayer删除。',
 'ReviveUpdatePacket构造唯一显式serialize调用，executeClient按entityUUID找当前客户端玩家后deserialize；服务端executeServer为空。attachCapability挂匿名ICapabilityProvider，只有LazyOptional/getCapability，没有ICapabilitySerializable或serialize/deserialize转发；源码未见存盘回读Bleeding的接线。整个官方Java源码搜索未见该PersistentData标志reader，只有put/remove；不据名字推断资格恢复。',
 'knockOut保存DamageSource及CombatTrackerClone内存快照，snapshot构造复制entries及combat时刻/标志，kill在当前玩家死亡前overwriteTracker用于伤害归因，非旧玩家→新玩家的PlayerEvent.Clone。playerLeave若出血主动kill，revive/kill清helper、PersistentData flag、强制pose；这是一条当前会话救援状态机。nbt缺字段直接get默认，计时不clamp，客户端同步不等于永久进度持久。',
 '作为负面筛选借鉴：不能因serializeNBT、INBTSerializable、PersistentData或Clone类名就当持久迁移证据；必须追真实存档回调与新玩家恢复消费者。Dynasty永久字段需要真实Clone接线和白名单，不能搬出血计时、pose、tracker或临时免疫/命令权限。',
 '依赖Forge/CreativeCore及原生Player持久层未完整展开，结论限本固定仓库未读到持久回读接线，不能断言所有集成环境必定不保存。PlayerReviveServer.kill含配置banPlayerAfterDeath政策，绝不应用Dynasty，未执行任何死亡/ban动作。Darkhax-Minecraft/PlayerRevive旧404排除仍有效；正确官方来源不作为对旧URL的虚构修复信用。',
 '所有NBT接口/网络/Capability/CombatTrackerClone合1排除链，0条迁移建议、0信用。普通复活玩法/内存damage快照不凑成持久迁移。')
