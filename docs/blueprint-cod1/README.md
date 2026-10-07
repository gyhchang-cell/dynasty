# cod1 第 1～5 项：实现进度与验证记录

## 2026-10-07 机关怪续作

新增第21～23项巡山木甲犬、青铜双头蛇傀和八足地工蛛：独立行为与骨骼动画、真实天工城/矿场落点、同遭遇警戒、铁栏攀爬、顶棚爬行及落地冲击、9种功能掉落。`dynasty_army` 服务端回归 **134/134** 通过，构建通过；这不是全项目或客户端验收。当前 **0 DONE / 23 PARTIAL / 71 NOT_STARTED**，单机、双人及性能仍待验收，全部 cod1 任务尚未完成。下一条目是第24项幽灯鬼面蝠。[当前缺口](remaining-20261007.md)，[本轮日志](evidence/mechanical-21-23-134.txt)。下方保留历史记录，旧静态 content-definitions.json 不代表最新实现数量。

## 2026-10-07 cod1 同步核对

交付分支 cod1 接续整个项目 main 的既有成果。本轮新增碧水玄蛟幼崽和巨臂石敢当，包括独立行为、模型动画、生态/结构生成、功能掉落和既有击杀进度。当前 **0 DONE / 20 PARTIAL / 74 NOT_STARTED**；全部任务尚未完成，单机、双客户端和性能验收仍待完成。本轮蓝图怪物服务端回归 **117/117**、构建通过；这不是全项目全部测试命名空间的重新验收。[逐项实现及验收缺口](remaining-20261007.md)，[本轮日志](evidence/frontier-19-20-117.txt)。下方保留历史记录。

## 2026-10-06 cod1-3 续作断点

从 `cod1-2` 的 `658bd616` 继续，保留之前全部实现。新增缚魂白布童子：帝陵暗角真实结构入口、倒退凝视移动、40 tick 背后诅咒、回头/遮挡打断、30 tick 定身与一次饱食度扣减、有限灯晕、服务端存档与多人目标隔离、骨灯握持/三条四节布带/碎灯死亡动画，以及三种功能掉落。复用原生成预算、遭遇 SavedData 和攻击时钟。

本批继续接入纸人剑客：真实护甲/吸收结算后的致死替身、保留至少1HP、背后5格安全搜索与侧后方回退、60秒保存冷却、同一实体重聚、Z字寻路、一次纸剑接触和真实延迟流血；帝陵中庭三个固定点共用原遭遇预算/存档。极薄纸扎模型、原生阶梯动画及功能掉落已接入；任务书由现有生成器同步材料配方，29项任务测试通过，旧ID与奖励保留。

继续接入墓穴飞颅：帝陵三个低光空中落点、原版飞行控制与普通碰撞、锁点俯冲单次咬合和回升、最多三个腐蚀污血区、护甲耐久损耗、绝对过期清理、读档冷却/成员身份、四组四节内脏骨骼、七段实际动画与三种功能掉落。补上原地面移动缺少飞行加速度的问题，并隔离旧死亡掉落测试中的外来物品统计。

新增赤目朱蛤：主世界沼泽/湿地/洞穴水岸真实自然生成池，至少12格连通水体且覆盖9个水柱、1～2只与局部上限；约6格抛物线跳跃、五节视觉舌头和服务端锁向射线、一次命中/约1格牵引、真实重击触发六枚火毒弹、共享限量毒区与绝对过期、冷却读档、34骨骼8段动画、发光毒腺及功能掉落。复用原投射物、毒区、攻击时钟、同步和生态注册。

新增枯木树精：同一实体的静止伪装/接近苏醒、横扫、锁点根须预警与可破坏牢笼、最多两个牢笼和绝对过期、重载保留生命与动作身份、双人破笼、林地泥土与真实木材生成条件、六根独立根足/开合树心/三段朽木死亡、三种功能掉落。复用既有战斗、生态和同步链路。

