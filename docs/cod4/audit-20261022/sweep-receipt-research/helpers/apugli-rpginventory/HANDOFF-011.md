# 第十一批：按扫描合并的真实伤害与共享燃料结算

交 Carson：1 条待审候选，3 组零增量排除，credit=0。不预增主计数；尤其本项的实体 hurt 到布尔消费在同次 heat 调用，未冒称跨 tick 成功队列。主审如判断与当前主题相关性不足，请整体排除。

`batch-011.json` 主方法为 `EntityMeltingModule.interactWithEntities:123-179`。完整链包含原生方块 ticker 选择、已注册 SmelteryBlockEntity、父 serverTick 的结构和服务端边界、模 20 相位、两个控制器共享的 heat、一次扫描 fuel probe、逐目标 hurt -> fill -> local melted、phase0 取燃料及 phase3 后续余额扣减。Smeltery/Foundry 两控制器只算同一条待审链。

观察：tick12 每秒扫描真实结构 AABB，每个 eligible 活实体 hurt=true 才产液并置本扫描布尔结果；fuel supplier 在扫描中只取一次。控制器接到汇总 true 后可取一份燃料，后续 phase3 扣余额。借鉴是区分逐目标伤害事实、产物接纳与共享资源账：聚合 true 可以表示任一目标通过 hurt，不能证明所有目标/产液/燃料结算成功，更不能替代方天每目标带身份回执。

具体边界：supplier 实际只验证已有 fuel 或模拟燃料温度，并不检查产液容量；满 tank 的 fill=0 也能 melted=true，允许丢弃余液。hurt true 未量健康差。实际 drain 数量异常只打日志仍加 fuel，不能当原子事务。local 布尔没有逐目标 UUID、攻击序号、TTL 或跨 tick 的一次消费保证；目标可每秒再次受击。只证明真实玩法的伤害事实和分相资源消费，不证明本项目修复或运行验收。外部 Mantle ingredient/recipe 枚举、Forge handler 内部不另计，Lombok getter 只记录字段声明不造完整方法。

`excluded-011.json` 保留实际阅读与去重：SpittingModule 六个完整方法复用既有 charge/010 流体弹，finishTime 只结束声音粒子；SlingKnockback 四方法仅同步 IS_BONKING 作用域，didBonk 在 performAttack 前即 true、结果被忽略，不能包装成延后伤害事实；SlimeBounceHandler 四方法复读确认和006已入账链完全重复。双跳虽已阅读，尚未展开完整调用者且不直接相关，仍是未提案、零信用。

14 个固定提交文件，41 段完整方法与 4 段明确声明范围（45 个证据范围，不是实现数）。来源仍是已授权缓存 `SlimeKnights/TinkersConstruct@f4e77d43f39ba1047bf93ae816b7e1beaab514c2`，逐文件 Git blob/源码 SHA256/原文行范围核对 errors=[]。`source-index-011.json` 和 `validation-011.json` 可复核。无网络、无下载代码执行、无编译/测试/游戏/屏幕操作，未改生产、QA、主账、主待办，不备份待办。

第十批精确化补充：`FluidEffectProjectile.onHitBlock:268-308` 在应用后若有残液且当前块变成 air，会于290行直接 return，因此绕过后方301-303的 updateCannonStack。不能把“consumed>0会尝试回写”概括为所有方块路径必然回写；JSON原文已包括该分支。本批另存 `addendum-010.json`，同链credit=0，原提交保留，不另提新候选。

断点：010两链已送；011此链待主审。不要再重提其两个控制器、recipe缓存、实体种类、燃料handler或所排除模块。后续仍只能从已有固定源选语义不同的状态/消费者，未读线索为0；没有声称完成20条增量、1000门槛或十小时总量。
