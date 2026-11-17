# Halley batch 015 — Forestry 官方旧格式兼容（credit0）

固定 ForestryMC/ForestryMC `mc-1.12@72e15b0f08daa25d8293cf28b5d5e1da200f9161`，GitHub 与 CurseForge Source 已核实。只提交 **3 条** 待审语义家族：

1. 旧物品/方块 MissingMappings 与 BLOCK_ENTITY ID fixer 合并为一兼容家族。目标存在且非 AIR 才 remap，保留原 namespace；BE 成功仅改 id。下划线旧名自动生成但不覆盖已有映射。所有静态别名、两个同构事件、注册代理合并，不按行数计。旧温室多对一不转换额外角色状态，ignore 不代表恢复成功。
2. 工作台持久配方记忆 → 缺注册过滤 → 玩家选择 → 真实 IRecipe 消费。保存模板 ItemStack、锁、最后使用时间和配方 ID 列表；过滤缺失项后旧选择序号可能偏移。`selectedRecipe > size` 漏 `==size` 和负值，可能中断整体构造；Slot byte/int 兼容 reader 不做无符号处理/范围检查，writer 统一 int。库存 codec、9 槽、锁和各支持方法不另计。
3. 真实分析机旧嵌套能量 → 当前平铺 Energy → 裁剪 → 工序扣款。旧 key 只要存在就优先，writer 不删旧 key，可反复读旧值。持久电量与临时工序分开：成本/计数未保存，恢复已占分析槽会跳过设置成本的移入路径；这是静态边界观察，没有运行验证。其他机器复用同 reader 不再计。

JSON/JSONL 包含完整方法、Git tree/blob、源/摘录/规范化 SHA256、具体应用与重复风险。92 完整方法、1 静态初始化块、4 字段声明只是证据，2034 下载文件和 10283 索引方法不是参考数。document-integrity.json 全文件及证据 AST/hash 无错；主账只读快照 1053 行，primary 机械匹配 0 不能代替 Kepler 语义审核。

未深审原生/Forge 底层所有行为、所有配方材料等价 helper、tank/遗传写入；因此不宣称任意旧物品无损、合成原子或完整基因恢复。本批没有 Clone 实现，不把机器临时状态纳入玩家永久白名单。未编译/测试/游戏/服务/GUI/TCP/屏幕操作，未执行上游源码，未动主账、生产、待办或原存档。十小时与剩余范围未完成；后续同 commit 的遗传物品/玩家研究/邮件恢复尚未审读，不计信用。
