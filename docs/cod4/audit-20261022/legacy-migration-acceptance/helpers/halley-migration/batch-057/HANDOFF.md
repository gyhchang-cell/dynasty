# Halley batch-057 → Kepler

2待审建议＋2排除，credit0/accepted=false。同053官方Betweenlands commit eafac1c217cdf304d477b025708e0dadf82b6953与真实tree/blob/source；未重复下载。

1. 旧蟹产物完整NBT恢复：三个tag全部null才服务器补抽，部分缺失/错型/空compound不触发；writer始终写三compound。真实捕获物品→解码实体→拆解台chop已追完；旧捕获载荷临时重建没有可见写回，每槽又重建，不能把实体重存幂等推成物品重读幂等。Silt/Bubbler仅换表同族合1。
2. Anadia嵌套物品载荷：部位产物/体型/宝物标志与物品绝对rottingTime恢复，真实腐坏决定拆解产物并禁止放生；熏制复制外层，再替换嵌套raw meat保Count但不保子栈tag/Damage。fishColour这里是活性/腐坏/熏制状态，非纯视觉换色；整鱼payload/期限/转换同链合1。Entity读setter会setHealth(max)，rottingTime不在entity writer，绝不把上游副作用移植为本项目回血或永久Clone字段。

排除：LastKilled cap消费者仅客户端模仿声音；GrubHub/WaterFilter的INVENTORY LEGACY SUPPORT只是实时旧库存API注释，不是存档迁移。方法/关键字/下载数均不计。

完整方法与具体触发/输入/输出/观察/限制/风险见JSON；文档核对0源hash/AST错误。174方法137字段仅支持规模。主账1239行只读快照：两建议主方法机械0匹配；两个排除的accessor/模板与已有支持匹配已保留，不能把0主方法匹配当语义接受。

不编译、不测试、不执行上游、不游戏/GUI/屏幕、不改主账生产待办原档。十小时最低时段仍未完成，继续独立对象审阅。
