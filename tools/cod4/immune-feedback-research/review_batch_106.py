"""Three distinct native Create combat/control settlement policies, no action wrappers as credits."""
from ledger import B,O,record,verify
import json
r='Creators-of-Create/Create';p='src/main/java/com/simibubi/create/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def resource(name):
 s='src/generated/resources/data/create/create/potato_projectile/type/'+name+'.json'
 return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
common=[f('Create.java',105,166),f('AllItems.java',419,425),f('AllEntityTypes.java',69,72),w('content/equipment/potatoCannon/PotatoCannonItem.java'),w('api/equipment/potatoCannon/PotatoCannonProjectileType.java'),w('api/equipment/potatoCannon/PotatoProjectileEntityHitAction.java'),f('content/equipment/potatoCannon/PotatoProjectileEntity.java',64,72),f('content/equipment/potatoCannon/PotatoProjectileEntity.java',171,269),f('content/equipment/potatoCannon/PotatoProjectileEntity.java',311,332),w('foundation/damageTypes/CreateDamageSources.java')]
# Do not claim the tooltip or all cannon item methods read: restrict to complete native ammo/use methods.
common=[x for x in common if x[0]!=p+'content/equipment/potatoCannon/PotatoCannonItem.java']+[f('content/equipment/potatoCannon/PotatoCannonItem.java',60,164)]
keys=[]
k='create-native-cardboard-cancels-attack-but-retains-dismount-and-directed-client-knockback';keys.append(k)
record(k,r,[w('content/equipment/tool/CardboardSwordItem.java'),w('content/equipment/tool/KnockbackPacket.java'),f('Create.java',105,166),f('AllItems.java',182,188),f('AllPackets.java',234,234),f('AllPackets.java',241,247),f('AllPackets.java',255,262),f('AllSoundEvents.java',138,140),f('AllSoundEvents.java',520,526),f('AllSoundEvents.java',578,597),f('AllSoundEvents.java',759,767)],
 '固定7ff2760，真实CARDBOARD_SWORD注册，自动订阅AttackEntityEvent HIGHEST。主手命中Living且非ARTHROPOD则先bonk声音、cancel攻击；另模拟knockback：基础属性+2/附魔/冲刺，正值调用stopRiding→Living.knockback，并对ServerPlayer目标发KnockbackPacket。客户端handle只校验LocalPlayer非null又调用同helper；creature/misc非player另加slowness60amp9，无视addEffect返回；末尾减攻击者速度并停冲刺。AllPackets原生注册codec。',
 '计1：原生取消伤害后仍专门执行控制并按玩家目标补送客户端控制，非Boss免控或一个hurt=false包装。stopRiding在knockback前，即击退事件/抗性拒绝不代表仍骑乘；正值前有返回，声音/取消已发生。packet只有yRot/strength两个float，无维度/实体身份/事件代际/有限数值校验；接收目标是本地玩家，不是裸ID实体查找。handler自身无主线程调度，Catnip分发未读，不能假定无排队或线程不安全。bonk无本类节流，非灰字。',
 'Boss控制拒绝应先于下马和全部运动；音效与文字只跟明确server裁决，不从AttackEntityEvent canceled推断。S2C反馈验证当前维度、目标身份及生命周期，普通阴阳体质保持type9。',
 'CardboardSword和KnockbackPacket全文、onCtor与register全文及直接sound调用方法已读。事件NeoForge/Catnip底层辅助0；未实机，不声称有双重实际击退/跨维故障或观感。原声资源只研究调用，不复制资产。','native_damage_cancel_independent_control_replay')
