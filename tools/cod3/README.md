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
| 奇观 | 25 个保留编号；三个专用 GeckoLib 远景模型/三级 LOD；极光飞羽与流星雨使用专用几何并通过原生验收；水晶穹顶与玄冰蓝洞由原版 Jigsaw 在新区块地下生成并常驻；其余客户端场景具有世界锚点/种子/时序/恢复/预算，无服务端视觉实体 | 雾/季节使用雨、月相、时间代替；三个模型与两洞穴的图形画面、另外十八种完整环境表现仍需验收和补齐 |
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

## 2026-10-18 夜空奇观续做

极北天幕·极光飞羽（#15）与星辰坠落·流星雨（#20）已改为独立正式几何，共用夜间/天气淡出、远近降级与安全渲染。完成100张夜空参考审阅，流星另补6张专门画面；两项共用基础参考，不冒充206张独立图。五项专用服测试、24个原生场景及48次截图通过。只删除两条完成行，外部清单与镜像均为1432行；详见 [续做记录](../../docs/cod3/continuation-2026-10-18-night-sky.md)。

## 2026-10-18 白昼与落叶续做

白虹贯日·祥云献瑞（#21）完成77面原创太阳天象及17项原生场景检查，已删除清单行，外部与镜像均1431行。神树落叶（#19）实际几何与树冠落点已实现；复查捕获并修正客户端高度图导致的屋顶下暗叶，构建和九项服务器测试通过，最终原生复验因主显示器不可用仍待进行，保留清单行。详见 [续做记录](../../docs/cod3/continuation-2026-10-18-day-foliage.md)。

当前 `aurora.init.gradle` 的 `-PskyScenic=21,19` 联合测试两项，`19` 可单测金叶，`15,20` 可单测夜空；`0` 现在包含15/20/21。原生旧联合 PASS 不等于金叶验收通过，须查看人工复查结论。

## 2026-10-18 金叶第二轮参考与验收

按用户最新要求，已研究过的任务继续制作前也补看100张不同参考。金叶（#19）追加100张，与既有cod3参考哈希无重复，本项累计200张；根据对照收窄叶尖、压低浅色面，并修正整片叶子的离地间隙。3,025组几何、九项专用服及17项原生场景/34张截图通过，人工确认屋顶暗叶问题消失。现已删除本项一行，外部清单和镜像均1430行，详见 [最终记录](../../docs/art/cod3-golden-leaves-v1/README.md)。旧的“显示器不可用/待复验”记录为历史状态，以此次第二轮验证为准。

## 2026-10-18 百草化萤续做

奇观#7完成原创像素萤点、独立振翅/升起与地表分叉绿脉。另看100张不重复游戏参考，严格筛除菜单与近似构图。4,525组几何、11项专用服、19个原生场景/38张截图通过并人工复查；只删除本项一行，两份清单均1429行。`-PskyScenic=7` 可单独运行本项19场景；测试使用静音临时世界。详见 [验收与参考记录](../../docs/art/cod3-fireflies-v1/README.md)。

## 2026-10-18 银瀑、古阵、水晶穹顶续做

新增逐图参考300张（每项100张，不是300个模组）：银瀑、古阵参考记录分别在docs/art/cod3-silverfall-v1与cod3-ancient-array-v1；水晶穹顶参考在cod3-crystal-canopy-v2。完成三项实际资源/表现并分别删除奇观#8、#2、#9整行，外部cod3.txt与镜像同步；本轮1429→1426行。其他未验收项继续保留。

银瀑/古阵：15服务器测试，3025帧几何检查各一套，34原生场景/68开关对照图。水晶穹顶：6服务器测试，自然普通世界seed1518实际locate/单片生成/9光源/13可见顶面线/通道检查，7原生视图。音频仅静默检查，没有播放声音或操作用户存档。

最终合并本地包：build/cod3-crystal-canopy-20261018/dynasty-1.4.0-cod3-scenic-20261018.jar，SHA256 62b78669ed7555e65d3fd33e6afa891602a3ada4f7b6ced513ef6ee3221fa1bd。正式冻结class与资源核对见docs/cod3/verification-20261018-silverfall-array.json、verification-20261018-crystal-canopy.json；删除记录分别在同目录deletions-20261018-{silverfall,ancient-array,crystal-canopy}.json。未提交、未推送。

