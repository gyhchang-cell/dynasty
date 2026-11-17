# 第八批：矿业空间与完整建筑边界

实际查看4份本地模板的16张新研究图和2张历史对照图，逐例记录七方面观察，筛查157个历史归档/成员组合。没有将组合数、图片数、炉桶数或矿石数转成建筑计数。

**1份DUN02小型覆顶维修/储料工作棚提案，正式新增0。** 裸梁操作跨、露天矿坑和晶洞附属设施各留研究记录，不作为三份完整建筑提案。

[逐例观察](manual-review.json) · [完整提案](reference-proposals.json) · [原始来源](sources.json) · [补剖和梯段](detail-evidence.json) · [历史去重](dedup-evidence.json) · [接口](interface-audit.json) · [陈设与顶层原始状态](fittings-and-cover.json) · [验证](verification.json)

| 编号 | 来源 | 用途/规模与决定 |
|---|---|---|
| F01 | [data/terralith/structures/underground/largeminingoutpost.nbt](F01-whole.png) | DUN02小型低平顶矿业维修/储料工作棚；12×6×9，单层，不覆盖巨型工坊或完整矿场。 |
| F02 | [data/terralith/structures/underground/smallminingoutpost.nbt](F02-whole.png) | 开放梁框/附属储料操作跨，未作为完整覆盖工坊提案；不凭同池第二个NBT另计。 |
| F03 | [data/kaisyn/structures/village/exclusives/piglin/houses/piglin_mine_1.nbt](F03-whole.png) | 露天采掘坑及人工边缘设施，仅地形和高差研究。 |
| F04 | [data/kaisyn/structures/village/exclusives/piglin/houses/piglin_mine_2.nbt](F04-whole.png) | 晶洞壳及入口采掘设施，仅洞腔与附属操作空间研究。 |

## 核实的区别

- F01仅12×6×9，尽管文件名为large；中央20格灰色投影是青色地毯，不能当大型矿石工作台。炉3、桶7及工具沿边布置。
- F02顶部y5仅外周24格梁，中央5×5空白；没有F01的连续覆盖，不凭同池large/small两个NBT分别累计完整覆顶工坊。
- F03主要是露天凹坑及矿石岩边；F04主要是高晶洞壳及入口器具。岩石高点、矿体、天然壳与炉具不自动构成完整房屋。
- F04保存高18格、占用最高y16，侧梯只在y1..5；不宣称18格可用楼层、洞顶环廊或运输线已经连通。
- F01与旧C004实际图对照：前者双工作跨敞口平覆棚，后者封闭方祭室加前院；最邻近几何分数仅筛查用途。

## 可应用原则

- 文件名large/small与实际尺寸分别核对，不能套巨型工坊标签。
- 覆顶棚、裸梁跨、露天坑和晶洞设施先分清，再讨论相应用途。
- 分类投影把地毯、矿石、栏杆和活板整格显示；器具与原始方块状态复核后再作布局观察。
- 将热工器具、储料和工作留空分边布置，可以作为小型矿业支援房的尺度参考；没有运输、加工或机器玩法验收。
- 局部五格梯只说明模板内梯段，不能补成洞顶环廊、主矿道或索道动线。

既有三类前哨各仍1/1000、缺999；原义庄/墓园148/1000、缺852；COD6正式参考仍0。当前没有任何范围达到1000，不开始建筑制作。

未运行Java、Gradle或游戏；没有联网请求，未操作声音、亮度或存档。未改生产程序、模型、贴图、任务、指南针或主清单，未删除提示词。所有图片是离线NBT分类整方块研究图。
