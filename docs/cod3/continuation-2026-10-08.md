# cod3 续做与原文删减记录 · 2026-10-08

仓库 `gyhchang-cell/dynasty`，工作分支 `cod3`，本轮基线 `2d8e34f32af2c6deba7e9dc687e10bd1fed4e64d`。在独立检出中修改；保留此前 `6ec66e2` 的实现和 PR12 兼容修复。不合并主分支，不修改其他工作分支。

## 本轮实现

- `BossSequenceDefinition` 覆盖任务列出的 17 个 Step 类型，增加独立 `params`、JSON 往返、旧目录兼容、步骤排序与边界校验。参数深拷贝，拒绝未知类型、负 tick、越界持续时间、非法 VFX 和非有限半径。
- `BossSequenceRunner` 只在服务端启动，校验 checkpoint 身份、字段与范围，损坏存档立即安全进入 COMBAT；preview 也计入 watchdog。到达定义时长的同一 tick 解开无敌、AI 和血条。可见性不再每 tick 被覆盖，并存入 checkpoint，在实体重新加入世界时恢复。
- 同步快照通过类型化定义只选当前仍有效的 VFX。WAIT、音效、SET_*、未来及已结束步骤不再被误当作 VFX；保留原始开始时间、seed、颜色、持续时间和比例。客户端离开 Boss 32 格范围或失去该实体时清理该序列效果。
- 死亡执行器执行原文的九种白名单步骤；禁止死亡阶段通过步骤重开血条、切换战斗阶段或直接授予世界状态。世界奖励仍由原来的结算流程负责。
- 新增八项 GameTest：全类型及旧目录序列化、非法数据拒绝、晚加入快照、八类损坏 checkpoint、预警与保存恢复、准确结束 tick、死亡白名单、永久遗留物部分领取后保存恢复。

**步骤数据类型完整不等于全部分镜已实现。** 当前执行器仍未绑定专属的 arena/preset、视觉实体、局部雾、镜头震动、对白、Boss phase 和世界状态 Step。未知执行器显式报错并跳过，不猜测地形、奖励或玩家输入。模型/动画 Step 目前仍为状态记录，不能当作已完成专属模型演出。镇渊继续使用自己的祭典与奖励系统。

## 原稿进度核对

`tools/cod3/README.md` 中原有的实现范围仍有效。以下任务按“任务索引中的具体 Acceptance”判定已完成，删除对应索引行；后文要求更高或混有未完成内容的整节不删除。

| 删除的任务 | 证据与边界 |
| --- | --- |
| C3-SEQ-001 | 本轮完整 Step 数据模型、params、JSON 往返与拒绝非法定义的 GameTest；不宣称所有 Step 的场景执行器完成 |
| C3-SEQ-002 | 现有服务器 runner + 六 Boss 时间线；NBT 恢复、损坏 checkpoint、watchdog 和结束时刻回归。保存恢复测试使用真实实体 NBT，不冒充两台真实客户端实测 |
| C3-SEQ-003 | `RitualAltarBlock` 已调用 `start(boss,20)`，显示名字预警，保留 200tick 抗性；六个绑定已有自动测试 |
| C3-SEQ-004 | 实体 persistentData 随实体保存，通用事件接入；没有另建与 Boss 实体状态脱节的计时器 |
| C3-DEATH-003 | 54 槽 `LootableRemains.Remains` 实际注册、可领取、NBT 保存与部分领取后恢复测试；专属雕像外观仍未完成 |
| C3-VFX-002 | `Cod3VfxRenderer.Geometry` 已有 decal/ring/beam/spline/mesh/after 六类原语及状态恢复；此前的 FBO 验证记录仍在。未把几何原语当作 40 个完整特效/伤害模板 |
| C3-UI-001 | `WorkshopBlockEntity` 三输入槽、ContainerData、共用 deposited、旧存档迁移；原有专用服测试再次覆盖 |
| C3-NPC-001 | `DynastyNpcEntity` 的 11 状态与 `NpcDialogue.open` 钩子已有实现；不删除 NPC 故事、完整对白、专属功能和生成生命周期要求 |
| C3-SECRET-001 | `SecretDefinition` 14 种事件类型，`SecretTracker` 世界 SavedData、玩家持久化领取、重复领取测试；30 个具体秘密与未接入故事奖励继续保留 |
| C3-TEST-001 | 现有 SEQ/DEATH/UI 自动化骨架与本轮八项新增测试；完整双人/客户端/资源重载矩阵仍保留 |

仍保留 13 个任务索引行。特别是 DEATH-001/002 的完整失败恢复和重启不双发验收、VFX 实际伤害区域一致性、工坊真实双人/shift-click验收、NPC DialogueNode 条件/后继节点及专属功能、秘密的完整世界落点和奇观精确条件，没有按“存在类名/存在表项”误删。

20 Intro、20 Death、40 VFX、15 NPC、30 秘密、25 奇观、10 世界状态的详细规格均保留，因为仍含专属分镜、模型、战斗绑定、故事或真实客户端验收缺项。开头历史工程扫描中有已过时描述；必须以当前源码及此核对记录判断进度，不能据其重复创建已有系统。

## 原文保真

`remaining-tasks.txt` 是上传的 `cod3_new(3).txt` 的删除式子序列。只删除十条已完成任务索引、已完成的祭坛预警小节，以及已经实现的 LootableRemains 建议新增条目。没有补写、改写、摘要、重编号或调整剩余行顺序。`remaining-deletions.json` 保存源/结果 SHA-256、删除行号与原文；字节与差异校验只允许删除。混合章节、全局约束和所有未验收项保留。

构建与测试结果见 `tools/cod3/verification/continuation-2026-10-08.md`。
