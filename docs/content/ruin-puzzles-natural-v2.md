# 解谜遗迹 · 自然生成与探索玩法（v2）

本轮把 v1 的三个机关（星盘 / 编钟 / 四象灯）**接进自然生成**，做成三座可以真正在生存里找到的
小型遗迹，并补上主题奖励、难度三档、指南针入口与测试。机关状态机复用 v1，没有另起一套解谜系统。

## 1. 玩家怎么找到并体验

| 遗迹 | 维度 / 群系 | 机关 | 入口 | 奖励主题 |
| --- | --- | --- | --- | --- |
| **九霄观星密室** `dynasty:star_vault` | `#dynasty:jiuxiao` | 星盘归位 | 门楣上有线索石板 | 符纸 / 玉 / 符箓材料 |
| **古乐遗址** `dynasty:music_ruin` | 主世界 `#minecraft:is_overworld` | 编钟回声 | 同上 | 科举与书院材料、货币、补给 |
| **四象封印室** `dynasty:seal_vault` | `#dynasty:underworld` | 四象点灯 | 同上 | 锻造 / 探索材料、补给 |

* 结构注册在 `dynasty:` 命名空间，`/locate structure dynasty:star_vault`（其余同理）可以定位；
  假人/管理员也能用 `/dynasty_find star_vault`（需要先进入对应维度，且主手拿探险者指南针）。
* 进屋流程：**门外门楣线索石板（一句话说明这是哪种机关）→ 主室里的部件各自带一块线索石板 →
  解开后中间的封印石门消失 → 控制器上方生成一次性公共奖励箱，后室有附魔台、书架与锻造台**（2026-09-25 v5 更新，取代原控制器直接领奖）。
* 三档难度（入门 / 进阶 / 挑战）：**生成时按结构坐标哈希决定**，写进控制器方块状态，
  四座遗迹里总能遇到不同档；玩家看到的是同一间房，但线索组合 / 编钟音序（3、4、5 音）/ 初始亮灯完全不同。
* 房间有四种朝向（也由坐标哈希决定），跨区块边界照样成立。

## 2. 新增 / 修改文件

**新增（机关与生成）**
```
src/main/java/com/dynasty/puzzle/RuinLayout.java           纯几何：房间格子、朝向旋转、运行时编号、难度/朝向哈希
src/main/java/com/dynasty/puzzle/PuzzleRuinPiece.java      结构部件：写 WorldGenLevel，按世界坐标定部件编号
src/main/java/com/dynasty/puzzle/PuzzleRuinStructures.java 三个 Structure（生成点 + 类型）
src/main/java/com/dynasty/puzzle/PuzzleRuinGameTests.java  GameTest：真实生成一遍三种遗迹（待统一执行）
tools/puzzle/gen_ruin_loot.py                              唯一配置源：3 结构 + 3 结构集 + 9 奖励表
tools/puzzle/RuinLayoutTest.java                           几何 / 朝向 / 索引对齐 / 九档可解 / 连通性测试
tools/puzzle/test_ruin_data.py                             数据与注册契约检查
tools/puzzle/run_ruin_tests.sh                             一条命令跑上面两个测试
src/main/resources/data/dynasty/worldgen/structure/{star_vault,music_ruin,seal_vault}.json
src/main/resources/data/dynasty/worldgen/structure_set/{star_vault,music_ruin,seal_vault}.json
src/main/resources/data/dynasty/loot_tables/puzzles/{star,music,seal}_tier{0,1,2}.json
docs/content/ruin-puzzles-natural-v2.md                     本文档
docs/content/ruin-puzzles-natural-lang-additions.json       待合并的三座遗迹名（中英）
```

**修改（都是最小改动，已在交付里列明）**
```
src/main/java/com/dynasty/structure/DynastyStructures.java      +3 结构类型、+3 部件类型与反序列化器（约 35 行）
src/main/java/com/dynasty/puzzle/PuzzleService.java             奖励改为按「机关 + 难度档」选主题表（新增 rewardTable）
src/main/java/com/dynasty/DynastyCompassBridge.java             +3 个指南针目的地；维度支持带命名空间（主世界）
```

**没有**动：兵器模型/数值/熟练度/饰品效果、皇宫/书院/星坛等既有建筑主体、任务 SNBT 与生成器、
配方、贴图、共享语言文件（三座遗迹名放在独立片段里等合并）。

## 3. 冲突与规则

* 生成阶段**只写 WorldGenLevel**，每一笔都经过 `StructurePiece.placeBlock` 的分块裁剪与包围盒判断，
  不调用管理员放置命令、不加载周围区块。
* 房间内容的朝向由**内容旋转**实现（不使用 `rotate` 的方块状态），因此星盘朝向 /
  灯阵环序 / 门楣位置在四种朝向下都一致；部件的「第 i 件」按运行时同一套排序（(y,x,z) 与环序）在
  生成时算好再写初始状态，所以**存档重载后答案不会变**。