新增鸣沙石蝎：真实沙地自然生成、保留普通碰撞的潜沙、必经出沙前摇、左螯命中后才允许尾刺、短时减速/中毒、有限范围鸣沙及挖掘/举盾延迟、读档动作恢复、六足独立地面IK与七节尾骨、碎壳死亡、三种功能掉落。修复测试夹具中立即换武器尚未应用属性的问题，并隔离药效计时测试受到场外刺客的伤害；未削弱正式技能或伤害断言。

当前完整服务端回归 **272/272**、构建通过；[树精与石蝎完整日志](evidence/regression-cod1-3-272.txt)，[朱蛤完整日志](evidence/regression-cod1-3-254.txt)，[飞颅完整日志](evidence/regression-cod1-3-246.txt)，[纸人238项日志](evidence/regression-cod1-3-238.txt)，[童子231项日志](evidence/regression-cod1-3-231.txt)。当前 **0 DONE / 18 PARTIAL / 76 NOT_STARTED**；最新单机及双客户端实机验收仍未通过，不能拿服务端测试替代。剩余 12 基础怪、15 精英、12 Boss、25 神器、12 神影继续按 `cod1_new.txt` 实施；下一断点是碧水玄蛟幼崽（第19项）。本地拉取 `cod1-3` 后先检查本批单机与双客户端表现，再从现有代码接续；旧 JAR 的他人修改保留，需自行重新构建更新运行包。

## 2026-10-06 cod1-2 历史断点

分支从已合并前轮 cod1/cod2 的 `ffdff276` 继续，未更换既有实体或结构 ID。补齐乱军共享目标及附体死士配合钩锁；原 9 只怪的 23 种命名掉落已接入铁砧、原版弩弹药、解毒食用或材料回收。新增披甲叛将护卫（关隘上层）和阴兵鬼卒（古战场），均已接入模型、动画、攻击时钟、结构遭遇、持久化和掉落。

本批又接入尸变力士：帝陵前室固定生成、拖步/撑地奔袭、锤地、受击毒斑及冷却、卸载恢复、骨骼动画与三种功能掉落。完整服务器回归 **225/225**，构建成功；[最新完整日志](evidence/regression-cod1-2-225.txt)，[前一批 218 项日志](evidence/regression-cod1-2-218.txt)。当前 **0 DONE / 12 PARTIAL / 82 NOT_STARTED**；仍欠最新客户端单机/双人验收及剩余 18 基础怪、15 精英、12 Boss、25 神器、12 神影。原 9 只不能仅因补齐掉落就改标 DONE。旧目录快照留作历史，当前实现以源码和本段为准。

本地接续请拉取 `cod1-2`，先保留本地未提交修改。下一未启动条目是缚魂白布童子；先为现有 12 只补最新单机/双人验收。云端显示套接字权限及自动审批阻塞未解除，不能把服务器 GameTest 当作客户端通过。

## 2026-10-06 前轮合并记录

PR #1 的三处合并冲突已解决，保留古战场与主分支沉沙地宫的运行入口。续补祭酒前排死士附体优先级、卸载盟友恢复时的失效附体清理，以及完整实体读档的战斗/遭遇成员回归。当前构建成功，服务器 **198/198**，任务与罗盘 Python 测试 **39/39**。

最新客户端验收被云端套接字权限阻塞，自动审批拒绝放行；**不沿用旧截图宣布本轮单机/多人通过，仍为 0 DONE / 9 PARTIAL / 85 NOT_STARTED**。最新任务源为 [cod1_new.txt](cod1_new.txt)，验证及本地接续点见 [本轮记录](evidence/continuation-20261006.txt) 与 [服务器完整日志](evidence/regression-20261006-198.txt)。下方 20261005 的验证内容保留为历史记录。


