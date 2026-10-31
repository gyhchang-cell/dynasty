"""Two native control/combat receipt policies, generic transport is supporting zero."""
from ledger import B,O,record,verify
import json
r='VazkiiMods/Botania';p='Xplat/src/main/java/vazkii/botania/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
shared=[w('network/clientbound/BotaniaEffectPacket.java'),('Forge/src/main/java/vazkii/botania/forge/xplat/ForgeXplatImpl.java',488,493),('Forge/src/main/java/vazkii/botania/forge/network/ForgePacketHandler.java',1,69)]
k='botania-native-deferred-control-revalidation-and-qualified-target-receipt'
record(k,r,[w('common/item/equipment/bauble/CharmOfTheDivaItem.java'),w('common/block/flower/functional/HeiseiDreamBlockEntity.java'),f('common/item/BotaniaItems.java',292,292),f('common/item/BotaniaItems.java',394,401),('Forge/src/main/java/vazkii/botania/forge/ForgeCommonInitializer.java',420,439)]+shared,
 '原生Forge LivingHurtEvent直接来源Player→Diva.onEntityDamaged，服务端Mob且canChangeDimensions且随机命中且真实装备→server.tell TickTask延至当前tick末。charmMobs再次模拟mana250、目标存活/敌对或中立/非自己的宠物/20格；枚举目标周围40宽目标列表并排除本体、共同载具、自己的宠物。brainwashEntity只在旧target非Enemy时清target、把HurtByTargetGoal提升-1且清ignoreClasses、设置lastHurtByMob，返回true才heal/unsetRemoved、creeper fuse2、实际扣mana、声音和跟踪目标S2C。',
 '独立的延迟控制资格重验与已接受AI转移准备回执家族1；花调用同brainwash合并0。不是直接强制setTarget新目标，不保证下轮HurtByTargetGoal能完成追击；canChangeDimensions是源码明确TODO的Boss识别近似。延迟后未重新验证amulet仍装备/玩家维度，实际扣mana返回值未检查。DIVA收包由mc.execute处理，在当前world按id找目标，无则break；用目标现坐标宽高随机50个sparkle，没有UUID/维度代际保护。',
 '拒控文字应以明确拒绝决定产生，不能把已提交AI重定向或canChangeDimensions判据等同所有Boss免控。异步回执须重新核对目标身份、维度和最终接纳，而非只沿用捕获引用。',
 '完整Diva/Heisei/EffectPacket/ForgePacketHandler及native listener/发送方法和实际物品注册已读；监听lambda完整，未将超大初始化方法整体称全文。只核API粒子请求，未追sparkle具体渲染，也无运行/像素或最后AI动作实测。','native_deferred_control_revalidation')
k2='botania-native-chain-hit-identity-budget-versus-client-missing-target-truncation'
record(k2,r,[w('common/item/equipment/tool/ThundercallerItem.java'),w('common/item/equipment/tool/manasteel/ManasteelSwordItem.java'),f('common/item/BotaniaItems.java',224,224),f('common/item/BotaniaItems.java',394,401),w('common/proxy/Proxy.java'),f('client/core/proxy/ClientProxy.java',78,82)]+shared,
 '原生已注册Thundercaller.hurtEnemy在4跳/雷暴10跳预算中，每次以上个target为中心8格找Enemy/Living且不在alreadyTargetedEntities的实体，原生hurt调用后无论bool均记录id、推进前一目标、伤害递减。非空列表按attacker tracking+self发送起点及有序id数组。EffectPacket客户端当前world逐id解析，每个目标中心作为下一条起点，首个missing即break整条剩余链，Proxy最终BoltRenderer.add。',
 '按一次连锁攻击的目标身份去重与有序视觉消费失败策略计1，非每跳/音色/packet包装加数。首个原始受击entity未预先加入集合，可能后面被选到一次；选择无LOS/活体明确过滤、hurt失败仍有闪电。实际ClientProxy标todo并忽略传入颜色/seed/ticksPerMeter，不能声称颜色已按参数呈现。追踪attacker不保证所有连锁目标都已在接收端加载，missing使后段全部丢弃。',
 'Boss回执需独立的按目标时间节流，不能照搬单次连锁集合；表现存在不能反证实际hurt接纳，更不能把false当控制免疫。缺失目标可仅丢该回执，不应误连错误实体。',
 '整类native item/剑基类、完整网络编解码及消费、真实注册和Proxy方法均已读。BoltRenderer底层几何未读，仅记录其入队调用，深度/画面可辨识无静态通过；该支持层不额外计数。','native_chain_target_dedup_feedback')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'botania-batch95-deferred-control-and-chain-feedback','credited_chains':[k,k2],'rationale':'Deferred control requalification differs from immediate damage immunity; native ordered chain target budget and failed-lookup truncation is one whole combat feedback policy. Flower wrapper, transports, particles and hops zero extra.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
