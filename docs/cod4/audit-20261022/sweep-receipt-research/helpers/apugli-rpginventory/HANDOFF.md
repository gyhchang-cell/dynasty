# Apugli / rpginventory → Carson

本批建议有效 **7 条独立实现**，完整审阅但范围/结构独立性待裁定 **2 条（0 分）**，辅助反例 **3 条（0 分）**。相对 80 条目标尚缺 **73 条**。79 段方法证据不是 79 条实现；最终入账 0，由 Carson 审核、跨批去重和决定计数。本岗不修改 accepted/progress 等主账本。

## 核验来源与版本

- 用户指定的 [MerchantPug/Apugli](https://github.com/MerchantPug/Apugli) 官方入口跳转到 [ChrysanthCow/apugli](https://github.com/ChrysanthCow/apugli)，GitHub API 的 repository.json 同样确认当前名称。原 gradle.properties 保留 MerchantPug 作者及 gh_owner，不能将此次改名当作第二个仓库。
- 固定提交 `fcbadb4b288996f1767ce3d954522270e88681aa`，默认分支 `1.20.4`；该提交 gradle.properties 声明 Minecraft `1.20.4`、Apugli `2.11.0`。没有构建，也不宣称运行兼容性。
- [TheRedBrain/rpginventory](https://github.com/TheRedBrain/rpginventory) 精确网页和 GitHub API 均返回 404，已保存 API 响应。无法区分私有、删除或不存在，故排除，未猜测替代地址，未研究其他仓库，未计数。
- 快照 540 个已保存文件全部用 Git blob SHA-1 对照缓存递归 tree 核验；递归重建各 tree 对象后，根树与 commit.json 中 `a9ccf9f7179ff627f18d17a76196cf71edb14f1b` 一致。各条另有整文件 SHA-256、完整方法范围、excerpt 和固定提交链接。

## 交付入口

- `batch-001.json`：7 条建议，均为 `reviewed_valid_pending_carson`，`proposed_credit=1`、`credit=0`。
- `scope-pending-reviewed.json`：客户端周期动作（与弹射物周期动作可能结构合并）、延迟体型 power（真实玩法任务但非战斗）两条，均已读全文，范围未定，0 分。
- `auxiliary-reviewed.json`：通用元动作网络分派、兔跳资源窗口、物品拾取延迟三个辅助反例，0 分。
- `reviewed.jsonl`：上述 12 条统一逐条格式；每条含用户所需 repo/revision/path/source_local/source_sha256/line/end_line/excerpt/observation/application/limits/url。
- `source-index.json`、`validation.json`、`handoff.json`：源证据索引、校验结果、机器可读移交。
- 原始资料和本地证据封装脚本在 `tools/cod4/sweep-receipt-research/helpers/apugli-rpginventory/`。`build_batch.py` 仅处理缓存，不联网，不导入/执行下载代码；可从项目根运行进行复核。

## 7 条建议及去重边界

| chain_id | 相关机制 | 合并范围 |
| --- | --- | --- |
| hit-history-expiry | 成功 hurt 后命中表跨 tick 保留、超龄/来源失效删除 | Fabric/NeoForge、条件读出、S2C差分均为一条 |
| custom-projectile-entire-lifecycle | 延迟连发、来源 UUID 解析、目标条件、命中/来源终止销毁 | 激活/调度/持久化/创建/命中/销毁整链只计一条 |
| projectile-hit-settlement | 命中累计到阈值或方块碰撞/discard 后结算冷却 | 两个终止路径及工厂包装合并 |
| cloud-effect-lease | 等待期、到期比较、目标授权延迟撤销、云移除时撤权 | 扫描/授权/撤权、两个 spawn 包装合并 |
| projectile-periodic-actions | 实体生命周期驱动周期动作和移除清理 | 条件、tick 注入和相位表同链 |
| block-scheduled-tick-action | 以当前世界/方块/坐标及随机延迟提交玩法调度 | 注册与执行同链，原版消费实现未在授权范围审阅 |
| key-input-deferred-lifecycle | 物理按键变更由 server.execute 消费至玩家 power 条件、重生清理 | 采集/网络/组件/条件一条，非传输库关键词 credit |

## 对 4991 → 4992 的可借鉴点与限制

1. 命中表与云租期显示跨 tick 保留和到期比较的实际用法；延后消费不能以产生刻必须等于消费刻作为唯一有效性条件。这里只提出研究方向，**没有确定本项目 TTL 数值，也没有修改方天代码**。
2. 伤害成功证据应来自成功回调；弹射物碰撞在 hurt 之前，不等同于已造成真实伤害。Apugli 的 hurt=true 也不能单独证明健康值减少或 directActor。
3. ownerUUID 在当前 ServerLevel 解析比裸数字 ID 更具体，但缓存 owner 只排除 KILLED/DISCARDED，不完整覆盖换维度/卸载。回执仍需独立的来源、目标 UUID 与原始维度快照校验。
4. 清表、discard、use 冷却均不自动证明严格一次消费；动作先执行再清理可能遇异常/重入。实现时要区分主消费、过期丢弃及终止清理，交正式修复岗决定。
5. 具体反例已逐条记录：previousHits=hits 引用别名、S2C 年龄自比较、云重施加时间未阻止重复动作、周期调度混用 owner/Projectile 年龄、延迟体型序列化读写不一致。不得照搬。

## 本岗边界与未完成项

仅审阅固定默认分支，不声称遍历全部历史版本。rpginventory 无法核验，Apugli 的加载器包装和同链变体不补数；不足 80 如实交付，未审查候选不计。本批至多建议 7 条，主研究总目标 1000 的进度由 Carson 维护，本岗没有推算或改写总数。

没有运行游戏、服务器、Gradle 或任何下载代码。仅写两个约定 helper 目录，没有改正式 Java、正式资产、主账本或总待办；没有备份任务清单，没有删除游戏内容。

外部服务结果已保留：rpginventory 404 后停止该来源。最初系统 Python HTTPS 证书校验失败，随后用本机 curl 获取一次有效资料；现阶段全部使用缓存，不循环请求。tree API 顶层 SHA 回显提交值导致的本地断言问题，已通过重建 Git tree 对象解决，没有为此重取外部资料。
