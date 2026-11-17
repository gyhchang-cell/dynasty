# Halley 免疫反馈辅研交付 001

交付的是 **3 个家族的核心静态链审查 + 1 个感染物品部分候选家族**；**有效参考新增 0、主账 credit 0**。最多 30 是上限，没有为了凑到 30 拆方法或包装。80 个证据范围只是这些家族内的完整方法/文件，不是 80 个独立实现。若按最初 30 个有效实现目标衡量，仍缺 30。

主账只读：组装时 `reviewed.json` 为 32 条，已比较 `dnp-health-delta-worldtext`。未改 reviewed/progress/semantic-dedup、生产、资产或待办；没有备份清单、删除内容、外部请求、启动游戏/服务器或执行上游代码。

| 家族 | 固定来源 | 结论与移交重点 |
| --- | --- | --- |
| AssortedUtil damage numbers + AssortedLib 桥接 | Util `5853d33fee5f996f71ae5c215d0d21fdb3d2e3fc`；Lib `a2c9a9ff75231667b337e673c27f73f5e684914f` | level 对象改变即清状态；原生 damage event 保存最新来源 5 tick，HP 净变化消费时分类。来源不单次消费、无 UUID/攻击序号、无每目标限频或总弹窗上限。5 tick 关联窗口不是节流。只可参考时序边界和生命周期；普通灰色类型不是 Boss Immune。 |
| luavixen damage numbers | `b77ee7071a54093849f4c6e0b72e055e0a9cf7f1` | HP 差→粒子链与主账 DNP 家族高度重合；256/64/16 总量 cap、32 tick 参数、颜色和三平台都不另计。无来源/免疫分支；未见切世界清队列及自然死亡引用主动回收。 |
| Floating Damage 数据包 | Modrinth `kubdoMLE`，版本 `LVErYFzu` / 1.2，version.json 标 Minecraft 1.21.5 | 0 计数反例：正 dealt 阈值才设置 pending；blocked advancement 自身没有 reward。下一 tick 处理后清 pending/修饰；玩家单槽覆盖不是事件累计。`@n[HurtTime:10s]` 不保存原 target，聊天接收者也用就近 `@p`。life=10 内层误选所有 text_display；pack.mcmeta 第 8 行裸说明导致严格 JSON 解析失败。 |
| Werewolves tooth + Vampirism fang | Werewolves `20b3fa0cd4264c9d8855d23c8ab2a80d90adb306`；Vampirism `83c220f47cd030eed4c779c90f5786b261075869` | 两份 use 方法全文已审、Git blob 已核，保守合并一个部分候选。服务端区分配置禁用、已具身份、感染资格拒绝；直接向使用者发 overlay。是玩家主动感染物品提示，非 Boss 伤害免疫。缺 Helper/感染效果全文，不能声称审完免疫判定链。 |

## 关键证据边界

- Util/Lib 缓存只有选定 Java 和固定 Git 树。mixin、loader、服务 provider、Gradle 版本文件在树中存在但无本地正文；批次列出路径与 blob ID，明确未读。两端 Java 方法签名一致不等于发行物依赖版本匹配、已激活或可运行。
- 数据包完整阅读入口、全部 modifier、处理/显示/清理核心及两个金额边界。其余数千阈值包装未逐一方法审查，也不作为独立参考。`dealt` 与纯阻挡的原版触发时序没有授权缓存证据，不能断言全阻挡一定显示或一定被门限排除。
- 数据包投射物分支有原版经验球拾取声，非 blocked 分支的嗡声，也没有免疫声音冷却。这批没有找到可新增计数的 Boss 免疫嗡声/防刷屏实现。
- 补充分界后，只读了两份 build/item-use-references 感染物品源码及各自 source.json/tree.json。校验 blob 后将这两份全文复制到本人 tools helper 的 sources 子目录；原缓存未改。Helper/感染效果仅有固定树路径，无正文，未补下载。语言资源和 vanilla overlay 的显示寿命/刷新实现未审，不把 API 名称当作完成渲染或限频证据。
- 两种感染物品都在配置允许分支末尾 shrink(1)：感染成功、已具身份或免疫拒绝均会消耗；管理员禁用分支不消耗。可借鉴“原因不同，文案不同”，不能直接移作 Boss 免疫规则。

## 可核对文件

- [批次 JSON](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/immune-feedback-research/helpers/halley-immune/batch-001.json)：每个家族及内部证据包含 repo/revision/path/source_local/source_sha256/line/end_line/excerpt/observation/application/limits/url；保留去重风险、未取得配置清单及固定来源。
- [校验结果](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/immune-feedback-research/helpers/halley-immune/verification-001.json)：52 个源码文件的哈希/本地来源，Java Git blob 与固定树核对，摘录逐字匹配及完整方法闭合范围，数据包 archive SHA512，pack 严格解析诊断；只保留主文件哈希，不复制主清单。
- [本地静态组装器](/Users/a15356015027/Desktop/dynasty/tools/cod4/immune-feedback-research/helpers/halley-immune/build_batch.py)：只运行本人编写的文本审查/校验逻辑，不导入或运行下载代码。重跑会按当时主账读取并更新本人批次；最终晋级与语义去重仍由 Russell/主协调负责。

本批所有 `research_credit`、`suggested_credit`、`master_credit` 均为 0；不要求主协调先接受这批才能继续其独占的 Boss 拒控研究。
