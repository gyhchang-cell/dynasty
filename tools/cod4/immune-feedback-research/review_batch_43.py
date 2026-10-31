"""Cold Sweat pinned native cancellation, explicit receipt, target once-stamp chains."""
from ledger import B,O,record,verify
import json
r='Momo-Softworks/Cold-Sweat';p='src/main/java/com/momosoftworks/coldsweat/';keys=[]
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
base=[(p+'ColdSweat.java',37,95)]
def add(k,refs,c,o,l):
 for f,a,z in base+refs:assert 1<=a<=z<=len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
 record(k,r,base+refs,c,o,l,'固定bce1f30aecd137c04c4210684a9fd40b92841080，本地Git tree/blob及SHA；全文关键game方法/原生调用已观察，不运行或编译上游，正式代码资产TODO不动，不启动游戏；普通阴阳不新增灰字，generic wrapper/常量变体0。','native_damage_control_refusal_and_feedback');keys.append(k)
e=p+'common/capability/handler/EntityTempManager.java'
add('coldsweat-native-hoglin-boot-hot-floor-final-cancel',[(p+'core/init/ItemInit.java',45,46),w(p+'util/registries/ModItems.java'),(p+'common/event/ProcessEquipmentInsulation.java',47,48),(p+'common/event/ProcessEquipmentInsulation.java',229,236)],
 '实际注册HOGLIN_BOOTS物品与真实ModItems引用→已订阅ProcessEquipmentInsulation→原生LivingAttack source.is(HOT_FLOOR)+脚槽exactitem则setCanceled true。',
 '一个独立原生装备危险地板伤害取消生产点1，不把四件盔甲或名字常量拆数。无creative/装备破损/温度/能源门，仅exactitem脚槽。未清火或所有fire源、无目标反馈包；此监听取消当前伤害不等于Boss控制免疫。外部原生source处理不声称所有magma配置都进此门。',
 '最终取消必须说明准确来源/条件；Boss拒控不能套装备免疫，也不能据取消假设已有灰字。')
add('coldsweat-native-ice-resistance-vanilla-freeze-cancel',[(e,97,99),(e,615,621),w(p+'common/effect/IceResistanceEffect.java'),w(p+'core/init/EffectInit.java'),w(p+'core/init/PotionInit.java'),w(p+'util/registries/ModEffects.java'),(p+'config/ConfigSettings.java',290,295)],
 '真实ICE_RESISTANCE注册+3600/7200tick实际Potion定义→原生LivingAttack→source.equals(entity.level.damageSources.freeze())且hasEffect和配置enabled→cancel。',
 '独立已经进入原生伤害事件的抗冻裁决1，不按药水时长/效果常量拆。这里是DamageSource.equals具体freeze对象，不是ModDamageSources.COLD或任意IS_FREEZING tag；不能把同名寒冷视作完全相同入口。无清除冷状态/降温/解除移动控制或灰字。配置enabled与hasEffect合取，只有effect存在不充分；没有逐次音效生产。原版DamageSource.equals内部未引用，不冒称所有包装源匹配。',
 '拒控枚举/策略应精确，通用hurt false或“寒冷”名字都不足以判Boss Immune。')
a=p+'common/capability/temperature/AbstractTempCap.java'
add('coldsweat-native-critical-temperature-source-denial-and-bound-hurt-sound',[(e,263,336),(e,837,839),(a,243,334),(a,439,481),w(p+'common/capability/temperature/PlayerTempCap.java'),w(p+'common/event/PlayerDamageSound.java'),w(p+'util/registries/ModDamageSources.java'),(p+'util/world/WorldHelper.java',363,376),(p+'util/ClientOnlyHelper.java',32,34),w(p+'core/network/message/PlayEntityAttachedSoundMessage.java'),(p+'core/network/ColdSweatPacketHandler.java',11,25),(p+'ColdSweat.java',109,123)],
 '真实LivingTick启用温度实体server→cap.tick计算写BODY相关traits后tickHurting→peaceful/grace/间隔门→body>=100 FireResistance配置或<=-100 IceResistance配置直接阻止相应自定义HOT/COLD hurt生产；其他按resistance blend伤害。真实LivingHurt自定义COLD且server Player→WorldHelper非silent→tracking_entity_and_self音包→client当前level entityId+soundregistry校验→EntityBoundSoundInstance原版PLAYER_HURT_FREEZE。',
 '本条独立自定义危温伤害生产拒绝与其真实受伤声链合1，hot/cold/属性阈值不拆；与原版freeze事件取消不同生产点。resistance减为0仍调用hurt，不等于hasIce/FireResist直接不生产，返回bool忽略。sound在LivingHurt不是最终HP证明，后续监听可能改/取消；无防重复/UUID/dimension/generation/level-null/finite音量校验，没有以entity缺失排队重放。isSilent阻止soundserver。sound key length以Java字符数写UTF8byte序列，原版资源ASCII不受此特定偏差，但不称任意非ASCII安全。hurtInterval>0后除rateInterval整数可成0，若配置1..3且rateInterval更大则存在除零静态可能，不称运行复现。EntityBound生命周期/原生声混音未读实际版本实现，不声称跨世界自动全清。',
 '真正拒绝需在控制生产/结算明确标记，再统一播灰字微光嗡声；不得从0伤/音包推出免疫，目标包须有身份和生命周期边界。')
