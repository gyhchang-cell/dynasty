"""Native fear pickup control immunity and attack-to-heal refusal. No generic networking credits."""
from ledger import B,O,record,verify
import json
r='Lycanite/LycanitesMobs';p='src/main/java/com/lycanitesmobs/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='lycanites-native-weight-heavy-pickup-refusal-and-safe-release-control-lease'
record(k,r,[w('core/entity/EntityFear.java'),w('ExtendedEntity.java'),w('core/network/MessageEntityPickedUp.java'),w('core/network/PacketHandler.java'),f('PotionEffects.java',36,258),f('PotionEffects.java',338,391),f('core/entity/EntityCreatureBase.java',3228,3275),f('EventListener.java',223,258),f('LycanitesMobs.java',145,177),f('LycanitesMobs.java',210,217),f('LycanitesMobs.java',278,296),f('shadowmobs/entity/EntityShade.java',134,179)],
 '原生Shade成功melee后概率specialAttack在5格活体/非队友/非骑乘且骑手AttackEntityEvent允许时加fear；实际PotionEffects LivingUpdate已注册，活动fear且非creative/spectator→每实体ExtendedEntity至多一个EntityFear，实际fear实体注册核对。EntityFear server onLivingUpdate→canPickupEntity拒IGroupBoss/IGroupHeavy、weight、不允许载具/乘客、其他非Fear占用，允许后pickup→ExtendedEntity.setPickedUpByEntity。ExtendedEntity原生LivingUpdate持续随picker移动，死亡/weight/超32格释放；Fear失效/目标失效杀代理，下轮释放。',
 '计1：控制实际pickup准入和weight触发租期释放，飞行能力快照/安全位置回退及S2C一并归此家族，不按fear/spawn/packet/getter拆数。Boss/Heavy即使已带fear也可不被搬动，代理会仅随目标，不能把status存在当已控制。释放恢复allowFlying/isFlying并noClip=false、回最后非solid位置、速度/落距0；只有脚位solid判断不等于完整碰撞安全。非空picker改非空会覆盖原能力快照，异常被吞；client静态HashMap未见此类内卸载清理。网络按维度广播两整数id，无UUID/维度字段/入队，missing picker被当null释放且可能误回safePos。',
 'Boss拒控灰字必须跟最终准入拒绝而非仅状态添加成功；控制效果已存在但被重量/体型策略拒绝的情况需要明确。S2C查不到目标时不能凭空制造一次解除或移动。',
 '完整Fear/ExtendedEntity/Message/PacketHandler、完整PotionEffects.onEntityUpdate与native pickup方法已读。EventListener.onEntityUpdate完整已读，注册callsite只截关键块，不冒称preInit整方法。生产Shade特殊攻击方法完整，AI父类全部调度未读不称运行实测。fear自有声音为API挂接，未听音/截图/客户端测试。普通体质不追加灰字。','native_pickup_control_admission_and_release')
k2='lycanites-native-attacker-debuff-converts-rejected-damage-event-into-target-heal'
record(k2,r,[w('elementalmobs/entity/EntityFaeBolt.java'),f('elementalmobs/entity/EntityNymph.java',119,123),f('core/entity/EntityProjectileBase.java',169,369),f('PotionEffects.java',301,329),f('LycanitesMobs.java',145,177),w('PotionBase.java')],
 '原生Nymph.attackRanged发FaeBolt；FaeBolt setup baseDamage0且可配置debuff，onEntityLivingDamage给lifeleak，getDamage恒0。完整EntityProjectileBase.onImpact通过canDamage后先调用onEntityLivingDamage，之后仅damage!=0才hurt，因此零伤害也会施加debuff。真实注册lifeleak和PotionEffects listener核对：onLivingAttack跳过已取消/nulltarget/nonliving attacker，server且attacker活动lifeleak，取消原攻击并target.heal(event.amount)。',
 '计1：攻击者负面状态把一次被拒伤害事件转换成目标治疗，区别目标护盾吸收/反射/转移，不是仅tag更名。治疗金额取LivingAttack原amount而非最终减免后伤害/实际HP差；满血也cancel、不能据无HP变化判无拒绝。canDamage含server/PVP/owner队伍门；friendlyFire配置布尔条件按源码原样，不据名称猜语义。Fae本身status添加无成功返回，不能用粒子或onEntityLivingDamage true断言控制被接纳。',
 'Boss灰字应只在控制被拒绝时生成，不能把伤害转治疗、零伤害status投射物或满血无变化统一视作免控。',
 '完整Fae/Projectile原生impact/canDamage和Lifeleak listener已读，实际Potion注册/事件bus可达；Nymph attackRanged完整。全部射弹反射构造/世界出生分发未读，只称原生方法链静态观察；无新Boss文本/网络实现也无实机观感通过。','native_attack_rejection_converted_to_heal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'lycanites-batch98-pickup-refusal-and-attack-to-heal','credited_chains':[k,k2],'rationale':'Final control pickup admission and lease teardown one whole family; attacker-debuff native damage cancellation converting to target healing is independent. Packet/attributes/particle wrappers and effect colour/name variants zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
