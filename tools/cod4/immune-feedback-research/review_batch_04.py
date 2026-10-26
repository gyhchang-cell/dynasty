from ledger import record,verify
p='src/main/java/twilightforest/entity/boss/'
record('tf-hydra-root-and-part-authority','TeamTwilight/twilightforest',[(p+f,a,b) for f,a,b in [('Hydra.java',575,645),('HydraPart.java',93,100),('HydraHeadContainer.java',801,807),('HydraHeadContainer.java',942,948),('HydraHeadContainer.java',969,971)]],
 '完整HydraPart.hurtServer委托parent.attackEntityFromPart→服务端检查、同源本体/部件排除、死头/死颈排除、source owner平方距离→张嘴条件下super全伤/闭嘴时round(伤害/护甲倍率)；root.hurtServer只接受BYPASSES_INVULNERABILITY。已读完整所有决策方法和mouth/dead/addDamage辅助；其他地形破坏副作用不计。',
 '本体根节点的false不代表所有部位免伤。普通距离阈值400是平方距离（20格），迫击炮多200平方单位，不是多200格。dying/dead部位拒绝；部件成功后才ENTITY_DAMAGE。闭嘴减伤可能四舍五入到0，但不能统一标Boss拒控。',
 '文字反馈的语义目标必须归本体，拒绝原因却要保留部位/阶段，避免本体和部件重复通知；不能拿根hurt覆写孤立判断整个Boss。',
 '头状态动画时间表和原版super内部不在本条计数对象；尚无文字/自定义拒绝回执，不据静态推断画面。','immunity_rejection_semantics')
record('tf-urghast-reflected-fireball-immunity-exception','TeamTwilight/twilightforest',[(p+'UrGhast.java',147,181)],
 '完整isInvulnerableTo→isReflectedFireball以direct LargeFireball+source Player识别反弹→火焰/窒息/原版免伤条件；同文件hurtServer完整读用于核对tantrum=damage/10与真实healthLost记录的区别。',
 '玩家反弹LargeFireball显式豁免免伤判定；同一种火球伤害的攻击者身份会改变结果。tantrum仅十分之一减伤，不是immune；完整拒绝判断本身无自定义文本/声音。',
 '服务端需保留直接来源和归属来源，展示原因不能只按伤害类型。减伤的低数值不能自动显示灰字。',
 '本条研究主体为两个完整免伤判定方法；tantrum AI/getter/phase切换不计作完整生命周期研究。未运行网络或可视验收。','immunity_rejection_semantics')
verify()
