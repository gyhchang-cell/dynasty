"""Manually reviewed fixed Wizardry chains; textual evidence only, no Java execution."""
from reference_evidence import Evidence,row
import json
E=Evidence(13)
R='Electroblob77__Wizardry'
r=lambda file,method=None,**kw:E.ref(R,file,method,**kw)
P='pending_primary_semantic_review';S='support_only_not_effective'
geometry=[r('EntityForcefield','contains',signature='Vec3d vec'),r('EntityForcefield','contains',signature='AxisAlignedBB box'),r('EntityForcefield','contains',signature='Entity entity'),r('GeometryUtils','getVertices',signature='AxisAlignedBB box')]
lookup=[r('EntityForcefield','getSurroundingForcefield',signature='World world, Vec3d vec'),r('EntityForcefield','getSurroundingForcefield',signature='World world, AxisAlignedBB box, Vec3d vec'),r('EntityForcefield','getSurroundingForcefield',signature='Entity entity'),r('EntityUtils','getEntitiesWithinRadius')]
producer=[r('Forcefield','Forcefield'),r('Forcefield','addConstructExtras'),r('SpellConstruct','cast',signature='EntityPlayer caster'),r('SpellConstruct','spawnConstruct'),r('WizardryEntities',span=[144,144]),r('Spells',span=[361,361])]
rows=[]
rows.append(row(13,1,'wizardry-forcefield-native-attack-membership-denial-with-global-defender-exemption',P,
 [r('EntityForcefield','onLivingAttackEvent'),*lookup,*geometry,*producer,r('ItemArtefact','isArtefactActive')],
 '原生@SubscribeEvent LivingAttack入口先检测trueSource是Player、projectile且ring_defender活动便return；此例外没有核对该玩家是否拥有受影响力场。其余仅非unblockable、有trueSource且immediateSource不是EntityForcefield时比较受害者与trueSource周围的力场对象身份，不同才cancel；两者null或同一对象不cancel。实体归属用整个AABB八角严格在球内，边界算外；20半径内多个field取最近中心。间接来源按trueSource而非弹体所在侧判定。此事件没有拒伤文字/声音/粒子或冷却。',
 '最终拒绝需把来源、目标与实际策略一并纳入权威原因；不能将持戒攻击者全局例外概括为仅射穿自己的护盾，也不能从无伤推定Boss灰字已出现。',
 '检索当前371主账及helper旧批未见Wizardry Forcefield既有项；与既有独立EntityShield attackEntityFrom始终false不同，这里是两个空间归属的原生事件取消。contains/三种lookup/戒指包装合并支持，不额外计数。主岗仍需最终跨项目语义去重。',
 ['固定提交fe5d05a7a134836dd972e3680a900619c7e9c134；Git tree/blob与源码字节在序列化时核验，不代表运行验收。', 'EntityUtils球形筛选实际遇第一个超半径目标时remove后break，不能宣称列表中每个剩余元素都通过半径检查。', '伤害类型原生内部与第三方event优先级未运行；记录本地订阅代码，不宣称所有插件组合最终拒伤。']))
