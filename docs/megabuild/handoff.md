# 大型建筑（天工山城 / 山麓采矿庄园）交付说明

> 下文为DeepSeek原始交付记录。Codex已完成后续改进与接入，当前数据、验证和搭建方法见 [codex-review-v2.md](codex-review-v2.md)，不要把本页旧统计当成最终发布结果。

状态：**框架 + 纯几何生成器 + 离线验证已可运行**；MC 结构胶水已写完并通过 `javac` 独立编译，
但**尚未接入公共注册**（按分工交给 Codex），**GameTest 未执行**（Codex 的 runClient 占用 Gradle）。

## 1. 新增文件清单

```
src/main/java/com/dynasty/structure/megabuild/Blueprint.java          纯画布：局部坐标→方块种类、统计、旋转、走线验证、ASCII 预览
src/main/java/com/dynasty/structure/megabuild/TiangongCitadel.java    天工山城生成器（176×176×40，确定性）
src/main/java/com/dynasty/structure/megabuild/MiningEstate.java       山麓采矿庄园生成器（96×96×28）
src/main/java/com/dynasty/structure/megabuild/MegabuildStructures.java 独立 DeferredRegister：2 结构类型 + 2 部件类型 + 反序列化器
src/main/java/com/dynasty/structure/megabuild/MegabuildPiece.java     通用部件：Kind→方块、placeBlock 分块裁剪、NBT 保存 seed/朝向
tools/megabuild/gen_deliverables.py                                   生成战利品表 / 成就 / 任务素材 / 语言增量 / 接入补丁
docs/megabuild/handoff.md                                             本文档
docs/megabuild/quest-proposals.json                                   两座建筑各 6 个任务节点素材
docs/megabuild/lang-additions.json                                    结构中英名增量（待 Codex 合并）
docs/megabuild/integration.patch.txt                                  公共注册接入补丁（待 Codex 合并）
src/main/resources/data/dynasty/loot_tables/chests/tiangong_*.json    两档战利品表
src/main/resources/data/dynasty/worldgen/structure/*.json             结构 JSON
src/main/resources/data/dynasty/worldgen/structure_set/*.json         结构集 JSON
src/main/resources/data/dynasty/advancements/tiangong_*.json          两个探索成就
```

## 2. 结构 ID 与尺寸 / 实方块统计（离线生成器实测）

| 结构 | ID | 画布 | 最终非空气方块 | 台基填充 | 建筑主体 | 装饰与内容 |
| --- | --- | --- | --- | --- | --- | --- |
| 天工山城 | `dynasty:tiangong_citadel` | 176×176×40 | **155 687** | 123 412 | 29 122 | 3 153 |
| 采矿庄园 | `dynasty:tiangong_mining_estate` | 96×96×28 | 15 215 | 8 856 | 6 260 | 99 |

* 四朝向旋转后实体块数完全一致（155687 / 155687 / 155687）。
* 「至少 100000 最终非空气方块」按**总非空气方块**达标；但其中**台基填充占比大**（三阶平台），
  「建筑主体」目前 2.9 万。若 Codex 要求主体本身 ≥10 万，需继续用同一套 `hall()/tower()/hollowBox()` 扩充院落与层叠殿阁（见 §6）。
* 台基是「地表之上的分层平台」，不是直插世界底部的实心柱。

## 3. 接入补丁（Codex 合并，本轮未直接改公共文件）

见 `docs/megabuild/integration.patch.txt`，核心三处：
1. `DynastyContent`（或等价注册点）加两行：
   `MegabuildStructures.STRUCTURE_TYPES.register(modEventBus); MegabuildStructures.PIECE_TYPES.register(modEventBus);`
2. `src/main/resources/data/dynasty/worldgen/structure/{tiangong_citadel,tiangong_mining_estate}.json`（已生成）
3. `.../structure_set/*.json`（已生成，天工山城 spacing=96 / separation=48；采矿庄园 spacing=64 / separation=32，均比既有建筑更稀疏）。

## 4. 奖励表 / 成就 / 语言 / 任务素材

* 战利品：`chests/tiangong_common.json`（普通储物间：食物/火把/铁铜/低阶素材）、`chests/tiangong_rich.json`（密库：玉、朱砂、精钢、淬炼材料，数量克制）。
* 成就：`advancements/tiangong_citadel.json`、`tiangong_mining_estate.json`（探索定位，`minecraft:location` 触发）。
* 语言增量：`docs/megabuild/lang-additions.json`（结构中英名 + 成就中英名，键完整、不覆盖总表）。
* 任务素材：`docs/megabuild/quest-proposals.json`（两座建筑各 6 节点，含 item ID、数量、建议前置、检测方式、收益）。

## 5. 复现步骤与真实结果

```bash
# 1) 纯生成器（无游戏、无 Gradle）：编译 + 离线预览
javac -nowarn -proc:none -sourcepath src/main/java -d /tmp/megabuild \
  src/main/java/com/dynasty/structure/megabuild/Blueprint.java \
  src/main/java/com/dynasty/structure/megabuild/TiangongCitadel.java \
  src/main/java/com/dynasty/structure/megabuild/MiningEstate.java
java -cp /tmp/megabuild com.dynasty.structure.megabuild.TiangongCitadel   # 155687 非空气方块、四朝向一致、ASCII 俯视/立面
java -cp /tmp/megabuild com.dynasty.structure.megabuild.MiningEstate     # 15215 非空气方块

# 2) MC 胶水独立编译（含结构/部件类，用 Gradle 导出的 classpath，不并发开 Gradle）
javac -nowarn -proc:none -cp "build/classes/java/main:<classpath>" -d /tmp/mb_all \
  src/main/java/com/dynasty/structure/megabuild/*.java                    # 12 个类全部编译通过

# 3) 待 Codex 统一执行：
./gradlew --offline compileJava
./gradlew --offline runGameTestServer
```

## 6. 未验证项（不要当成已完成）

1. **主路线离线走线 `walkable()` 目前返回 false**：几何上入口→内街→台基阶梯→主殿→密库都在，
   但离线 BFS 的「两格净空 + 楼梯 + 跳一格」模型还没有完全对上真实放置；需要继续校准
   `Blueprint.walkable`（尤其是台阶与门槛的一格高差），或等接入后用 GameTest 在真实世界验证。
2. **GameTest 未执行**、**新世界实际生成未测**（`/locate`、地形贴合、四朝向、跨区块都没跑过）。
3. 公共注册与语言合并未做（交 Codex）。
4. 采矿庄园的主路线/房间尚未做离线走线断言。
5. 十二个「有用途空间」已具备雏形（山门/内街/工坊院/主殿/密库/粮仓/藏书楼/守卫营/药圃/采石场/矿坑/塔楼/廊桥），
   但「十至十五分钟主线路程」与「支路淬炼/锻造材料收益」还需在真实世界按走线实测后再调。

## 7. 给 Codex 的接口

* 只改 `Blueprint.Kind` → 方块映射（`MegabuildPiece.blockState`）就能换材质；
* 只改 `TiangongCitadel` 里的 `hall()/tower()/hollowBox()/stairsCut()` 调用就能加建筑 / 扩主体体量；
* 不要改 `Blueprint.rotate/at/key` 与 `TiangongCitadel.SIZE/HEIGHT` 的语义，否则会影响已验证的四朝向一致性；
* 宝箱统一走 `chests/tiangong_common`，密库想更肥再挂 `tiangong_rich`（表已备好）。
