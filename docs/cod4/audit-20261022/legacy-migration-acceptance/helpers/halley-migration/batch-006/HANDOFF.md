# Halley 第六批：两条独立 owner 链建议，credit0

文件 `batch-006.json`、`reviewed-suggestions.jsonl` 保存完整方法范围/源码文本、固定commit/tree/blob、源SHA256、摘录SHA256、AST规范化SHA256与具体观察/应用/限制/重复风险。`document-integrity.json` 为静态证据核对；不代表游戏测试。两条均未accepted，主账最终信用由Kepler确定。

- **SoL食物历史集合与派生生命**：`Cazsius/Spice-of-Life-Carrot-Edition@37c243c5bcf50d5582ce81596e85b3f465b222a8`，官方1.20分支。foodList注册ID集合读写→按resetOnDeath策略Clone→Respawn同步与当前配置重算固定UUID生命modifier，整链一条。默认不重置。仍注册但不再可食用的历史可保留，当前过滤决定收益；原注册查询返回null则丢失该引用，不提供旧别名。未读ForgeRegistry默认项内部，不把null guard误说成任何缺失ID都一定返回null。reader先clear，坏字符串可使恢复中断；这不是安全事务模板。
- **Diet按suite定义恢复、死亡公式与效果清理索引**：`illusivesoulworks/diet@c737eab4b0024bd245a71aa8e90fb188bc1874a3`，官方1.20.x分支。各组值、Active、Eaten、Modifiers写盘，但Clone仅复制逐组值、Active及非死亡时Modifiers，不复制Eaten/suite；suite本身未写入该持久格式。每80tick清旧UUID并按当前组条件重加效果，是实际游戏属性消费，不是仅UI。默认死亡AMOUNT/loss100是该模组自己的惩罚，**不借机为Dynasty新增惩罚**。构造初始化组集合后load只replace，定义缺失/未知组/格式错误边界已列。

每物品、每组、公式各分支、condition枚举、getter、网络与跨平台移植均不另计。底层方法和字段是支撑，不是参考数；字段声明单独source_declarations，与完整方法分开。与其他玩家能力Clone和派生属性家族仍须主责语义去重，首方法哈希未撞主账不能替代语义审核。

未编译、未执行上游代码、未启动游戏/服务器/GUI，不触原存档、主账、生产、主待办。无需游戏QA。本批交付后继续后续来源，未宣称十小时范围完成。
