from ledger import record,verify,B
r='BobMowzie/MowziesMobs-Public';p='src/main/java/com/bobmowzie/mowziesmobs/'
root=B/'sources'/r.replace('/','__')
def whole(rel):return (p+rel,1,len((root/(p+rel)).read_text().splitlines()))
record('mowzie-wroughtnaut-window-direction-rejection',r,[(p+'server/entity/wroughtnaut/EntityWroughtnaut.java',112,204),whole('server/ai/WroughtnautAttackAI.java'),whole('server/ai/animation/AnimationFWNVerticalAttackAI.java'),whole('server/ai/animation/AnimationAttackAI.java'),whole('server/ai/animation/SimpleAnimationAI.java'),whole('server/ai/animation/AnimationAI.java'),whole('server/entity/MowzieLLibraryEntity.java')],
 'registerGoals注册垂直攻击动画Goal和WroughtnautAttackAI→目标距离/朝向/概率与连击计数选择VERTICAL_ATTACK→AnimationAI每tick匹配动画→垂直攻击tick27..84设vulnerable，其他tick及stop复位→原生hurt读取source.getEntity及方向角→拒绝分支playSound并false，允许分支取消当前动画后super.hurt→父类仅在原生hurt成功后发送受击/死亡动画。所有Goal包装和共享动画基类合并一条。',
 '不是简单背后永远可伤：必须处在vulnerable窗口，且方向判断落入实际允许分支。arc=220，但跨360分支最后表达式是-relativeArc+90/2，不能改述成对称220°而掩盖源码算式。存在source.entity时先可能设置target，即拒伤也可获得仇恨；窗口外及窗口内阻挡均undamaged音量0.4/pitch2，没单独节流。只有没有entitySource时才检查BYPASSES_INVULNERABILITY，不能声称任意有攻击者的bypass都绕过盔甲。没有本类自有浮字或拒伤包，拒伤不调用父类hurt动画。KNOCKBACK_RESISTANCE基础值1。',
 'Boss Immune应从明确拒绝分支生产原因，而非从未扣血或未播放hurt动画推断；真实窗口/方向和bypass优先级必须保持，不把已有攻击动画镜头震动复制进灰字反馈。',
 '已读整段hurt和完整Goal/父类相关方法；LLibrary动画传输是外部平台契约，未运行或证明画面可辨；只确认源码自有音效调用，不宣称拥有去重/跨维度清理。','boss_rejection_semantics')
record('mowzie-frostmaw-arrow-rejection-wakeup',r,[(p+'server/entity/frostmaw/EntityFrostmaw.java',768,815),(p+'server/entity/frostmaw/EntityFrostmaw.java',831,860),whole('server/entity/MowzieLLibraryEntity.java')],
 '原生Frostmaw.hurt全方法→先fall拒绝、lava空动画发DODGE、fire倍率→directEntity instanceof AbstractArrow专门拒绝→undamaged音效、根据source.entity设仇恨，休眠状态按水晶/难度发送ACTIVATE并同步ACTIVE→false；非箭才走super.hurt成功后shouldDodgeMeasure和苏醒。读取ACTIVE/HAS_CRYSTAL同步字段getter/setter及父类hurt动画链。',
 '箭矢按directEntity判断，玩家归属按source.entity判断；普通箭与特殊来源区分不能只依赖玩家持物。箭矢分支在damage*1.25之后拒绝，不产生实际伤害但会苏醒，和平模式禁止激活而不取消拒箭音；不需要HP变化才能发拒伤反馈。fall直接false没有相同音效，lava先发DODGE并不等于lava免疫。没有逐目标拒伤限频、灰字或自有拒伤S2C。',
 '拒伤语义可同时包含行为状态变化；为Boss灰字接入只能加回执，不能用false反向冻结已有苏醒逻辑或把所有false共用一种原因。',
 '本条与Wroughtnaut方向窗口语义不同；不把重复音效、父类动画包装或多个水晶变体另算。没有真实客户端/多人或像素验收；外部动画库内部不计。','boss_rejection_semantics')
verify()