这里记录 94 个蓝图条目的身份、既有工程对应关系和世界落点。当前为 **9 个基础怪 PARTIAL，剩余 85 项 NOT_STARTED，0 项 DONE**；30/15/12/25/12 的类别总数不变。目录不是运行时注册文件，`ACTIVE_RUNTIME` 不等于完整验收。

真实运行时已有卒伍刀手、橹盾甲士、符法祭酒、山精山魈、拒马长枪兵、连弩阵卒、铁索斥候、溃军死士、阵亡掌旗官；另外 85 项未启动。本轮仅开发 cod1，服务器回归 **172/172**（dynasty 146、dynasty_army 26），`:build` 成功；见 [完整服务器日志](evidence/regression-20261005-172-cod1.txt)。任务 Python 回归 34/34，任务书与世界生成引用检查通过。普通 Gradle test 为 NO-SOURCE。此前 179 项记录包含 12 项 cod2，不能与本轮数量直接比较。

当前资源：四模板 230 骨骼 / 410 cuboids / 31 clips；军系五只 264 / 642 / 35。灰模、黑剪影、原有自产 atlas 和动作/死亡五视图已生成。握持通道、两手接点、落地死亡、斥候独立膝撞、断旗落地、山魈真实攀壁接触已做检查；这仍不等于最终美术质量完成。

云端已验证青龙偃月刀单机 56 张截图、双客户端各 14 阶段；引信修复后的五军系单机及双客户端各 23 阶段。新增古战场通过单机、真实 TCP 重连，并在两个 JVM 完全退出后加载原存档：双方保留原七个 UUID 和探访任务记录，最终双方截图已复看。范围仍是**空闲遭遇持久化**，不等于活动战斗重连/重启、专用服务器、整合包 UI 或最终美术验收。Mac 的旧显示器阻塞保留为历史记录，未声称修复 Mac 环境。详见 [当前状态](evidence/current-client-status-20261005.json) 与 [实机记录摘录](evidence/runtime-20261005-cloud.txt)。

本轮修复两个已复现原因：中断/读档后的引信遗留冷却；无顶板测试场地被自然砂砾埋住目标、阻断视线。前者修正式运行逻辑，后者补测试隔离顶板及悬空砂砾回归，没有放宽三秒、伤害、AI 或碰撞断言。历史那次失败日志不在当前检出中，不能把本轮原因冒称为已证明的历史根因。

## 文件

| 文件 | 用途 |
| --- | --- |
| `content-definitions.json` | 全部 94 个精确名称、源文行号/摘要、候选 ID、同类旧内容参考、必填世界落点、资源存在性和验证状态 |
| `world-placement.tsv` | 94 行世界落点表；可在表格工具中打开。包含维度、标签、生成/来源、数量、重生、任务占位、Boss Arena、神器来源和神影锚点 |
| `registry-snapshot.json` | 原有源码注册位置与资源路径/哈希清单，不复制大量工作区贴图 |
| `baseline-build.json` | 修改前完整构建成功证据；普通 Gradle test 为 NO-SOURCE，不等于 GameTest 或进游戏测试 |
| `catalog-validation.json` | 最近一次生成时的静态校验结果 |
| `template-verification.json` | 历史四模板快照；本轮结果以 evidence/current-client-status-20261005.json 为准 |
| `army-verification.json` | 历史军系快照；本轮新增战场入口及验收见当前状态文件 |
| `models/model-manifest.json` | 九个实际资源模型的骨骼、cuboid、clip 与握持信息 |
| `stage0-2-audit.md` | 独立阶段边界核对、实现审查及尚未解决的验收差距；不改写原任务范围 |
| `../../tools/blueprint/catalog.py` | 可重复提取、生成、检查工具，无第三方依赖 |

## 可重复检查

从仓库根目录运行：

