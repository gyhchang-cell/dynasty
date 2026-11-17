"""Four native Alex's Caves policies, manually read, fixed blob provenance, no runtime claims."""
from ledger import B,O,record,verify
import json
r='AlexModGuy/AlexsCaves';p='src/main/java/com/github/alexmodguy/alexscaves/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
common=[f('AlexsCaves.java',92,134),f('AlexsCaves.java',143,177)]
keys=[]
def add(k,refs,chain,obs,lesson,limits,cat):
 record(k,r,common+refs,chain,obs,lesson,limits,cat);keys.append(k)
add('alexscaves-native-sonic-refusal-converts-to-coalesced-counterattack-charge',[
 f('server/entity/ACEntityRegistry.java',85,85),f('server/entity/living/ForsakenEntity.java',99,119),f('server/entity/living/ForsakenEntity.java',394,400),f('server/entity/living/ForsakenEntity.java',490,501),w('server/entity/ai/ForsakenAttackGoal.java')],
 '真实Forsaken实体注册与registerGoals→ForsakenAttackGoal；原生hurt在SONIC_BOOM直接setSonicCharge(true)且false、不superhurt，其他攻击仅golem减半。同步boolean初始false；Goal完整tick在当前target活着时，(距离>20且随机.01或hasSonicCharge)&&!sonicEnqueued→排入sonic并setCharge(false)，下次tick有LOS、距离<200才安排SONIC_ATTACK或BLAST，playSound；动画限定时刻安排按距离延迟的音爆hurt或5tick间隔AOE。',
 '不同于仅换damage tag的静态免伤清单：拒绝结果写入合并boolean资源，原生AI消费后产生延迟反击；重复音爆在消费前合并为一次charge。native hurt写charge没有server判断，但实际Goal反击不是客户端文本。没有目标/距离时可能保留charge，不等于每次拒伤即时可见回执；反击hurt返回值未检查仍有声音/knockback，不把它当目标已伤。整个拒伤→蓄能→消费家族1，音色/动画/两攻击包装0。',
 'Boss拒控灰字必须由此次明确拒绝生产，不能把后来反击的声音或合并资源当逐次回执；区分事件节流和能力排队合并。',
 '完整关键hurt/同步访问器/Goal类和真实注册已读；未逐行全Forsaken tick/第三方Citadel动画网络/像素音效，不声称灰字、闪光、精确视觉同步。普通阴阳体质需求不变。','native_refusal_resource_conversion')
add('alexscaves-native-orbiting-spirit-consumption-refusal-and-fading-exclusion',[
 f('server/item/ACItemRegistry.java',107,108),f('server/entity/ACEntityRegistry.java',51,51),w('server/item/SpearItem.java'),w('server/item/ExtinctionSpearItem.java'),w('server/entity/item/DinosaurSpiritEntity.java'),f('server/event/CommonEvents.java',198,213)],
 '真实ExtinctionSpear注册继承SpearItem.use→startUsingItem；首个onUseTick生成3+HerdPhalanx的GROTTOCERATOPS spirit、ownerUUID与环绕offset。原生LivingDamageEvent player正在使用该spear时killGrottoGhostsFor(player,true)：30范围内ownerUUID相等、正确type、!isFading，找到候选setFading(true)→true→event.cancel并SHIELD_BLOCK声。releaseUsing将所有同owner合格spirit置fading。spirit同步FADING/owner，tick淡出至0discard，非使用spear或owner缺失开始fading。',
 '以真实世界实体集合提供一次拒伤库存，原生消费者把选中实体先标fading，使同刻后续事件不再消费它；不是单纯盔甲常量或计数charge换名。所谓closest实现比较closest.distanceTo(player)>spirit.distanceTo(closest)，并非正确的两个候选到player距离比较，原样记录不修上游。owner获取服务器走全服PlayerList，未额外查owner维度；拒伤查询只在当前世界30范围，原生onUseTick生成本身无server侧判断。拒伤与淡出整链1，三个spirit/包装/光环数/模型0。',
 'Boss反馈节流状态应在发送前原子地更新；结束/失主应清理世界对象。不要把声明closest或UUID存在视为维度与距离安全已证。',
 '完整Spear/ExtinctionSpear/Spirit及damage消费和注册已读；未读spiritRenderer或声资源、不宣称实际环绕可辨识。只是相关原生拒伤资源与生命周期研究，不向项目新增spirit机制。','native_entity_resource_refusal')
