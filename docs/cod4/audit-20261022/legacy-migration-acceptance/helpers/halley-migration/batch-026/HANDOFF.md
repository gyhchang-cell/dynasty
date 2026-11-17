# Halley → Kepler：第026批，credit0

官方 ActuallyAdditions 1.12.2固定 `12206a03a383a035758d6615c5da3ae32adaac81`，复用023源码、tree/blob。两条待合并建议，非自动接受：

1. 玩家接口UUID绑定：完整追放置绑定、探针捕获/取消与拷入、SAVE_TILE/SYNC恢复、SAVE_BLOCK排除、HUD、实际PlayerInvWrapper和充能。工具离线/sneak清理不会取消已经拷到Tile的绑定；read仅查UUID一半键且缺键不清旧值。getPlayer依当前世界UUID+范围，展示名不做主键；缓存wrapper被外部继续持有的后续校验未见。充能changed标志始终false、CustomEnergyStorage直接读无clamp，记录限制而非复现或修复结论。不是Clone。
2. 刷怪笼类型转换：捕获只存实体类型并杀原实体，非全实体快照；转换先从目标NBT删除SpawnPotentials/SpawnData再read/setEntityId，随后dirty/update、清工具载荷和消耗。载荷只检查非空，使用时未再校验注册/黑名单；主手取源与传入hand写回不一致，均仅静态观察。原生Spawner实际生成及失败行为未执行，不能声称全元数据或事务保障。

65完整方法+13字段共78支持节点，13文件；源/Git blob/摘录/AST hash及parse错误0，主账机械primary匹配0。字段数、黑名单条目、探针/多个capability均非额外参考。共享023–025基类和codec不加数，与MCA实体墓碑及玩家世界进度对象的语义边界见JSON。所有accepted=false/credit0，主责裁定。

研究继续，不启动游戏/编译/测试/屏幕，无主账/生产/待办/原存档改动。十小时和全部剩余范围未结束。
