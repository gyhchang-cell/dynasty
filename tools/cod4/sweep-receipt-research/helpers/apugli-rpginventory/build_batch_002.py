"""Package manually reviewed Apugli batch 002 from the pinned local cache only."""
import datetime
import hashlib
import json
import pathlib
import runpy

HERE = pathlib.Path(__file__).resolve().parent
BASE = runpy.run_path(str(HERE / 'build_batch.py'))  # our own local evidence helper, not downloaded code
WORKSPACE, ROOT, DOCS = (BASE[k] for k in ('WORKSPACE', 'ROOT', 'DOCS'))
PIN, REPO, method = (BASE[k] for k in ('PIN', 'REPO', 'method'))
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
PRIOR_FILES = ['batch-001.json', 'auxiliary-reviewed.json', 'scope-pending-reviewed.json',
               'reviewed.jsonl', 'HANDOFF.md', 'handoff.json', 'validation.json', 'source-index.json']
PRIOR_HASHES = {name: hashlib.sha256((DOCS / name).read_bytes()).hexdigest() for name in PRIOR_FILES}
PRIOR_ROWS = [json.loads(line) for line in (DOCS / 'reviewed.jsonl').read_text().splitlines()]
ROWS = []


def add(key, specs, observation, application, limits, basis, valid=True, duplicate_of=None):
    evidence = [method(*s) for s in specs]
    row = dict(evidence[0])
    row.update(candidate_id='apugli-rpginventory-002-' + key, chain_id=key, batch='002',
               status='reviewed', decision='reviewed_valid_pending_carson' if valid else 'reviewed_excluded_zero_credit',
               requested_repo='MerchantPug/Apugli', canonical_repo=REPO,
               proposed_credit=int(valid), credit=0, final_count_owner='Carson', reviewed_at=NOW,
               observation=observation, application=application, limits=limits, scope_basis=basis,
               evidence=evidence, duplicate_of=duplicate_of,
               dedup_key=f'{REPO}:{key}', external_runtime_tested=False,
               counting_unit='Entire gameplay state lifecycle; wrappers, callbacks, cleanup paths and mirrors share one unit.')
    ROWS.append(row)


add('durability-slot-reentrancy-window', [
    ('common:power/ActionOnDurabilityChangePower', 'private void executeAction(', 'reserve slot before user callbacks'),
    ('common:power/ActionOnDurabilityChangePower', 'public void tick()', 'expire the entire dedup set at the next power tick'),
    ('common:power/ActionOnDurabilityChangePower', 'public void onRemoved()', 'clear on power removal'),
    ('common:power/ActionOnDurabilityChangePower', 'public boolean doesApply(', 'equipment/item condition'),
    ('common:power/ActionOnDurabilityChangePower', 'public void executeIncreaseAction(', 'same lifecycle wrapper'),
    ('common:power/ActionOnDurabilityChangePower', 'public void executeDecreaseAction(', 'same lifecycle wrapper'),
    ('common:power/ActionOnDurabilityChangePower', 'public void executeBreakAction(', 'same lifecycle wrapper'),
    ('common:mixin/xplatform/common/ItemStackMixin', 'private int apugli$captureDamageValue(', 'pre-change amount snapshot'),
    ('common:mixin/xplatform/common/ItemStackMixin', 'private void apugli$executeDurabilityChangeActions(', 'post-change action selection'),
    ('fabric:platform/FabricPlatformHelper', 'public Entity getEntityFromItemStack(', 'item linked entity lookup')],
    'ItemStack.setDamageValue在HEAD读取旧Damage并可能修改输入，TAIL按新旧差选择耐久增减/损坏动作。每个ActionOnDurabilityChangePower.executeAction先按stack对象引用找EquipmentSlot或玩家背包索引；若该槽已在operatedStacks便返回。将Either槽键加入Set发生在entityAction/itemAction之前，抑制动作自己再次改耐久导致的同槽递归；tick和onRemoved清整个Set。三个动作包装合并计一。',
    '真实物品玩法中先登记再回调的短生命周期去重，可借鉴方天在执行二次伤害前标记或移走回执，避免自身事件重入。清理相位必须明确，不能只要求消费时仍等于产生tick。',
    '窗口由power.tick清理决定，未标记绝对gameTime，不能保证ServerTick.END边界；按槽位而非物品UUID/攻击ID，同槽换物也会被抑制，不同power各有Set。无server侧检查、维度快照和try/finally；回调失败后槽键仍占用到清理。旧Damage字段位于ItemStack实例且可被嵌套setDamageValue覆盖；TAIL参数与最终NBT/clamp结果不一定等同。',
    '实际耐久事件→回调前保留一次操作证据→下一power tick/移除清理；新增状态表，未出现在batch001。')

