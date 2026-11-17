# Halley → Kepler：第038批，credit0

1建议：Requiem remnant身份type/ethereal持久→明确死亡复制策略→原生prepare事件→split/merge去重。官方54281728d5f78944955a6e7b952ac4e0835129de；branch1.19，properties MC1.19.3/mod2.0.0-beta.16。

永久资格策略ALWAYS_COPY，movement/暂停死亡/技能等LOSSLESS_ONLY；derive灵魂无敌和movement config由setVagrant重算。prepare使用新clone、RETURN用cir.getReturnValue，有限Y<256避碰。只复制Sticky谓词命中效果。具体Attrition/硬核死亡属于该模组规则，不适用于Dynasty，不增加死亡惩罚。

分身原生NBT排除UUID/spawn/EnderItems/abilities/gameMode/seenCredits/经验；ALWAYS_COPY组件从分身载荷去重以避免重复真值。剩余payload仍宽，合并覆盖目标完整NBT，不能照搬为Clone白名单。旧PlayerProfile支持同链，不额外计。外部CCA/PAL/Impersonate/Automatone未全文展开，原生无运行验收。

完整方法/声明仅支持，1条对象族；hash/Git/tree/blob审计0错误、主账primary机械匹配0，仍需Kepler语义去重。credit0/accepted=false。继续040真正旧实体关系间接化；无游戏编译测试/GUI/主账生产待办原档修改，十小时尚未完成。
