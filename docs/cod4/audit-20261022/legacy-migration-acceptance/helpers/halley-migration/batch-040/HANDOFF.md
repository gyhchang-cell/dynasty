# Halley → Kepler：第040批，credit0

1条实际旧格式关系迁移：官方Requiem54281728d5f78944955a6e7b952ac4e0835129de。pre-beta14三个record类型别名归一entity_ref；entity_clerk refs首项→record；Mortician直接obelisk record改成独立NPC record，并在obelisk写PROJECTED_MORTICIAN指针。完整record读写/codec/维度有效性、实体baseTick、home AI、生成防重、失联衰退都合1链。

关键限制：新record存在但lookup失败不回退旧refs；迁移开关一次尝试后清，目标未就绪无每tick重试。未知字段/codec失败不是无损隔离，DataResult整record不插入；多个旧别名映射同键无merge。缺维度拒绝record。Runestone清同pos旧记录未比较dimension；非null UUID指向缺记录不新建，dirty触发未证明。均静态观察，无游戏复现。

124完整方法+42声明、23文件只是证据规模；Git/tree/blob/source/excerpt/normalized哈希0错误，主账primary机械匹配0，仍需语义审查。captured_souls/灵魂交易未沿完整链，0附加建议；非正式早期soulId预期已纠正。所有3别名、getter、codec支持同族不多计，credit0/accepted=false。

继续041玩家已见rift永久资格/实际菜单导航及042瓶装灵魂链；无游戏编译测试GUI主账生产待办原档修改，十小时未完成。