add('explosion-parameter-consumption-and-effect-task', [
    ('common:mixin/xplatform/common/ExplosionMixin', 'private float apugli$changeDamage(', 'consume damage modifiers then null'),
    ('common:mixin/xplatform/common/ExplosionMixin', 'private double apugli$modifyOtherEntitiesKnockbackX(', 'same knockback parameter group'),
    ('common:mixin/xplatform/common/ExplosionMixin', 'private double apugli$modifyOtherEntitiesKnockbackY(', 'same knockback parameter group'),
    ('common:mixin/xplatform/common/ExplosionMixin', 'private double apugli$modifyOtherEntitiesKnockbackZ(', 'clear after final component'),
    ('common:mixin/xplatform/common/ExplosionMixin', 'private float apugli$reduceVolumeOfRocketJump(', 'consume volume once'),
    ('common:mixin/xplatform/common/ExplosionMixin', 'private float apugli$increasePitchOfRocketJump(', 'pitch deliberately not cleared in this implementation'),
    ('common:mixin/xplatform/common/ExplosionMixin', 'private boolean apugli$cancelDamagedEntity(', 'source/target predicate before explosion hit'),
    ('common:action/factory/entity/ExplodeAction', 'public void execute(', 'server gameplay action entry'),
    ('common:action/factory/entity/ExplodeAction', 'protected void summonExplosion(', 'write explosion instance parameters and send effect packet'),
    ('common:action/factory/entity/ExplosionRaycastAction', 'public void execute(', 'alternate raycast origin; zero extra credit'),
    ('common:action/factory/entity/ExplosionRaycastAction', 'protected void summonExplosion(', 'same parameter family at a hit position'),
    ('common:power/factory/RocketJumpPowerFactory', 'default void executeJump(', 'real rocket-jump target producer'),
    ('common:power/factory/RocketJumpPowerFactory', 'default void handleRocketJump(', 'same explosion consumer family'),
    ('common:network/s2c/SyncExplosionPacket', 'public void handle()', 'deferred client task: finalize only'),
    ('common:network/s2c/SyncExplosionPacket', 'private <C> ExplosionDamageCalculator createBlockConditionedExplosionDamageCalculator(', 'captured-world block condition consumer')],
    'ExplodeAction、ExplosionRaycastAction和RocketJump创建单个Explosion，先写damage/knockback/volume/pitch与source-target条件再explode/finalize。ExplosionMixin在第一个伤害参数拦截中apply后把damage列表置null；击退X/Y仍读取列表，Z读取后置null；音量消费后置null，pitch未清。实际SyncExplosionPacket收到后排Minecraft.execute，在执行时按userId解析当前level实体，重建Explosion并只finalizeExplosion(true)，没有客户端再次explode。所有入口、参数组、客户端任务合并一条。',
    '借鉴一次性状态绑定到实际玩法任务实例，以及权威伤害结算和延后表现的分离。参数已消费与参数为空应能区分；对回执需在约定消费点消耗一次，而不是让后续目标意外丢失。',
    '伤害列表第一次hurt拦截即清，可能只修饰首个受害者；这是一项限制而非保证整次爆炸正确。apply抛异常时清空未发生；pitch不清，不能宣称全部字段严格一次消费。客户端用数字ID和当前level，无原始维度/UUID/level-null/TTL保护；包中hasCalculator在handle未作分支。直接source为空时target条件检查被跳过。三种爆炸起点不是三个credit；服务器和客户端也不是两个。',
    '实际爆炸玩法的一次性参数消费与延后表现任务，非通用传输库；全家族只计一。')

add('fatal-damage-snapshot-to-kill-credit', [
    ('fabric:mixin/fabric/common/LivingEntityMixin', 'private void apugli$captureDamageAmount(', 'capture before hurt calls die'),
    ('fabric:mixin/fabric/common/LivingEntityMixin', 'private void apugli$runActionsOnTargetDeath(', 'later die-hook actor selection'),
    ('common:power/factory/ActionOnTargetDeathPowerFactory', 'default void onTargetDeath(', 'prime-adversary filter and cooldown settlement')],
    'hurt调用die之前将amount放入受害实体的apugli$damageAmountOnDeath；die后续注入在服务端读取该字段。source实体与getKillCredit不同且killCredit存在时优先采用killCredit并传primeAdversary=true后return；否则仅接受source.getEntity为LivingEntity的路径。onTargetDeath筛选includes_prime_adversary，再检查actor-target和damage条件，执行后use冷却。',
    '借鉴在原事件仍持有上下文时保存实际参数，供后续结算入口使用；直接伤害来源与历史击杀归属是两种身份，不能把killCredit当作当前directActor。将源证据时间和消费入口关联比依赖全局当前tick更明确。',
    '该延后发生在同一同步hurt→die调用链，不能宣称已演示跨tick排队。amount字段没有epoch/attack ID、清零或一次消费标志；由其他入口直接die、重入或历史值残留的情况未保护。use在动作之后，异常/递归可能绕过冷却；无UUID/维度快照和短TTL。batch001审阅的是hurt RETURN命中表，本条不重复计算该命中表或RETURN分派。',
    '真实致死伤害上下文跨两个事件阶段消费，并区分直接来源/历史归属；与命中历史TTL不同的字段和终止事件。')