add('alexscaves-native-persisted-target-control-lease-spatial-rearm-and-release-receipt',[
 f('server/entity/ACEntityRegistry.java',82,82),w('server/entity/ai/WatcherAttackGoal.java'),f('server/entity/living/WatcherEntity.java',91,99),f('server/entity/living/WatcherEntity.java',126,133),f('server/entity/living/WatcherEntity.java',151,186),f('server/entity/living/WatcherEntity.java',205,293),f('server/entity/living/WatcherEntity.java',302,342),f('server/entity/living/WatcherEntity.java',358,385),f('server/config/ACServerConfig.java',66,67),f('mixin/LivingEntityMixin.java',147,153),f('server/event/CommonEvents.java',198,213),w('server/message/PossessionKeyMessage.java'),f('client/ClientProxy.java',555,577)],
 '真实WatcherGoal.tick→attemptPossession；canPossessTargetEntity玩家Persisted_NBT lasttime按worldTime差对config默认300tick放行；施法者自身>100tick且上次站点distSqr>10门，成功记录站点时间、玩家时间/possessedFlag和targetUUID。Watcher.tick服务端UUID解实体，同步ID/strength，控制中每tick更新lastPossessionTimestamp并broadcast77；近距<1/strength释放/施法者死→清flag/更新时间/broadcast78/清UUID与ID。受控的LivingDamageEvent拒绝非bypass且非Watcher来源。',
 '实际控制准入“每目标持久时间+施法者时间/空间再装填”及它的释放回执整家族1，不按包装/flag/UI/音色拆。client77只本地被控玩家且config允许切镜头，78请求appearance粒子/恐吓声/还原camera；server回执并非灰字。源码else丢失/死目标分支只清ID/timeout，未清flag/UUID，不能说各生命周期路径全清理。stopPossession先减strength但用旧值>=1&&timeout>40；>140每tick加.1后减.05。Key包信任playerId、无sender同一身份检查且possessed.equals缺null防护；实体内比较目标，但不应称完整收包安全。',
 'Boss灰字节流可借鉴按目标记录，但用稳定目标身份/世界生命周期而非单纯entityId；重复禁止应明确最终控制门与理由。释放音/镜头特效不能替代拒控文字。',
 '完整Watcher关键方法/Goal/Key/Proxy原生调用已读；注册mixin配置、appearance粒子内部未补，未声称运行/画面质量/重登行为通过。持久数据只是源码观察。普通体质不加灰字。','native_target_control_rearm_lifecycle')
add('alexscaves-native-effect-admission-qualified-stun-receipt-with-target-orbit-expiry',[
 f('server/item/ACItemRegistry.java',98,99),w('server/item/PrimitiveClubItem.java'),f('server/potion/ACEffectRegistry.java',21,29),w('server/potion/StunnedEffect.java'),w('server/message/UpdateEffectVisualityEntityMessage.java'),f('server/event/CommonEvents.java',216,232),w('client/particle/StunStarParticle.java'),w('client/particle/AbstractTrailParticle.java'),f('client/ClientProxy.java',328,328)],
 '真实PrimitiveClub原生hurtEnemy服务器概率.8→addEffect(STUNNED)返回true才选HIT声、S2C type3 target/source/duration并派生DazingSweep；否则MISS声。溅射先hurt(1)不检查bool，再分别addEffect成功才发状态包。UpdateEffectVisuality收端当前player.level按ID查living/source且距离<32，type3映射STUNNED，removeNoUpdate或addEffect；不enqueue，未限制接收方向/UUID/维度。注册StunnedEffect每tick概率按实体宽度请求STUN_STAR，降低movement并停Mob MOVE/JUMP/LOOK。',
 '一套真实“以最终效果接纳bool分离hit/miss声音、显式目标反馈、跟随实体头位/到期清理”的战斗反馈链1，不按splash/packet/星星绘制包装另计。星粒子工厂实际已注册；getOrbitPos普通目标眼位+朝向和体型偏移，Sauropod用headPart；tick实体仍Living且失STUN删除，实体ID查不到返回ZERO但不立即remove，依30..34tick寿命，存在原点残影/ID复用边界。render前2age跳过、真实四顶点camera billboard加64槽trail；itemEntityTranslucentCull是继承的vanilla RenderType方法，此次未读vanilla实现，不冒称穿墙/深度策略已查。',
 'Boss需要明确拒控reason，而不能仅把任何addEffect失败叫免疫；成功与失败声需按最终接纳关联。目标缺失应清理，S2C显式校验维度/身份/有限参数，别复用第三方当前世界ID包的缺口。',
 '完整Club/状态/消息/星粒子/Trail已读且注册核对；普通STUN禁攻消费者与已阅Arcanus同类不新增独立数，纯trail绘制辅助0。外部Minecraft/Forge管线、shader与像素未验；无正式资产制作。','native_effect_qualified_feedback_anchor')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'alexscaves-batch92-native-policies','credited_chains':keys,'rationale':'Sonic rejection converts into AI charge; owner-bound orbiting world spirits consumed before rejection; persisted per-target/spatial possession admission and teardown; effect-success-qualified feedback with native orbit expiry =4 distinct native policies. Wrappers/render libraries/parts/constants, gum rider policy shared with existing mounts and reskin effect exclusions zero. No guard old ledger credit.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
