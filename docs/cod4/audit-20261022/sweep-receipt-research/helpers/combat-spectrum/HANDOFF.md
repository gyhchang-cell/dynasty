# 方天横扫回执研究：BetterCombat / Spectrum 辅助移交

本批提交 **29 条已读完整相关方法/调用链的独立实现建议**：BetterCombat 2 条、Spectrum 27 条。另有 **16 条辅助/排除记录，信用均为 0**。距本岗目标 80 条尚差 **51 条**；没有声称完成 80 或全体 1000。所有建议均待 Carson 最终审核、跨仓语义去重并决定计数；本批 `credit=0`、`master_credit=0`，仅 `proposed_credit=1` 表示建议。

两仓库的官方 GitHub 页面、公开非 fork 元数据及对应提交已实际核对，均存在，没有虚构来源：

| 仓库 | 固定分支 | 固定提交 | 建议数 |
| --- | --- | --- | ---: |
| [ZsoltMolnarrr/BetterCombat](https://github.com/ZsoltMolnarrr/BetterCombat) | 1.20.1 | `8814f0297bb85f4513646e73d604069487ce7322` | 2 |
| [DaFuqs/Spectrum](https://github.com/DaFuqs/Spectrum) | 1.20.1-fabric | `8011b7e71db6d14eaa2dc85d35372c506e59f236` | 27 |

## 可核对文件

- [batch-001.json](batch-001.json)：29 条逐项观察、应用点、限制；每条有要求的 12 个来源/证据字段，以及完整方法签名、结束行、摘录哈希和固定提交 GitHub 链接。
- [evidence-contexts.json](evidence-contexts.json)：291 个去重后的辅助方法/全文上下文；`support_evidence` 逐条引用。上下文没有独立信用。
- [reviewed-zero-credit.json](reviewed-zero-credit.json)：16 条零信用决定，包括通用队列包装、普通冷却、未追全链及同步 BFS。
- [source-manifest.json](source-manifest.json)：两个源码快照的提交核对、归档哈希和全部 1648 个文本文件的 SHA256。源码只保存在本岗 tools 目录。
- [verification.json](verification.json)：主账本只读格式/同仓条目扫描快照。扫描时 accepted/reviewed/candidates 没有这两个仓库的条目；这不等于跨仓语义去重已通过。
- [independent-validation.json](independent-validation.json)：另一份本地自编校验器结果，1648 个文件哈希、45 条审查记录和291处辅助证据的精确摘录/行号/URL/引用均通过。仅校验证据完整性，不把静态推断变成运行证明。

## 最有用的借鉴与边界

1. **SP16 HeartboundChest**：使用 `lastTick + 20 > now` 保持跨 tick 告警，直接证明“产生刻不等于消费刻”不应自动作废。但原实现缺少年龄非负下界，tick0也被哨兵排除；它是持续窗口，不是一次消费。
2. **SP20 格挡反击**：`consumePerfectCounter` 先清令牌再返回资格；可借鉴一次取走语义。它没有绑定目标 UUID、维度或动作代次，部分提前清窗口路径值得警惕。
3. **SP01/SP02/SP04/SP05**：无线红石、采收、实体吸收、共鸣各有独立真实玩法消费者；通用 EventQueue 与包装不另计。队列按调用次数倒数，delay=d 在 d+1 次 tick 才触发；先回调再 remove 有异常和重入边界。
4. **SP06 Pastel**：真实物品载荷、剩余延迟、世界键/网络身份和到达时目标解析形成一条完整运输生命周期；长时持久化不可照搬为短伤害回执。
5. **SP27 炮塔**：事件接收和攻击时都存在世界/目标复核；底层 vanilla 振动调度未下载阅读，不宣称掌握其精确时延。
6. **BC01/BC02、SP23/SP24**：动画/本地 `ATTACK_HIT`、穿透推进或声效不等于服务端伤害成功。InkProjectile 的成功分支才以 `damage(...)` 的返回值控制后继击中行为。

针对已确认的 4991→4992 问题，仅提出研究原则：区分请求和真实成功回执；记录产生时间与来源/目标 UUID、维度、动作身份；消费时以明确的非负有限年龄及身份条件复核；合格回执先取走再结算，清理无效/过期条目。没有据这些案例指定 TTL 常数，没有修改正式修复代码，也没有照抄外部实现。

## 数量和未完成部分

本批按独立生命周期合并同链包装、分支、派生载荷及颜色/时间档位，尤其 BlackHoleChest 的 Item/XP 只合计1条，LightShard/LightMine/LightSpear 不拆成多条，通用 EventQueue/SchedulerMap 都是0条。弱相关的离线补偿、普通红石调度等已在各条 limits 中说明，Carson 可继续收紧。

没有宣称两仓库已被穷尽：制造机、多阶段 AI 等其它潜在候选尚未形成审查条目，均不计数；不为补到80而将关键词命中或未读源码算入。未完成的 Detector、RedstoneGravity、MiningProjectile、AzureDike 等具体限制保留在零信用文件，便于后续续查。本批移交后可由 Carson 恢复这两个仓库的研究。

## 操作约束

全程未启动游戏、服务器或构建；未运行任何下载的代码；仅运行本地自编的静态下载、组装和证据核验脚本。只写入用户授权的本岗 tools/docs 两个目录，未改正式 Java/资产/待办，也未写 Carson 的 accepted/progress 等主账本。主账本可能由其他岗并行更新，所存 SHA 仅是只读扫描时点，不是全项目冻结证明。
