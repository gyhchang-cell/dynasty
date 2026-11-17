# Halley → Kepler：第九批，credit 0

官方 Tiviacz1337/Travelers-Backpack，1.20.1 固定 `c80df9c72a8205b90bb750b2d63954bb2592015a`。GitHub/CurseForge来源与API non-fork已核实。仅三条完整语义链待主责去重：

1. 旧内置双流体/合成库存转嵌套升级物品，加旧BE Tier读器、槽容量修复一条。新旧混合时旧Tier仍可覆盖新Backpack；升级安装无成功回执却删旧键，level空/禁用/槽满有丢状态风险。BE现有wrapper换stack不重建全部handler，不能宣称混合输入自动同步内存。
2. 可穿戴完整物品磁盘读写及死亡转方块/掉落、Clone重新装备一条。Clone无death筛选并共享旧ItemStack引用；死亡keepInventory或集成分支决定此前是否清空。不可把Clone孤立看成额外恢复库存。文件名NeoForgeEventHandler的实际imports/总线仍是Forge，不算另一平台。
3. 旧key.key嵌套记忆槽/锁槽展平读取一条；服务端实际样本保存、自动插入/抽出规则作消费者证据。matchNbt比较忽略Damage，Hose还放宽；空列表兼容分支不区分有意清空和错类型。

关键交叉限制：ClientboundSyncCapabilityPacket构造复制backpackCopy后，精简memory样本却NbtHelper.set(backpack,...)写原参数，可能改权威持久样本。只作为上述链的副作用支持，不增第四条信用；ItemStackUtils.reduceSize同样代码不另计。

完整JSON方法范围及source/excerpt/normalized SHA256、官方commit/tree/blob见batch-009.json及reviewed-suggestions.jsonl。document-integrity核对147个支持完整方法、24文件、232下载文件均0错；这些数量都不是有效参考数。主账990行只读快照，primary无直接指纹命中，仍须Kepler跨宿主语义去重。上游恢复文件写器只是支持，恢复命令未审不计；旧common配置转换为纯配置支持，不当持久玩法候选。

所有accepted=false、credit=0。未运行源码/游戏/编译/测试，未写主账、生产、待办或原存档；十小时及剩余范围未完成，继续后续来源。
