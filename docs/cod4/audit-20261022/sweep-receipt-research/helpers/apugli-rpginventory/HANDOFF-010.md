# 第十批：挂钩收线事实与流体弹剩余载荷

交 Carson：2 条完整待审候选，credit 全部为 0。没有给主账加数，没有宣称 937/1000 的缺口已补齐。沿用人类已授权的固定其他来源；Apugli 已读包装和 rpginventory 的既有 404 不增加信用，不发起新仓库请求。

来源为 `SlimeKnights/TinkersConstruct@f4e77d43f39ba1047bf93ae816b7e1beaab514c2`。16 个源码文件逐个对缓存的未截断提交树核验 Git blob，再记录整文件 SHA256。12 段原版父层方法来自本机版本化 Forge 1.20.1-47.4.10 映射源码 Jar，保存 Jar/源码哈希，明确只有本地 artifact 版本，没有虚构原版 Git commit 或 URL。来源本轮未在线重验，网络请求为 0。

- `batch-010.json`：两条主方法及完整支持链、来源原文/行范围/哈希、具体观察/借鉴/限制/语义去重。
- `source-index-010.json`：来源元数据、16 个固定提交文件及本地父层方法。
- `validation-010.json`：79 段完整方法和 2 段配置声明，共 81 个唯一证据范围，文本/行范围/哈希核对 errors=[]。方法数不是有效实现数，核对不是编译/游戏测试。
- `reviewed-010.jsonl`：逐候选可审阅记录。

候选 1，`hooked-target-captured-impact-to-later-reel-damage`：主方法 `tools/entity/CombatFishingHook.java:205-287`（含 Override）。实际 `FishingModule.onToolUse:70-133` 先创建鱼钩，碰撞 `onHitEntity:192-198` 只捕获 impactVelocity 并挂住目标；后续用户收线经原版 retrieve 才触发 hurt 和 oldHealth-currentHealth 回调。原版 tick 限制 owner 存活/未移除/任一手仍能抛竿/32 格距离，并在挂住状态检查 target 未移除与同维度；正常 retrieve 最终移除钩并清 owner.fishing。装备替换与主手新获得抛竿能力还有显式取消路径。区别于已有 ThrownTool 原槽回收与 ThrownShuriken 命中退款，本项状态是“先挂目标、捕获速度，再由后续玩家动作伤害消费”。

具体限制：正数 retrieve 是杆损耗，不能当伤害成功；hurt true 也不保证正健康差。回调重取当前手持杆和 modifiers，而非原始物品代次；换成相同 modifiers 的另一杆可通过此处换装比较。父 tick 的 target 维度检查不是 pullEntity 内原子再验。1200tick 只是落地/贴墙计龄，没有统一短 TTL；正常 discard 不保证异常重入 exactly-once。外部 Mantle helper 和客户端 swing 实现不在本固定树，本批不据此承诺其内部时序/来源处理。

候选 2，`cannon-payload-flight-current-source-and-remaining-fluid-consumer`：主方法 `tools/entity/FluidEffectProjectile.java:221-253`（含 Override）。完整链由炮的真实红石 scheduleTick4 -> shoot 创建流体载荷并扣 source tank -> 弹体飞行 -> 命中时重新读取 recipe 和原坐标当前 slot0 -> 按最大效果返回比例扣载荷 -> 耗空移除/残量继续。实体命中、方块延续、邻块及所有配方分支合并为一项。实际 moltenClay 配方 `FluidEffectProvider.java:175-182` 同时伤害和掉砖，因此伤害失败而掉砖返回正值时，流体消耗仍可为正。通用资源结算不是成功伤害事实。

具体限制：来源只有炮坐标，loaded/current capability 不验证原 block entity 类型或实例代次；执行后回写还会再次解析当前 handler，没有 compare-and-set。未运行复现这种替换风险。发射和掉落 addFreshEntity 返回均未检查；资源消耗也不是实际 spawn 接纳凭证。命中击退早于伤害成功；没有显式目标 UUID 去重账本、统一 age TTL 或发射配方快照。主账已排除的同步 BlockInteract/PlaceBlock、纯缓存和已有 ToolAttackUtil 都只作零增量支持，绝不另包装；若本项相关性不足，请整体按 0 排除。

两项均只读比较主 accepted/reviewed 和本岗 001–009，主方法没有已有条目，JSON 同时写明最近语义家族与独立状态/消费者。未读新线索仍为 0。未改生产、QA、主待办、主账；未备份待办、未启动/编译/测试/操作屏幕。没有声称十小时总量已完成。下一断点继续固定来源的新生命周期，不再次提案钩子分支、效果模板或此批父层包装。
