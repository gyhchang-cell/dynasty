"""Charging hit storage and shared-target post-grasp lockout; two final policies."""
from ledger import B,O,record,verify
import json
r='Sweenus/SimplySwords';p='common/src/main/java/net/sweenus/simplyswords/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
common=[f('SimplySwords.java',148,365),w('mixin/ServerWorldMixin.java'),w('item/interfaces/UniqueWeaponActiveAbility.java'),f('api/SimplySwordsAPI.java',267,326),f('api/SimplySwordsAPI.java',406,414),f('util/HelperMethods.java',94,170)]
k1='simplyswords-native-charge-absorb-counter-mode-qualified-refusal'
record(k1,r,common+[w('item/custom/ThunderbrandSwordItem.java'),f('registry/ItemsRegistry.java',860,865),w('mixin/ServerPlayerEntityMixin.java'),f('mixin/LivingEntityMixin.java',156,207),f('world/ThunderbrandAbilityManager.java',64,265),f('world/ThunderbrandAbilityManager.java',308,346),f('world/ThunderbrandAbilityManager.java',485,493),f('world/ThunderbrandAbilityManager.java',508,540),f('world/ThunderbrandAbilityManager.java',648,655),f('world/ThunderbrandAbilityManager.java',670,674),f('world/ThunderbrandAbilityManager.java',737,745),f('world/ThunderbrandAbilityManager.java',757,782),f('world/ThunderbrandAbilityManager.java',827,838),f('world/ThunderbrandAbilityManager.java',874,880)],
 '实际thunderbrand ITEM注册→Item.use→共享输入/解锁/CD/mana→API.activateWeaponWithProvenance→item.activate→manager.start，按ServerWorld+actorUUID存CHARGING。原生ServerPlayer或非玩家Living.damage HEAD→handleIncomingDamage true取消；ServerWorld.tick推进蓄力/冲刺，Item.onStoppedUsing取消charging，可带memory恢复。',
 '蓄力期间按被击次数存能、模式决定是否最终拒绝的独立政策1；非amount数值累计，cap默认15只限制记数，不限制继续拒绝。排bypass/非正amount/creative/spectator；须同手仍持同item，但不要求同stack对象。grounded模式仍累计并发absorb声光，却returnfalse放行伤害，且加Resistance仅减伤；insulator标志直接true而不累计/不发该absorb。普通charging true；DASHING仅defenseUntil之前且非grounded拒绝，该phase wrapper不另计。retaliate只对attacker==direct的Living加slow，不验addStatusEffect布尔。声音pitch随stored封顶变化，不是Boss拒控语义，也无按目标反馈节流。',
 '一个“吸收”声音可能来自未拒绝伤害的分支；Boss灰字必须由明确控制拒绝生产，不能绑定声光函数或hurt=false的概括。保护期间cap和UI阈值须分别验证。',
 '固定708a57bc591e0af75ae0c5ec6beb0d8ff22f67af；完整关键native/物品/拒绝/phase推进/清退/声音/恢复方法已读。释放链的调度已读作上下文，但未将链伤害/雷电几何另计，也未审所有mastery配置。未运行游戏、听音、TCP或像素验收。','native_charge_counter_damage_refusal')
k2='simplyswords-native-gloam-shared-target-grasp-immunity-aftercare'
record(k2,r,common+[w('world/GloamMechanicsManager.java'),f('world/GloamStainManager.java',228,336),f('world/GloamStainManager.java',450,501),f('world/GloamStainManager.java',751,753),f('world/GloamStainManager.java',778,810),w('effect/GloamGraspEffect.java'),f('registry/ItemsRegistry.java',1077,1082),f('registry/EffectRegistry.java',159,166),w('item/custom/WraithmawSwordItem.java'),f('world/WraithmawAbilityManager.java',66,148),f('world/WraithmawAbilityManager.java',390,411),f('entity/WraithmawCutlassEntity.java',132,155),f('entity/WraithmawCutlassEntity.java',177,265),f('entity/WraithmawCutlassEntity.java',533,559),f('mixin/LivingEntityMixin.java',82,95),f('mixin/LivingEntityMixin.java',359,364)],
 '实际wraithmaw物品输入→manager.activate生成cutlass→原生Entity.tick分阶段下落/方块碰撞→embed→createGloam→createPatch/createCircle。ServerWorld.tick推进stain，每5tick仅onGround且友伤允许并在几何内的目标recordContact；GloamMechanics.tick每目标累计exposure，到1触发grasp并设置now+duration+immunity锁。原生Living移动输入与jump钩子消费GLOAM_GRASP，observer显示复用前条链不重复计。',
 '按world+targetUUID共享的抓取后免重复控制与接触暴露归零为独立最终拒再控点1，不按owner/多个patch/效果阶段重复。处于immunityEndTick之前即使持续接触也exposure0、不再触发grasp，但仍可每5tick施加基础slow，故非所有控制免疫。owner最近接触6tick内保留归属，其他owner仍可更新source；锁跨owner共享而非每个施法者独立。triggerGrasp先置锁后addStatusEffect，未检查布尔，即便effect被其他模组拒绝也会锁并发声/粒子；不能把这些回执当控制已成功或Boss被明确拒控。锁覆盖实际grasp时长加额外窗口，默认状态Expiry不保存，不是永久Boss标志。',
 '区分拒绝再控、控制实际接纳、减速仍生效和普通目标临时保护；Boss回执需要在最终拒控理由处生产，按真实目标限频，与玩家体质type9分开。不要照搬未经接纳就播放成功声光。',
 '原生启用链、producer、每目标暴露/免控最终判断、接触过滤、实际移动/jump消费者完整关键方法已读。复杂cutlass命中/地形/视觉其他分支只作上下文0；实际groundring之外的Gloam绘制未完整审。未启动游戏或证明实际观感。','native_shared_target_control_reapplication_lockout')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'simplyswords-batch74-charge-and-aftercare','credited_chains':[k1,k2],'rationale':'被击次数储能且有发声但放行模式的原生拒伤点，与暴露累积后的跨owner目标抓取免再控点独立；普通dash无敌、slow常量、显示阶段、声音wrapper合并0。Waxweaver尺寸/友伤筛选仍候选0，不以目标筛选泛化Boss免疫。'})
(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
