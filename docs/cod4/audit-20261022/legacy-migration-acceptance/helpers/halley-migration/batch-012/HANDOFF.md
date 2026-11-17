# Halley batch 012 — Astral Sorcery 世界对象（credit0）

2 条人工审阅语义建议，170 个完整方法与 1 个完整静态初始化块仅支持链，不按函数/下载/组件数量计数。JSON/JSONL 包含固定 commit/tree/blob、source SHA256、完整范围原文、摘录及归一化 SHA256、输入/输出/触发/观察/应用/限制/语义重复风险。主账只读机械核查无 primary 命中，仍由 Kepler 人工去重。

- **Tree Beacon 持久树**：主方块存组件坐标/权重，组件存父链接和原 BlockState，读后实际收获并在主灯塔拆除时恢复原树。同一完整树对象只提1条。未知方块可落AIR；缺子链接成为null而tick直接equals；父区块未加载和父对象不存在同被getTileAt(false)判null，组件随后清为空气而非revert。没有原TileEntity NBT，不能宣称任意方块完整恢复。上游生长静态注册块全文入证据，未执行生成/删方块。
- **Celestial Gateway 世界目录及ACL**：世界node才是实际传送权限权威，tile同时保存副本；owningPlayer_present缺失会使子compound被忽略，owner为空时放行。读集合不clear且同坐标first wins；networkRegistered=true而目录丢失不自动重新登记；onLoad无tile剔除未标dirty。真正传送在授权后延迟调度，执行前不重验目标ACL/结构。每个维度/颜色/ACL槽及支持库不拆计。

来源复用 batch011 官方 AstralSorcery@3599b4819dba3553896f87c0505ccd84bafb0550。新增仅支持官方 ObserverLib@ea1750af50610a15685a41db59d9c0a9e4db11f4（声明1.16.5-1.5.2），63个Java与Astral固定依赖1.16.5-1.5.2.v77官方sources.jar逐字节相同，见 tools同批provenance/observer-declared-source-artifact.json，源码包SHA256 f78dd0ea14df7ba9b323d5d688a83f5d332c0f9b497e13fd705cc51836e24e1d。证明源码对应，不是已安装二进制/游戏验证。

初始1.5.3分支探针已排除，非新候选；来源保留说明记录修正。GlobalWorldData用Guava Files.copy，不套用batch011 java.nio.Files.copy覆盖限制；仍有IOException后markSaved、队列不安全同步、目录名规范化碰撞和错误清理风险。任何上游文件备份/删除代码均只读，绝不操作用户文件。

本助手未改主账/生产/待办/原存档，没有构建、测试、游戏、图形操作或屏幕唤醒解锁。主账当前761/1000仅只读上下文，不归助手信用。十小时及其余范围未完成，继续新来源选源。