c=p+'common/entity/Chameleon.java'
add('coldsweat-native-mounted-chameleon-rider-immunity-proxy',[(p+'core/init/EntityInit.java',12,19),(c,73,75),(c,155,164),(c,190,234),(c,293,313)],
 '真实注册Chameleon实体，可信玩家原生mobInteract服务器startRiding→native isInvulnerableTo若vehicle Player：inWall/fall直接true，否则creative或代理player.isInvulnerableTo；原生LivingHurt如果vehicle就是source.entity取消；原生projectileImpact若目标Chameleon且骑Player则SKIP_ENTITY并hurtTimestamp前移20。',
 '独立骑乘代理免疫家族1，所有wrapper/来源/载主hurt保护不拆；cataclysm既有carried directsource安全相同部分0，本条独立依据代理载主实际isInvulnerableTo与投射物SKIP行为。不是驯养owner无条件安全，onHitFromOwner实际vehicle而非trustedUUID，投射物门不查source owner。代理分支不再OR本实体super，不能假定自身其他基础免疫也保留。无灰字/flash/hum，intid骑乘包细节未全读，不称TCP挂载画面成功。',
 '当前目标的最终拒绝与载主/owner身份区分，按真实拒绝原因回执；不要将友军/骑乘安全都当Boss拒控。')
l=p+'common/item/SoulspringLampItem.java'
add('coldsweat-native-soul-hit-target-once-stamp-before-damage-receipt',[(p+'core/init/ItemInit.java',24,24),(l,160,174),(l,190,228),(p+'util/world/WorldHelper.java',499,529),w(p+'core/network/message/ParticleBatchMessage.java'),(p+'core/network/ColdSweatPacketHandler.java',25,29),(p+'util/world/WorldHelper.java',363,376)],
 '真实SoulspringLamp物品原生LivingAttack：Player source/nonPlayer目标/真实主手灯/fuel<64/非undead/target NBT未SoulSucked→先目标persistent once标记+按maxHP补fuel→需要时额外hurt至8(忽略bool)→server按目标AABB体积clamp5..50 SOUL粒子批包/同维度广播；client-only本次事件分支才播灯声。',
 '明确按实际受击目标一次消耗/防递归回执生产位点1，不把通用粒子包/绘制/音效/持灯效果包装拆分。once标志在extra hurt之前，避免extra hurt重入再产fuel/粒子；但本次原生伤害后续被其他mod取消也不会回滚fuel/once，不能叫伤害成功或Boss免疫提示。目标persistent标志非每tick冷却，没有在该链清除/按attacker分开，后来的持灯人也跳过。粒子是出生坐标快照不跟随实体，DIMENSION广播不是仅跟踪；默认minSetting=-1忽略粒子质量门；HashSet不是事件/目标节流，也未设packet size/finite/dimUUID校验。client sound分支不保证native事件确在client发生，不能假定双端都听到。实际粒子寿命/像素未验，普通SOUL资源不是新建模型。',
 '可借真实目标once/重入保护思路，但Boss应按被拒控制语义+短期逐目标预算；伤害失败不代表资源/回执未生，拒控提示不要永久只播一次。')
f=O/'semantic-dedup.json';x=json.loads(f.read_text());x['groups'].append({'family':'coldsweat-native-batch43','credited_chains':keys,'rationale':'靴子危险地板取消1；原版freeze状态门1；自定义危温伤害生产拒绝+真实绑定受击声1；骑乘代理免疫+skip1；受击SoulSucked目标once+重入防护/明确粒子回执1。来源/阈值/声音/网络包装、冷热换色0额外。FreezeKnockback降攻击者推力和普通温度负面效果暂0，不以所有状态代码凑数。'});f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');verify()