```sh
python3 tools/blueprint/catalog.py --check
python3 tools/blueprint/catalog.py --generate --source '/Users/a15356015027/Desktop/code x提示词/cod1.txt'
python3 tools/blueprint/refresh_army_audit.py --server-log docs/blueprint-cod1/evidence/regression-20261005-179-guard-counter.log
python3 tools/blueprint/catalog_evidence_tests.py
```

`--check` 只读，检查原文精确名称、94 项类别计数、唯一 ID、真实维度 ID、各类别必填字段、标签存在性、最终 Boss 保护以及 DONE 的实机证据。资源在扫描后出现/消失会单独列出，不会悄悄被算成已完成。

`--generate` 机械生成 JSON/TSV 并刷新资源存在性。保留已有 `implementationStatus`、`verification` 和 `implementationEvidence`；对于非 NOT_STARTED 条目，还保留实施者填写的实际资源、属性、生成/来源字段。初次基线构建证据与静态清单默认保留；只有显式 `--refresh-inventory` 才重新扫描清单。该参数用于校正扫描器，不表示重新建立构建基线。

`refresh_army_audit.py` 提取四模板与五军系实际注册、属性、技能、地点与资源。测试数量从完整成功日志及当前注解读取，不硬编码；失败或不同子集的日志拒绝刷新。可显式传入 `--solo`、`--network`、`--template-solo`、`--template-network`，但必须是完整、角色一致、动作身份吻合且冻结 classpath 仍与当前编译输出逐字节一致的运行。缺少最新客户端通过证据就保持 PENDING，不设置 DONE。证据解析器另有 18 个临时文件回归测试，它们不是游戏测试。

原文可通过 `--source` 指定位置。目录仅保存名称、技能名、出现/获得地点和引用行号等工程索引，不重抄模型、技能和剧情设计全文。JSON 中的源摘要可识别文档变化。

## 状态含义

- `auditStatus=MISSING`：初次审计没有发现这一身份的已实现内容。`rebel_soldier`、`royal_guard`、`houyi_bow` 等只是可参考的旧实现，不能等同于新名称的蓝图条目。`reuseCandidates` 明确标记 `REFERENCE_ONLY_NOT_SAME_CONTENT` 并给出实际源码/资源证据。
- `implementationStatus=NOT_STARTED/PARTIAL/DONE`：实际工作状态，与初次身份审计分开。PARTIAL 必须列明实现文件和缺口；DONE 必须有资源和实机证据。
- `PROPOSED_PENDING` 标签、任务节点与 Reward Hook 是待接入的工程键，**这些键不存在活动生成或奖励入口**。四模板原蓝图中的未来场景保留在 `pendingWorldPlacement`，与已有运行时落点分开；山魈 `naturalSpawnActive=true`，三种军队模板通过结构入口生成，不是一般自然散刷。
- `null` 明确表示尚未定案，不表示 0 或已完成。属性数值需参考当前成长体系校准；未指定的神影持续时间需由能力时间轴决定。
- 未启动条目的数量、上限、光照/高度建议和精英重生规则是准备实施的配置；四模板的实际值带 `ACTIVE_RUNTIME`。字段记录存在的代码，不承诺刷怪平衡或实机行为已验收。
- 新装饰掉落统一 `PENDING_REGISTERED_ITEM_AND_USE_MAPPING`，先核实已有材料与实际用途，不为凑蓝图注册无用途物品。
- 所有条目初始为“未实机验证”。静态校验通过、编译通过、模型存在、截图生成均不能单独替代单机和双人验证。

## 真实维度与地点限制

工程已有 5 个模组维度：`dynasty:celestial_dynasty`、`dynasty:underworld`、`dynasty:jiuxiao`、`dynasty:dragon_palace`、`dynasty:zhenyuan_arena`。目录不新增维度。

普通军队、山林、墓穴、机关遗迹默认映射到 `minecraft:overworld` 中符合原文的结构/区域。初次快照中的 `dynasty:cod1/...` 地点标签仍为 PROPOSED_PENDING，没有虚构注册；当前 `dynasty:blueprint/...` 入口如下；旧目录快照没有为本批重新生成。

