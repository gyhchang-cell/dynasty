# Halley batch-051 → Kepler

3条待审建议、1条未接线助手排除，credit0、accepted=false。固定官方wisp-forest/numismatic-overhaul tag0.2.19+1.20 commit `bff95760b08dc6a3237b80abb879e46a59be3e5b`，tree `21d495b7d45146c51fe54ae62fd346850842d461`。注意源码属性仍为mod_version0.2.18、MC1.20.1/CCA5.2.1，不能用tag名声称构建已对应发布jar。

建议分别为玩家已提交货币余额/死亡后Clone、钱袋双表示真实消费、owned shop持久库存+报价+资金+owner。Pawn与Shop恢复几乎同构，已合并一条；不按币种、方法数、download或字段计信用。

兼容int[]→long[]助手在固定Java树只见定义，没有发现玩法调用，excluded_records保留但不给候选。钱袋数组长度错误返回0，use仍会清袋；不声称容错保留。Shop旧未知Item变EMPTY会在Offer构造抛错，可能阻断后续owner/余额恢复；没有隔离未知报价。具体限制详见batch-051.json。

全方法范围/完整全文、源码SHA256/Git blob、摘录/归一hash与调用证据齐备，文档核对0解析/哈希错。外部CCA5.2.1/owo未完整展开、无运行验收。没有编译、测试、游戏、GUI、原存档或主账/生产/待办改动。十小时范围继续。
