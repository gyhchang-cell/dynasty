"""Manually authored observations from complete methods read in this continuation."""
from reference_evidence import Evidence, row
import json

PENDING = 'pending_primary_semantic_review'
SUPPORT = 'support_only_not_effective'
W = 'TeamLapen__Werewolves'
R = 'CoFH__RedstoneArsenal'
F = 'stal111__Forbidden-Arcanus'

def batch010():
    e = Evidence(10)
    r = lambda file, method=None, **kw: e.ref(W,file,method,**kw)
    registered = [r('WerewolvesMod','WerewolvesMod'),r('WerewolvesMod','setup')]
    incoming = lambda focus: r('ModPlayerEventHandler','onEntityIncomingDamage',focus=focus)
    rows = []
    rows.append(row(10,1,'werewolves-transformed-fur-tag-skill-conjunctive-native-incoming-denial',PENDING,
        [incoming([210,212]),*registered,r('WerewolfPlayer','get'),r('WerewolfPlayer','getForm')],
        '原生LivingIncomingDamage的受害者必须Player且Helper.isWerewolf；WEREWOLF_FUR_IMMUNE来源tag、当前form.isTransformed与WOLF_PAWN技能三者同时成立才cancel。没有声音、粒子、文字或按目标冷却。该if后没有return，因此仍继续本方法的SURVIVALIST随机分支；不能把cancel当整条函数立即退出。',
        '对拒伤原因明确标记条件组合；普通体质/技能拒伤不等同Boss免控，也不要求生成Boss灰字。',
        '同一完整206..228方法内210..212为本条固定焦点；下一条214..226是不同的运动概率决策，不按来源tag成员/技能常量拆。Russell可合并；本助手credit0。',
        ['WEREWOLF_FUR_IMMUNE数据tag成员、Helper.isWerewolf及技能获取实现缺固定缓存，不声称具体火/落伤列表或生存可达性。', '事件注册入口setup完整已读；没有真实运行拒伤验收。']))
    rows.append(row(10,2,'werewolves-survivalist-motion-conditioned-two-stage-dodge-no-clamp',PENDING,
        [incoming([214,226]),*registered,r('WerewolfPlayer','getForm')],
        'SURVIVALIST形态：速度向量lengthSqr>0.01、ARROW_AWARENESS技能、精确DamageTypes.ARROW且random<0.4时cancel。else-if绑定整个箭条件（含roll），所以箭roll失败后仍可进入疾跑+有causing entity+MOVEMENT_TACTICS的第二次roll；第二门chance为配置+已装备refinement加值，代码不clamp。非Player、不在形态或其它来源不自动免疫。',
        '多阶段拒绝的原因/反馈必须跟最终实际分支一致，不能把箭40%误写成全部命中最终40%；动作状态和攻击来源要参与权威判定。',
        '同一containing方法保留固定214..226焦点；箭/疾跑两子roll合并一个运动闪避策略，不拆成2。与上一条稳定tag门不同，是否独立最终由主岗判断。',
        ['配置实际值、获取/同步技能链未缓存，不能给出第二门默认概率或已测合成概率。', '没有源类型标签泛化到所有投射物；没有拒伤声光/灰字实现。']))
    rows.append(row(10,3,'werewolves-bite-result-qualifies-stun-attempt-and-cooldown-before-effect-acceptance',SUPPORT,
        [r('WerewolfPlayer','bite',signature='int entityId'),r('WerewolfPlayer','bite',signature='LivingEntity entity'),
         r('WerewolfPlayer','canBite'),r('WerewolfPlayer','canBiteEntity'),r('WerewolfPlayer','onUpdate'),
         r('StunEffect','applyEffectTick'),r('StunEffect','shouldApplyEffectTickThisTick'),
         r('ModKeys','handleInputEvent'),r('ClientEventHandler','onZoomPressed'),r('ClientEventHandler','onFOVModifier')],
        '同level整数entityId解析Living后，bite检查biteTicks/形态/等级/spectator/玩家权限与距离（BLOCK_INTERACTION_RANGE+1）。DamageHandler.hurtModded返回flag为true才发两类bite声、写biteTicks、尝试STUN/BLEEDING并同步；addEffect返回值忽略。Stun每tick将XZ清0、Y设min(0,Y)，不是全轴冻结。onUpdate仅level>0时两侧biteTicks减1。客户端原生按键发ServerboundBiteEventPackage后立即onZoomPressed；FOV20次回调衰减，与服务端flag无确认关联。',
        '受伤flag、状态接纳、控制生效、声音和客户端预测视野必须分开；付冷却不证明眩晕被Boss接纳。仅静态阅读视野代码，未操作camera。',
        'MPS009已有原生hurt布尔门控副作用家族；本链因缺原版本DamageHandler/实际C2S handler/效果注册，保留支持0，不将Stun与Bleeding两个常量各算1。',
        ['Vampirism缓存是另版本/包路径，不能桥接冒充此固定提交DamageHandler全文。', '没有C2S网络执行/实际镜头变化证明；不声称flag必然等于原生HP损失。']))
    rows.append(row(10,4,'werewolves-fear-direct-native-ai-reset-without-status-denial-chain',SUPPORT,
        [r('FearAction','activate'),r('FearAction','getCooldown'),r('FearAction','isEnabled')],
        'Fear activate扫描以玩家blockPos构造AABB外扩10,3,10中的Mob，排除Helper.isWerewolf；对每个直接setTarget(null)、navigation.stop，再按离玩家格子向量*3生成逃跑path并moveTo(1.7)。不调用addEffect/hurt，不查Boss标志/LOS/成功path；无目标也return true。getCooldown配置秒*20。',
        '仅否决药水无法阻止直接改AI目标/导航的控制。有效控制成功回执不能从activate true推断。',
        '属于直接AI控制辅助上下文；本缓存无ModActions/DefaultWerewolfAction完整激活入口，不当完整已闭链有效参考。',
        ['不能证明实际Boss具备可用navigation或会维持逃跑；未运行。', '框架和注册缺失保留0，不按每Mob/向量常量拆数。']))
    rows.append(row(10,5,'werewolves-sixth-sense-integer-id-alert-suppression-lifetime-support',SUPPORT,
        [r('ModEntityEventHandler','onTargetChange'),r('ClientPayloadHandler','handleAttackTargetEventPacket'),
         r('ModHUDOverlay','attackTriggered'),r('ModHUDOverlay','handleScreenColorWerewolf'),
         r('ModHUDOverlay','onClientTick'),r('ModHUDOverlay','onRenderWorldLast'),
         r('WerewolvesModClient','WerewolvesModClient'),*registered],
        '原生newAboutToBeSetTarget是ServerPlayer且狼人有SIXTH_SENSE时，发攻击者整数id。客户端callback enqueueWork→attackTriggered，仅首次id入list；waitTicks==0才screenPercentage100/waitTicks100/橙色。每tick有技能则percentage减10、wait减1，wait归零不清id，因此同id不会再触发；冷却中其它新id也先入list且不闪。技能消失/玩家null或死/不再Werewolf清列表。RAGE可覆盖红色。GUI Pre画上下gradient，非世界目标文字。',
        '提示限流与对象去重寿命要分别设计；整数id复用/旧警告不能误关联新Boss。',
        '并非免疫回执或战斗文字；且packet codec/注册不在缓存，只作具体战斗反馈生命周期支持0，不计网络包装。',
        ['没有特定世界切换清理hook；若切换经过null player可清，但不能声称始终跨维安全。', '不声称完整S2C实际通路或已观察视觉；attackTargetScreenPercentage不是这里实际触发的字段。']))
    rows.append(row(10,6,'werewolves-weakening-applicable-source-type-check-unresolved-api-support',SUPPORT,
        [r('ModEntityEventHandler','onWerewolfWeakeningEffectApplied'),*registered],
        '实际Applicable listener写的是event.getEffectInstance().getEffect() instanceof WerewolfWeakeningEffect且!Helper.isWerewolf(target)时DO_NOT_APPLY。仅记录源码字面表达式；没有把getEffect包装类型擅自换成value，也未看到WerewolfWeakeningEffect完整类。',
        '最终效果接纳门要以实际API对象与最终拒绝原因核验；不能仅搜索DO_NOT_APPLY就认定已能运行。',
        'API/效果类缺失，明确不计真正生效拒控实现；不以名字猜成所有非狼都免疫眩晕。',
        ['未编译该历史模组，不判API兼容性通过/失败；不修改外部代码。']))
    return e.finish(rows,[dict(reason='Halley批001已研究WerewolfTooth感染拒绝，本轮避开，不再次研究申请信用。',credit=0)])

