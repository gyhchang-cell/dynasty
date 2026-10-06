# cod2 实施状态

## 2026-10-05 云端续开发交接

分支 `codex/cod2-continuation-20261005`，基线 `7888e007ad35b5a01348731166ee28d417e95095`。以下为本批更新；后面的“第一阶段”是历史记录。**沉沙玄宫仍为 PARTIAL，cod2 未整体完成。**

- 修复自然生成拿到 `ChunkAccess` 后被错误拒绝，以及原版废矿候选点使所有落点被排除的问题；保留已有 Structure、ID、巨龙/庄园避让和出生点距离限制。
- 修复三段楼梯被房间覆盖、试炼超时直接打开前进出口、侧门未封闭、调试命令选错房间/陷阱的问题。
- 毒箭为真实服务端三连射实体，带中毒、禁止拾取、有时限；石碑需要镐，解锁实例共享且持久化的返程吊篮；门和翻板恢复碰撞时避开占据者。
- `BlueprintSpawns` 复用原驻军 SavedData 接入前室两刀手、两长枪兵，固定可站立落点，100 tick 间隔，4 个总量上限；卸载保留 UUID，清除后不重复生成。没有注册第二套生态管理器。
- 增加独立客户端 QA 源集，不打入正式 jar；用真实客户端交互、BE/实体包、资源重载、客机断线重连验证机关。

验证：驻军批次的 189 项相关回归与 build 通过；旧存档毒箭兼容补丁后的最终 23 项 cod2 测试与 build 通过；最终构建的单机及双客户端均通过六阶段检查。早期驻军独立测试的区块可见性/自然地形干扰已修正，原断言保留。

尚缺：昭明帝和其 `startEncounter`、精英/中层指定怪、最终奖励的真实发放及唯一账本接入、整座地牢从自然发现到通关的实机验收。九座剩余地下城、完整十区生态、30 事件、全实体模型动画也未完成；不要把框架/注册/测试通过记作这些条目 DONE。此分支没有纳入另一个工作区的 cod1 未提交修改。

本地接续：先保留本地未提交内容，获取本分支，检查和本地 cod1 的合并差异；从沉沙玄宫剩余链路继续。若 Boss 依赖仍不存在，保持 PARTIAL，不换名旧 Boss 充数。新批次的验证证据见 `evidence/continuation-20261005.txt`。

客户端复测（Java 17、可用图形桌面；每次换新 run-id，准备后不要同时重新编译。先释放 Gradle 构建锁，再启动两个实际 JVM）：

```sh
./gradlew -I tools/blueprint/cod2-client.init.gradle -Pcod2ClientRun=prepared-new -Pcod2PrepareOnly runClient
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/prepared-new/launch.json local-pair-new
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/prepared-new/launch.json local-solo-new --solo
```

隔离存档及观测输出在 `build/cod2-client/<run-id>/`。这是运行链路检查，不代表最终建筑、美术和完整地牢验收。

本轮未全部完成。已完整阅读 979 行设计文档并核对现有工程，建立 [IMPLEMENTATION_MAP.json](IMPLEMENTATION_MAP.json)：10 地牢、10 生态区、30 事件的原文要求与缺失清单。模型/动画尚未开始，目录或规划清单不代表功能已实现。

## 当前实现

仅推进文档实施顺序的第一阶段：数据层、机制接口、最小跨区块试验结构。工程原有祭坛、最终 Boss、角色注册和任务系统保持不变。新增部分通过 `DynastyContent.register` 接入，未替换旧系统。

