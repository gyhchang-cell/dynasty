# 2026-10-10 沉沙玄宫本地接续验收

本次继续完成两条具体要求，并逐条从外部 `cod2.txt` 删除：隐藏工匠室的高阶机关图纸与补给，以及敲碎四角无字碑中的一座后永久开启返程吊篮。**Cod2和沉沙玄宫仍未整体完成。**

## 隐藏工匠室

独立稀有物品 `dynasty:high_grade_mechanism_plan`，有真实原版无序配方和中英文说明。图纸1张、铁锭4个、铜锭2个、红石1份合成8个现有机关齿轮，所有输入包括图纸均消耗。普通图纸不能代替，满背包不会提前消耗图纸；重复取结果不能复制齿轮。图纸固定出现在隐藏补给箱，保留普通图纸和食物/箭/金锭，室内有真实工作台。入口裂纹砖可用生存镐挖开，外围壳体保持保护。

首批71项服务端与8+4客户端验证详见 [工匠室报告](CONTINUATION_ARTISAN_20261010.md)。本批主工作区11+5阶段再次包含完整破墙、进入、共享箱、合成及存档重开流程；并检查图纸与齿轮的模型和贴图不是missing texture。主工作区已有齿轮贴图修正予以保留。

## 四角石碑与永久吊篮

地宫台阶四角相对坐标为 `(20,1,9)`、`(43,1,9)`、`(20,1,22)`、`(43,1,22)`，均有干燥落脚地面和头部空间。石碑四个独立破坏键与公共 `return_lift` 键分开：敲碎其中一座只移除该座外观和碰撞，另外三座保留，吊篮对所有玩家永久开放。左右键的旧交互兼容；验收使用客户端真实生存镐START采掘包。

沿用自定义BlockEntity和SavedData、稳定的离散楼层式返程升降；下层触发点 `(41,1,8)` 到入口神道平台 `(41,73,8)`。单向回程不跳过前进谜题；出口碰撞、世界边界、支撑和液体检查保留。死者不能激活机关。解锁及独立石碑键在房间reset、区块存储、资源重载、客机断线和整个游戏进程退出重开后均保留。

旧存档中的 `return_lift` 键和原石碑ID继续有效。新石碑/工作台只影响新生成区块，没有自动补建、重掷旧箱战利品或覆盖玩家建筑。

## 验证与证据

| 检查 | 当前主工作区结果 |
|---|---|
| 原生Cod2服务端GameTest | 73/73必需测试通过 |
| Gradle build | 成功，1分12秒 |
| 真实单机 | 11阶段通过 |
| 真实TCP双客户端 | 11阶段/人通过 |
| 单机实际存档、新JVM重开 | 5阶段通过 |
| 双机实际存档、新JVM重开与重新连接 | 5阶段/人通过 |
| 配方引用 | 576项、0错误、0警告 |
| 战利品引用、脚本语法和相关diff空白检查 | 通过 |

新2项原生测试覆盖四座实际结构石碑、空手不能解锁、原生镐采掘、只破所击石碑、共享解锁/去重/reset，以及实际ServerPlayer的锁定、出口被堵、死者拒绝、存活者和第二名玩家返程。保留原服务器传送逻辑，未用FakePlayer的空传送实现替代。

真实客户机11阶段先完整验收工匠室8阶段，再真实敲碑、每人右键原结构吊篮到上层、重载资源和客机重连；结束正常保存并退出。新进程从实际存档副本加载，检查原生保存的玩家上层位置、唯一消耗图纸/8齿轮、单独石碑破坏与公共解锁；重开后再次使用实际吊篮。移到机关旁和提供基础合成材料属于测试夹具，破墙、开箱、取物、合成、敲碑及升降调用均通过实际客户端协议。没有生成第二份图纸/齿轮或直接写成功状态替代验证。

当前证据见 [SHA256清单](evidence/shortcut-20261010/manifest.json)、[73项主工作区日志](evidence/shortcut-20261010/server-integrated1.log)、[运行时依赖快照](evidence/shortcut-20261010/runtime.json)。客户机日志压缩、阶段结果和截图在该目录 `solo/`、`pair/`、`solo-restart/`、`pair-restart/`。测试世界只在 `build/`，未纳入证据/Git。

保留失败记录：第一版升降测试使用Forge FakePlayer，它主动禁用传送，改用真实ServerPlayer及原生packet listener后通过；第二版旧战斗夹具在同一tick重复生成、随机候选不推进且大型夹具覆盖邻近区域，改为真实服务器tick等待并垂直隔离大结构后通过全部测试。客户端测试程序增加原生选中物品栏同步包及临时世界暂停页恢复；未改生产同步逻辑以配合测试。

本批检查的是功能与持久化，未认证整座建筑最终美术、自然发现到Boss通关、机关移动平台的完整视觉质量或TPS。瞬移后的部分截图在区块网格重建前抓取，不能当成完整视觉验收。

## 提示词与未完成部分

[删除账本](DELETIONS_20261010.json)共7处已验证删除，最后一处同时去掉已经没有子项的“捷径与隐藏房间”标题。以原始备份顺序减去这7处文字，可完全重建当前外部提示词；剩余需求原文保留。

当前实际注册表仍缺 `dynasty:zhaoming_di` 和cod1 `startEncounter`/奖励绑定；披鳞执金吾、巨锤金甲力士及指定帝王最终素材/甲胄也未完成。文档要求先完整验证第一座地牢再扩展其余，因此不能将缺Boss的地牢标记通关完成。其他九座地牢、27个未实现事件、完整10区生态、所有职业人形返工、11类动画完整验收与TPS矩阵仍保留。没有以旧Boss改名或目录/数据定义充当成品。

所有修改已落在本地主工作区，未提交或推送GitHub；其他本地任务的并行改动保留。当前源码清单及哈希见 [同名JSON](CONTINUATION_CHENSHA_20261010.json)。

## 复测

```sh
JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home ./gradlew --offline -I tools/blueprint/cod2-client.init.gradle -Pcod2Artisan -Pcod2PrepareOnly -Pcod2ClientRun=chensha-prepared-new runClient
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/chensha-prepared-new/launch.json chensha-solo-new --solo --shortcut
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/chensha-prepared-new/launch.json chensha-solo-restart-new --solo --shortcut --resume-from build/cod2-client/chensha-solo-new
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/chensha-prepared-new/launch.json chensha-pair-new --shortcut
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/chensha-prepared-new/launch.json chensha-pair-restart-new --shortcut --resume-from build/cod2-client/chensha-pair-new
```
