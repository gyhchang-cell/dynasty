# Apugli 补充研究 → Carson

本轮交付 **6 条新增整链建议**、**15 组已审阅零增量记录**，相对“至少再 20 条”尚缺 **14 条**。固定提交仍为 `fcbadb4b288996f1767ce3d954522270e88681aa`（Apugli 2.11.0 / Minecraft 1.20.4）。全部来自已核验的官方迁移仓库缓存，没有再请求外部服务，rpginventory 404 未阻塞研究。

本轮实际核对并保存 **113 段不同的完整方法范围**，它们是调用链证据，不能按方法数计信用。所有建议 `credit=0`、`proposed_credit=1`，待 Carson 最终复核；没有向主账写入任何信用，也没有复用首批已接受条目的信用。

## 文件

- `batch-002.json`：6 条建议，每条包含指定 12 项来源/审阅字段及完整 supporting evidence。
- `excluded-002.json`：15 组已完整核对但不新增计数的记录，含同链、模板、镜像、缺失方法及孤立网络候选的明确排除理由。
- `reviewed-002.jsonl`：本轮统一逐条记录，共 21 组。
- `validation-002.json`：113 段方法摘录、固定文件 SHA-256 与首批 Git blob 核验索引的一致性；首批 8 个交付文件未改变的哈希证明，以及只读检查主账主方法无重复的结果。
- `handoff-002.json`：机器可读移交。封装脚本是 `tools/cod4/sweep-receipt-research/helpers/apugli-rpginventory/build_batch_002.py`，只处理缓存、只写本轮 helper 文件，不运行下载代码。

## 新增建议

| chain_id | 观察和相关性 | 主要限制 |
| --- | --- | --- |
| durability-slot-reentrancy-window | 耐久动作先将槽键加入 operatedStacks，再执行可能重入的动作；power tick 和移除清表。真实短生命周期去重链。 | 窗口由 power tick 决定；槽键不是攻击 ID，异常后仍占用至清理。 |
| explosion-parameter-consumption-and-effect-task | 实际爆炸实例消费伤害/击退/音量参数并清空；服务端结算后，客户端任务只 finalize 表现。 | 首次 hurt 就清伤害参数，可能仅影响首目标；pitch 不清。包没有 UUID/维度/TTL。三个爆炸入口与客户端任务合并一条。 |
| fatal-damage-snapshot-to-kill-credit | hurt 在调用 die 前保存 amount，die 选择直接来源或 killCredit 后消费；研究同步跨回调上下文族。 | 没有事件 ID、TTL 或清零；不能证明跨 tick。放置、附魔伤害、繁殖和铁砧局部捕获变体全部并入零增量证据。 |
| weather-target-registry-lifecycle | power 注册/移除实体机会表，后续 ServerLevel.tickChunk 雷击事件读取目标。 | 静态表跨世界，无 alive/维度复核；当前世界在同坐标下雨不等于目标属于该世界。 |
| crawling-state-and-deferred-pose | 实体 power 生命周期控制姿势边沿；实际服务端 producer 发出姿势包，客户端任务查 Player 后应用。 | 旧包无代次/UUID/维度校验；最后 power 计数时机与状态拆箱有边界。服务端和客户端不分别计。 |
| block-condition-event-invalidation-lifecycle | 已注册的附近方块玩法条件产生空间证据；成功 setBlock 事件失效缓存，后续条件读取，断开时清理。 | 缓存键缺世界/side；“年龄”按查询次数而非 tick，非短 TTL；定向失效只处理首个依赖中心。属于具体玩法完整链，不把通用缓存计入。 |

上述建议也包含失败边界和反例，不意味着这些实现可以直接移植。致死上下文族只代表一种同步跨阶段模式；若主研究要求每条必须含跨 tick 或明确任务容器，可继续降为辅助，不应为数量反向放宽范围。

## 去重与零信用结果

只读核对了 Carson 首批裁定，遵循原版薄包装和客户端同构周期算法不新增计数的口径：

- 放置方块 pending pair、附魔伤害 HEAD 布尔到后续取消门、繁殖另一亲本字段、铁砧输入字段等均保存完整方法，但同步 capture/use/clear 结构归于一个上下文族，不各加一条。
- 三种爆炸 producer、伤害/击退 XYZ/音量参数及延后客户端表现属于同一爆炸生命周期；共一条建议。
- 宠物伤害方向包装、last-attacker/target 包装、伤害量阈值循环和附近反伤方向包装均无独立的新延迟状态，零信用。
- 装备的两个 setter 入口没有去重生命周期；owner/killCredit 静态条件、免疫预检、入服保护计数读取、冻结旧阈值保留均不自动算回执实现。
- `ModifyEnchantmentLevelPowerFactory.java` 和 `EdibleItemPower.java` 在固定缓存树缺失，无法补全相应玩法链；没有虚构方法或借其他仓库补链。
- `SyncSinglePowerPacket` 有客户端排队函数，但全树未找到实际 producer/注册；实际 syncPower 走 ApoliAPI，因此此孤立网络候选零信用。
- `CustomProjectileAction` 与首批 CustomProjectile 整链重复；通用 FireProjectile 的原版后续消费未在授权范围核对，零信用。

## 对本项目的研究结论

耐久动作的“先登记再回调”是本轮最直接的重入/一次消费参考。爆炸参数的“第一次拦截就清掉”则说明消费范围必须是一次攻击还是单个目标，需要先定义清楚。全局雷击目标表与方块条件缓存都展示了缺世界身份可能污染后续消费的真实玩法反例。

这些证据支持在正式研究整合后区分产生刻、有效年龄、任务/攻击身份与消费状态；本岗未确定横扫 TTL 数值，未改 `FangtianSweep`，未替正式修复作运行验证。

## 执行边界

没有启动游戏、服务器、Gradle或下载代码；本轮无外部请求和重试。只写约定的两个 helper 目录，本轮未改首批文件、主账、正式 Java/资产、总待办。没有备份任务清单，没有删除任何游戏内容。数量不足如实交付，不声称完成 20 条或总目标 1000。
