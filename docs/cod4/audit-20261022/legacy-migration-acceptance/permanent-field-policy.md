# 永久字段语义审计（部分覆盖，非全部永久进度声明）

本表扩展了死亡样本的5个字段，仍是研究阶段候选政策，不是正式复制代码。当前按确切来源确认47个永久根字段候选，另1个按事件防重领收据候选；历史24任务的57个已知键另列。它们并非本次旧档里都出现或都已实测丢失。

| 来源 | 字段与语义 | 候选处理 |
|---|---|---|
| DynastyStats | merit/rank/loyalty/rebellion | 同时保留原整数；官阶现有重算继续生效 |
| DynastyManual.giveOnce | dynasty_manual_given | 一次发书收据 |
| DynastyMerit.onEvent | dynasty_merit_evt_，6个正奖励事件 | 精确有限名单的布尔收据，不能整个merit前缀复制 |
| DynastyMerit.onFirstObtain | dynasty_merit_seen_，18个正奖励物品 | 精确有限名单，避免死亡后重复首次奖励 |
| DynastyWeaponGifts.grant | dynasty_gift_，金锏/尚方剑/七星刀/射日弓4个 | 保留收据，不调用grant发物品 |
| DynastyWeaponGifts.onMobKill | dynasty_boss_kinds、dynasty_boss_kinds_list | 计数与种类列表一起保留，不只复制一半 |
| DynastyWorldEvents | dynasty_festival_day | festival:LocalDate的当日已触发收据；与活动buff有效期不同，保留以免死亡重复触发 |
| DynastyBossCombat | dynasty_firstkill_，10个既有Boss/神兽 | 旧根收据保留；当前新收据也写PlayerPersisted。新修复不碰整个PlayerPersisted；ArmyEncounters仍读根收据的前置条件需保留 |
| DynastyWorldEventManager | DynastyEventMonsterKills | 累计击杀、上限10000；玄鸟止戈门槛100，无时间窗 |
| 同上 | DynastyXuanniaoBlessing | 最近祝福事件UUID防重修装备/奖励收据；单独候选，只保留收据，不恢复其效果。尚无原生死亡验证 |
| 历史d0007965^ | dq_p_0..23、dq_c_0..23及9个已知dq_e_ | 计数、已领奖、事件事实；不自动认定FTB完成，不发奖励 |

明确排除：`dynasty_merit_kill_window/earned` 是10分钟收益窗；`dynasty_rank_notice` 是派生提示；`DynastyArmyPermitUntil` 是12000tick通行有效期；`DynastyCompassNext` 是5秒请求冷却。伤势及最近受击时间属于原有伤势规则，另行负责。反击、蓄势、短时免疫、姿态/位置/临时挑战等不因“字段写进NBT”就变成永久进度。

已有PlayerPersisted、School、Army、Slot及SecretTracker的克隆职责不重复覆盖；`EquipmentBehaviors.saved`实际取PlayerPersisted.dynastyCod4。盔甲联机原生死亡证据（receipt-death.json及run-04/result-death.json）已证明其中保命/玉蝉冷却、守卫租约deadline/generation由现有克隆职责保留，原冷却前不能再次触发。这些有期限状态虽需保留，仍不是本次根级永久字段白名单：新修复不得复制、覆盖或合并PlayerPersisted/dynastyCod4，也不得重置冷却。皇冠、饰品抽取历史、站点标记同由现有容器负责。此证据不能外推所有根字段或旧档完整覆盖；独立来源与精确所有权见armor-clone-boundary.json。

扫描找到76个非GameTest、直接调用getPersistentData的源码文件，这是候选文件数量，**不是76个都已完整审阅**；别名、包装函数及世界SavedData不能仅凭文本扫描宣称已覆盖。偏好/模式、其他NPC与挑战状态、Bounty/Dungeon/世界事件完整账本等未核实体系继续列限制，不提前纳入复制白名单。

确切键列表、NBT类型、来源哈希、排除理由及76文件索引见 [permanent-field-policy.json](permanent-field-policy.json)。复核：`python3 tools/cod4/legacy-migration-acceptance/audit_field_policy.py`。本地字段审计不计入外部1000研究。