add('placed-block-pending-action-pair', [
    ('common:mixin/xplatform/common/BlockItemMixin', 'private void apugli$onPlaced(', 'choose and store pending power/state pair'),
    ('common:mixin/xplatform/common/BlockItemMixin', 'private void apugli$executeActionAfterPlaced(', 'later place hook consumes pair and nulls it'),
    ('common:power/ModifyBlockPlacedPower', 'public void executeAction(', 'actual pending block-action consumer'),
    ('common:power/ModifyBlockPlacedPower', 'public void generateSeed()', 'advance/sync selection seed'),
    ('common:power/ModifyBlockPlacedPower', 'public void fromTag(', 'seed persistence, no extra credit'),
    ('common:power/ModifyBlockPlacedPower', 'public Tag toTag()', 'same seed persistence'),
    ('common:power/ActionOnBlockPlacedPower', 'public void executeAction(', 'separate immediate action in same placement entry; zero extra credit')],
    'placeBlock HEAD根据玩家、heldItem条件构造power/state候选，用首个power的seed选中一对并暂存BlockItemMixin.pair，更新seed后用setBlock返回值替代原placeBlock结果。后续place内获取clickedPos处，若pair非null便调用选中power.executeAction(Optional.of(pos))，随后pair=null。seed可NBT读写，但pending pair不持久化。',
    '借鉴产生事件中先确定实际被选中的实现与状态，再由后续阶段消费该结果并清空；回执需要明确拥有者与目标，避免后续消费重新随机或依赖当前装备。',
    '这是方块玩法跨方法暂存，非跨tick调度；字段挂在BlockItem实例，没有按player/position/level隔离。setBlock失败也可能已写pair，某些退出路径是否到达消费注入未经运行证明；动作异常会跳过pair=null。动作使用power.entity.level和稍后context.pos，无原始维度/位置快照复核。前置ACTION_ON_BLOCK_PLACED早于成功确认，不能把它当成功回执。',
    '实际placeBlock产生、place后续阶段一次消费的pending状态；与batch001 schedule_tick方块调度是不同状态及调用链。')

add('enchantment-damage-phase-guard', [
    ('fabric:mixin/fabric/common/LivingEntityMixin', 'private float apugli$modifyDamageBasedOnEnchantment(', 'HEAD direct-source gate and boolean snapshot'),
    ('fabric:mixin/fabric/common/LivingEntityMixin', 'private void apugli$preventHitIfDamageIsZero(', 'later hurt phase reads snapshot and rejects'),
    ('common:power/factory/ModifyEnchantmentDamagePowerFactory', 'default boolean doesApply(', 'damage/pair/mainhand-enchantment guards'),
    ('common:power/factory/ModifyEnchantmentDamagePowerFactory', 'default float applyModifiers(', 'real damage modifier and callback loop'),
    ('common:power/factory/ModifyEnchantmentDamageDealtPowerFactory', 'default float applyModifiers(', 'dealt wrapper; merged'),
    ('common:power/factory/ModifyEnchantmentDamageTakenPowerFactory', 'default float applyModifiers(', 'taken wrapper; merged')],
    'hurt HEAD仅在source.getEntity为LivingEntity且source.getDirectEntity()==attacker时加入dealt附魔修饰；taken修饰仅要求attacker为LivingEntity。方法将是否改变原伤害写入实体级apugli$hasModifiedDamage，并返回新值；稍后hurt调用isSleeping处的注入在hasModifiedDamage且amount==0时setReturnValue(false)。工厂还要求damage/bientity条件和攻击者当前主手有对应附魔。dealt/taken映射共享同一工厂，整链合一。',
    '借鉴明确检查直接来源，避免投射物/间接actor被当原生近战；后续阶段以先前结果决定拒绝，而不是仅检查玩家手持物。回执应保存本次攻击来源证据和最终成功结果。',
    '同步hurt内分阶段消费布尔字段，不证明跨tick；无回执ID/UUID/维度或TTL，重入hurt可能覆盖共享hasModifiedDamage。附魔/主手在当下读取并非触发时快照，crit可在实际伤害成功前发送；动作也在工厂循环内发生，不能证明health减少。后续amount==0拒绝不等于所有0伤害都拒绝。',
    '真实战斗direct-source身份门与跨阶段状态消费；非两个模板wrapper credit，与batch001 hurt RETURN命中表不重算。')

add('weather-target-registry-lifecycle', [
    ('common:power/RedirectLightningPower', 'public void onAdded()', 'register per-living-entity aggregate chance'),
    ('common:power/RedirectLightningPower', 'public void onRemoved()', 'recompute/remove registered target'),
    ('common:mixin/xplatform/common/ServerWorldMixin', 'private void apugli$captureSkeletonHorseSpawn(', 'capture event phase flag'),
    ('common:mixin/xplatform/common/ServerWorldMixin', 'private Vec3i apugli$redirectLightningToPowerHolder(', 'later world tick consumes registered target list')],
    'RedirectLightningPower.onAdded把该LivingEntity所有同类power机会之和存进静态STRUCK_BY_LIGHTNING_CHANCES；onRemoved重算，总和0时移除。ServerLevel.tickChunk先捕获骷髅马分支布尔，稍后雷击位置参数回调在非该分支时按机会降序遍历登记实体，当前world判isRainingAt其坐标并随机命中后返回目标坐标。',
    '借鉴实际事件稍后消费的目标登记表需要配套解除注册，并同时验证目标所属世界；仅保存活Entity引用和坐标不足以保证换维度后来源仍正确。跨事件暂存布尔也需按调用/任务隔离。',
    '不是一次消费攻击队列，登记会持续用于多个天气事件；无TTL、UUID键、isAlive/isRemoved或entity.level==this检查。表是跨世界静态全局，当前world只检查外部实体坐标是否下雨，不能等同维度校验。onRemoved时getPowers是否已排除自身由外部power生命周期决定；断线/卸载移除未证实。',
    '真实模组世界tick雷击玩法对已登记目标的延后使用及移除生命周期；非通用缓存。')