| 模板 | 已接入的真实地点 | 实际编组/限制 |
| --- | --- | --- |
| 卒伍刀手 | `#dynasty:blueprint/ritual_sites`：`star_altar`、`herbal_retreat` | 祭祀点2名刀手+1祭酒；Y -32～220 |
| 橹盾甲士 | `#dynasty:blueprint/military_sites`：`great_wall_gate`、`tiangong_citadel` | 每标记1名；Y -32～220 |
| 符法祭酒 | 上述祭祀点标签，以及新古战场编组 | 每祭祀点/战场1名；Y -40～240 |
| 山精山魈 | `#dynasty:blueprint/shanxiao_habitat`：原版森林或山地标签 | 主世界Y 50～240，权重4，组1～3，24格内同类最多3只，白天通过率1/4 |
| 拒马长枪兵 / 连弩阵卒 | 上述军事点标签 | 1盾 + 2弩 + 1枪的有限编组；不影响安全村落 |
| 铁索斥候 | 上述森林/山地标签，以及新古战场编组中的2名 | 主世界Y 60～220；夜间；光照0～7；权重2、组1～2，32格同类上限2 |
| 溃军死士 / 阵亡掌旗官 | `#dynasty:blueprint/battlefields`：`ruined_battlefield` | 新区块地表结构；夜间光照≤7；1掌旗+1祭酒+2斥候+3死士，无普通生物群系散刷 |

结构生成只搜索玩家所在真实结构的已加载安全落点，每100 tick主世界最多新增2只；成员UUID、累计产出、冷却和清理状态持久化。最后成员死亡/永久移除后须等待12000 tick再重置整组，区块卸载不当作死亡；成员跨维度后永久移除仍清理其主世界marker。结构编组固定，但权重已用于生成尝试门槛：刀手白天8/10、夜晚10/10；祭酒明亮白天2/4、夜晚或光照≤7时4/4；盾士1/1。目录将其记为 `ACTIVE_STRUCTURE_ATTEMPT_GATE` 并提取实际分母、权重和通过率；不是抽取不同怪物的随机池，也不会增加编组数量、局部上限或绕过冷却。三种军队没有全地图自然入口；原四只击杀任务保留，另接入五军系击杀与古战场探访支线，不改主线门槛或最终奖励；部分特殊掉落及用途仍待实现。

阴司精英青灯判官鬼差与彼岸冥舟使用已有 `dynasty:underworld`；雷泽巨灵及云顶神器两界环使用已有 `dynasty:jiuxiao`。准确结构入口仍需实现对应 marker/trigger。未把普通怪或普通神器自然生成接进最终 Boss 场地。

## 最终 Boss 冲突

当前正式最终 Boss 是 **镇渊帝君 `dynasty:zhenyuan_sovereign`**，注册在 `src/main/java/com/dynasty/ritual/ZhenyuanBosses.java`，由 `ZhenyuanRitualService` / `ZhenyuanRitualSavedData` 管理出场、场次、祭坛与唯一宝匣奖励。

蓝图 **四象逆脉·混元祖兽** 的 `dynasty:hunyuan_zushou` 仅为候选 ID；`dynasty:zhenyuan_arena` 只记录其拟使用的真实维度。条目标记 `PENDING_CONFIRMATION`，在确定前置/隐藏 Boss 身份前，不挂现有四象贡品流程、不替换镇渊帝君、不增加最终奖励来源。

## 三个未定神器绑定

12 种神影中，以下 3 种对应神器没有出现在第 4 项 25 件的明确物品列表里：