rows.append(row(13,2,'wizardry-forcefield-authoritative-repulsion-independent-of-hurt-and-client-predicted-cue',P,
 [r('EntityForcefield','onUpdate'),r('EntityMagicConstruct','onUpdate'),r('EntityMagicConstruct','getCaster'),r('EntityMagicConstruct','isValidTarget'),r('EntityUtils','getEntityByUUID'),r('EntityUtils','isLiving'),r('AllyDesignationSystem','isValidTarget'),r('ItemArtefact','isArtefactActive'),*geometry,*producer],
 '真实entity onUpdate先父类寿命检查，再按radius+4候选筛选；有效Living用最近AABB顶点预测nextDistance<=radius，非Living用entity当前位置距离与预测顶点距离判穿入/穿出。ring_defender按投射物owner非有效目标去掉友方弹；ring_interdiction对Living先尝试1MAGIC伤害且不看返回值，也在isRemote分支前。服务端无论hurt真假都会反向*.2加法线速度、地面负Y改.1、调整position、播放deflect声，MP另发SPacketEntityVelocity。每5tick的lifetime*.99在每个接触目标循环内执行，多目标同tick多扣。客户端独立重算：若目标Player位置在球内直接return整个onUpdate，后面目标粒子也跳过；否则FLASH+12DUST，不是服务端成功hurt回执。',
 '拒伤并不阻止独立运动控制；免控检查需要覆盖直接position/velocity生产点。视觉应关联权威拒绝结果，避免独立预测误当状态已被Boss接纳。提示节流不能套用这里按接触者扣总寿命的预算。',
 '空间穿越/推离链与上一条LivingAttack跨场取消入口独立：本链不要求有效DamageSource，伤害可false仍改变运动。Living/非Living、两戒指、声音/粒子、寿命消耗合并一条producer，不按分支或粒子数拆。与主账MPS hurt门控位移相反，但主岗可按跨项目控制链重复降级。',
 ['AllyDesignationSystem无caster时target非null即true；owner失效后不自动保持先前盟友保护。该差异只作边界，不新增守卫信用。', 'spawn同步caster整数ID失败仅warn；未运行spawn次序或实际TCP。', 'SEARCH_BORDER_SIZE=4并非保证所有高速弹体都拦截；球筛选break问题见上一条。', '客户端粒子生产点全文已读，不声称渲染器/声卡或两客户端已观察通过。']))
rows.append(row(13,3,'wizardry-forcefield-interaction-centre-versus-complete-body-membership-support',S,
 [r('EntityForcefield','onPlayerInteractEvent'),r('GeometryUtils','getCentre',signature='AxisAlignedBB box'),*lookup,*geometry],
 '原生PlayerInteract先拒非cancelable；先取block bbox转世界坐标，EntityInteract/Specific再覆盖为目标bbox。仅用目标bbox中心点和玩家position点比较场归属，异场cancel。与attack使用整个entity AABB严格内含不同，跨界大型实体可出现交互/攻击资格不同。没有Boss类型或addEffect否决，没有反馈。',
 '共享语义必须明确采用位置点还是完整身体，不应把一个入口通过直接推广到另一个入口。',
 '相同空间归属拒绝政策与013-01合并支持0；不是新的免疫实现信用。', ['原生PlayerInteract所有子类实发顺序未运行；不声称每次click都会触发。']))
rows.append(row(13,4,'wizardry-forcefield-explosion-list-pruning-native-dispatch-gap-support',S,
 [r('EntityForcefield','onExplosionEvent'),*lookup,*geometry],
 '订阅ExplosionEvent基类，按爆点所在场筛除AffectedBlockPositions异场块中心，并从PlayerKnockbackMap移除异场完整AABB玩家。代码不移除affectedEntities、不取消爆炸、不直接hurt=false。不能从修改knockbackMap推断所有玩家实际免伤；Start/Detonate哪时列表/map已填充需要原生爆炸调度上下文。',
 '世界破坏、爆炸实体受伤和客户端运动包是不同结算面；反馈不应把部分列表筛除等同整次爆炸免疫。',
 '缺固定原生Explosion生命周期，保留支持0；不按blocks/knockback两个集合拆计，不复用013-01重复申请。', ['未读对应版本Forge原生ExplosionEvent发布点，明确不计完整native爆炸免疫链。']))
rows.append(row(13,5,'wizardry-forcefield-custom-hitbox-ray-clipping-without-direction-segment-clamp-support',S,
 [r('EntityForcefield','calculateIntercept'),r('RayTracer','rayTrace'),r('SpellRay','shootSpell')],
 'calculateIntercept投影无限直线到球后始终取near root，没t的0..1裁剪。RayTracer先限定搜索AABB并把endpoint裁到block，再用intercept到origin的正距离小于当前endpoint距离选最近，不核验intercept沿前向；因此并非无任何范围上界，但也不能把距离比较描述为有向线段参数验证。SpellRay shootSpell只在onEntityHit true才缩ray粒子range，false调用onMiss，客户端再画ray。未读取具体射线Spell的onEntityHit/onMiss，不推定最终免伤效果。',
 '几何命中与技能接纳布尔必须分开；拦截体只被raytrace命中不自动意味着拒绝后的视觉可靠。',
 '通用几何/共享分派仅支持0；不把三方法当三处相关游戏机制。与013-01场内伤害判定无独立新增信用。', ['零长度line与球内origin情形仅静态边界，不宣称复现bug或已测试。']))