* 结构集稀疏度：间距 44 / 48 / 56，隔离 14 / 18 / 20（既有 `stone_grove` 是 42/14），salt 各不相同，
  不会和其它建筑扎堆。
* `spawn_overrides` 为空：**不额外增加常驻怪物、巡逻队或 Boss**。
* 奖励表只引用真实存在、当前阶段可获得的物品（脚本会校验物品存在 + 违禁奖励黑名单）。

## 4. 真实执行过的测试

```bash
bash tools/puzzle/run_ruin_tests.sh
== 1/2 Python 数据与注册契约 ==
通过 82 项，失败 0 项
✅ 遗迹数据 / 注册 / 奖励表 / 指南针 / 文案片段 全部符合约定
== 2/2 Java 几何 / 索引 / 九档可解性 ==
通过 19 项，失败 0 项
✅ 遗迹几何 / 朝向 / 索引对齐 / 九档可解性 / 连通性 全部通过
```

Java 测试测的是**生产代码**（`RuinLayout` + `PuzzleRules`），覆盖：
四种朝向 × 三种机关都在 13×6×13 包围盒内；旋转四次回原位且保持距离；星盘朝向随房间一起旋转；
星盘初始朝向 / 灯阵初始亮灭在**四种朝向下**都落在运行时认定的「第 i 件」上；
星盘三档「开局未完成 + 按线索可解」；灯阵三档「开局未完成 + 按 BFS 解点得亮」；
编钟三档长度递增（3/4/5）且正确序列通过、长度不足不通过；入口可进入；
**封印门在时宝室完全进不去**、门移除后宝室可站人且所有部件仍可达。

测试过程中它真的抓出并修掉了三个实现缺陷（不是改测试糊过去）：
1. 包围盒 11×11 装不下 180° 朝向 → 改成 13×13；
2. 门口那格被「墙」和「空气」重复写入（集合语义下门口是堵的）→ 改成**每格单一来源** `roleAt`；
3. 封印墙只砌到 y=2，能从上方绕过 → 封印墙顶到天花板，并在封印门与门口补了地板。

数据契约检查（82 项）覆盖：结构 JSON ↔ Java 注册 ↔ 结构集 ↔ 群系标签一一对上；
间距不低于既有建筑、salt 不重复、`spawn_overrides` 为空；九张奖励表存在、条目真实、难度递增、
不含 Boss 信物 / 毕业武器 / 永久成长；`PuzzleService` 的表名规则与文件名一致；指南针包含三座遗迹；
共享语言文件没有被擅自写入。

## 5. 尚未验证的部分（不要当成已完成）

* **没有跑 GameTest**：`PuzzleRuinGameTests` 已写好（真实跑一遍 `postProcess`，断言写入数量、
  部件数量、门楣线索、控制器/难度档、开局不全亮），但本轮**没有执行**
  `./gradlew --offline runGameTestServer` —— 另一位开发者的 `runClient` 正占着 Gradle，
  按分工不能并发构建。命令留给最终统一执行。
* **没有在新世界实测生成**：`/locate` 与真实地形下的房间外观、`beard_thin` 贴合效果、
  四种朝向在真实地形里的可达性都还没跑过；本轮用的是「生产几何 + 生产索引算法」的等价验证。
* **多人抢领 / 背包满重试 / 存档重载**沿用 v1 已有机制，本轮只补了主题奖励表，没有重跑端到端多人测试。
* 三座遗迹的**中英文名**需要把 `docs/content/ruin-puzzles-natural-lang-additions.json` 合并进
  `assets/dynasty/lang/{zh_cn,en_us}.json`（或它的生成器字典）；未合并时 `/locate` 显示结构 id，
  指南针列表里仍是中文标签。
* 探险者指南针的**配置白名单**：桥接会尊重罗盘自己的 allowed-structure 列表，
  如果玩家装了罗盘但配置里没放行新结构，会被拒绝搜索（桥接有明确提示，不会静默失败）。

## 6. 给 Codex 的接口（后续美化）

* 只需要改 `RuinLayout.shell()` 的 `roleAt()` 与 `PuzzleRuinPiece.shellState()`：
  前者决定「哪一格是什么用途」，后者决定「这个用途用哪块方块」——加屋檐、换玉阶、铺地砖都不用碰机关。
* 房间尺寸契约：控制器在局部 `(CX, CY, CZ) = (6, 1, 6)`，包围盒 **13×6×13**；
  部件偏移由 `RuinLayout.partOffsets(kind)` 给出（星盘四角 / 编钟一排五个 / 四象灯环四向），
  改动它们必须同时满足 `tools/puzzle/RuinLayoutTest`（越界、可达、索引对齐都会拦）。
* 不要改 `RuinLayout.rotate/variantFor/facingFor` 的语义：世界里的旧房间会重新按坐标算难度与朝向，
  改了等于把已生成遗迹的答案换掉。
