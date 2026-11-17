# 第七批：藏书用房参考核查

实际研究8份本地模板的32张新图，重看4张历史对照图；逐例记录布局、比例、立面、屋顶、材质、动线、地形。筛查149个历史归档/成员组合，不把这些组合数算成参考数。

**本批5份分用途、分规模提案，正式新增0。** 两份柱基缺证/未组装待核，一份历史设计家族变体排除。五份提案不能直接合成DUN04或DUN07的5/1000。

[逐例观察与实际看图哈希](manual-review.json) · [完整提案](reference-proposals.json) · [原始来源](sources.json) · [门梯补剖](detail-evidence.json) · [历史去重](dedup-evidence.json) · [外接池](interface-audit.json) · [原始陈设与特征配置](fittings-and-dependencies.json) · [家族排除](variant-family-audit.json) · [验证结果](verification.json)

| 编号 | 原始设计 | 范围与决定 |
|---|---|---|
| F01 | [data/trek/structures/village/cherry/houses/cherry_library_1.nbt](F01-whole.png) | DUN04单层小型藏经用房；13×15×16，书架与讲台及多入口关系，不包含整寺/悬崖/中式风格验收。 |
| F02 | [data/trek/structures/village/swamp/houses/swamp_library_1.nbt](F02-whole.png) | 沼泽高脚小书楼上部研究；柱基池缺证，不提出完整建筑信用。 |
| F03 | [data/trek/structures/village/swamp_vanilla/houses/swamp_library_1.nbt](F03-whole.png) | 低高脚书屋室内与柱特征研究；未组装支柱，不提出完整落地建筑信用。 |
| F04 | [data/kaisyn/structures/village/flower_forest_japanese/houses/flower_forest_library_1.nbt](F04-whole.png) | 旧W018的改屋顶/内装同家族，排除独立设计计数。 |
| F05 | [data/kaisyn/structures/village/badlands_pueblo/houses/badlands_library_1.nbt](F05-whole.png) | DUN07小型单室典籍房；7×7×9，不覆盖藏丹塔或三岛仙观。 |
| F06 | [data/kaisyn/structures/village/birch_forest_romanian/houses/birch_forest_cartographer_and_library_1.nbt](F06-whole.png) | DUN07窄藏书阁加附属工作室；17×13×9，不覆盖炼丹/机关/整观。 |
| F07 | [data/terralith/structures/village/fortified/houses/library.nbt](F07-whole.png) | DUN04 T形小书舍；14×40×21保存、实际高15，不覆盖高塔或整寺。 |
| F08 | [data/terralith/structures/village/desert/houses/library1.nbt](F08-whole.png) | DUN04低层多室小藏书院；19×12×23，不覆盖悬崖大寺/千佛崖。 |

## 需要保留的区别

- F04与旧W018同9×9轮廓、同门及柱室组织；减一层屋盖并改书架内装仍不另计。原文/角色几何不完全相同不证明独立设计。
- F02有11处木柱接口，但当前归档未见对应池；F03有9处栅栏柱特征接口和1处空入口，已读嵌套配置，没有组装柱基。
- F07保存盒14×40×21，实际占用最高y14，即15格高；村民接口2、道路接口1。F06村民接口3、空入口1。
- F08七接口分别为道路2、幼年村民3、原版村民2；整组围院算一个设计，不能把房间、屋顶或实体点拆成独立例。
- 书架与讲台坐标用于识别藏书动线；未运行原生碰撞、读书交互、粉末块稳定或完整路径测试。

## 可借鉴原则

- 先用原始书架、讲台坐标区别内装与墙体；书架数量不等于可读/可达书籍数量。
- 单室、T形书舍、狭阁双功能长屋与围院组群各有不同进出和取书路线，不用一套屋顶替代用途观察。
- 保存盒高40格而占用仅15格时保留两项尺度，不把空白当藏经塔。
- 历史同家族改一层屋盖或更换内装仍须排除，原文与角色几何不同不是新设计证明。
- 道路、实体、空入口标识和支柱特征区别记录；支柱池缺证或未组装不能装作已落地。
- 村庄书屋只提供相应用房原则；不以日式或欧式参考研究冒充整座中式佛寺、道观制作完成。

既有三个前哨范围各仍1/1000、缺999；原义庄/墓园148/1000、缺852，COD6仍0。本批未修改这些账本。

未制作新建筑，未改生产程序、模型、贴图、任务、指南针或主清单，未删除提示词。没有运行Java、Gradle或游戏，没有联网请求；未操作声音、亮度、窗口或存档。研究图为本地NBT分类整方块投影。
