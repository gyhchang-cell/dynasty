# Halley batch 013 — Akashic Tome / Morph-o-Tool 合并家族（credit0）

两官方仓库合并为 **1 条** 待审建议，不按repo、方法、alias表、书籍种类或工具损坏分支再计。固定官方1.20分支：AkashicTome@f64391e5f11f21dca339a08f82822be1e1cf7f34；Morph-o-Tool@c159b0d4e00b085512e807099aff98c1ddeb64fe。55完整方法仅链支持，28源文件不代表参考数量。完整source/tree/blob/方法范围原文及两级hash在JSON/JSONL，审计无hash/AST错误。主账机械匹配0不能替代Kepler语义审核。

完整链覆盖实际合成写入 → 手持真物品与嵌套集合切换 → 书GUI/方块使用/工具自动或滚轮选择 → 服务端换栈 → 拆出/工具损坏返回其余集合。当前形态保留在真实ItemStack，存回集合前剔除嵌套data以防递归；target记录却在ItemStack.of前被移除，失败回基础物品不保留该原始目标载荷。强制Count1是载体策略，不能移植为任意旧任务册的数量恢复规则。

别名实际仅关联用途mod，不是旧ItemStack.id注册映射；未见真实旧ID修复，不给alias条数信用。本地任务册应先确认映射/依赖，再无损保留id/Count/tag，不能为fallback先清旧记录。

实际差别保留为限制，不拿相似模板再计：Tome允许同mod多本书并写definedMod，但99次碰撞上限最后仍可覆盖，也会在assemble修改原target；Morph相同mod返回EMPTY且损坏时返回余集。Tome服务端按modid重算，Morph从客户端接收整个栈/slot，未完整验证源载荷/槽归属。两边rawComp为空的显示名fallback仍继续解引用null；拆出时删除整个display，原名字等不保证保留。

semantic-duplicate-review.json记录方法对照与合并决策。原生ItemStack.of内部未本批重新验读，边界只声明本mod对empty的分支及先删除顺序，不宣称所有缺失ID一定同样处理。GUI/网络仅源码阅读，未启动任何程序/客户端/服务器/编译/测试；未动原档、生产、主账、待办或用户实例。十小时与剩余范围未完成，继续后续选源。
