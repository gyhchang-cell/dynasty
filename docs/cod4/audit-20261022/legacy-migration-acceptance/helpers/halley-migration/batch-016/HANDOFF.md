# Halley batch 016 — Forestry 真实持久玩法恢复（credit0）

沿用官方 ForestryMC/ForestryMC `72e15b0f08daa25d8293cf28b5d5e1da200f9161` 的全部固定源字节/Git tree/blob，不重新下载。交付 **3 条待审语义链**，支持方法 217 个、字段 14 个、证据文件 33 个均不代表参考数量。与 batch015 注册兼容/工作台/电量家族分开审查，所有记录 credit0、accepted=false。

1. **UUID world tracker + 研究笔记成功登记后消费**。WorldSavedData 名称用 UUID，登录/换维度重取研究而非全复制旧实体。读取历史集合为增量并集；mutation key 含父顺序，改 UID/次序不自动识别旧标记。未知 root/parent/组合、已研究不消费，但缺/未知结果 RST 会放宽为第一个组合。TYP 无范围检查；SPECIES 笔记未实现成功登记。副手取笔记而扣 currentItem 主手槽是静态边界。离线 registerSpecies 未直接 dirty，不保证此次更新落盘。未把登录恢复说成已审死亡 Clone。
2. **遗传蜂物品 → 染色体/allele 校验 → 蜂箱实际产物**。Slot 合法时读取双 UID、检查 allele class；坏值用已读取物种模板或默认模板替代。列表顺序影响 fallback；缺整槽保留 null，NBT 构造不做非 NBT 构造器那套完整校验。缺 Genome 与空 Genome 不同。writer 写解析后的新 UID/字段，不保存未知原始基因。deprecated allele lookup 存在，但本固定源码未找到实际填表调用，不拿 API 或别名数凑信用。
3. **玩家邮箱 → 信件 processed/附件 → 真实投递和取出写回**。信件与邮箱保存完整物品载荷；玩家投递复制目标栈、标 processed/清邮票再插入，成功才扣源。地址 equals 可按 UUID，hashCode 却用名字，持久文件名含名字与 UUID；未见改名迁旧文件，不能认为 UUID 相同就恢复旧信。内嵌 address 与目录名无一致性校验；玩家 carrier 忽略 doDeliver，false 也有写入，本正常入口传 true。原生刷盘与交易站分支未深审，不宣称原子/无损。

完整 JSON/JSONL 带来源、commit/tree/blob、source SHA256、全文方法范围、excerpt/normalized SHA256、具体适用点/限制和语义重复风险。document-integrity.json 全源与 AST/hash 无错；主账只读 1059 行快照、primary 机械匹配 0，仍需 Kepler 语义审核。semantic-duplicate-review.json 明列三链与 batch015 的边界；共享库存/玩家 profile/注册查询支持不重复计。

未编译测试、未开游戏/客户端/服务/GUI/TCP、未操作屏幕或原档、未执行上游代码；只运行辅助文档提取/哈希工具。未改主账、生产或待办。十小时与全部剩余范围尚未完成，后续继续，不以交批作为完成声明。
