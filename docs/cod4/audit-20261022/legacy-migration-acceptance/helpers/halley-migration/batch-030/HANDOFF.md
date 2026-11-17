# Halley → Kepler：第030批，credit0

官方PMMO固定 `f83904c929457f5d36c384faa3125ee87b2900fd`，复用029来源。1条区块放置者归属完整家族：capability序列化/恢复→放置记录与dirty→活塞搬移/破坏清理→作物/熔炉实际XP消费，含非持久breaker传播支持。

Chunk codec的BlockPos键是packed-long十进制字符串，UUIDUtil值；失败result空Map无未知原项旁存。维度暗含在区块，载荷没检查坐标属于该chunk或当前方块仍是原对象。活塞先取全量再统一写目标可避免重叠，但Pre就删源且未确认实际运动成功。

修正原选源预期：作物仅在线归属者能获XP，不是离线农作补发；熔炉离线profile命中时new临时ServerPlayer而不读旧存档，通过029队列延后发。不能视为原装备/位置上下文恢复。跨界cascading crop在source chunk写新坐标、breaker邻位只查本chunk，均记录静态边界，未复现。

62完整方法+8字段70支持节点、19文件，非70参考；189复用文件无新下载信用。Git/blob/source/AST/摘录hash与parse错误0、主账机械primary匹配0。与029最终XP真值方法共享支持不重复计，持久placed map与瞬时breakMap同对象链合并。1建议credit0/accepted=false，Kepler最终裁定。

继续031 vein玩家charge capability真实持久化/恢复/消费和死亡边界，不按getter凑数。十小时未完成，无游戏、编译、测试、上游执行、屏幕或主账/生产/待办/原存档改动。
