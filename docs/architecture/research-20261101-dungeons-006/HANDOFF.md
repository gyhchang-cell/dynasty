# 第六批：四份前哨资料及范围排除

实际查看4份本地NBT的16张新研究图，记录七方面观察，核查145个历史归档/成员组合。没有完全重复，不等于对当前范围有效；本批提案0、正式信用0。

[逐例观察和四视图哈希](manual-review.json) · [来源](sources.json) · [补剖](detail-evidence.json) · [去重](dedup-evidence.json) · [外接池](interface-audit.json) · [验证](verification.json)

| 编号 | 设计 | 不计入既有三个范围的理由 |
|---|---|---|
| F01 | [data/trek/structures/overworld/medium/desert_outpost.nbt](F01-whole.png) | 沙地内围小水池且保存五条热带鱼实体；十二个jigsaw全是悦灵/卫道士/掠夺者实体池，不是缺十二间房。可学单塔营地层次，但不进入已有三个限定范围。 |
| F02 | [data/trek/structures/overworld/medium/jungle_outpost.nbt](F02-whole.png) | 完整草泥营地有小水池；八个接口为掠夺者、熊猫和鹦鹉实体池，无房间待拼。可学营地遮挡控制，不计近地四哨棚、双高塔或角塔连L厅。 |
| F03 | [data/terralith/structures/regular/desert_outpost.nbt](F03-whole.png) | 沙地基裙无jigsaw，主屋及低厅不需外接房池；可留小驻守屋与外廊比例原则，不为既有高角塔范围借用计数。 |
| F04 | [data/terralith/structures/unsorted/villager_outpost.nbt](F04-whole.png) | 土草路径基裙无jigsaw，未缺房间；可作DUN05小街屋上下厅、外廊的局部原则，不因outpost文件名就计DUN03军哨范围。 |

## 学习原则

- 树冠、仙人掌、实体接口与人工哨棚/石柱/房间分别识别，不能拿植物制造建筑数量。
- 同叫outpost，单塔营地、树下篱院、低屋廊组和村民站屋用途与尺度不同。
- 低主屋带侧棚不能借高角塔连厅的门槛，单塔也不能借双高塔门槛；保留不适用记录。
- 研究资料可以有用但不计入当前范围，不能为了数字把相似词汇和完整模板直接当有效参考。

[三类正式参考范围](../research-20261101-scoped-outpost-ledger/HANDOFF.md)各仍1/1000、缺999；原义庄/墓园148/1000、缺852，COD6仍0。没有为了增加数字将不同用途、规模的资料并入。

本批没有开始制作、修改生产程序/模型/贴图/任务/指南针/主清单，也没删提示词。未运行Java、Gradle、游戏或网络；未动声音、亮度、用户存档。研究图是本地NBT分类整方块投影，不是原生材质、碰撞或玩法验收。