add('crawling-state-and-deferred-pose', [
    ('common:power/CrawlingPower', 'public void onAdded()', 'register transient player state'),
    ('common:power/CrawlingPower', 'public static void tickOnceForge(', 'later living tick applies/reverts pose on edges'),
    ('common:power/CrawlingPower', 'public void onRemoved()', 'last-power removal clears map and pose'),
    ('common:power/CrawlingPower', 'private static void setWasActive(', 'same transition storage'),
    ('common:power/CrawlingPower', 'public static boolean wasActive(', 'same transition read'),
    ('neoforge:ApugliForgeEventHandler', 'public static void onLivingTick(', 'real gameplay tick entry'),
    ('neoforge:platform/ForgePlatformHelper', 'public void setForcedPlayerPose(', 'authoritative pose change and actual packet producer'),
    ('neoforge:network/s2c/ForcePlayerPosePacket', 'public void handle()', 'deferred client task with Player-type validation')],
    '爬行power在onAdded为Player建立WAS_ACTIVE=false；LivingTick调用tickOnceForge，在滑翔/睡眠/旋转等冲突状态回退姿势，否则由是否持有CRAWLING与wasActive边沿选择设置SWIMMING或清除。onRemoved在最后同类power条件下移除表项并按旧状态清姿势。ForgePlatformHelper真正修改服务端forced pose，并发送ForcePlayerPosePacket；客户端Minecraft.execute排队后按entityId找Player并应用。服务端状态机和客户端消费合并一条。',
    '借鉴登记、边沿执行、最后持有者移除与冲突中止的完整瞬态状态生命周期；延迟执行前至少验证消费对象类型，回执还需原始UUID/维度及攻击身份。',
    '不是战斗伤害回执，相关性是实际玩法延后任务/生命周期。WAS_ACTIVE以Entity引用全局保存，无TTL或维度键；wasActive直接拆箱可能在缺项时异常，remove也会拆箱。最后power数量减1依赖回调时机；姿势包无序列/代次/UUID/维度/level-null保护，旧姿势任务可能晚于新状态应用。',
    '实际爬行玩法状态驱动并由已证实producer产生延后姿势任务；不把S2C镜像另计。')

add('block-condition-event-invalidation-lifecycle', [
    ('common:condition/factory/entity/CachedBlockInRadiusCondition', 'public boolean check(', 'gameplay query and usage-age cleanup'),
    ('common:condition/factory/entity/CachedBlockInRadiusCondition', 'public static boolean getReturnValue(', 'consume cached nearby-block evidence'),
    ('common:condition/factory/entity/CachedBlockInRadiusCondition', 'private static int incrementCountIfPosCheck(', 'real block predicate producer'),
    ('common:condition/factory/entity/CachedBlockInRadiusCondition', 'public static void invalidate(BlockPos pos, SerializableData.Instance data)', 'condition-specific invalidation'),
    ('common:condition/factory/entity/CachedBlockInRadiusCondition', 'public static void invalidate(BlockPos pos)', 'world-event invalidation'),
    ('common:condition/factory/entity/CachedBlockInRadiusCondition', 'public static void clearCache()', 'disconnect cleanup'),
    ('common:mixin/xplatform/common/LevelMixin', 'private void apugli$markConditionDirty(', 'successful world mutation invalidates evidence'),
    ('common:registry/condition/ApugliEntityConditions', 'public static void registerAll()', 'actual entity-condition registration'),
    ('fabric:client/ApugliClientFabric', 'public void onInitializeClient()', 'actual disconnect clear-cache invocation')],
    '注册的cached_block_in_radius实体条件实际扫描entity.level中的block_condition，按BlockPos与data缓存单点结果和中心/依赖坐标集合。后续条件check复用结果；Level.setBlock RETURN仅成功时invalidate(pos)使旧空间证据失效。check还依据实体距离及使用年龄移除部分数据，Fabric客户端断开调用clearCache清三张表。这里完整串起具体玩法消费者、世界事件生产者与生命周期清理，不以cache关键词独立计。',
    '借鉴只有成功状态变化才使旧证据失效，以及从产生到后续消费之间必须维护依赖/边界。对回执不应沿用BlockPos全局键：至少纳入原始维度、来源与目标UUID；过期应是明确tick年龄而非查询次数。',
    '专用模组玩法缓存，不是战斗回执队列；其生命周期对照相关，但不能据此确定方天TTL。ENTITIES年龄按每次check递增、阈值为该data实体数，绝非世界tick短TTL。缓存键缺Level/维度/side，可能跨维度或同进程客户服务端串值；定向invalidate找到第一个依赖中心就break，其他中心可能残留。客户端断开清理不证明服务端停服/卸载清理；只记录缺陷，不运行修复。',
    '实际方块半径玩法条件的成功事件失效、延后消费与清理调用链；纯缓存基础设施不计，本条保留了完整玩法使用证据。')