- `src/main/java/com/dynasty/dungeon/DungeonDefinition.java`：包含文档要求的落点、piece、marker、状态和奖励键。
- `DungeonMechanism.java` / `DungeonRoomController.java`：三个破封目标和三个射击目标，重复交互不重复计数；IDLE→WARNING→ACTIVE→RECOVERY；没有玩家时暂停、不补发错过的伤害帧。
- `DungeonStateStore.java`：维度、地牢实例 UUID、房间三级隔离；进度、永久捷径、世界唯一/玩家奖励记录序列化。唯一奖励接口尚未接入成品地牢奖励。
- `DungeonContent.java` / `DungeonMechanismBlock.java` / `DungeonMechanismBlockEntity.java`：六种无物品注册的工程机关块，服务端判定、原版 BlockState/BE 包同步、防普通开采/活塞、封门与翻板碰撞切换。每个房间仅 core 驱动；只访问已加载的有限 marker 列表。
- `DungeonProbeStructure.java` / `DungeonProbePiece.java`：正规 Structure/StructurePiece 三段结构，13×7×48，固定入口与连接点，共 18 个机关 marker。生产代码不主动强加载额外区块。试验结构**没有 StructureSet，不自然生成**。
- `DungeonCommands.java`：仅管理员的房间/机关/陷阱调试操作。
- `DungeonFrameworkGameTests.java`：框架自动化测试，不认证成品地牢或客户机视觉质量。
- `tools/blueprint/generate_cod2_probe_resources.py`：生成试验 Structure、补给 LootTable、工程占位模型/BlockState 和隔离的测试模板。不是最终美术。
- `tools/blueprint/cod2-test.init.gradle`：GameTest 存档放在 `build/cod2-gametest/<run-id>`，不使用用户存档。

## 验证边界

自动化覆盖正式结构生成和真实服务器放置、piece NBT/负坐标跨区块裁切、18 marker 的实例绑定、真实 `.dat` 文件读取、进度去重、奖励去重、房间/维度隔离、重载不重放伤害、机关碰撞和关键块保护、资源解析以及调试命令树。

最终隔离运行 **12/12 GameTest 通过**，日志 [framework-gametest.log](evidence/framework-gametest.log)。完整 jar 构建 **BUILD SUCCESSFUL in 2s**，日志 [final-build.log](evidence/final-build.log)。产物为 `build/libs/dynasty-1.4.0.jar`，未部署。真实试验房放置记录的 703ms 同时包含 QA 主动加载三块区块及磁盘保存，不是纯生成时间，也不能外推至大型地牢。

隔离服务器测试通过不等于单机客户机、双人联机或视觉验收。地牢客户机项目均为“未实机验证”。最小试验房性能不代表大型成品地下城性能。最新全量回归 **179/179 必需测试及 build 通过**（原系统146、军系21、地牢12），日志见 [179 项回归](../blueprint-cod1/evidence/regression-20261005-179-guard-counter.log)。较早运行出现后台光照 `MissingPaletteEntryException`，还有一次死士引信断言失败，均保留原记录；未声称间歇性失败已彻底定位消除。

## 下一阶段依赖冲突

cod1 目前有九个基础怪的运行时实现，均为 PARTIAL；仍有 21 基础怪、15 精英、12 Boss、25 神器、12 神影未启动。军系五只在盾兵最新修改之前通过23阶段单机与真实双客户端动作/死亡检查，亦实际测试资源重载和空闲实体重连。该结果不能当成新构建或完整重进矩阵通过。当前两个 Minecraft 客户端都因主显示器不可用而无法启动，最新实机验收 PENDING。第一座镇岳孤陵所需的昭明帝亦不存在，尚不能按要求验证“入口→三层→机关→捷径→Boss→奖励→重进世界”。用户本轮已授权补齐所有剩余内容，不代表这些依赖已经实现。

不能把旧怪换名充当这些 Boss，也不能用空钩子当作完整遭遇。用户已明确授权完成 cod1、cod2 的全部剩余内容，依赖实现的授权障碍已解除；上述缺失数量是实施基线，不代表补齐完成。现有镇渊最终 Boss 不会被覆盖。

## 测试方法

工程隔离测试（每次使用新的 run-id）：

```sh
./gradlew --offline -I tools/blueprint/cod2-test.init.gradle -Pcod2TestRun=framework-new runGameTestServer
./gradlew build --offline
```

若自行进入独立测试世界，管理员可在已加载的空地使用：

```text
/place structure dynasty:dungeon_framework_probe ~ ~ ~
/dynasty dungeon room complete probe
/dynasty dungeon room reset probe
/dynasty dungeon trap test poison_arrow
```

普通测试：右键三块破封石，用玩家射出的箭命中三枚兽眼后，宝室封门开启；重复命中不得重复计数。退出重进后应保持进度。调试 reset 不清空唯一奖励账本。试验结构仅为工程验证房，不是镇岳孤陵成品，勿放在已有建筑上；它会占用起点区块向南 48 格、向东 13 格的地表区域。此轮未同步游戏实例或导出整合包。
