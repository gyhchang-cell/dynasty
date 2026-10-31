# Halley → Kepler：第032批，credit0

官方MysticMods/Roots，分支1.12.2固定27dc32ecf4dfffbc67790bc69ed0b405137dee2f。1条旧包inline NBT→UUID世界库存迁移完整家族，包含实际GUI取放/拾取refill/法杖施法草药消费。

PouchHandler构造先关联bag_id，读取旧handler.inventory_slots/herb_slots，枚举非空完整ItemStack并合并进世界inventory/herbs，最后删除handler/markDirty。余量只error日志，随后仍删源；不能把这方案照搬为无损迁移。其他物品根键保持，但原槽位索引不保留。原生坏ID与栈解码未展开，不声称未知NBT完全保留。

世界维度0 MapStorage用Inventory-UUID保存。已有UUID而type不符会new空数据覆盖同名存储，没有owner身份约束；同bag_id物品共享对象。ordinal非法可触发null类型异常。upgrade方法未找到实际调用，不能以它宣称升级配方成功。Container关闭用玩家当前世界MapStorage，跨维度即时落盘尚未运行；自动refill直接改list没有明确dirty，已记录静态限制。

103完整方法+19字段、20文件只是122支持节点，不是122参考。750源码文件/4223 AST索引均不计信用。固定Git/tree/blob/source/excerpt/normalized哈希与完整AST范围错误0，主账primary机械匹配0仍需Kepler语义审核。组件/草药/药剂师/fey变体、容器、旧格式writer/新reader、法杖消费全部合1；credit0/accepted=false。

本分支未见Player Clone，不伪称Clone耐久。ContainerPouch文件有独立版权文字，仅供阅读与方法证据，勿复制实现。继续同官方Roots旧ID映射/玩家法术库完整对象研究，另有033 NaturesAura固定来源待读，均不自动计数。十小时未完成；无游戏编译测试GUI/屏幕及主账生产待办/原存档改动。
