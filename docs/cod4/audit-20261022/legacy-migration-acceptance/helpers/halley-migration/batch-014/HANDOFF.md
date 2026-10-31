# Halley batch 014 — Modular Routers（credit0）

官方 desht/ModularRouters，MC1.20.1-master 固定 commit `7e90aa8d59f43cc82cb0c752f9f35731750ef718`。交付 **2 条** 实际持久玩法恢复链，均待 Kepler 语义去重，不自动计主账。100 个完整方法、3 个字段声明、21 个证据文件仅为链支持；233 个下载文件、1544 个索引方法都不是有效参考数量。

1. **安全升级 → 保存升级库存 → 重载编译 UUID 名单 → 实际菜单访问**。Owner 是名字/UUID 的字符串列表，Players 以 UUID 为键。编译先清派生集合再合并，缺 owner 会忽略整个名单，最终空集合允许访问；持任意手 Override Card 也允许。非法 UUID 无局部保护。重设 owner 不清旧 Players，名单 UI 上限不约束 reader。菜单打开后 stillValid 不重查权限。fakePlayer 仅审到同 owner profile 的构建，不宣称最终攻击边界已读。
2. **模块持久 GlobalPos/Face → 编译 Sender2/3 → capability → 真实库存传输**。维度和坐标而非显示名决定目标；未加载返回空 capability，成功缓存依赖失效通知。Sender3 实际 validate 的同维短路绕过黑名单，与诊断方法不一致。多目标名字更新会调用单 Target writer，不能把显示名刷新当完整多目标迁移。未见旧 ID/维度别名映射；各等级/面/维度/多目标键不拆计。

完整 JSON/JSONL 包含固定 Git tree/blob、源 SHA256、方法范围与原文、excerpt/normalized SHA256、具体应用限制及重复风险。document-integrity.json 的所有源/Git blob/完整 AST 检查无错误；主账 1049 行快照只读，primary 机械匹配 0，仍必须人工判定语义重复。升级 tooltip 里的 deserialize 明确未当作放置恢复证据；Forge/原生物品恢复及 Filter 全策略未深审，不扩张主张。

仅执行本辅助目录自写文档/哈希工具，未编译测试、未执行上游代码、未开游戏/服务/GUI/TCP、未操作屏幕或原档，未改主账/生产/待办。十小时和剩余范围未完成，继续后续研究。
