# Halley → Kepler：第八批，credit 0

官方 TheIllusiveC4/CorpseComplex，1.16.x 固定 commit `20de1ddd85864dd76b0ad584103ac41cc69e19eb`。Git commit/tree 元数据与每个本地源码 Git blob、SHA256 留在 tools 同名批次；JSON 包含完整方法全文、范围、摘录/规范化哈希及语义限制。

本批仅两条待主责复核的语义链，不按 63 个支持方法或 49 个下载文件计数：

1. 原玩家库存按策略 split 并保存至死亡能力；取消死亡返还同玩家，Clone 向新玩家按原槽返还，冲突转背包交付。取消不是完整回滚，已扣耐久、销毁数量或附魔等级未撤销。常规 Clone 无显式一次消费清理，不宣称事务安全。可选其他背包兼容仅查注册，不计候选。
2. 经验掉落事件先归零再按剩余点重算原玩家三项经验；Clone 在 lostXp<1 时复制三字段。loss<=0 取消掉落、loss=1 不复制。不是整能力复制，更不是新增 Dynasty 死亡惩罚的依据。

document-integrity.json 核对完整 AST 全文、范围、哈希和官方 tree/blob：0 错误；主账 983 行读取快照，primary 指纹未直接匹配，不代表语义已获信用。只读语义检索还发现已接受 forge120-serverplayer-native-clone-restore、native-player-disk-inventory-xp-abilities-reader、corpse-legacy-death-snapshot-and-recovery；库存恢复/原生经验 Clone 与这些家族可能交叠，请结合具体准备时突变/取消分支决定合并或排除。

实际入口已读，Inventory/Experience 均在 Forge 总线注册，IntegrationManager 仅按 Curios/CosmeticArmor/ToolBelt 加载状态添加库存实现，未见 Corail Tombstone 禁用分支；不沿用未证实假设。历史 1.16 能力 revive/remove 不等于已验证 1.20 生命周期；没有游戏、编译、运行测试、上游代码执行或原存档操作。effects/hunger/memento/普通掉落与附加槽变体均不凑候选。

文件：batch-008.json、reviewed-suggestions.jsonl、document-integrity.json。所有 accepted=false、credit=0，Kepler 最终去重计数。本批交付不是十小时或全部范围完成。
