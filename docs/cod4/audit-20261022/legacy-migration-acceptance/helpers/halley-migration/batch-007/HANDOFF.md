# Halley 第七批：Waystones 两条待去重链，credit0

`TwelveIterations/Waystones@0c2160e6cb0cdf9b79978f335821496ab385595d`，官方1.20.1固定快照；声明Waystones14.1.21、Balm7.3.38+1.20.1、Forge47.3.27。支持依赖官方`TwelveIterations/Balm` tag v7.3.38，tag object996a432f9228af6285b3fa0831d2cd17bb11e79a，解到commit6120c9fb26446d4c2ddb669e4fe016f653fcb3f3；其properties亦声明Minecraft1.20.1/Forge47.3.27。完整Git tree/blob与源码SHA256均在source-manifest/provenance。未证明发布二进制字节同一性，不运行上游。

两条建议完整保存在`batch-007.json`与`reviewed-suggestions.jsonl`；源方法全文/范围/摘录与AST规范化哈希/观察应用限制风险均附，全部credit0、acceptedfalse。

1. **世界传送点目录、旧Origin兼容与物理UUID重连**。旧WasGenerated先推WILDERNESS/UNKNOWN，新Origin解析成功覆盖，失败保留回退；缺Type恢复WAYSTONE，缺Owner影响实际编辑授权。SavedData按UUID恢复，未命名sharestone主动丢弃，重复UUID后项覆盖。blockentity与放置物品UUID有效时重用目录对象并定位，无效时可建新身份。不能将旧ID未知安全保留或所有丝触物品携UUID视为已证明。
2. **玩家激活UUID有序列表、读时清理与真实跨平台根域**。列表读取会删除全局目录找不到的UUID引用，普通同步/菜单读取也可能变更持久域。Forge经Balm进入PlayerPersisted/BalmData；目标域为空才取Fabric根数据；Fabric导入Forge回退受根BalmData存在条件限制，COPY_FROM直接共享旧compound引用。Balm钩子、Mixin及Fabric复制均支持此真实玩法链，不另计通用框架/平台信用。Forge原生Clone未本批重复审查，不宣称新增运行验收。永久解锁与同域cooldown必须区分，不能整域复制为Dynasty永久白名单。

`document-integrity.json`只核对证据字节/完整AST范围与哈希、主账只读碰撞信息；方法和下载数不是有效参考数。与旧世界目录、玩家引用列表、Clone家族须Kepler最终语义去重。未命中首方法哈希碰撞不能自动accepted。

BoundScroll和WarpPlate的部分实际方法另已阅读，但本批未补完其全部恢复/消费边界，**未包装成额外候选**。Balm库不能独立增加信用；不同物品键、代理、网络、排序getter及平台拷贝不计新实现。

无游戏、GUI、编译、测试、上游执行、原存档操作；不改主账/生产/主待办。本批不是十小时目标完成，后续独立来源继续。
