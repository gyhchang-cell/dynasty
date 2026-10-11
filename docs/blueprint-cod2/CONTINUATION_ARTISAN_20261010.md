# 2026-10-10 沉沙玄宫隐藏工匠室

本批完成“水银瀑布后破墙进入工匠殉葬室，取得高阶机关图纸与补给”这一独立要求。**Cod2和整座沉沙玄宫仍未全部完成**；昭明帝、指定精英、最终奖励和完整自然探索通关等要求保留。

## 实现

新物品 `dynasty:high_grade_mechanism_plan` 为稀有、不可叠放的消耗型图纸，具有中文/英文名称和实际配方提示。隐藏补给箱固定包含一张高阶图纸，保留普通图纸、食物、箭和金锭。房内新增原版工作台。

原版无序合成：高阶图纸1张 + 铁锭4个 + 铜锭2个 + 红石1份 → 机关齿轮8个。使用现有可装入机关延长预警的 `qimen_gear`；配方消耗图纸与材料，普通图纸不能代替。获得图纸时解锁配方书。图标复用现有图纸贴图，未声称完成新美术。

隐藏入口沿用有意可采掘的裂纹砖墙，外围机关夯土壳仍受保护。宝箱采用原版LootTable及开箱后持久化；已取空的旧箱不补货。新工作台只影响更新后生成的结构区块，不改写玩家旧建筑。

## 验证

- 合并后的主工作区：71/71必需Cod2原生GameTest通过，随后build成功。新增3项覆盖实际结构列、原生生存破墙与壳体保护、真实战利品和原版箱NBT、消耗配方、拒绝普通图纸、重复点击及满背包保护。
- 独立工作区真实单机：8阶段通过；游戏正常退出保存后，在新JVM中加载实际存档副本，另4阶段通过。
- 合并后的主工作区真实双客户端：8阶段/人通过；主客机均退出后，在新JVM加载实际存档副本并重新TCP连接，另4阶段/人通过。
- 客户端真实动作覆盖挖矿START/STOP包、正常走过破墙入口、原生ChestMenu/CraftingMenu交互、两人同时查看同一箱、唯一图纸归属、取空同步、资源重载、客机重连、原生合成8齿轮、装备同步及重开后的消耗/箱子持久化。未通过直接发图纸或直接发齿轮替代实际开箱/合成；合成基础材料由QA夹具提供。
- 配方检查：576项、0错误、0警告；战利品引用检查通过。测试源码为单独源集，不进入正式jar。所有游戏存档位于 `build/cod2-client/`，证据目录不包含世界文件。

[证据清单与SHA256](evidence/artisan-20261010/manifest.json)、[主工作区71项服务端日志](evidence/artisan-20261010/server-integrated1.log)、[运行时快照](evidence/artisan-20261010/runtime.json)。客户机日志压缩在 `solo/`、`solo-restart/`、`pair/`、`pair-restart/`；原始观察结果和截图同目录。

第一次服务端测试有两项失败：测试调用 `destroyBlock` 绕过正常采掘进度，及旧巨锤夹具等待实体区块不足。改为生存采掘处理器，旧夹具改为同水平加载区域的高空隔离，保留伤害/逃脱断言后重跑全部通过。重开存档QA曾停在实验性世界确认页，现仅对自己的临时存档确认原版/Forge实验性提示，未跳过世界加载或持久化验证；主工作区另有自定义维度，使用的提示类型与独立工作区不同。

## 提示词与范围

验证完成后仅删除隐藏工匠室对应完整一行。本轮前5处删除加本次共6处，原文备份、删除原文及哈希见 [DELETIONS_20261010.json](DELETIONS_20261010.json)。重建“原始文件减6处原文”与当前外部 `cod2.txt` 完全相等，未修改剩余需求。

其余9座地下城、27个未实现事件及完整生态、模型、动画验收继续保留。以上使用实际结构夹具，不能作为自然发现、Boss通关或TPS测试结果。源码清单及当时文件哈希见 [同名JSON](CONTINUATION_ARTISAN_20261010.json)。

## 复测

```sh
JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home ./gradlew --offline -I tools/blueprint/cod2-client.init.gradle -Pcod2Artisan -Pcod2PrepareOnly -Pcod2ClientRun=artisan-prepared-new runClient
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/artisan-prepared-new/launch.json artisan-solo-new --solo
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/artisan-prepared-new/launch.json artisan-solo-restart-new --solo --resume-from build/cod2-client/artisan-solo-new
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/artisan-prepared-new/launch.json artisan-pair-new
python3 tools/blueprint/run_cod2_clients.py build/cod2-client/artisan-prepared-new/launch.json artisan-pair-restart-new --resume-from build/cod2-client/artisan-pair-new
```
