# -*- coding: utf-8 -*-
add('levelz-player-skill-profile-reload-reconciliation-selective-clone-and-derived-attribute-rebuild',
pick('level/LevelManager.java','readNbt')+whole('level/LevelManager.java')+whole('level/PlayerSkill.java')+whole('level/Skill.java')+whole('level/SkillAttribute.java')+whole('init/EventInit.java')+whole('init/LoaderInit.java')+whole('data/SkillLoader.java')+whole('util/PacketHelper.java')+whole('util/LevelHelper.java')+whole('network/LevelServerPacket.java')+whole('config/LevelzConfig.java')+whole('mixin/player/PlayerManagerMixin.java')+pick('mixin/player/PlayerEntityMixin.java','readCustomDataFromNbtMixin writeCustomDataToNbtMixin attackMixin')+whole('mixin/player/ServerPlayerEntityMixin.java')+whole('LevelzMain.java'),
'PlayerEntity原生read/write TAIL；服务端JOIN、COPY_FROM和AFTER_RESPAWN；成功数据包重载后refreshSkills及属性重建。',
'根级Level/LevelProgress/TotalLevelExperience/SkillPoints和Skills[{Id,Level}]；当前数据包整数技能ID及maxLevel；alive与levelRetainPercentage/resetCurrentXp配置。',
'恢复已注册技能，补新技能0级、校正负等级或退还超上限点数；按存活返回/死亡政策复制进度并重建临时属性modifier；未知旧技能不隔离，数字ID无别名映射。',
'LevelManager.readNbt从NBT标量直接读取，Skills为COMPOUND列表；PlayerSkill构造读int Id/Level，未注册ID直接continue，重复ID后项覆盖，未先清空现有map。只有非有限LevelProgress修正0，其他标量未统一非负约束。refreshSkills仅遍历当前SKILLS，缺项补0、负等级归0；不允许高等级时超过当前maxLevel的差值退回skillPoints并截断，未遍历删除旧map中已移除技能。SkillLoader读取数据包显式数字id，检查连续ID，key只用于语义/显示/attribute标识；持久化只有Id，无旧新ID别名或版本标记，重排复用ID可能错配。原生COPY_FROM只有alive复制；死亡AFTER_RESPAWN保留率100默认走完整profile复制，resetCurrentXp默认true清当前progress/totalXp；小于100分支按float比例截断整体等级、未用点及各技能，再按HashMap迭代分配剩余点，未证明跨保存稳定顺序。PacketHelper.updatePlayerSkills复制五项明确数据，但setPlayerSkills直接赋旧map引用，不是深拷贝。PlayerEntity的killedMobsInChunk/killedMobChunk等瞬态字段未被该profile链复制。JOIN/重生/成功数据包重载重新按已恢复技能更新属性；LevelHelper先移除同skillKey临时modifier再添加值=每级系数*当前等级，并可重设base，避免重复叠加当前同ID。物品使用/攻击真实读取所需技能，等级实际参与解锁；服务端StatPacket检验点数和技能上限后修改profile并重建属性。首次连接只有原生optional玩家NBT为空才发startPoints，已有存档缺LevelZ键不等同首次连接。',
'参考永久进度显式字段复制、数据定义变化后的限幅退款、重登后派生属性重建；任务历史应保留稳定ID并隔离未知旧值，而不是照搬整数ID过滤。避免拷贝整个entity数据，明确区分永久资格与可重算属性。',
'固定MC1.21.1/mod2.0.12源码，不是本项目直接可移植实现。没有显式旧别名兼容，不能声称旧技能全集保留。allowHigherSkillLevel允许保留超上限；重载不移除旧key modifier/旧playerSkills，旧定义改key或删技能可能留旧态，未实测。百分比死亡是上游可配置设计，不得作为本任务增加死亡惩罚；只能借鉴边界划分。NBT read重入及浅map别名并不保证副作用隔离；未执行原生事件/mixin/网络/属性验收。所有writer/Clone/reload/消费方法共一条profile链。',
'与Reskillable028、PMMO029、PST003共有玩家技能永久进度主题，但这里具体整数ID→当前数据定义校正/超限退款、alive及保留百分比分支、浅map复制和重建modifier是实际对象语义。Kepler需按现有同对象/移植家族去重；绝不按技能数、restriction类别、方法或版本拆credit。')
add('excluded-levelz-clumped-experience-orb-derived-family',
pick('entity/LevelExperienceOrbEntity.java','readCustomDataFromNbt')+whole('entity/LevelExperienceOrbEntity.java')+whole('init/EntityInit.java')+pick('mixin/player/PlayerEntityMixin.java','dropXp')+whole('mixin/player/ServerPlayerEntityMixin.java'),
'真实掉落等级经验球native实体NBT保存/读回、合并、年龄到期、拾取进度兑换。',
'Health/Age/Value短整型、Count整数、可选clumpedMap字符串数字key→次数。',
'有clumpedMap按map恢复；没有则旧Value+Count重建map；拾取逐桶value*count向玩家profile授权后discard。不提交新候选。',
'完整实体类注明Clumps启发。reader无clumpedMap时以旧amount/pickingCount为一桶，有map则Integer.parseInt逐key无捕获；setClumpedMap重新汇总value*count到amount，可能int溢出。Count至少1，但map空时amount默认1，负map值/次数未过滤。writerValue为short，会截断汇总总量，但保存map中每桶int可在当前reader重算。merge合并每value计数，discard被合并orb，年龄取较小；wasMergedIntoExistingOrb更新map后pickingCount却由先前clumpedMap计算，后续拾取真正用map。onPlayerCollision仅server、pickupDelay0且orbAge>20，逐map桶授权后discard；tick年龄6000到期；target追踪不持久化。真实dropXp由resetCurrentXp控制，不能为进度恢复额外制造返还。',
'支持理解未领取奖励的旧单值→多桶恢复边界及应核查的数值守恒，但不计本批独立建议。',
'主账已有native-unclaimed-experience-orb-merged-count-and-redemption-restoration和relics经验球家族；本实体明显原生经验球/Clumps衍生，高重复风险。即使多桶表示有差异，也先排除，不凭对象命名换皮凑数。Clumps原实现未另取源码比对，因此不能宣称完全逐行同源或独立发明。没有原子跨实体/玩家存档保证。',
'排除：原生经验球和Clumps衍生同族风险；同一实体的reader/writer/merge/consumer只是一链，独立候选0/credit0，是否值得主责另核仅供提示。')
