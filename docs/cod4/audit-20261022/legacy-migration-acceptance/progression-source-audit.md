# 原生死亡进度丢失：只读源码核查

状态：已确认迁移遗漏，尚未修复；1000处研究门槛未达到，不制作正式Java。工具仅读取源码和主协调的run-05-death证据，未操作世界或Java窗口。

同UUID `380df991-f603-344c-a090-369bad2a924a` 的死亡前后JSON显示：背包的ID、Count、完整物品NBT逐项相同；根级 `dq_p_18=1`、`dynasty_merit=420`、`dynasty_rank=3`、`dynasty_loyalty=10`、`dynasty_manual_given=1b` 均消失。`PlayerPersisted` 皇冠/里程碑复合标签完全相同。两次记录gameTime差261；真实按钮C2S复活、复活后存活240ticks及临时keepInventory的使用范围由主协调原始证据说明，不把261误写成采样存活时长。

## 原生链路与项目处理器

本任务私有快照的Forge1.20.1-47.4.10 `ServerPlayer.restoreFrom`（1118–1165行）在keepInventory分支复制背包、经验；随后只把根数据中的 `PlayerPersisted` 放入新玩家，再调用 `ForgeEventFactory.onPlayerClone(new,old,!keepEverything)`。该工厂方法仅发出事件，不自动复制其余ForgeData。这与“背包不变、PlayerPersisted保留、根进度消失”的实际证据一致。

当前项目并非完全没有Clone处理器：

| 处理器 | 实际迁移/重置范围 |
|---|---|
| DynastySchoolProgression.onClone | 自己的SAVE_KEY复合标签.copy |
| DynastySlotProgression.onClone | PlayerPersisted内槽位数据，清饰品缓存 |
| expansion.ContentProgress.clone | 原PlayerPersisted复合标签.copy |
| army.ArmyRoster.clone | 自己的军队KEY数据.copy |
| cod3.SecretTracker.clone | PlayerPersisted和cod3_progress_8、30；注释明确连续姿态/水下/限时装备挑战重置 |
| expansion.ExpansionSupplies.Guidance.clone | 删除寻路引导，清保暖临时状态 |

上述已审阅处理器没有复制本次丢失的Stats根字段、manual标志或历史dq任务字段。DynastyStats的功名、官阶、忠诚、叛乱在明确数值操作中写入，未发现这些字段的有意死亡清零/扣减。DynastyRankPerks.apply会按功名重算官阶，所以只补官阶不补功名仍会被重算回去。

边界：项目 **确有** 原有伤势死亡规则 `DynastyInjury.onDeath(Player)` 调用 `set(player,of(player)+25)`，LivingDeathEvent分发到它。不能笼统声称“无死亡惩罚”。它没有写上述功名/官阶/忠诚/手册/旧任务字段；本次永久进度修复不得顺带改写伤势，也不增加死亡惩罚。事件扫描结果包括测试与正式来源，测试回调没有当成正式处理器。本结论限定于已审阅字段读写及处理器，不宣称检查了所有代码的全部死亡语义。

## 永久字段候选与明确排除

候选白名单：Stats的四个整数值、手册已发放布尔标志、历史任务已核准的计数/领奖/事件事实，以及DynastyMerit有限名单的一次性事件/首次拾取标志。严格存在和类型检查，复制原Tag的独立副本；不调用会加成、发奖励、加效果或再发手册的数值/领奖API。完整候选在JSON，实施前仍需细化类型错误、新旧冲突与事件顺序策略。

`dynasty_rank_notice` 是派生提示，不是永久进度源。击杀收益时间窗、临时免疫/反击/冷却/姿态/坐标、寻路引导、保暖和现有重置机制不应因全ForgeData复制而残留。已有处理器管理的PlayerPersisted/流派/槽位/军队不能由新修复整体覆盖。

历史 `d0007965^` 的DynastyQuestManager与DynastyQuests已固定到本目录文本快照并记录git对象和哈希：任务索引0–23；`dq_p_`为整数计数，`dq_c_`为领奖布尔，`dq_e_`为事件事实。任务18为击杀九尾狐4只，因此 `dq_p_18=1` 仅是1/4进度，不等于完成或领奖。保留这些事实不意味着把旧索引直接映射到FTB新任务ID，更不能自动重领奖励。

证据索引、文件SHA256、事件扫描和逐项前后数据见 [progression-source-audit.json](progression-source-audit.json)。复核命令：`python3 tools/cod4/legacy-migration-acceptance/audit_progression.py`。这份本地根因审计不计入外部1000研究数。

后续扩展：上述5字段仅为实测样本。更广的有限名单、节庆/武器赠礼/首杀/累计击杀收据、时间窗排除与未审阅范围见 [permanent-field-policy.md](permanent-field-policy.md)；该说明仍不声称所有永久进度均已审计。