def batch011():
    e = Evidence(11)
    r = lambda file, method=None, **kw: e.ref(R,file,method,**kw)
    reg = [r('ModItems','register'),r('RedstoneArsenal','RedstoneArsenal'),r('RedstoneArsenal','capSetup')]
    energy = [r('IFluxItem','getEnergyPerUse'),r('IFluxItem','hasEnergy',signature='int amount'),
        r('IFluxItem','useEnergy',signature='int amount, boolean simulate'),
        r('IFluxItem','useEnergy',signature='boolean empowered, @Nullable Entity entity'),r('IMultiModeFluxItem','isEmpowered')]
    rows = []
    rows.append(row(11,1,'rsa-capability-shield-special-flux-block-source-and-defense-precedence',PENDING,
        [r('FluxShieldItem','canBlock'),r('FluxShieldItem','onBlock'),r('FluxShieldItem','onUseTick'),*reg,*energy],
        '实际FluxShieldItem注册Core ShieldHandler能力包装。canBlock先IShieldItem.super.canBlock true便直接true；只有父接口false时才检查target.isBlocking、target.isInvulnerableTo、火源+火抗拒绝；之后仅msgId精确flux且canBlockDamagePosition才true。onBlock可先empowered repel；amount>=3且非creative才按min(库存,ceil(amount)*500)循环抽能，最后原样return amount，不能把onBlock返回值描述为零伤。onUseTick无2000能量就releaseUsingItem。',
        '特殊伤害盾资格必须保留父策略的短路优先级；已经无敌/火抗的命中与真的盾挡应在反馈原因上分开。',
        '不同于旧主账FluxArmor消耗charge cancel的结算链；本条是shield capability的特殊源资格门，onBlock抽能/包装合并支持。',
        ['CoFH IShieldItem/ShieldItemCoFH原生最终调度与canBlockDamagePosition内部未缓存，不声称所有方向/伤害最终数值已闭合。', '父接口true先于子类否决，不能把后续条件说成所有成功盾挡必需条件。', '无游戏/网络验收，待Russell判语义有效性。']))
    rows.append(row(11,2,'rsa-shield-paid-repel-before-block-admission-with-two-motion-paths',PENDING,
        [r('FluxShieldItem','use'),r('FluxShieldItem','repel'),r('FluxShieldItem','getRepelRange'),
         r('FluxShieldItem','getRepelStrength'),r('FluxShieldItem','onBlock'),*energy,*reg],
        '原生use只要empowered就先尝试repel，随后才hasEnergy(true)决定super.use或FAIL；非creative正常配置若恰2000能量，repel可花2000后block入口失败。repel成功付费后扫描AABB(range=4)并严格distanceSqr<16，排creative/spectator，未查盟友/Boss/LOS/药水资格。Living走原生knockback(strength1.5,-dx,-dz)；非Living覆写normalize(dir)*strength并hasImpulse=true。无目标也先付费；onBlock也可再次调用repel。',
        '动作入口失败不代表之前控制没发生；拒控须覆盖直接运动入口和受伤前副作用，不能只拦addEffect。',
        '与上一条特殊伤害盾资格不是同一个决策：本条甚至可在use最终FAIL前独立发生；Living/非Living两运动分支合并一个producer，不按xyz/目标类型拆。',
        ['外部getEnergyStored/extractEnergy及creative判定内部未全读；恰2000示例限定普通非creative且只执行一次该方法，不宣称双端实测。', 'Living原生knockback内部抗性未读，不声称无视击退抗性；非Living也不等于所有Boss能被移。', '该类use/repel没有本地server side门；不声称已排除预测重放。']))
    rows.append(row(11,3,'rsa-sickle-prehurt-knockback-and-eligibility-not-accepted-hit-budget',PENDING,
        [r('FluxSickleItem','onLeftClick'),r('FluxSickleItem','onLeftClickEntity'),
         r('FluxSickleItem','getSweepHitBox'),r('FluxSickleItem','hurtEnemy'),*reg,*energy],
        '左击consumer要求strength>=.9、非sprint/secondaryUse、能量>=500。枚举SweepHitBox的Living，跳过本人/盟友/empowered幼体/marker盔甲架/不可reach。通过资格就hit=true，先knockback(.3)，再playerAttack hurt且不看bool。只要至少一合格对象就抽一次能，声和sweepAttack即使没有对象也执行。onLeftClickEntity在empowered且幼体时返回true；不与扫击资格混为实际hurt接纳。',
        '最终hurt=false不能撤回先行位移；命中预算/付费按候选资格而非实际受伤，免疫回执不可从hit局部变量猜。',
        '与008 SpellEngine伤害忽略bool后offset位移及009 MPS hurt true门同题，明确存在语义合并风险。不同时间点/nativeknockback是否足够独立由Russell决定，绝不自动+1。',
        ['ILeftClickHandlerItem外部原生输入/事件调度未缓存；不声称实际C2S链已验。', '不按候选筛选常量/幼体变种或每目标各计。']))
    rows.append(row(11,4,'rsa-existing-flux-charge-full-chain-duplicate',SUPPORT,
        [r('RSAEvents','handleLivingAttackEvent'),r('RSAEvents','handleLivingHurtEvent'),
         r('FluxShieldingHelper','findShieldedItem'),r('FluxShieldingHelper','onUseFluxShieldCharge')],
        '全文重核与主账redstonearsenal-native-charge-shield-refusal-with-break-cue-and-self-hud一致：<=500且有charge的Attack拒伤/10tick，Hurt另减500，Curios代码注释，charge消耗声/红尘同链。已有记录还包含完整wrapper/HUD，不能拿发现的新方法包装再申请信用。',
        '旧记录直接作为去重锚点，保留0而非重新拆按伤量/部件计数。',
        '明确主账既有完整链，重复0。', ['本轮仅重新阅读上述完整方法；不声称重新跑过旧链全部动态验收。']))
    rows.append(row(11,5,'rsa-hammer-shockwave-parent-native-hit-consumer-missing',SUPPORT,
        [r('FluxHammerItem','useOn'),r('FluxHammerShockwave','onHit'),r('FluxHammerShockwave','getDamageSource')],
        'hammer useOn地面/empowered/足能前门，client先破块声；server addFreshEntity成功才扣能/加160CD，无论add结果最终SUCCESS。Shockwave.onHit只给living owner力量70tick；getDamageSource按owner Player/Living/其它选PLAYER_ATTACK/MOB_ATTACK/IN_WALL。',
        '生成成功、真正击中、受害者接纳和owner增益四者不能凭同一声/boolean互换。',
        'CoFH Shockwave父实体原生tick/碰撞不在缓存，onHit调度是否要求hurt true未读，支持0；原生伤害source常量不拆数。',
        ['不宣称owner增益已证明实际伤害发生；不声称击中Boss触发拒控。']))
    return e.finish(rows)

