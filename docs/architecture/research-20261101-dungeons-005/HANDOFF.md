# 第五批：住宅与同设计家族研究（2026-11-01）

实际研究8份本地NBT的32张新图，逐例记录布局、比例、立面、屋顶、材质、动线和地形。核对137个历史本地归档/成员组合，未见原文或旋转归一角色/占用完全相同；137不是有效建筑信用数。

F02云杉小屋与F03雪地小屋虽然哈希不同，仍是同一旋转/覆雪家族，只以F02提出一例。五个提案分属不同小住宅用途、规模，不合并成某范围5/1000。F05入口连接待核，F08仅厅廊附翼原则。

[逐例七方面研究](manual-review.json) · [提案及四视图证据](reference-proposals.json) · [家族排除](variant-family-audit.json) · [原始来源](sources.json) · [补剖面](detail-evidence.json) · [去重](dedup-evidence.json) · [实体池](interface-audit.json) · [验证](verification.json)

| 编号 | 原始设计 | 范围及决定 |
|---|---|---|
| F01 | [plains_cottage.nbt](F01-whole.png) | SCOPED_WHOLE_BUILDING_PROPOSAL：DUN05街区带院错层民居；36×26×44保存宅地，不覆盖整城、客栈或官衙。 |
| F02 | [spruce_cottage.nbt](F02-whole.png) | SCOPED_WHOLE_BUILDING_PROPOSAL：DUN05单主室带小阁层住宅；12×12×10，作为F02/F03家族唯一代表。 |
| F03 | [snow_cottage.nbt](F03-whole.png) | SAME_DESIGN_FAMILY_VARIANT：仅F02旋转/覆雪/局部改动的变体研究；无独立设计提案。 |
| F04 | [maison.nbt](F04-whole.png) | SCOPED_WHOLE_BUILDING_PROPOSAL：DUN05小型水院民居宅地；18×15×28，不覆盖忘川河或水关。 |
| F05 | [haunted_house.nbt](F05-whole.png) | HELD_COMPLETENESS_OR_ROUTE：高脚小厅与细塔的局部；地面入口连接待核，不计完整相关建筑。 |
| F06 | [explorer_cabin.nbt](F06-whole.png) | SCOPED_WHOLE_BUILDING_PROPOSAL：DUN05同层双翼住宅；30×22×28，不覆盖全街区或大型厅堂。 |
| F07 | [sorcerers_house.nbt](F07-whole.png) | SCOPED_WHOLE_BUILDING_PROPOSAL：DUN05低层L形小街宅；15×9×15，不含上腔路径或巫术机关验收。 |
| F08 | [wooden_manor.nbt](F08-whole.png) | SUBSPACE_PRINCIPLES_ONLY：DUN05厅廊附翼局部原则；29×46×48地上长宅，非完整判官内衙。 |

## 应用原则

- 先区分宅地、房体、屋盖和烟囱的占用，保存盒不当居室面积或净高。
- 单室阁层、错层带院宅、双翼住宅和水院住宅须各保留用途与规模，不能统一写作大型内衙。
- 原始哈希和角色几何均不同仍可能是同一设计家族，F02/F03按布局、阁层与烟囱对应只留一例。
- 实体拼接点不等于缺少房间；屋盖内门和高实体点不当可用上层入口。
- 短连续梯只证明该梯段存在，高脚屋仍需单独确认地面入口，不能因此宣称全楼可达。
- 学习空间与比例，不直接复制外来建筑，也不把欧式屋盖研究当中式风格验收。

正式义庄/墓园旧范围仍148/1000、缺852；COD6仍0。本批正式新增0，不开始新建筑制作，没有制作资产、任务或指南针同步完成的主张。不同范围不转借信用。

未运行Java、Gradle、游戏或网络；未重试429来源，未修改声音、亮度、用户存档、生产代码、模型、贴图、主清单或提示词。研究图是原始NBT的本地结构渲染，不代替原生材质、碰撞、地形或玩法验收。
