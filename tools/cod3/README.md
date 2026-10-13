# cod3 开发与验证

目标环境：Minecraft 1.20.1、Forge 47.4.10、Java 17、GeckoLib 4.8.4。

`src/main/resources/data/dynasty/cod3/catalog.json` 是本轮内置定义。原稿的 20 入场、20 死亡、40 VFX、15 NPC、30 秘密、25 奇观、10 世界状态完整保存在目录中。定义在启动时校验并缓存；目前不支持运行中重载该目录。

机器保持现有八条有序投料配方，无新增燃料、温度或液体机制。空手打开未完成机器；潜行右键随时打开 GUI；完成后普通空手右键仍可直接领取。侧面/顶部输入、底部输出，GUI、右键和漏斗共用同一计数器与库存。

NPC 使用 `dynasty:npc_<角色ID>`，可用对应刷怪蛋检查；普通右键开启各玩家独立的对白，潜行右键交易。自然生成的驿站、药庐、商队、长城、石林与学院包含 home marker，旧区块不会被全图补刷。

管理员可用原版命令放置秘密测试控制器，例如 `/setblock ~ ~ ~ dynasty:story_anchor[kind=14]`；kind 0–29 对应目录中的秘密 1–30，kind 30–44 是 NPC home marker。正式玩家只看环境线索，无内部编号。

## 实际接入范围

| 系统 | 本轮运行行为 | 仍需故事/资产接入的部分 |
|---|---|---|
| Boss Sequence | 六种祭坛 Boss 的服务器计时、预警、无敌窗、AI/血条切换、保存恢复、晚观察同步与 watchdog | 其余拟议 Boss 无 Registry 绑定；逐角色分镜中的地形预设、专属台词、变体和大型模型动画尚未逐项实现。原稿全文保留为描述 |
| 死亡 | 六 Boss 的延迟掉落/XP、首杀、奖励阶段凭据、永久遗留物容器与清场；叛将留下可拔原掉落剑的双半块青铜跪像，其他容器使用原创漆木铜扣匣；取消死亡/复活能解除锁定 | 20 种死亡意象并非全部有专属雕像和完整过场；低天花板下跪像安全回退为遗留物匣 |
| VFX | 40 种公共组合、独立时序与原版音效、共享服务器范围和危险轮廓、有限雾体、真实模型残影、远近/LOW 降级与状态恢复 | 全部专属艺术分镜和世界中实体残影仍需逐项检查；纯视觉发送不创建伤害 |
| NPC | 15 实体/独立骨架与道具/11 动画状态；三条初见、五条普通对白；铁匠修复、校尉祭奠、实际交易库存、home 保存与游商重生冷却 | 角色支线、迁居与完整随机商人事件仍未逐项接入 |
| 秘密 | 玩家/世界领取归属、持久化、明确事件触发、失败反馈、已有物品降级奖励；16 种地标放入自然结构；#12 真实白鹿静步跟随、个人灵契和可往返洞天 | 部分触发只是现有机制的替代实现；多数入口/支线奖励尚未绑定真实故事房间。#10 的新维度与主线冲突，仍保持禁用 |
| 奇观 | 25 个保留编号；三个专用 GeckoLib 远景模型/三级 LOD；水晶穹顶与玄冰蓝洞由原版 Jigsaw 在新区块地下生成并常驻；其余客户端场景具有世界锚点/种子/时序/恢复/预算，无服务端视觉实体 | 雾/季节使用雨、月相、时间代替；三个模型与两洞穴的图形画面、其余完整环境表现仍需验收和补齐 |
| 世界状态 | 10 个持久化 flag、一次广播、NPC 消费；叛将→01、始皇→09、四象供台齐备→08、镇渊胜利→10 | 02–07 的正式剧情来源与生态/关键结构预设尚未接入。未创建季节/新维度系统 |

镇渊帝君继续使用原有祭典、竞技场、入场和奖励流程，未绑定通用 Sequence。

## 验证入口

本机 JDK 路径如与 `gradle.properties` 不符，用 `-Dorg.gradle.java.home=<JDK17>` 覆盖。

```sh
python3 tools/cod3/verify_assets.py
./gradlew build
./gradlew -I tools/cod3/qa.init.gradle runGameTestServer
./gradlew -Pcod3Namespaces=dynasty,dynasty_cod3 -Pcod3TestHeap=3g \
  -Pcod3TestRun=build/cod3-full-regression -I tools/cod3/qa.init.gradle runGameTestServer
./gradlew -I tools/cod3/render-qa.init.gradle runClient
```

完整服务器套件含大型结构模板，需要比独立 cod3 测试更大的堆。所有测试世界均位于独立 `build/` 目录。客户端 harness 只打开隔离的标题画面，真实 FBO 绘制 40 VFX 的两档、25 奇观、15 NPC 正侧面、八 GUI 的空/满背景和 30 地标，并记录 GL 状态检查；它不等同于双人联机、所有 GUI 缩放和完整世界画面的人工验收。

