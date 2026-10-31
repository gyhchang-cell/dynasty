# Halley 辅研分界（主账维护者留档）

按用户最新分工，Halley只写 `helpers/halley-immune/`；每批最多30处建议，均为候选、不可自动计入主账。本人独占reviewed/progress/semantic-dedup/最终实现。

已计30条，请先用reviewed.json避免重复。以下本地资料让给Halley继续完整调用链辅研；本人不再并行补这批伤害数字/免疫提示：

- `tools/cod4/immune-feedback-research/sources/AssortedMods__AssortedUtil/` 固定5853d33fee5f996f71ae5c215d0d21fdb3d2e3fc。实际游戏代码在mods/damagenumbers；主账暂未计。我已全文读DamageNumbers/DamagePopup/DamageKind、client入口、mixin及config；level对象变更清表、原生damage packet来源记忆5tick、HP变化与来源分离、默认40tick弹跳文字值得核实。不能把普通灰色伤害类型当灰色Boss Immune。请补mixin激活配置、依赖版本与桥接一致性，写完整观察供复核。
- 同链辅助库 `sources/AssortedMods__AssortedLib/` a2c9a9ff75231667b337e673c27f73f5e684914f；FabricClientHelper174–185、ForgeClientHelper179–191已读实际event桥接。库本身0计数，HEAD是否匹配该mod声明版本未确认，不声称运行兼容。
- `sources/luavixen__damagenumbers/` b77ee7071a54093849f4c6e0b72e055e0a9cf7f1，13Java已完整取得。主要生产和绘制方法已读；与已有DNP/njlent健康差值家族高度重合，请只提确实独立语义，不因32tick/颜色/版本另计。本人暂不晋级。
- `sources/Modrinth__kubdoMLE__LVErYFzu/` oSzoukaua Floating Damage Rev1.2，固定版本与archive SHA512见source.json。完整mcfunction/json已取得；数千阈值文件是同链数值包装，不是数千处有效研究。核心全文已读：advance→score/storage→process_data→text_display→tick kill。blocked modifier没有自己的reward；正数damage阈值门如何覆盖纯block要保留限制。@n[HurtTime:10s]不是原目标ID、life10分支又as所有text_display，pack.mcmeta尾有非JSON说明；需审慎，不称已运行通过。可作为0计数反例，不能强推完整有效。
- 本地 `build/item-use-references/TeamLapen__Werewolves/.../WerewolfToothItem.java` 与 `TeamLapen__Vampirism/.../VampireFangItem.java` 有明确免疫提示，但属玩家主动感染物品而非Boss拒控。若研究须说明相关性/身份区分；相同模板最多合并一条且范围不符可排除。未入本研究sources，复制时固定来源验证，勿改原缓存。

3ColumnsC/FloatingDamageIndicators固定528e907188b1db1fb7c68c7b995ae5bb83247896实际仓库只有README/LICENSE/gitignore，无源码，0计数。discovery-20261026.json中其余无source_url项目不算有效。

本人继续本地Boss拒控/控制免疫/原生回执及节流来源，不制作资产，不启动游戏。最近外部补Ice_and_Fire EntityMutlipartPart超时（curl28），已存external-failure-20261026.json；不循环重试。