# The following are fully read negative decisions, never extra credit for templates.
add('tame-hit-factory-family-excluded', [
    ('common:power/factory/TameHitActionPowerFactory', 'default void execute(', 'resolve tame owner and synchronous callbacks'),
    ('common:power/factory/ActionOnTameHitPowerFactory', 'default void execute(', 'outgoing wrapper'),
    ('common:power/factory/ActionWhenTameHitPowerFactory', 'default void execute(', 'incoming wrapper'),
    ('fabric:mixin/fabric/common/LivingEntityMixin', 'private void apugli$runDamageFunctions(', 'same producer already evidenced in batch001')],
    '成功hurt RETURN对宠物伤人/被伤两方向调TameHitAction；工厂从tamable.getOwner解析owner，null便退，按方向选择owner实体对，检查三个条件，执行两组动作后use。',
    '可作来源与持有者不同的反例：宠物是actor，冷却持有者是owner，回执不能只存一个player引用。',
    '两个包装为同一同步hurt分派，无新增延迟状态/TTL或调度；生产回调在batch001已有，不能拆成新命中回执credit。',
    '仅身份方向对照，无新增独立生命周期。', False, 'batch001:hit-history-expiry producer callback')

add('last-attacker-factory-family-excluded', [
    ('common:power/factory/TargetHurtActionPowerFactory', 'default void execute(', 'shared synchronous cooldown callback'),
    ('common:power/factory/ActionOnAttackerHurtPowerFactory', 'default void execute(', 'direction mapping'),
    ('common:power/factory/ActionOnTargetHurtPowerFactory', 'default void execute(', 'direction mapping'),
    ('common:condition/factory/entity/AttackerConditionCondition', 'public boolean check(', 'read lastHurtByMob'),
    ('common:condition/factory/entity/AttackTargetConditionCondition', 'public boolean check(', 'read lastHurtMob'),
    ('common:condition/factory/entity/AttackConditionsCondition', 'public boolean check(', 'same pair predicate helper')],
    '两个target-hurt包装将getLastHurtByMob映射为不同powerHolder/actor/target；两种攻击关系条件分别读取lastHurtByMob、lastHurtMob再共用AttackConditionsCondition。没有本仓库自管历史年龄。',
    '提醒历史最后攻击关系与本次source/directActor不能等同，尤其不能把非null当新鲜回执。',
    '实际条件和hurt同步回调，但没有新增事件储存/清理/调度实现；原版关系时限实现未在授权仓库内审阅。包装和方向镜像合并0分。',
    '缺独立延迟消费生命周期。', False)

add('harm-threshold-template-excluded', [
    ('common:power/factory/HarmActionPowerFactory', 'default void execute(', 'same-hit bounded callback loop'),
    ('common:power/factory/ActionOnHarmPowerFactory', 'default void execute(', 'outgoing wrapper'),
    ('common:power/factory/ActionWhenHarmedPowerFactory', 'default void execute(', 'incoming wrapper'),
    ('fabric:mixin/fabric/common/LivingEntityMixin', 'private void apugli$runDamageFunctionsBeforeDamaged(', 'before-actuallyHurt producer')],
    '工厂用amount或min(targetHealth, amount)除amount_to_trigger，受limit或maxHealth*4限制同步循环动作，最后use；伤人/受伤两个包装共享实现，并从actuallyHurt之前触发。',
    '有界循环不是回执队列；调用前伤害量也不是确认健康已下降。',
    '没有累计跨事件阈值、pending状态或过期逻辑；amount_to_trigger=0等边界未保护。模板换方向不能计两条，本组0分。',
    '同步调用而非延迟消费，负例。', False)

add('nearby-retaliation-family-excluded', [
    ('common:power/factory/DamageNearbyPowerFactory', 'default void execute(', 'synchronous nearby damage and late cooldown'),
    ('common:power/factory/DamageNearbyOnHitPowerFactory', 'default void execute(', 'outgoing mapping'),
    ('common:power/factory/DamageNearbyWhenHitPowerFactory', 'default void execute(', 'incoming mapping')],
    '同一工厂在target.level扫描AABB，排除attacker/target并逐一检查双实体条件，同步nearby.hurt，再执行附加动作，循环后use。两个wrapper只映射命名与inflictor。',
    '横扫反例：忽略hurt返回值就执行附加动作会把尝试伤害当成功；use在循环之后也不提供重入前预占。',
    '无延迟任务/短TTL/独立消费账本。两个方向和多个目标不能凑多条；本次仅研究风险，不改任何生产或下载代码。',
    '同步范围攻击，缺本研究所需新增生命周期。', False)

add('owner-and-prime-predicate-only-excluded', [
    ('common:condition/factory/bientity/OwnerCondition', 'public boolean check(', 'owner identity predicate for three entity kinds'),
    ('common:condition/factory/bientity/PrimeAdversaryCondition', 'public boolean check(', 'kill-credit equality predicate')],
    'OwnerCondition对宠物/云/弹射物比较getOwner与给定actor的对象身份；PrimeAdversaryCondition只比较target.getKillCredit与actor。',
    '可对照owner、directSource和killCredit的含义，不能把三者混为相同攻击来源。',
    '只是通用已注册玩法条件，没有找到新的具体延后任务使用它们；不单独计数。死亡归属消费已在本批另一整链记录，此处不再加credit。',
    '没有完整独立使用生命周期。', False, 'batch002:fatal-damage-snapshot-to-kill-credit (kill-credit semantics)')