永久青铜跪像和遗留物匣的续做、68 种独立实际检查及五视角记录见 [2026-10-11 续做](../../docs/cod3/continuation-2026-10-11-remains.md)。后续若只检查这批资源，先运行 `python3 tools/art/cod3/validate_remains.py`；单客户端世界验收入口为 `tools/art/cod3/remains.init.gradle`，不会在普通构建中打开游戏。

衔草白鹿、92 种独立检查与洞天往返见 [白鹿续做](../../docs/cod3/continuation-2026-10-11-white-deer.md)。只读资源检查使用 `python3 tools/art/cod3/validate_white_deer.py`；实际客户端入口 `tools/art/cod3/white_deer.init.gradle` 仅在显式加载时生效。白鹿新增的是独立秘密奖励维度，不改变四象主线。

青苍龙影、玄武负岳、金乌巡天的专用非人形模型、真实逐面 UV 与三级 LOD 已接入，构建和四项无界面 GameTest 通过。实机画面因主显示器不可用仍待验收，三个完整提示继续保留，见 [奇观续做](../../docs/cod3/continuation-2026-10-11-scenic.md)。软件资源检查入口为 `tools/art/cod3/review_scenic.py`；`scenic-server.init.gradle` 只运行独立测试，`scenic.init.gradle` 只在显式使用时准备客户端配置。

后续接入两处常驻洞穴 NBT/世界生成，通过同一隔离套件的六项独立测试，见 [洞穴资源与复验](../../docs/art/cod3-caves-v1/README.md)。旧 09/24 自然计时光场改由常驻方块结构承担；不会在已生成区块补挖洞穴。

`build_catalog.py <原任务文件>` 可重建内置目录；NPC 与地标的确定性生成脚本也在本目录。构建与运行不依赖原任务附件。

## 2026-10-08 续做

当前源码进度与按原文删减的依据见 [续做记录](../../docs/cod3/continuation-2026-10-08.md)，本轮构建及 19 项专用服回归见 [验证记录](verification/continuation-2026-10-08.md)。后续任务原文为 [remaining-tasks.txt](../../docs/cod3/remaining-tasks.txt)；完整分镜、剧情与真实客户端验收仍需继续。

## 2026-10-09 对话续做

对话节点、条件分支、后继节点与每玩家 nonce 会话的实现，以及启动协议修复见 [续做记录](../../docs/cod3/continuation-2026-10-09.md)。完整打包与 26 项专用服测试见 [验证记录](verification/continuation-2026-10-09.md)。本轮上传原名 `cod3(1).txt` 保持不变，仅删除已完成的 C3-NPC-002 索引行；[剩余原文](../../docs/cod3/remaining-tasks.txt) 仍含十二项任务及未完成的详细规格。

## 2026-10-10 本地续做

死亡重启结算、八工作台实际 Menu、NPC 修复/祭奠/对白/重生、秘密触发、奇景恢复及四十模板时序和范围的变化见 [续做记录](../../docs/cod3/continuation-2026-10-10.md)，38 项专用服与 191 个图形检查见 [验证记录](verification/continuation-2026-10-10.md)。直接删减用户本地 `cod3.txt`，保留未完成原文；[剩余任务](../../docs/cod3/remaining-tasks.txt) 与该文件字节一致。

多人同时在该 checkout 构建时，可追加 `-I tools/cod3/isolated-build.init.gradle -Pcod3IsolatedBuild=build/<自己的独立目录>` 隔离编译输出。同一个输出目录的构建、服务器测试和客户端检查应串行执行。

## 2026-10-10 续做验收

VFX14–40 完成专属几何与残影补齐，190 项专用服回归、246 项图形检查，以及两台原生 Forge 客户端各82场景/140截图通过。见 [续做说明](../../docs/cod3/continuation-2026-10-10-vfx.md)。

真实世界 QA 为可选源集 `tools/cod3/client-qa.init.gradle`。先使用独立 `--project-cache-dir build/cod3-continuation-20261010/gradle-cache` 和 `-I tools/cod3/isolated-build.init.gradle -Pcod3IsolatedBuild=build/cod3-continuation-20261010/stable-compiled`，再加 `-I tools/cod3/client-qa.init.gradle -Pcod3ClientRun=<fresh-id> -Pcod3ClientPrepare runClient` 导出配置。用 `tools/blueprint/freeze_client_classpath.py --launch <launch.json> <fresh-freeze-id>` 固定实际运行字节，再运行 `python3 tools/cod3/run_native_clients.py <frozen-launch.json> <fresh-run-id>`。仅使用 `build/cod3-client` 临时世界和 loopback 25591；QA 类不进入 JAR。两个客户端均生成 PASS 才通过。
