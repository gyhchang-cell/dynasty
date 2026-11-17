# Jason → Carson：第三批补充审阅，全部 credit 0

本批新增 **2 条完整玩法链建议**、**8 组零增量审阅**，共 **103 段不同完整方法范围**。方法数不能当实现数。两个建议均为 `reviewed_valid_pending_carson`，最终范围与去重由 Carson 裁定；本岗未写主账。没有声称补足至少 20 条，也没有声称已工作满十小时。

文件：`batch-003.json`（2 条建议）、`excluded-003.json`（8 组排除/辅助）、`reviewed-003.jsonl`（统一记录）、`validation-003.json`、`branch-source-index-003.json`。每条记录和 supporting evidence 带固定提交、完整方法行范围及摘录、源文件 SHA-256、源码本地路径和固定 GitHub URL；每条主记录另带具体 observation/application/limits。

## 两条建议及实质边界

1. **behavior-goal-registration-revocation**：`fabric/behavior`，提交 `5cf41d11dbb4308b0796505e6c9d3541bad09217`，源码配置 Minecraft 1.18 / Apugli 1.5.1。实际注册的 ModifyMobBehaviorPower 每 10 个实体刻收集候选、按行为实例检查登记、向选择器加入 FleeEntityGoal，在条件失效或 power 移除时撤销。候选表、已登记表、实际执行器三个层次都有源码。新观察是**任务所属容器必须随句柄记录并在同容器撤销**：这里 Flee 加进 goalSelector，却记在 modifiedTargetSelectorGoals，后续向错误 selector 删除，有残留风险。候选列表不清/不去重、UUID 引用比较、无维度与已登记死亡对象清理也逐项记录。Passive 变体、注册、取消路径共一条，不拆数。
2. **enchantment-gameplay-invalidation-and-deferred-remove**：`next/1.20`，提交 `456c63617e147a845dd6908d6a9ef29c60ac7dd4`，源码配置 Minecraft 1.20.1 / Apugli 2.9.1。已在同一版本补全 UUID 桶、power 修饰值/条件快照、物品结果重建、真实附魔消费钩子、空槽持有者、移除回滚、实际 producer 与注册过的延后客户端任务。新观察是**变化被哪个作用域消费**：结果按物品存，变化快照却只按 power 存，首物品更新快照后其他已有物品结果可能保留旧值；anyMatch 短路进一步影响变化遍历。延后 remove 只查当前实体/power ID，缺 UUID/维度/代次。无 TTL、空实例表与外层桶残留、可变物品哈希键、普通非空物品持有者来源未闭合均列为限制。具体玩法完整链可供范围审阅，不能当通用缓存单独计数。batch002 中缺源条目仍为零，不把新版本代码拼回旧版本或再计一次。

这两条不重复 coordinator-receipt 的 12 条建议：新增依据分别是选择器登记/撤销容器错配、按物品结果与按 power 脏标志的消费作用域错配。主协调既有的攻击动画/冷却不等于伤害、取消门和弩状态建议不另申报。

## 零增量记录

- BunnyHop：完整核对落地宽限计数。比较 `>4` 在递增前，第 5 次无资格后为 5，第 6 次才 reset；第 6 次恢复资格也先 reset。是移动资源状态，未证明独立回执任务，不计。
- PacketAction：完整核对单双实体、两方向、注册与调用。双实体 C2S encode/decode 的动作类型不一致；排队后按发送者当前 level 查数字 ID，另一端未验证非空。是通用可配置动作运输，缺具体战斗配置消费证据，不计。
- Raycast：完整核对条件、接收者与穿透选择。target_condition 检查 actor 且真则返回，target_action 仍传 actor；缺条件在平台层为 true。穿透采集还有距离量纲与遍历顺序问题。同步查询不新增延迟实现。
- 瞬时效果免疫与雷击回调：分别记录 HEAD 取消、雷击条件极性；不把配置 Set/外部冷却包装当自有去重或时钟。不重报主协调已有前置表现/取消事实原则。
- 耐久动作：实际破损分支广播、shrink、setDamageValue(0)，不能用 TAIL 的新 Damage 阈值覆盖全部破损。仅补 batch002 同一整链的入口限制。
- Edible：同版完整补读 use、16/32 时长、finish、实体/物品动作、eat 与营养回调。传给物品动作的 `originalStack` 实际可能已 shrink，并非快照；原版使用计时/取消内部不在授权仓库内，零信用。
- Forge 伤害阶段：监听器 setAmount(finalAmount)，各动作收到的仍是先前 amount；死亡值来自外部 Apoli IPowerDataCache，生产/年龄/清空未审阅。补充已有同步伤害/致死族，不计新实现。

## 来源、核验和未完成范围

先用原缓存完成默认分支审阅，再对**同一个已确认官方迁移仓库**查询分支。7 次逻辑请求均 HTTP 200：分支清单 1 次，两个分支各 tree / commit / 固定提交 archive。所有响应保存在 helper 源码目录，没有服务错误后的重试。TheRedBrain/rpginventory 的既有 404 保持排除，没有再次请求或猜测 URL。

两个新增版本只抽取文本：198 + 556 = **754 文件**。本地重建全部 Git tree 对象并与对应 commit root 比较，逐文件 Git blob SHA-1 一致，再记录 SHA-256。没有运行下载代码、编译、游戏或服务器。各条链只使用同一个 revision 的证据。

只读参考了 protocol、主 accepted/reviewed 和 coordinator-receipt 批次。核对时主 accepted 为 812 行，其中 Apugli 7 条；不把它们重新申报。主账此后可能由其他协调者推进，该数字只是本次观察快照。

仍未审阅的官方历史分支仅是来源线索，不计任何 credit；本批未证明全 Git 历史穷尽，也未达到原目标 80。普通非空物品绑定、外部 Apoli/原版执行器细节、运行行为仍未闭合。后续研究应保留这些限制，不能靠变更版本、包装方法、平台镜像补数量。

本批只写两个约定的 apugli-rpginventory helper 目录，未改或备份总待办、主账、生产 Java、资产或游戏内容。对话列表中没有独立的 Carson 入口，本移交文件供主研究者读取；不冒称已经直接通知 Carson。