| 神影 | 原文对应神器 | 目录处理 |
| --- | --- | --- |
| 太白剑仙器灵出窍 | 封魔剑冢·玄天剑（或顶阶神剑） | `artifactId=null`，待明确现有或未来物品身份 |
| 九天玄女引天刑 | 九天玄刹雷泽巨灵相关神兵 | `artifactId=null`，不可擅自绑定普通雷枪 |
| 烈火祝融九龙绕体神像 | 无相黑佛骨舍利（神火类兵刃） | `artifactId=null`，Boss 素材不自动等同武器 |

其余 9 个绑定使用目录中的拟定神器 ID。所有神影 `allowedDimensions` 继承对应神器的实际使用策略，禁止单独限定为主世界，也不注册可攻击的服务器 Mob。

## 基线与可复用架构

修改前 `./gradlew build --offline` 成功，日志 `/tmp/dynasty-cod1-baseline.log`，结果 `BUILD SUCCESSFUL in 3s`。Java 17、Minecraft 1.20.1、Forge 47.4.10；GeckoLib 4.8.4 已在 `build.gradle` 与 `mods.toml` 配置，无需重复引入。

源码扫描是独立的静态工作区快照，不冒充该次基线构建的逐字节归档。注册位置包含辅助函数调用；静态 item site 数量不是服务器实际 Item registry 的总数。语言/物品工厂动态注册应在运行时注册表测试中继续核实。

| 接缝 | 现有文件 | 集成约束 |
| --- | --- | --- |
| 内容注册 | `DynastyContent.java`、`entity/DynastyEntities.java`、`ritual/ZhenyuanBosses.java` | 保留所有旧 ID；初次快照 21 个普通注册 + 1 个最终 Boss |
| 人形攻击同步 | `entity/DynastyHumanoidMob.java`、`entity/CharacterMeleeGoal.java` | 已有一次起始时间同步及 50% 动画时刻命中；叛军、禁军、叛将使用此行为 |
| 模型 | `client/character/DynastyCharacterModel.java`、`DynastyCharacterRenderer.java` | 旧角色为自定义原生 EntityModel，不能声称已满足新 GeckoLib 骨架；镇渊已有 GeckoLib Geo/Animation |
| Boss 调度 | `entity/DynastyBossMechanicDriver.java`、`DynastyBossMechanics.java` | 全局事件已有阶段/盾/预警，同时实体内部有 AI；接入新系统须避免双重阶段和叠加攻击 |
| 战斗事件 | `DynastyCombatEvents.java`、`DynastyBossCombat.java`、`DynastyBalance.java` | 多层增伤/减伤/首杀；新能力不能重复倍率或重复奖励 |
| 属性上限 | `Dynasty.java`、`DynastyAttributeCaps.java` | 主类解开属性上限，不能依赖旧 Balance 注释推断高生命无效 |
| 生成约束 | `entity/DynastySpawnPlacement.java`、`ImperialPatrolPopulation.java` | 自然生成立足/碰撞/局部上限与命令/刷怪蛋/结构入口分开 |
| 网络 | `network/DynastyNetwork.java` | 协议初次为 6；StatsRequestPacket 被重复注册；新包接入避免隐式重排现有 ID |
| 神器逻辑 | `DynastySchoolWeapons.java`、`DynastySchoolCombat.java`、`QinglongDescent.java`、`DynastyBowRitual.java` | 复用服务端验证、时间轴、唯一事件及清理范式；青龙与太阳 DamageType 特殊处理不能递归或重复结算 |
| 现有神影 | `client/ImperialWeaponRenderer.java`、`ImperialDragonRenderer.java`、`HouyiAvatarRenderer.java` | 保留关羽/青龙/后羿渲染；它们不等于 12 种新神影已完成 |

下一批仍受文档的“实现→构建→资源→实机”门槛约束。古战场正式生成器与编组已接入；普通地形随机分布实测、部分材料用途、活动战斗重连/重启、专用服务器验收、最终美术与平衡矩阵仍未完成。目录全覆盖不代表剩余 85 项已经实现，也不代表 cod2 的十座成品地牢完成。
