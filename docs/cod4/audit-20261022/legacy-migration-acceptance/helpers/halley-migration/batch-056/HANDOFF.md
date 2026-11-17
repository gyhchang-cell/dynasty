# Halley batch-056 → Kepler

2条待审建议、1条排除，全部credit0/accepted=false。沿用053官方The Betweenlands固定commit eafac1c217cdf304d477b025708e0dadf82b6953、tree 194e44209e5494bc78378963e15cbfc8ba944373和原始source/blob；没有重复下载计数。

1. 区域共享战利品：容器持久StorageID连接共同pool，恢复已分配数量、种子和保底次数。生成前先清容器LootTable，扣共享量后填槽，部分填充失败不退款；item匹配未核NBT/metadata，临时EntryKey不比较poolRoll，空栈分支重复iterator.remove。storage原始lootSeed未保存（已建pool自身seed有保存），不能称所有未来pool随机状态无损。pot/chest、种子、保底、refill/regenerate全部同链合1。
2. 真正蟹笼生产：tile捕获timer和本地fraction/时间戳连接持久区域预算、卸载票据保留量；每20tick实际消费推进后捕获实体变物品。OwnerUUID读要求STRING而writer setUniqueId、重新new TokenBucket后reader未重绑world/pos，是明确恢复边界；不声称外部原生加载顺序已动态验证。所有token类只是这个真实玩法对象的支持，不计通用限流/缓存信用。

排除：SpiritTreeKillToken只定位到真实击杀生产、列表读写，未找到玩家进度/领取等玩法消费者，0信用；不因kill/token/NBT字样纳入。

完整方法/具体观察与限制/去重风险见JSON。文档核对0哈希或AST错误；190方法、184字段仅支持规模，绝非有效实现数。主账1237行只读快照主方法机械0匹配仍需语义去重。本批未完整读巨型tower生成方法（截断），明确只选完整的小绑定/入口方法。

无编译/测试/上游执行/游戏/服务器/屏幕操作；不改主账、生产、待办或原档。十小时最低时段尚未结束，继续实际其他独立数据对象审阅。
