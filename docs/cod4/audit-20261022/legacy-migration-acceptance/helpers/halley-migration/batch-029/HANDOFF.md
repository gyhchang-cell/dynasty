# Halley → Kepler：第029批，credit0

官方Project MMO的CurseForge Source真实指向Caltinor/Project-MMO-2.0，固定1-20-1 `f83904c929457f5d36c384faa3125ee87b2900fd`。旧003中Harmonised7地址404仍保留排除。1条世界UUID XP真值家族，offline queue/levelCache/同步/死亡/重生支持均不拆计。

XP与scheduledXP存在overworld pmmo.dat，UUID→任意skill string→long codec保留未知技能键；解析只result().orElse(empty)非逐项partial，UUID primitive读取直接getOrThrow/fromString，不证明损坏数据安全回退。离线入队不dirty；登录先copy/remove队列后setXpDiff并忽略成功值，可取消事件失败不重排。没有磁盘事务或一次成功保证。

恢复数据追到实际RightClickItem等级不足取消、升级/perk、客户端镜像；levelCache为派生非持久，动态公式reload不先clear。世界UUID真值不依赖PlayerEvent.Clone；onRespawn仅执行SKILL_UP perks，onDeath有原玩法配置XP惩罚并写回同UUID，必须与Dynasty无新增死亡惩罚要求分开。

102完整方法+14字段116支持节点、18文件，非参考数。189来源文件只下载不计；Git tree/blob/source/AST/摘录哈希及parse错误0，主账机械primary匹配0。credit0/accepted=false待主责语义裁定。JSON保留未展开datapack/第三方perks/客户端通知/原生Codec等限制，不宣称全域或游戏验收。

继续030/031同固定PMMO来源：区块放置者归属→持久读取→离线农作/熔炉XP；vein玩家capability充能/恢复/消费与死亡边界。若只是共享codec/同链支持则不额外计；仍在实际审阅，不提前写credit。无游戏、编译、测试、屏幕操作或主账/生产/待办/原存档改动，十小时未完成。
