# Halley → Kepler：第028批，credit0

官方Reskillable release/1.12.2固定 `34b9efe3e61dc5a5db6685cec63cc62e2111434d`。CurseForge官方Source经Lanse505/Skillable-2实际重定向本仓；母项目与其他版本不再计。仅一份PlayerPersisted技能档家族。

已完整追PlayerPersisted/SkillableData.SkillLevels的level/skillPoints/unlockables读写、弱引用缓存实例交接、登录/END tick、实际等级/解锁包saveAndSync、装备与世界交互锁、永久特性激活。Skill/Unlockable现行写dot→读colon是编码，不据此宣称完整旧namespace迁移；没有显式Clone回调，未验证原生跨死亡复制。

未知技能/trait会被重写新compound抹掉，解锁只看键存在而不读布尔值；缺skill键不清内存旧值，getLevel才clamp。缓存key是player.hashCode移位而非UUID，WR不一致会把旧缓存快照灌给新对象，这不是可靠Clone实现。TraitUndershirt永久解锁在PlayerPersisted，防致死CD另在根entityData，支持本任务永久白名单和临时状态应分离的结论；不改生产死亡规则。

166完整方法+14字段180支持节点、21文件，非参考数。99固定来源文件下载不是99研究数；Git/blob/source/AST/摘录hash和parse错误0，主账机械primary匹配0。整体1建议accepted=false/credit0，Kepler最终语义去重。没有游戏/编译/测试/图形/上游执行或主账/生产/待办/原存档修改。后续029官方PMMO固定源已取，仍为未审候选，十小时继续未结束。
