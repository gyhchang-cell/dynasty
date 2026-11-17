# 地下城建筑研究与空间接口交接（2026-11-01）

本批实际研究12份固定本地原始NBT，逐张查看36张整体、平面及纵剖图，逐例写明7方面观察。全部为离线方块占用近似，未启动Java或游戏。

完整城防布局强候选4例（F01/F02/F07/F08），完整单塔但仅对应子空间5例（F03/F05/F09/F11/F12），排除或待核3例（F04/F06/F10）。F02是完整遗址布局候选，不是完整有顶住宅；F10内部建筑与连通性仍不充分。

正式台账仍148/1000，原范围缺852；COD6仍0/1000。十地下城不得继承义庄148例。本批正式新增0；强候选未自动分摊到10个目标。原先15份聚落模板也没有变成15个信用。

## 实际研究证据

[逐例7方面观察](manual-review.json) · [原始来源与NBT校验](sources.json) · [去重依据](dedup-evidence.json) · [验证结果](verification.json)

| 编号 | 原始设计 | 判断 | 可借鉴内容 |
|---|---|---|---|
| F01 | [catalonian_castle.nbt](F01-whole.png) | COMPLETE_FORTIFICATION_LAYOUT_CANDIDATE | 低围墙院落包围高主堡，前侧门楼、角塔与后部主厅分开；不是单塔复制成城。 |
| F02 | [ruined_castle.nbt](F02-whole.png) | COMPLETE_FORTIFICATION_LAYOUT_CANDIDATE | 整体为密集城堡遗址，底层网状分室，上部多塔残墙，侧向伸出的桥把入口与主残堡联系。 |
| F03 | [dark_tower.nbt](F03-whole.png) | COMPLETE_TOWER_SUBSPACE_ONLY | 近圆形封闭塔，水平木楼板反复分层，顶部露台；外壳本身完整，不是外接房间组件。 |
| F04 | [underwater_dungeon.nbt](F04-whole.png) | EXCLUDED_OR_INCOMPLETE_LAYOUT | 15×10×15石块内部只有零碎水腔和刷怪/箱位置，缺乏完整入口与房间组织证据。 |
| F05 | [illager_tower.nbt](F05-whole.png) | COMPLETE_TOWER_SUBSPACE_ONLY | 方形塔四角粗柱围中央楼层，上部收成台阶状顶；外墙、门、内楼板均在同一模板。 |
| F06 | [stray_ruins.nbt](F06-whole.png) | EXCLUDED_OR_INCOMPLETE_LAYOUT | 雪覆盖的残墙与地基，只有断开的围合痕迹；没有完整楼板和入口体系。 |
| F07 | [castle.nbt](F07-whole.png) | COMPLETE_FORTIFICATION_LAYOUT_CANDIDATE | 紧凑围合堡以高主塔和低门楼包围小院，室内和环形外墙包含于一个完整模板。 |
| F08 | [villager_castle.nbt](F08-whole.png) | COMPLETE_FORTIFICATION_LAYOUT_CANDIDATE | 宽大城墙围生活院落，主厅坡顶位于一侧，内有低矮房舍和围墙通道；完整围城布局而非单栋主厅。 |
| F09 | [tower_island.nbt](F09-whole.png) | COMPLETE_TOWER_SUBSPACE_ONLY | 小塔坐于中央岛台，外围分散小石团不与主塔连接；一个塔设计，不是多座完整建筑。 |
| F10 | [abandoned_castle_pillager.nbt](F10-whole.png) | EXCLUDED_OR_INCOMPLETE_LAYOUT | 木栅围合内有两座不同高度残塔、树和破损中部木构，属于完整占地的遗址场景，内部建筑连通未证实。 |
| F11 | [tower_of_ice.nbt](F11-whole.png) | COMPLETE_TOWER_SUBSPACE_ONLY | 冰壳内收纳窄木层与竖向梯井，顶部小台是附属层，同一冰塔不能按五刷怪位拆分。 |
| F12 | [witch_tower.nbt](F12-whole.png) | COMPLETE_TOWER_SUBSPACE_ONLY | 小方塔上下叠室，侧向悬出木件与斜屋面、烟囱构成偏心轮廓；完整塔模板非独立顶片。 |

## 9处矛盾的建筑约束

以下均是既有来源约束；未新增蓝图、实际ID、奖励代码或任务数据。每条精确原文与生产源码片段见[接口约束](architectural-interface-constraints.json)。

