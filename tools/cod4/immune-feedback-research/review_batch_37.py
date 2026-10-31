"""Artifacts fixed native damage denial, not names or cross-loader copies."""
from ledger import B,O,record,verify
import json
r='ochotonida/artifacts';p='common/src/main/java/artifacts/';q='neoforge/src/main/java/artifacts/';keys=[]
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
base=[w(p+'Artifacts.java'),w(q+'neoforge/ArtifactsNeoForge.java'),w(p+'component/ComponentType.java'),w(p+'component/ComponentQuery.java'),w(p+'equipment/EquipmentSlotManager.java'),w(p+'equipment/EquipmentSlotAccess.java'),w(p+'integration/minecraft/ArmorSlotProvider.java'),w(q+'neoforge/integration/curios/CuriosCompat.java'),w(q+'neoforge/integration/curios/CuriosSlotProvider.java'),w(p+'util/ItemDamageUtil.java'),w(p+'ArtifactsMixinPlugin.java')]
def add(k,refs,chain,obs,lesson):
 record(k,r,base+refs,chain,obs,lesson,'固定4b67278df94e4d3669119f1abb24a1c3a758afe1，Git tree/blob及SHA256本地校验。Mixin Java注解/shouldApplyMixin及实际item组件已读；原始mixins JSON本地未缓存，未补外网，不能声称运行启用或画面通过。无游戏/正式代码/资产/待办变更；codec/平台port/属性包装0额外。','native_damage_refusal_and_immunity_window');keys.append(k)
add('artifacts-native-equipped-source-tag-conditional-invulnerability',[w(p+'mixin/ability/damageimmunity/LivingEntityMixin.java'),w(p+'component/ability/DamageImmunity.java'),w(p+'component/ability/EntityCondition.java'),(p+'registry/ModItems.java',272,295),(p+'registry/ModItems.java',321,333),(p+'registry/ModItems.java',651,664),(p+'registry/ModDataComponents.java',130,132)],
 '真实SHOCK_PENDANT注册启用配置+IS_LIGHTNING条件ALWAYS，CHARM_OF_SINKING为水中摔落免疫，STRIDER_SHOES热地板变体→isInvulnerableTo RETURN原结果||装备DamageImmunity条件与source tag→Equipment query经已注册Armor/Curios provider、cooldown/disabled/cosmetic过滤。',
 '最终来源tag+环境条件拒绝计1，三item/不同tag/不同平台不增数。original true短路不表明装备真的拒伤；findAny是reduce遍历非首个结果early return，不能当按目标节流。DamageImmunity.isNonCosmetic才查enabled。没有明确灰字/闪光/S2C拒绝原因，tooltip灰字属于静态物品说明不当世界战斗文字。Curios reduce遍历getStacks未使用tryEquip中的activeStates门，不声称停用slot被同一门过滤。',
 '来源标签与目标身份分开，Boss拒控回执只由明确策略拒绝生产，普通装备/体质免疫不扩加灰字。')
add('artifacts-native-cross-necklace-post-hit-invulnerability-tick-extension',[w(p+'mixin/attribute/invincibilityticks/LivingEntityMixin.java'),w(p+'mixin/attribute/LivingEntityMixin.java'),w(p+'component/ability/EquipmentAttributeModifier.java'),w(p+'registry/ModAttributes.java'),(p+'registry/ModItems.java',239,253),(p+'item/ArtifactProperties.java',107,117),(p+'registry/ModDataComponents.java',210,217),(p+'event/ArtifactHooks.java',53,68),(p+'event/ArtifactHooks.java',85,149),w(q+'neoforge/event/ArtifactHooksNeoForge.java')],
 'CROSS_NECKLACE实际bonusInvincibilityTicks属性并ignoreCooldown=false→原生EntityTick.Post/装备变化→EquipmentAttributeModifier.Ticker装卸永久modifier→createLivingAttributes添加可同步基础属性→原生hurtServer和handleDamageEvent每次写invulnerableTime后加(int)attribute。',
 '独立于source-tag isInvulnerableTo的原生受击无敌帧扩展计1；两native注入合计1，不因client/server或属性值拆数。只加窗口并不拒绝触发当前伤害，也未读原版后续hurt门全文，不能声称对所有伤害等价免疫。属性上界1200不等于Boss文字节流。注入没有ordinal/每次防重；若目标版本同方法多次写字段，每次都会调用，但未运行不称已复现倍加。实际post-damage cooldown helper仅client分支，而已见beforeLivingDamaged注入是server setHealth，不能凭组件名声称冷却权威生效。',
 '不要把无敌帧/物品冷却/拒控提示节流混为一门；控制免疫必须拒当前尝试，灰字窗口独立并有清理。')
add('artifacts-native-warp-drive-pearl-impact-damage-call-refusal',[w(p+'mixin/ability/enderpearldamageimmunity/ThrownEnderPearlMixin.java'),w(p+'component/ability/SimpleAbility.java'),(p+'registry/ModItems.java',439,450),(p+'registry/ModDataComponents.java',148,150)],
 '真实WARP_DRIVE的nullifyEnderPearlDamage组件→原生ThrownEnderpearl.onHit中ServerPlayer.hurtServer WrapOperation→真实装备可用simpleAbility则直接false不执行hurt，否则原样调用。',
 '独立的最终原生伤害调用拒绝计1，不与一般source-tag免疫合并，也不把WarpDrive饥饿替代/投掷动画当额外研究。只替换该onHit伤害调用，没有在此拒绝传送或提供拒控语义回执；return false有明确生产原因，但其他hurt false仍不能类推。组件查询排cooldown/broken/toggle，初始itemconfig enabled是另组件饥饿费用字段，不声称此门和投掷总开关完全相同。',
 '最终拒控返回值应携带拒绝原因；原版声音若表示成功传送，不能直接拿来当Boss嗡声。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'artifacts-native-batch37','credited_chains':keys,'rationale':'来源tag条件免疫、原生受击无敌帧延长、原生末影珍珠伤害调用拒绝各1；装备/平台/常量换壳和通用query0。CureEffects tag成员激活未补齐暂0，kitty纯清仇恨0，absorbDamage实际为攻击者回血非拒伤0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