add('invulnerability-condition-only-excluded', [
    ('common:condition/factory/entity/CanTakeDamageCondition', 'public boolean check(', 'hypothetical-source eligibility only'),
    ('common:condition/factory/entity/JoinInvulnerabilityTicksCondition', 'public boolean check(', 'read vanilla join protection counter')],
    'CanTakeDamage构造假想source再查isInvulnerableTo和抗火；JoinInvulnerabilityTicks只读取ServerPlayer accessor计数并比较。',
    '免疫预检与短保护计数的读取都不能代替实际hurt成功回执。',
    '没有本模组实现的counter递减/消费链；原版计数器实现不在范围内，故两种条件本组0分，不因Ticks关键词加分。',
    '读取外部计数不是研究完整短TTL实现。', False)

add('equip-callback-mirrors-excluded', [
    ('common:mixin/xplatform/common/PlayerInventoryMixin', 'private void apugli$setStack(', 'inventory setter event'),
    ('common:mixin/xplatform/common/PlayerEntityMixin', 'public void apugli$equipStack(', 'player setter event'),
    ('common:power/ActionOnEquipPower', 'public void executeAction(', 'shared synchronous consumer')],
    'Inventory.setItem在列表更新前检查armor/offhand并触发power；Player.setItemSlot TAIL也触发同一power.executeAction，其按slot/item条件同步执行动作。',
    '同一玩法可能有不同事件入口，计数应按实际消费状态而非setter数量；前后阶段也不能自动视作两次不同成功。',
    '无去重记录、任务队列、过期或异步消费；未运行证明同一动作路径是否重叠触发。两入口合并0分。',
    '多个同步入口不构成新增有效生命周期。', False)

add('enchantment-cache-unresolved-excluded', [
    ('neoforge:power/ModifyEnchantmentLevelPower', 'public void onAdded(', 'delegates to missing factory'),
    ('neoforge:power/ModifyEnchantmentLevelPower', 'public void onRemoved(', 'delegates to missing factory'),
    ('neoforge:power/ModifyEnchantmentLevelPower', 'public ConcurrentHashMap<UUID, ConcurrentHashMap<ComparableItemStack, ListTag>> getEntityItemEnchants()', 'UUID table accessor only'),
    ('neoforge:util/CoreUtil', 'public static int getModifiedEnchantmentLevel(', 'lookup uses living entity against UUID-keyed map'),
    ('neoforge:util/CoreUtil', 'public static Map<Enchantment, Integer> getModifiedEnchantments(', 'same incomplete consumer family')],
    'ModifyEnchantmentLevelPower声明UUID→item→enchant表及power表，onAdded/onRemoved都委托ModifyEnchantmentLevelPowerFactory.super。缓存树中不存在该Factory源码；CoreUtil却对getEntityItemEnchants().containsKey(living)查Entity对象。',
    '身份键类型必须端到端一致；不能看到UUID字段便宣称完整owner校验或生命周期清理已证实。',
    '缺实际工厂初始化/清理/失效方法，调用链无法在授权缓存提交闭合；不能补写缺失方法、猜测其他版本或声称构建运行成功。本组0分。',
    '真实源码存在但关键方法缺失，不能审查计数。', False)

add('single-power-packet-without-producer-excluded', [
    ('neoforge:network/s2c/SyncSinglePowerPacket', 'public void handle()', 'deferred deserialize with bound-power checks'),
    ('neoforge:platform/ForgePowerHelper', 'public <P> void syncPower(', 'actual sync delegates to Apoli API instead')],
    'SyncSinglePowerPacket.handle排入Minecraft.execute，找LivingEntity、power container，再检查configuredPower非null/isBound和NBT非空后反序列化；但本缓存全树未见new SyncSinglePowerPacket或注册该类的调用，实际ForgePowerHelper.syncPower走ApoliAPI.synchronizePowerContainer。',
    '排队后验证持有power和数据非空是辅助观察，但只有收包函数不能证明真实玩法任务在运行使用。',
    '缺生产者/注册及具体玩法闭合链；包无UUID/维度/TTL且level可能null。孤立网络包装不计，不能为凑数把它当已研究有效调度。',
    '纯孤立网络候选、玩法使用未证实。', False)

add('projectile-action-duplicate-family-excluded', [
    ('common:action/factory/entity/CustomProjectileAction', 'public void execute(', 'alternate producer of already-reviewed CustomProjectile'),
    ('common:action/factory/entity/CustomProjectileAction', 'protected Entity createProjectile(', 'same owner/action fields and lifecycle'),
    ('common:action/factory/entity/FireProjectileAction', 'public void execute(', 'immediate configured entity spawn loop'),
    ('common:action/factory/entity/FireProjectileAction', 'protected Entity createProjectile(', 'owner assignment; no in-repo consumer for vanilla types')],
    'CustomProjectileAction与batch001 power发射器一样创建CustomProjectile并设置owner、命中/每tick动作和条件；FireProjectileAction立即批量创建配置类型，Projectile设置owner后shoot，再可合并NBT。',
    '替换发射入口并未产生新的命中/销毁状态机；owner在NBT合并前写入也不证明最终owner未被覆盖。',
    'CustomProjectile生命周期已在batch001计为整链，不能再把这个入口加分。通用FireProjectile的后续原版类型消费链未审阅；没有TTL或任务队列，均0分。',
    '同生命周期替代入口/未闭合通用创建器。', False, 'batch001:custom-projectile-entire-lifecycle')