rows.append(row(13,6,'wizardry-native-magic-arrow-hurt-rejection-consumes-nonpenetrating-projectile-template-support',S,
 [r('EntityMagicArrow','onUpdate'),r('EntityMagicArrow','doOverpenetration'),r('EntityMagicMissile','onEntityHit'),r('EntityMagicMissile','onBlockHit'),r('EntityMagicMissile','tickInAir'),r('SpellArrow','cast',signature='EntityPlayer caster'),r('Spells',span=[267,272]),r('WizardryEntities',span=[110,110])],
 '完整onUpdate：disableDamage或玩家canAttackPlayer拒绝的Player直接清raytraceresult，弹体穿过而不hurt；其它命中调用attackEntityFrom，true才onEntityHit/knockback/附魔及PvP命中包。false且非overpenetration仍setDead，旧反弹代码是注释不得算实现；true对Enderman保留弹而false没有该例外。MagicMissile onEntityHit声音/FLASH只在本地该hurt布尔true时进入；tickInAir轨迹此前已经绘制。实体onUpdate没有通用server-only包住hurt，不能把本地client布尔说成服务端认证收据。',
 '免疫false、玩家预筛选穿透与伤害成功应分别反馈；弹体消失不是伤害成功证据，轨迹也不是命中成功。',
 '大量onUpdate来自原版箭模板且主账已有MPS真实hurt门控副作用；未建立足够独立机制，明确支持0。不按不同元素箭/每个hurt分支再计数。', ['保留完整502行之前的onUpdate正文范围及实际Missile注册，不声称Minecraft原生模板已独立逐字对照。', '无真实客户端/网络/运行测试，不能声称服务器会同步专有成功命中粒子。']))
rows.append(row(13,7,'wizardry-decoy-unconditional-invulnerability-with-owner-and-lifetime-teardown-support',S,
 [r('EntityDecoy','isEntityInvulnerable'),r('EntityDecoy','onUpdate'),r('EntityDecoy','onDespawn'),r('Decoy','spawnDecoy'),r('Decoy','cast',signature='EntityPlayer caster'),r('EntitySummonedCreature','onUpdate'),r('ISummonedCreature','getCaster'),r('ISummonedCreature','updateDelegate'),r('EntityUtils','getEntityByUUID'),r('WizardryEntities',span=[94,94]),r('Spells',span=[412,412])],
 'Decoy实体isEntityInvulnerable无条件true（包含任何source入参），不是按amount扣血；原生damage消费者未在此缓存链中重读，所以不推断void等最终原生特例。Decoy spell服务端spawn并设lifetime，扫描16范围内正攻击caster的Mob按chance*potency改目标Decoy，caster横移两侧都执行。父updateDelegate超时onDespawn+setDead，子onUpdate owner UUID在当前world找不到或dead亦setDead+onDespawn。青色20DUST只在onDespawn客户端路径，不是免伤命中提示。',
 '无敌诱饵可吸收AI注意，但生命周期结束粒子不能当作每次Boss免疫回执；owner失效与原生伤害拒绝是不同原因。',
 '简单无条件override及生命周期支持，不够独立完整免疫消费链，支持0；不与旧Iron FrozenHumanoid一次受击自爆混为同机制，亦不自动+1。', ['原生EntityLivingBase.attackEntityFrom对isEntityInvulnerable的精确调用位置未读，保持缺口。', 'onDespawn可能经父寿命与子owner分支重复调用；仅静态观察，不声称实际重复视觉复现。']))
print(json.dumps(E.finish(rows),ensure_ascii=False))