k='create-native-potato-failed-hurt-rolls-back-only-post-prehit-fire-and-skips-followups';keys.append(k)
record(k,r,common+[resource('baked_potato'),f('content/equipment/potatoCannon/AllPotatoProjectileTypes.java',26,289),w('content/equipment/potatoCannon/AllPotatoProjectileEntityHitActions.java')],
 '真实PotatoCannon.use server从注册表按ammo找type，生成owner玩家的PotatoProjectile、设置ammo、位置/速度并入world。固定baked_potato JSON接pre_entity_hit set_on_fire60。native onHitEntity先pop粒子/命中声，再拒poweredWither或执行preEntityHit；随后才保存目标fireTicks=k、可能由燃烧弹体ignite。server hurt=false时还原k、kill并return，跳过onEntityHit、回收/掉落、击退、原版命中玩家回执、sticky。SetOnFire先直接setRemainingFireTicks且returnfalse继续结算。',
 '计1：实际原生失败回滚的作用域与阶段反馈次序，不是泛化所有箭伤拒绝。k在preEntityHit之后保存，故baked_potato的预先点火即使hurt=false也保留；rollback只撤掉之后燃烧弹体的ignite，不恢复入函数前所有状态。pop声/粒子可在damage/控制拒绝前出现，不能叫immune receipt。poweredWither提前return在pop之后且本分支不kill；Enderman hurt成功分支也提前return，不能把所有短路等同弹体消失。reload<10时写invulTime=reload+10仅在后段。',
 '对Boss免控拒绝必须明确禁止控制副作用，不借通用伤害失败回滚判定。反馈必须标明裁决类型；普通命中pop不能充当灰字/免疫闪光。',
 '完整onHitEntity、pop、damage helper、native use和type/命中action全文已读；所有ammo变体/注册/渲染mode包装不加数。基础Item.use网络及原版hurt内部未读，未运行上游，版本API不可直接移植。','native_failed_hit_partial_rollback_scope')
k='create-native-chorus-control-refusal-returns-recovery-result-with-success-only-dual-anchor-sound';keys.append(k)
record(k,r,common+[resource('chorus_fruit'),f('content/equipment/potatoCannon/AllPotatoProjectileTypes.java',26,289),w('content/equipment/potatoCannon/AllPotatoProjectileEntityHitActions.java')],
 '真实chorus_fruit JSON为on_entity_hit chorus_teleport diameter20，经PotatoCannon.use→native onHitEntity成功hurt后调用。ChorusTeleport.execute server Living最多16候选，先EventHooks.onChorusFruitTeleport；cancel直接returnfalse，randomTeleport成功才下马、原位置level声音+目标现位置声音、速度归零并returntrue。耗尽候选returnfalse。外层type.onEntityHit false被解释为允许回收：仍执行后续回收/掉落、物理击退等。',
 '计1：最终可取消传送裁决与上层“是否回收弹药”布尔契约混用，且成功后才产生原/新目标两锚点声效，区别伤害失败链。event取消立即终止16次搜索，不继续抽签；坐标用event修改值。false不等于没有伤害（此前hurt已成功）或没有其它控制（外层后续knockback仍可执行）；回收概率再决定drop/recover。无独立Boss标签/拒控灰字/防刷，不能将EventHooks取消一概称Boss免疫。',
 '灰字使用明确Boss控制拒绝原因，避免以弹药回收/执行bool替代；控制接受、物理后续、成功/拒绝声音和目标身份应分别核。',
 'ChorusTeleport及type接口、真实配置、外层native结算整链已读，EventHooks/vanilla randomTeleport底层辅助未读0，未声称存在Boss免疫注册者或实机可见。声音采样/双TCP未验；其它Potion/FoodEffects仅同链支持0。','native_control_refusal_vs_recovery_boolean')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'create-batch106-cancel-control-partial-fire-rollback-and-teleport-recovery-result','credited_chains':keys,'rationale':'Intentional canceled attack still dismounts/knocks and directs local-player replay; failed damage restores only fire snapshot after pre-hit stage; explicit teleport refusal bool interpreted as ammo recovery with later control retained. Three distinct native final policies, no per-ammo/codec/helper/render credits.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