| 矛盾 | 精确原文位置 | 唯一入口、层级、永久捷径约束 |
|---|---|---|
| REWARD-01 照胆通幽八卦镜 | [cod1.txt:1285](</Users/a15356015027/Desktop/code x提示词/cod1.txt:1285>)；[cod2.txt:166](</Users/a15356015027/Desktop/code x提示词/cod2.txt:166>) | 古观镜阵与DUN08玄潭龙坛保留不同地点身份；不得为二者各造一个同神器领取建筑。 龙坛属于DUN08底潭层；冰阶回程应与该实例入口关联。古观若作线索/谜题端，由协调确认唯一获得事件，建筑专岗不改奖励归属。 |
| REWARD-02 惊鸿流云金丝扇 | [cod1.txt:1265](</Users/a15356015027/Desktop/code x提示词/cod1.txt:1265>)；[cod2.txt:124](</Users/a15356015027/Desktop/code x提示词/cod2.txt:124>) | 水乡书香密室与DUN06血喜堂不可按名字近似合并。 黄金婚床属于苗窟最底祭祀组团的喜堂，不放入口或水下气室；倒钟乳石桥只能返入口，不生成第二通关入口。唯一实物来源由协调选择。 |
| REWARD-03 千机/天机罗刹百刃伞 | [cod1.txt:1298](</Users/a15356015027/Desktop/code x提示词/cod1.txt:1298>)；[cod1.txt:1305](</Users/a15356015027/Desktop/code x提示词/cod1.txt:1305>)；[cod2.txt:145](</Users/a15356015027/Desktop/code x提示词/cod2.txt:145>) | 江南机关房与DUN07后岛摘星台是两个空间；千机/天机别名先核实际ID，不能据两名字各建一间领奖房。 摘星台神匣位于后岛顶层，前池御风捷径落在既定台顶安全区；中岛下藏丹阁属于秘密支路，不能冒充同一神匣位置。 |
| REWARD-04 幽都忘川招魂幡 | [cod1.txt:1435](</Users/a15356015027/Desktop/code x提示词/cod1.txt:1435>)；[cod2.txt:103](</Users/a15356015027/Desktop/code x提示词/cod2.txt:103>) | 义庄神案与DUN05忘川彼岸龙纹台保留不同空间；必须由协调确定唯一神器获得事件，建筑端不重发。 DUN05已有真实ID/underworld入口见下；当前支池排水不是完整忘川干河底到殿后通道，不能标记该全线已实现。龙纹台、码头Boss与钱庄秘密也不能混为一处。 |
| REWARD-05 龙吟斩马断岳刀 | [cod1.txt:1204](</Users/a15356015027/Desktop/code x提示词/cod1.txt:1204>)；[cod2.txt:61](</Users/a15356015027/Desktop/code x提示词/cod2.txt:61>)；[cod2.txt:680](</Users/a15356015027/Desktop/code x提示词/cod2.txt:680>) | cod1瓮城与DUN03老帅战场采用同一规范战场实例，废墟中央拔刀与宝箱位置不能变成两个副本。 通关后取刀点和老帅倒下地点要落在同一最终战场语义范围；西墙裂缝只连接万人坑旁路与战区，不创建第二奖励入口。Boss/箱双发由协调实现唯一结算。 |
| SEQUENCE-01 四象终局 | [cod1.txt:516](</Users/a15356015027/Desktop/code x提示词/cod1.txt:516>)；[cod2.txt:701](</Users/a15356015027/Desktop/code x提示词/cod2.txt:701>)；[cod3.txt:1206](</Users/a15356015027/Desktop/code x提示词/cod3.txt:1206>)；[cod6.txt:70](</Users/a15356015027/Desktop/code x提示词/cod6.txt:70>) | 优先保留既有龙头、四柱、中央球与原传送入口；DUN10固定在现有专用前置区域，不为逆向摆贡再建维度/龙头。 四岛是同一固定区域的四分支；每岛桥汇到同一中央前置战区，中央裂隙调用原最终入口。混元前置/隐藏战区不得覆盖镇渊最终场地。当前专岗未核实生产维度ID，故不编造。 |
| LAYOUT-01 隐仙观 | [cod1.txt:1208](</Users/a15356015027/Desktop/code x提示词/cod1.txt:1208>)；[cod1.txt:1215](</Users/a15356015027/Desktop/code x提示词/cod1.txt:1215>)；[cod2.txt:126](</Users/a15356015027/Desktop/code x提示词/cod2.txt:126>) | 已有21×21三清试炼场保留原试炼入口与领取点；不将三座屋顶解释成cod2三座岛。 DUN07另有前池、中炉、后台拓扑；名称交叉只建立依赖。若协调复用旧试炼，必须显式映射到某个房间，旧场地只读保留，未满1000不扩建。 |
| SHORTCUT-01 万刃峰 | [cod2.txt:181](</Users/a15356015027/Desktop/code x提示词/cod2.txt:181>)；[cod2.txt:698](</Users/a15356015027/Desktop/code x提示词/cod2.txt:698>) | DUN09倒剑桥只算一条永久捷径；同桥两个端点、两个方向或多次加载不重复计条数。 至少再有1条、至多按要求共2～3条独立的已解锁路径，每条均须提供原路线端点、目的层、永久状态键与读档后证据。来源尚未定义额外线路，当前不提前创作几何或伪称完成。埋剑洞是隐藏房而非自动第2捷径。 |
| SCHEMA-01 场景数量 | [cod3.txt:1151](</Users/a15356015027/Desktop/code x提示词/cod3.txt:1151>)；[cod3.txt:1238](</Users/a15356015027/Desktop/code x提示词/cod3.txt:1238>) | cod3当前实际表行以已记录29秘密、7奇观为基准；标题30/25不是已完成场景数量。 不凭缺号补建场景，不把同一场景的视觉/声音/天气/昼夜变体算新建筑。指南针中文名绑定真实实例入口，奇观触发点不冒充可探索建筑。 |

