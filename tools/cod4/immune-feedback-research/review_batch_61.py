"""Relics: three independent native production points, shared framework gives no extra credit."""
from ledger import B,O,record,verify
import json
r='Octo-Studios/relics';p='src/main/java/it/hurts/sskirillss/relics/'
def w(f):
 f=p+f
 return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
base=[w('Relics.java'),(p+'utils/EntityUtils.java',216,239),(p+'api/relics/data/AbilityData.java',264,274),w('api/relics/data/AbilityRankModifierData.java')]
leaf='items/relics/back/LeafyMantleItem.java';clot='items/relics/ClotOfTimeItem.java';keys=[]
k='relics-native-leaf-surface-qualified-fall-denial';keys.append(k)
record(k,r,[(p+leaf,55,172),(p+leaf,307,325),(p+'init/RelicsItems.java',59,59)]+base,
 '已注册LEAFY_MANTLE物品→实际Curios equipped stacks→@EventBusSubscriber native LivingIncomingDamage→IS_FALL来源+camouflage可使用+getBlockPosBelowThatAffectsMyMovement实际block为LEAVES→setCanceled(true)/break；完整能力模板/能力可用条件已读。',
 '一个来源与接触环境联合最终拒绝点1，不是袍名/树种常量换壳。和Goety落地余额取消不同：无余额/消耗/主动下降条件，单看原生脚下运动影响block与已解锁camouflage；也不要求正在hide、progress满或disappearance等级。没有拒伤灰字/声/粒子，周围树叶多也不能满足脚下门。此方法无显式server门，依赖原生伤害事件实际侧；不假称双端执行保证。',
 'Boss拒控应在实际准入predicate成立时形成明确原因，不从已有隐身/视觉进度推断免疫；环境有无与已解锁能力需作为负例。',
 '固定da846fcb3223e88d7c926b4478506b3089caff51。完整最终方法及native注册/物品激活条件已观察。Curios/NeoForge通用框架辅助0，未证明自然获取/实际落地画面/声音/网络，不改正式源码/资产/TODO、不启游戏。','native_final_damage_refusal')
k='relics-native-environment-leaf-budget-lethal-truncation-and-deferred-consumption';keys.append(k)
record(k,r,[(p+leaf,55,172),(p+leaf,327,431),w('utils/ServerScheduler.java'),w('entities/LeavesBlockEntity.java'),(p+'init/RelicsItems.java',59,59),(p+'init/RelicsEntities.java',59,61),w('network/packets/sync/S2CSyncEntityTargetPacket.java'),(p+'network/NetworkHandler.java',47,62),(p+'network/NetworkHandler.java',114,120)]+base,
 '注册LeafyMantle revival ability需要level5→native LivingDamage.Pre伤害>=当前HP，计算health-.1截断候选/absorption差→可用revival按radius立方区搜LEAVES并按距离排序→总heal足够才按序排ServerScheduler延迟任务造LeavesBlockEntity/target+owner/毁方块→即时setNewDamage(health-.1)，溢出heal次tick另排；已注册leaf实体/target包consumer，scheduler由server Pre tick消费并在ServerStopped清空。',
 '一个按环境实体资源预算进行致命伤截断的生产点1，和独立脚下落地取消不同；也不是Invulnerable effect整次免伤。diff初值吸收-超额伤害，统计damage_negated写在potential足够检查之前，失败保命亦可能记统计，不能以计数当成功回执。树叶到延迟任务才销毁，无本链预约/当时仍是叶子重查，可与第二事件共享扫描资源，不能静态保证事务预算。截断保留.1计算值仍受后续伤害管线/absorption影响，不冒称实机不会死。leaf tick target缺失/死/200tick寿终，靠近目标只discard，本类没有在靠近时heal；治疗来源是Pre额外安排而非视觉叶子抵达。setTarget在addFreshEntity之前调用tracking发包，初追踪同步是否补齐未验。',
 '生产成功与统计/预备动画必须区分；延迟视觉不能作为拒控事实来源。目标生命周期、无目标清退、包先于实体出现和重复申请资源需静态列入Boss文字回执验证，不能只查构造粒子。',
 '完整包含方法和叶子实体/scheduler/target包已读，固定提交。叶子模型/OctoLib trail与伤害/paralysis第三方策略不另计，前述target包与既有Relics锚定共享0。此处不展开控制施加成功/渲染深度，不声称像素/TCP/声音通过。','native_damage_mitigation_and_receipt_order')
k='relics-native-use-bound-rewind-incoming-immunity-and-dimension-exit';keys.append(k)
record(k,r,[w(clot),(p+'init/RelicsItems.java',67,67),(p+'init/RelicsDataComponents.java',46,48),w('network/packets/S2CSpawnParticle.java'),(p+'network/NetworkHandler.java',47,62),(p+'network/NetworkHandler.java',114,120)]+base,
 '已注册ClotOfTime/能力rewind rank1 invulnerability→native server EntityTick.Post每实际物品槽记录按维度/方块变化的PathPointData/冷却→原生Item.use要求能力可用/路径至少2点/无CD后startUsingItem→@EventBusSubscriber Incoming仅serverPlayer实际isUsingItem+当前useStack为Clot+能力可用+invulnerability已启用才cancel→onUseTick沿历史插值，路径不足或结束/跨维度teleport成功stopUsingItem解除gate→tracking粒子包与本地RenderFrame预测。',
 '独立实际使用生命周期最终拒伤1；不与Ars对目标rewind黑名单合并（此为自用道具使用中Incoming最终取消），也不按路径点/维度/粒子拆。Incoming不查伤害tag/bypass/实际cursor或是否这tick已移动，只看使用状态和能力modifier；所以粒子存在不是本次被拒的证明，rank未开也可倒带移动。记忆长度按更新点数量截断，站立同block不记，不能把time*20点直接叫同秒数真实历史。server插值加速系数.01而client RenderFrame用.03且partial；不声称两端严格相同。跨维度目标存在才teleport/stop；目标不存在会继续后续分支，不能宣称维度字符串即保障安全。',
 'Boss免控文字应从明确cancel语义派发，不拿连续状态粒子代替拒绝回执。按tick事件寿命和实际use结束收口；跨维度应重验目标身份和不改变他人Camera，本例自己的倒带视角不是他人camera授权范例。',
 '固定提交，全ClotOfTime包含完整方法/本地预测/数据CODEC已读；network只pos/motion粒子当前world消费，无目标UUID/维度代际/事件去重，S2CSpawnParticle不是免疫语义包。NeoForge物品component同步内部/particle shader是辅助0，没运行、编译上游或正式修改。','native_final_damage_refusal')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'relics-batch61-native-final-sites','credited_chains':keys,'rationale':'同装备两处不同native最终生产：Incoming脚下环境取消与Pre环境预算致命截断；Clot真实使用状态Incoming取消另1。树种、装备槽、半径点、路径点、网络wrapper不计。LeavesBlock onHit的UUID去重与既有项目粒子/箭命中排除样式不另计；反疗/流体行走/卸装备受伤不为Boss免控凑数。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