add('capture-local-template-variants-excluded', [
    ('fabric:mixin/fabric/common/AnimalEntityMixin', 'private void apugli$captureBreedLocals(', 'capture breeding partner'),
    ('fabric:mixin/fabric/common/AnimalEntityMixin', 'private int apugli$modifyThisAnimalBreed(', 'first-parent cooldown condition'),
    ('fabric:mixin/fabric/common/AnimalEntityMixin', 'private int apugli$modifyOtherAnimalBreed(', 'second-parent cooldown and clear'),
    ('common:power/factory/ModifyBreedingCooldownPowerFactory', 'default boolean doesApply(', 'actual player/animal predicate'),
    ('neoforge:mixin/forge/common/AnimalEntityMixin', 'private int apugli$modifyOtherAnimalBreed(', 'loader mirror; never extra credit'),
    ('common:mixin/xplatform/common/AnvilScreenHandlerMixin', 'private void apugli$captureFieldsInAnvil(', 'capture enchantment and input stack'),
    ('common:mixin/xplatform/common/AnvilScreenHandlerMixin', 'private boolean apugli$allowEnchantingThroughAnvil(', 'condition consumes captured locals then clears'),
    ('common:power/AllowAnvilEnchantPower', 'public boolean doesApply(', 'concrete enchantment, left-stack and right-stack guards')],
    '繁殖finalizeSpawnChildFromBreeding HEAD保存另一只Animal，第二次setAge参数修饰使用该字段与loveCause检查power，两个返回分支都置null；Forge镜像相同。铁砧createResult在canEnchant前保存Enchantment与左输入ItemStack，后续INVOKE_ASSIGN检查player power和右输入附魔等级，允许/不允许两分支都清两个字段。',
    '补充暂存上下文在正常分支清理的实例和异常边界；繁殖中的玩家loveCause与目标Animal是不同身份，铁砧任务还需绑定同一次输入版本。',
    '真实玩法存在，但核心都是同一调用内字段桥接局部变量→检查→置null，与本批pending-pair模式高度相近；未出现新队列、短TTL或独立一次伤害回执，按用户不重复模板要求保守合并为零增量。繁殖跨加载器只作对照；二者异常/提前退出不保证清空，也没有transaction ID、UUID/维度快照。',
    '已完整核对的结构变体，零增量，避免靠更换玩法名补20条。', False,
    'batch002:placed-block-pending-action-pair (synchronous capture/use/clear pattern)')

add('edible-snapshot-unresolved-family-excluded', [
    ('neoforge:mixin/forge/common/FoodDataMixin', 'private void apugli$captureEatLocals(', 'capture eating stack/entity'),
    ('neoforge:mixin/forge/common/FoodDataMixin', 'private boolean apugli$isEdibleWithPower(', 'consume and clear local bridge'),
    ('neoforge:mixin/forge/common/LivingEntityMixin', 'private void apugli$captureEatLocals(', 'same family at effect step'),
    ('neoforge:mixin/forge/common/LivingEntityMixin', 'private boolean apugli$isEdibleWithPower(', 'same family, no additional credit'),
    ('neoforge:util/CoreUtil', 'public static boolean doEdibleItemPowersApply(', 'delegate to absent EdibleItemPower implementation')],
    '两处eat/addEatEffect HEAD保存stack/entity，在isEdible值回调中调用CoreUtil并在正常true/false分支清字段。CoreUtil进一步引用EdibleItemPower和EDIBLE_ITEM能力。缓存固定提交未包含EdibleItemPower.java。',
    '局部变量捕获与后续消费若没有完整具体power实现，不能证明整个玩法生命周期；两处不同入口也不能当两条。',
    '关键EdibleItemPower方法缺失且是本批已合并的capture/use/clear桥接结构；不访问别的仓库或猜旧版本补链，零信用。异常路径无finally，清字段也不能当跨tick短TTL。',
    '缺关键实际玩法方法、结构同族，完整链未成立。', False)

add('freeze-threshold-retention-excluded', [
    ('common:mixin/xplatform/common/EntityMixin', 'private int apugli$modifyTicksRequiredToFreeze(', 'retain prior threshold after power disappears'),
    ('common:mixin/xplatform/common/EntityMixin', 'private boolean apugli$allowFreezing(', 'power eligibility override'),
    ('common:power/factory/FreezePowerFactory', 'default boolean shouldDamage(', 'power damage eligibility')],
    '有FREEZE power时getTicksRequiredToFreeze记录修饰后阈值；power消失但ticksFrozen>0时继续返回旧阈值，冻结进度归零才清字段。canFreeze有power时直接true，shouldDamage额外检查配置条件。',
    '辅助说明维持已有玩法状态与设置短TTL不同，旧阈值保留不意味着新事件仍有效。',
    '保留时长依赖原版冻结进度，无本模组待消费事件、一次消费或短TTL上限；power damage条件只是同步预检。不能以Ticks/clear关键词算成combat/task queue实现，0分。',
    '真实状态保留但缺本题所需完整事件消费生命周期。', False)


