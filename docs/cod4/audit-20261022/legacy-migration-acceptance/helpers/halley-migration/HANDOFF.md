Kepler：本批完成 34 条完整链静态研究记录，全部 helper credit 0，未写主账。不是 34 条新增有效计数。以 reconciliation.json 的 2026-10-26T12:31:43Z 快照为准：19 个本 helper 家族已由主协调采纳；11 条已有/并行决定或同链重合，仅留补充证据；4 条 Waystones 已研究建议待合并。非重合建议上限 23，距离要求的 30 仍差 7，不用包装或字段模板补数。协调后续可能继续改变主账，合并前再核对。

- 待合并入口：suggestions-to-merge.jsonl（31–34，4 条 Waystones 完整链）。先独占保留并验证的官方仓库现名为 TwelveIterations/Waystones，旧 TwelveIterationMods URL 实际重定向，未虚构来源。固定 1.20.1 提交 0c2160e6cb0cdf9b79978f335821496ab385595d。
- 全量证据：batch-001.json / reviewed-suggestions.jsonl。每条有 repo/commit/revision/path/start/end/name/source/sourceSha256/text/excerptSha256/normalizedSha256/url、Git tree/blob、具体输入输出/观察/应用/限制/家族风险，以及完整支持方法。它们是研究记录，不是可批量自动接受的信用清单。
- 去重入口：reconciliation.json / overlap-and-decisions.json。8 号 tank 即使主账主方法不同也归已有储罐链；22 号图鉴同已有 Lectern 解锁链；14 号 owner 转换被主协调判重，不重新包装冰蛋；4/19 通用容器被拒绝；28 限槽桶仅 pending，不充新增。单/双箱、shaped/shapeless、卷轴/碎片换键、精灵瓶/屋、近似坐骑及平台包装均已合并。
- 验证：verification.json，175 个独立 AST 证据节点、59 个完整源文件；方法/构造器或完整 codec 字段边界、SHA-256、固定官方 Git blob、commit→tree 元数据均通过。Codec 字段只是支持证据，不是新增实现。无主方法内部 normalized 碰撞；语义判重仍由 Kepler 最终执行。

重要校正：10 号中间稿曾误写“组件展开数组”。最终观察已改为：世界存档和 CollapsibleBlockData 组件均保存 packed int，unpackOffsets 消费时按四个 5-bit 区间展开。请同步修正已采纳主账的观察，不能保留中间稿错误。7 号 onLoad 更准确为核对配方类型，不能夸大为完整条件校验。

优先借鉴的是：恢复载体后确认目标成功再删源；缺依赖不等于永久失效；保存事实/进度与战斗、移动、站立等待计时分别定寿命；容量变化明确回收溢出；稳定 UUID/维度与会话 entityId 分离。34 号首次调谐完成事实、31 号查询即删除无效已解锁 UUID、32 号旧 WasGenerated→Origin fallback 和缺主人导致权限放宽，均有实际完整调用方法可核对。

边界：Waystones 的死亡 Clone 由外部 Balm 持久数据钩子承担，本批未审 Balm，不声称已证明死亡保留；Scope 中初选的 Accessories Trinkets 导入未形成独立研究，未计数。21 号世界生成历史、17 号驯化时间和 28 号 no-sort 策略相关性较弱，已逐条注明。没用 GUI 状态或纯网络消息补数。所有方法索引只用于发现和 AST 提取，未审查方法不计数。

源码及工具只在 tools/cod4/legacy-migration-acceptance/helpers/halley-migration/；说明只在本目录。source-pins.json、provenance/、source-manifest.json 和 sources/ 可复核固定提交/整文件；额外 Waystones 下载只把 Java/LICENSE 作为静态文本保存。未执行上游代码、未启动游戏/服务器、未写生产/待办/主账、未备份清单、未删除游戏内容。

复核工具顺序：用 /usr/bin/python3 运行 helpers/halley-migration/review.py、validate.py，再用 python3 运行 reconcile.py。AST 库只读复用 guard-ownership-research/.work/python39，脚本禁止生成该依赖目录的 pyc。重跑只写 helper 自身；reconcile 仅读取当前主账。保留说明 SOURCE-RESERVATION.json 是选源过程记录，不代表来源已全部转为有效信用。