## 2026-10-18 金乌第二轮

金乌#25新增100张参考（11个模组），改进三足、双翼循环与LOD连接，修正公共动画包相位及独立顶点缓冲提交。81组动画检查、6项专用服、17项原生场景/34张对照图和人工检查通过；仅删除该行，两份清单1426→1425行。与本轮此前银瀑/古阵/水晶合计400张独立参考，4项验收。冰洞另100张已参考，尚未验收，不计入完成数。

最新合并包：build/cod3-sun-crow-20261018/dynasty-1.4.0-cod3-scenic-20261018.jar（SHA256 954ffb6d334acd30f4e6be7fcac817167d4bf0bc1b0dd6e67e70d9da7473a374）；验收与删除记录见docs/cod3/*20261018-sun-crow.json。未提交、未推送。

## 2026-10-18 冰洞第二轮

奇观#24完成连续阶梯冰花、贴顶悬冰、八处外露照明及局部轻微冰裂声；另看100张新参考（13个项目）。6项专用服、自然普通世界生成和7张实机图验收通过，删除对应行，两份清单1424行。与本轮银瀑/古阵/水晶/金乌共5项、500张独立参考。玄武另100张参考已完成，尚待验收。

最新已验收本地包：build/cod3-ice-bloom-20261018/dynasty-1.4.0-cod3-scenic-20261018.jar；SHA256 210e8c16591d591714eb8074accb483d58aa61a1ad72d83b369e3e82960a79eb。详见docs/cod3/verification-20261018-ice-bloom.json。未提交、未推送。

## 2026-10-18 玄武第二轮

奇观#10完成宽掌短爪、蛇段连接、四足错拍划水、实际水面定位及断续泡沫/水柱。新增100张独立参考（12个模组）；243姿态连接检查、构建/6项专用服和20场景40配对原生帧通过。与本轮银瀑/古阵/水晶/金乌/冰洞共6项、600张去重参考，覆盖91个不同项目。只删除已验收行，当前两份清单1423行。

最新已验收本地包：build/cod3-xuanwu-20261018/dynasty-1.4.0-cod3-scenic-20261018.jar；SHA256 5bce0cee988deafec30943bc7c61019e72134da485dd82a835899865c3ccaa97。详见docs/cod3/verification-20261018-xuanwu.json。未提交、未推送。

## 2026-10-20 青苍龙影第二轮

奇观#1完成连贯长躯、四足错相游动与头颌微动，晴朗黄昏可见、青白尾云与归属明确的微弱龙吟。模型与贴图由用户指定对话交接；PNG经审查保留。新增100张参考（23模组），243姿态连接检查、构建/6项专用服及17场景34配对原生帧通过。本轮累计7项、700张不重复参考、114个不同项目；并非每项100个模组。当前清单1422行。最终本地包：build/cod3-azure-dragon-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 d30268f8648aca347226bb8c7d63ee93ffd69ef9c7dd6924c579557168e6a3d4。未提交、未推送。

## 2026-10-20 深谷火树

奇观#13建筑、实际新区块Structure、真实场址夜间火星及轻微近场噼啪声接通。新增100张不重复参考/7项目，9项专用服与14场景静音原生检查通过；原生四向和步行视角人工复看。累计8项、800张不重复参考，当前清单1421行。没有修改任务/战斗逻辑；没有在旧存档任意玩家位置强行放置建筑。最终本地包：build/cod3-fire-tree-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 deb868726f29cbbb6eea876cf6878201d38cdf95db0294f3588f8f4a13bfa5e7。未提交、未推送。

## 2026-10-20 幽冥古舰

奇观#3实际资源及深水航道客户端演出接入；新增100张不重复图像、16个项目，累计9项900张。11项专用服检查、最终构建、20场景40张静音原生图通过，实际GeckoLib半格水线偏移已修正。两份清单现1420行；未完成项保留。最终包：build/cod3-ghost-ship-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 7c31e3ea41f42287f2e3375f7f23b21e90e24916d86617f587e2fcdcd14c9723。未提交、未推送。

## 2026-10-20 蜃楼幻市

奇观#14客户端原版图集幽影网格验收，13项专用服检查、18场景36张静音原生图通过。新增100张/12项目，累计10项1000张不重复图像；当前两份清单1419行。固定-Z朝向，无地形放置/实体/全局雾/任务战斗修改。最终包：build/cod3-mirage-street-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 85da74d104820b1d490d27a2b085549a4c148509d0b6a1e018e1f7673a6d3778。未提交或推送。

## 2026-10-20 神人开山

#6原生Gecko模型已验收：15项专用服检查、21场景42张静音原生帧、5个真实资源源文件/冻结运行时/JAR一致，前10项资源保留。新增100张/17项目，累计11项1100张不重复参考。两份清单1418行。最终包：build/cod3-stone-god-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 b15ba5ce9f3e7badabe99a68de514dc6f41fdcf35bbdaeb0cb0d190f4c873435。未提交或推送。

## 2026-10-20 龙宫倒城

#17真实源水倒置单LOD奇观已验收，17项专用服检查两次成功，20场景40张静音原生帧通过，保留前11项资源。新增100张/16项目，累计12项1200张不重复图像。两份清单1417行。最终包：build/cod3-dragon-palace-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 bdc337210cce3e8eb8eee1ed8663cfbae9fc87135542f38d4e9080c9b95ed226。未提交或推送。

## 2026-10-20 长城残影

#18已接入近建筑/远旗影及真实古战场/干地条件，19项专用服检查、20场景40帧静音原生验收完成。新增100张/21项目；累计13项1300张不重复参考。两份清单1416行。包：build/cod3-great-wall-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 2972c8cd5df4fc95d14d06162ff27a26bc219f5a8521d89a41276f3f06ac45d1。未提交或推送。

## 2026-10-20 兵俑/鬼市接入，原生画面待验

#4兵俑由“做建模的”交付三档19骨骼/56、45、24 Cuboid与4秒循环，“做贴图的”交付256px/336面UV正式原创图集并同步BB。主线绑定24个独立缓存实例、每tick0.01m的+Z行进、完整平坦干地路线、古战场结构与阴雨条件；远处为48个白粒阵，无声音，无服务器实体。

#22“做建筑的”交付原创建筑2981块/5564面/十二真实灯位。主线接入真实阴司干地、共享夜间时钟、近建筑/远鬼火LOD、局部微雾及有归属的低声叫卖；保留原生End雾，不依赖该无天空光维度的自然降雨，不改全局雾或亮度。

两项当前源/冻结客户端/候选JAR一致，构建与23项专用服务器检查通过。候选包build/cod3-ghost-army-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar，SHA256 7c88689db0a64bce455bad3cb87322dcf0b651849b36a0b387b7996ba13a4e8d。前13项资产和独立Scenic渲染类未变。参考新增模型100/贴图100/鬼市100，1600张已准备的获选图片逐文件SHA唯一；已正式验收仍13项1300张。

兵俑测试启动受Forge early display阻挡：找不到主显示器，glfwGetPrimaryMonitor失败，游戏未进入、截图0。保持显示器休眠、声音和亮度原状，失败的自有进程已结束；鬼市没有重复启动尝试。清单4和22保留，两份清单均1416行，SHA256 39207505086ccde098c53e48f9bccb75ed0cada96d8b60d04f54fec0fa390a5d。记录见docs/cod3/verification-20261020-ghost-army-pending.json、verification-20261020-ghost-market-pending.json。不要把BUILD或软件预览认作原生验收，不运行accept_tasks.py删除待办。

恢复后无需重复23项检查或重建，除非源码/资源改变。先为兵俑导出新v3启动并冻结/验证，保留失败v2；鬼市已有build/blueprint-client/frozen/cod3-ghost-market-20261020-v1/launch.json，仍须等显示器可用。每次只启动一个自有静音客户端，未做自然出现频率或独立多人客户端验证，不覆盖用户存档。未提交或推送。
