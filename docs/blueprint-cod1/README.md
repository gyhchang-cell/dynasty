# cod1 第 1～5 项：工程审计与内容落点目录

这里记录 94 个蓝图条目的身份、既有工程对应关系和世界落点。当前为 **4 个基础模板 PARTIAL，剩余 90 项 NOT_STARTED，0 项 DONE**；30/15/12/25/12 的类别总数不变。目录本身不是运行时注册文件；四模板的 `ACTIVE_RUNTIME` 只表示已有注册、资源和活动生成代码，不表示单机/双人验收通过。

卒伍刀手、橹盾甲士、符法祭酒、山精山魈已映射真实实现；另外26只基础怪、15精英、12 Boss、25神器、12神影尚未启动。最新服务器证据 `/tmp/dynasty-cod1-tests5.log` 为136/136通过，其中含17项新GameTest（包括跨维度成员清理、时段/低光权重和伤害回调致死时钟回归）；同一日志实际执行 `:jar`、`:reobfJar`、`:assemble`、`:build` 并报告 `BUILD SUCCESSFUL`，本轮生产构建通过。冻结资源实际为170骨骼、352 cuboids、30动画片段，计数与哈希记录于 `template-verification.json`，不等于实机质量通过。真实客户端 `ingame/solo-20261002-c/host` 的14阶段状态/截图流程也通过；其报告明确不代表多人或视觉质量通过。双客户端及最终模型质量仍由主代理验收。

## 文件

| 文件 | 用途 |
| --- | --- |
| `content-definitions.json` | 全部 94 个精确名称、源文行号/摘要、候选 ID、同类旧内容参考、必填世界落点、资源存在性和验证状态 |
| `world-placement.tsv` | 94 行世界落点表；可在表格工具中打开。包含维度、标签、生成/来源、数量、重生、任务占位、Boss Arena、神器来源和神影锚点 |
| `registry-snapshot.json` | 原有源码注册位置与资源路径/哈希清单，不复制大量工作区贴图 |
| `baseline-build.json` | 修改前完整构建成功证据；普通 Gradle test 为 NO-SOURCE，不等于 GameTest 或进游戏测试 |
| `catalog-validation.json` | 最近一次生成时的静态校验结果 |
| `template-verification.json` | 四模板服务器测试、单客户端14阶段截图流程及模型审查证据；多人/最终质量仍PENDING |
| `stage0-2-audit.md` | 独立阶段边界核对、实现审查及尚未解决的验收差距；不改写原任务范围 |
| `../../tools/blueprint/catalog.py` | 可重复提取、生成、检查工具，无第三方依赖 |

## 可重复检查

从仓库根目录运行：

```sh
python3 tools/blueprint/catalog.py --check
python3 tools/blueprint/catalog.py --generate --source '/Users/a15356015027/Desktop/code x提示词/cod1.txt'
python3 tools/blueprint/catalog.py --generate --refresh-templates --template-test-log /tmp/dynasty-cod1-tests5.log --solo-evidence docs/blueprint-cod1/ingame/solo-20261002-c/host
```

`--check` 只读，检查原文精确名称、94 项类别计数、唯一 ID、真实维度 ID、各类别必填字段、标签存在性、最终 Boss 保护以及 DONE 的实机证据。资源在扫描后出现/消失会单独列出，不会悄悄被算成已完成。

`--generate` 机械生成 JSON/TSV 并刷新资源存在性。保留已有 `implementationStatus`、`verification` 和 `implementationEvidence`；对于非 NOT_STARTED 条目，还保留实施者填写的实际资源、属性、生成/来源字段。初次基线构建证据与静态清单默认保留；只有显式 `--refresh-inventory` 才重新扫描清单。该参数用于校正扫描器，不表示重新建立构建基线。

`--refresh-templates` 显式提取 `BlueprintEntities`、`TemplateSkills`、`TemplateContentDefinitions` 及实际 biome modifier；结合 `BlueprintSpawns` 的固定编组、已消费的生成尝试权重、局部上限和保存标记，重建四模板的 PARTIAL 记录。必须显式提供 `--template-test-log`；测试总数从完整成功日志读取，新测试数从蓝图 `@GameTest` 注解读取，并与当前 `dynasty` 命名空间全部测试注解计数交叉核对，不硬编码136/17。缺失、失败、过时或不同测试子集的日志会拒绝刷新。`--solo-evidence` 只记录确有PASS报告和14张截图的单客户端流程，不将其扩大为视觉质量或双人通过。该操作不设置 DONE。源结构或测试结果不符时直接失败，不能把任意日志自动当成原证据。普通 `--generate` 不覆盖后续主代理补充的实机结果。

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

普通军队、山林、墓穴、机关遗迹默认映射到 `minecraft:overworld` 中符合原文的结构/区域。初次快照中的 `dynasty:cod1/...` 地点标签仍为 PROPOSED_PENDING，没有虚构注册；新实现的三个 `dynasty:blueprint/...` 标签另行记录如下。

| 模板 | 已接入的真实地点 | 实际编组/限制 |
| --- | --- | --- |
| 卒伍刀手 | `#dynasty:blueprint/military_sites`：`great_wall_gate`、`tiangong_citadel`；`#dynasty:blueprint/ritual_sites`：`star_altar`、`herbal_retreat` | 军事点3名刀手+1盾士；祭祀点2名刀手+1祭酒；Y -32～220 |
| 橹盾甲士 | 上述军事点标签 | 每标记1名；Y -32～220 |
| 符法祭酒 | 上述祭祀点标签 | 每标记1名；Y -40～240 |
| 山精山魈 | `#dynasty:blueprint/shanxiao_habitat`：原版森林或山地标签 | 主世界Y 50～240，权重4，组1～3，24格内同类最多3只，白天通过率1/4 |

结构生成只搜索玩家所在真实结构的已加载安全落点，每100 tick主世界最多新增2只；成员UUID、累计产出、冷却和清理状态持久化。最后成员死亡/永久移除后须等待12000 tick再重置整组，区块卸载不当作死亡；成员跨维度后永久移除仍清理其主世界marker。结构编组固定，但权重已用于生成尝试门槛：刀手白天8/10、夜晚10/10；祭酒明亮白天2/4、夜晚或光照≤7时4/4；盾士1/1。目录将其记为 `ACTIVE_STRUCTURE_ATTEMPT_GATE` 并提取实际分母、权重和通过率；不是抽取不同怪物的随机池，也不会增加编组数量、局部上限或绕过冷却。三种军队没有全地图自然入口；所有模板的未来场景任务钩子及部分特殊掉落仍待实现。

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

后续执行仍受阶段 2 门槛约束：4 个模板怪完成单机与双人验证后，才批量扩展剩余 26 只。目录全覆盖不代表该门槛已通过。