def main():
    # Match Carson's coarse semantic deduplication: do not count every instance
    # of synchronously captured locals as a new event queue implementation.
    context_variants = {'placed-block-pending-action-pair', 'enchantment-damage-phase-guard'}
    for row in ROWS:
        if row['chain_id'] in context_variants:
            row['proposed_credit'] = 0
            row['decision'] = 'reviewed_merged_zero_credit'
            row['duplicate_of'] = 'batch002:fatal-damage-snapshot-to-kill-credit (cross-callback context family)'
            row['limits'] += ' 本次进一步按粗粒度合并：与致死伤害上下文同属同步跨回调字段桥接，不再独立建议信用；保留全文证据而非删记录。'
        if row['chain_id'] == 'fatal-damage-snapshot-to-kill-credit':
            row['counting_unit'] = 'One synchronous cross-callback gameplay-context family; placement, enchantment, breeding and anvil variants remain zero-credit evidence, not additional implementations.'
            row['merged_variant_ids'] = sorted(context_variants | {'capture-local-template-variants-excluded'})
    assert PIN == json.loads((HERE / 'sources/MerchantPug__Apugli/commit.json').read_text())['sha']
    assert not list(ROOT.rglob('ModifyEnchantmentLevelPowerFactory.java'))
    assert not list(ROOT.rglob('EdibleItemPower.java'))
    index = {r['source_local']: r for r in json.loads((DOCS / 'source-index.json').read_text())}
    first_keys = {r['dedup_key'] for r in PRIOR_ROWS}
    assert not first_keys.intersection(r['dedup_key'] for r in ROWS)
    used_main = set()
    master_path = WORKSPACE / 'docs/cod4/audit-20261022/sweep-receipt-research/accepted.jsonl'
    master_bytes = master_path.read_bytes()
    master_apugli = [json.loads(line) for line in master_bytes.decode().splitlines()
                     if 'apugli' in json.loads(line).get('repo', '').lower()]
    master_primary = {(r['path'], r['line'], r['end_line']) for r in master_apugli}
    for r in ROWS:
        primary = (r['path'], r['line'], r['end_line'])
        if r['proposed_credit']:
            assert primary not in used_main
            assert primary not in master_primary
            assert not any((p['path'], p['line'], p['end_line']) == primary for p in PRIOR_ROWS)
            used_main.add(primary)
        for e in r['evidence']:
            raw = (WORKSPACE / e['source_local']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == e['source_sha256'] == index[e['source_local']]['source_sha256']
            assert '\n'.join(raw.decode().splitlines()[e['line'] - 1:e['end_line']]) == e['excerpt']
            assert e['excerpt'].rstrip().endswith('}')
        r['pin_verification'] = dict(kind='cached_commit_archive_and_reconstructed_git_tree',
                                    source_index='docs/cod4/audit-20261022/sweep-receipt-research/helpers/apugli-rpginventory/source-index.json',
                                    source_index_sha256=PRIOR_HASHES['source-index.json'],
                                    git_tree_sha='a9ccf9f7179ff627f18d17a76196cf71edb14f1b')
    valid = [r for r in ROWS if r['proposed_credit']]
    excluded = [r for r in ROWS if not r['proposed_credit']]
    common = dict(schema_version=1, repo=REPO, revision=PIN, reviewed_at=NOW,
                  requested_additional_valid=20, final_ledger_owner='Carson', applied_credit=0,
                  no_new_network_requests=True, downloaded_code_executed=False)
    def dump(name, obj):
        (DOCS / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    dump('batch-002.json', dict(common, proposed_valid=len(valid), gap=20 - len(valid), entries=valid))
    dump('excluded-002.json', dict(common, credit=0, entries=excluded))
    (DOCS / 'reviewed-002.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in ROWS))
    assert all(hashlib.sha256((DOCS / n).read_bytes()).hexdigest() == h for n, h in PRIOR_HASHES.items())
    validation = dict(common, valid=True, proposed_valid=len(valid), excluded=len(excluded),
                      gap_to_twenty=20 - len(valid), method_evidence_occurrences=sum(len(r['evidence']) for r in ROWS),
                      unique_method_ranges=len({(e['path'], e['line'], e['end_line']) for r in ROWS for e in r['evidence']}),
                      previous_batch_files_unchanged=PRIOR_HASHES,
                      main_accepted_read_only_sha256=hashlib.sha256(master_bytes).hexdigest(),
                      main_accepted_apugli_entries_at_check=len(master_apugli),
                      main_accepted_primary_duplicate_matches=0,
                      all_sources_match_previously_git_verified_index=True,
                      all_excerpts_match_full_method_ranges=True, duplicate_primary_methods_in_first_batch=0,
                      unreviewed_candidates_credit=0, main_ledger_written=False,
                      production_written=False, todo_written=False, game_started=False, server_started=False)
    dump('validation-002.json', validation)
    dump('handoff-002.json', dict(common, proposed_additional_valid=len(valid), gap_to_twenty=20 - len(valid),
                                reviewed_zero_increment=len(excluded), unreviewed_credit=0,
                                method_evidence_occurrences=validation['method_evidence_occurrences'],
                                source_cache='tools/cod4/sweep-receipt-research/helpers/apugli-rpginventory/sources/MerchantPug__Apugli/tree',
                                suggested_chain_ids=[r['chain_id'] for r in valid],
                                scope_limit='Pinned default branch only. Six are helper proposals, not Carson acceptance or evidence of twenty new implementations.',
                                dedup='Cross-callback synchronous context variants merged; explosion entrypoints and client/server tasks merged; loader mirrors and unresolved/network-only chains zero.',
                                first_batch_files_preserved=True, first_batch_credit_reused=0,
                                production_game_assets_main_ledger_todo_changes=0))
    print(json.dumps({k: validation[k] for k in ['proposed_valid', 'excluded', 'gap_to_twenty', 'method_evidence_occurrences', 'unique_method_ranges']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