def batch012():
    e = Evidence(12)
    r = lambda file, method=None, **kw: e.ref(F,file,method,**kw)
    rows = [row(12,1,'forbiddenarcanus-catcher-final-type-denial-before-entity-discard-control',PENDING,
        [r('PlayerEvents','onEntityInteract'),r('QuantumCatcherItem','onEntityInteract'),
         r('QuantumCatcherItem','isValidEntity'),r('QuantumCatcherItem','calculateAurealCost'),
         r('QuantumCatcherItem','useOn'),r('QuantumCatcherItem','summonEntity'),r('QuantumCatcherItem','playSound'),
         r('QuantumCatcherItem','getData'),r('ModItems',span=[79,81]),
         r('ModEventHandler','registerForgeEvents'),r('ForbiddenArcanus','ForbiddenArcanus')],
        '注册普通/染色catcher和BOSS_CATCHER均同类、仅注入不同blacklist tag。原生EntityInteract handler无条件cancel并把result设为item调用结果；item先算cost，再invalid(blacklisted或不alive)/已有stored→PASS，不足资源→FAIL。通过才服务端存StoredEntity、若多件先consume并给新普通catcher（满包drop），target.discard后cost.consume；sound在两侧成功分支外。cost按maxHealth四舍五入，friendly右移1，其它乘1.1取int。放出时server createEntity或落点不可replace则FAIL；addFreshEntity返回忽略，之后移除stored组件并true。',
        '明确的最终类型拒绝与资源不足应分原因；捕获直接discard不经过伤害/药水免疫，Boss拒控审查需考虑这类旁路。物品PASS也可能被外层事件cancel；release成功声不证明服务端生成已接纳。',
        '普通/颜色/Boss catcher只是同一policy输入tag变体，合计一条；捕获/放出/声音包装合并完整生命周期不拆。主账本轮无Forbidden-Arcanus记录。',
        ['blacklist JSON成员、StoredEntity.create/of内部和EssenceCost.hasEnough/consume缺固定缓存，不能声称具体Boss名单/跨维保真/扣费原子性。', '阴阳体/本项目Boss无需自动兼容此外部模组；没有实施修复。', 'sound release布尔在捕获调用传true、放出传false；按实际分支记录，不凭资源名猜意思。', '仅固定版本静态观察，不声称捕获/放出实机通过。']),
      row(12,2,'forbiddenarcanus-post-health-damage-blood-resource-support',SUPPORT,
        [r('EntityEvents','onEntityDamage'),r('ModItems',span=[103,104])],
        'LivingDamageEvent.Post仅精确PLAYER_ATTACK且causing Player、目标不在TEST_TUBE_BLACKLISTED时，若offhand空试管先换成血试管；随后offhand是RECEIVES_BLOOD才EssenceStorage.addEssence((int)(20*getHealthDamage()))。方法没有先检查healthDamage>0才换瓶。',
        '资源数值来自实际HealthDamage字段，与普通hurt尝试反馈区分；换容器本身仍不是成功伤害的充分证据。',
        '不是免控拒绝生产或战斗文字链，且EssenceHelper内部缺失，保留支持0，不因不同黑名单再计一条。',
        ['不声称0伤害一定进入Post事件；只读完整listener条件，未运行外部版本。'])]
    return e.finish(rows)

if __name__ == '__main__':
    for run in [batch010,batch011,batch012]:
        print(json.dumps(run(),ensure_ascii=False))