## 已有源码可复用的两处空间锚点

沉沙玄宫：`dynasty:chensha_xuangong`，主世界；GenerationStub为origin+(32,72,4)，origin地面基准=采样最高地形−72。72/48/24/0为入口/神道/九玄室/底层地板标高。底层return_lift在+(41,1,8)，目标+(41,73,8)。GenerationStub是结构锚点，不能未经净空核查当传送落脚点。

枉死城：`dynasty:yinsi_wangsi_cheng`，`dynasty:underworld`；GenerationStub为origin+(48,41,3)，origin=采样最高地形−40。已有坡道下降至街巷，内衙/屋顶另有标高。`wangsi_sump_drained`只清理x14..16/y6..8/z94..99封闭支池，不能冒称排干主河并贯通殿后；Boss仍为`UNBOUND_RIVER_DOCK`，secret与onceLoot定义为空。

准确生产路径（只读核对）：
- [DungeonDefinition.java](</Users/a15356015027/Desktop/dynasty/src/main/java/com/dynasty/dungeon/DungeonDefinition.java>)
- [ChenshaStructure.java](</Users/a15356015027/Desktop/dynasty/src/main/java/com/dynasty/dungeon/ChenshaStructure.java>)
- [ChenshaPiece.java](</Users/a15356015027/Desktop/dynasty/src/main/java/com/dynasty/dungeon/ChenshaPiece.java>)
- [WangsiStructure.java](</Users/a15356015027/Desktop/dynasty/src/main/java/com/dynasty/dungeon/WangsiStructure.java>)
- [WangsiPiece.java](</Users/a15356015027/Desktop/dynasty/src/main/java/com/dynasty/dungeon/WangsiPiece.java>)
- [WangsiArchitecture.java](</Users/a15356015027/Desktop/dynasty/src/main/java/com/dynasty/dungeon/WangsiArchitecture.java>)
- [WangsiSluice.java](</Users/a15356015027/Desktop/dynasty/src/main/java/com/dynasty/dungeon/WangsiSluice.java>)

## 协调接入约束

十座的规范入口地点、层级、秘密支路、永久捷径及准确原文路径均列于architectural-interface-constraints.json。除上述两座，其他8座本批未核实真实ID和落地坐标，明确留空。

任务和指南针显示原文中文建筑名，以实际维度、结构ID、实例键关联规范入场点。屋顶出入口、秘密房和返程捷径仍属于同一实例。发现建筑、到层、开捷径、完成战区、领取奖励分别记录；入口抵达不等于通关。

未满1000不做新建筑。程序、掉落、任务、中文指南针由协调接入，本批不宣称已实现或已验收。只改本独立研究目录，未删任何主清单项、未改正式参考台账、未重试429来源、未操作存档或声音亮度。
