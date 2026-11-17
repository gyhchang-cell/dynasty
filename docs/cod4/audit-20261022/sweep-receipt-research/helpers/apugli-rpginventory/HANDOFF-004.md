# Jason → Carson：旧版食物组件撤销链，credit 0

考试期间最新约束见 `CONTINUATION.md` / `continuation.json`：禁止编译、测试和启动游戏/客户端/服务器/GameTest，不影响屏幕或锁屏；只有用户明确通知后才恢复。以下是此前已封装的静态研究成果，未验收、未写主账。

第四批包含 **1 条待审整链建议、6 组零增量审阅、50 段不同完整方法范围**。与第三批合计 **3 条待审建议、14 组零增量、153 段不同完整方法范围**，全部 `credit=0`；方法数不能换算为实现数，未补足至少 20 条，未声称满十小时。

建议 `temporary-food-component-lease-and-slot-revoke` 来自官方 Apugli `architectury/1.16` 固定提交 `c465103bbb607a1b96e09f00b9a1443d7d810838`，源码配置 Minecraft 1.16.5 / Apugli 1.7.0+1.16.5。完整串起真实 baseTick、临时食物组件授予/撤销、对象引用归属检查、物品使用与复制、power 移除、实际平台发包、注册接收器及 queue 消费。

具体新增观察：源端清理前验证旧 FoodComponent 身份，包里只留下目标数字 ID 和槽位；客户端延后取当前槽位并无条件清理，丢失原物品与组件代次。旧清理可能作用于换槽或重新授予的新状态。清理四字段也未完全实现：setFoodUseAction(null) 被实际 setter 忽略。副手授予分支误读主手状态、predicate 改变后可能不回收、复制共享组件引用、广播再单发本人等边界均已逐项记入 JSON，不声称运行上已复现。

六组零增量记录保留完整方法证据：同链双 HEAD 动作入口与 return 值覆盖、外层状态效果替换仍保留 hiddenEffect 引用、只有 HUD 比例的 InvertedCooldown、旧 UUID 按键同步缺发送者绑定、旧附魔缓存持有者首次绑定与转手问题、旧 RocketJump 客户端重算和新版仅表现消费的差异。它们分别属于同链、模板、外部原版生命周期或已覆盖版本族，不另计数，也不重报 coordinator-receipt 的 12 条建议。

文件：`batch-004.json`、`excluded-004.json`、`reviewed-004.jsonl`、`validation-004.json`、`branch-source-index-004.json`。已保留完整方法行范围、摘录、固定源码哈希和 URL。第四批来源查询 5 次逻辑请求均 HTTP 200；250 个抽取文本文件逐个比对 Git blob，并重建全部目录树核对提交根。没有执行下载代码。

`feature/1.20` 与 `multiloader/1.19.2` 仅查询目录树，未逐方法研究，信用为零。没有跨版本拼接证据，没有证明全历史穷尽。Rpginventory 既有 404 未重试。

本岗没有启动或排队测试，故无可确认归属的待停止测试；没有终止用户或其他人的进程。考试指令后仅读取记录并整理文档，未再运行编译、测试或游戏。只写约定 helper 目录，不改或备份总待办，不删除游戏内容。
