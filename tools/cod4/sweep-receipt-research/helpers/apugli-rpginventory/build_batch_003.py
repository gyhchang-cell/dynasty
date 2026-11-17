"""Package manually read gameplay chains, including zero-credit exclusions. Offline only."""
import datetime
import json
from pathlib import Path
from evidence_003 import DOCS, WORKSPACE, CACHE, PINS, REPO, standard, behavior, dump, sha

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
ROWS = []


def std(branch, short, signatures):
    return [standard(branch, short, sig, role) for sig, role in signatures]


def beh(short, signatures):
    return [behavior(short, sig, role) for sig, role in signatures]


def add(key, evidence, observation, application, limits, decision, duplicate_of=None):
    row = dict(evidence[0])
    row.update(candidate_id='apugli-rpginventory-003-' + key, chain_id=key, batch='003',
               status='reviewed', decision=decision, credit=0,
               proposed_credit=int(decision == 'reviewed_valid_pending_carson'),
               final_count_owner='Carson', reviewed_at=NOW, evidence=evidence,
               observation=observation, application=application, limits=limits,
               duplicate_of=duplicate_of, dedup_key=REPO + ':' + key,
               counting_unit='One complete gameplay lifecycle; no per-method, per-version, wrapper or mirror credit.',
               external_runtime_tested=False, downloaded_code_executed=False)
    assert all(e['revision'] == row['revision'] for e in evidence), 'never stitch incompatible versions'
    ROWS.append(row)


add('behavior-goal-registration-revocation',
    beh('power/ModifyMobBehaviorPower', [
        ('public void tick()', 'ten-age-tick candidate collection, eligibility recheck and revoke'),
        ('public void onAdded()', 'registration lifecycle entry'),
        ('public void onRemoved()', 'power removal revokes tasks and selected threats'),
        ('public ModifyMobBehaviorPower(', 'compose predicates and enable ticking'),
        ('public boolean doesApply(', 'holder/mob pair gate'),
        ('public void addMobPredicate(', 'install holder/mob predicate'),
        ('public void addPowerHolderPredicate(', 'install power-active predicate'),
        ('public MobBehavior getMobBehavior()', 'same behavior instance'),
        ('public static PowerFactory<?> getFactory()', 'actual configured gameplay power')]) +
    beh('behavior/MobBehavior', [
        ('public void removeGoals(', 'remove from matching selector plus bookkeeping'),
        ('public boolean hasAppliedGoals(', 'behavior instance identity dedup'),
        ('public void addMobRelatedPredicate(', 'composed pair predicate'),
        ('public void addEntityRelatedPredicate(', 'composed holder predicate')]) +
    beh('behavior/types/FleeMobBehavior', [
        ('public void initGoals(', 'real FleeEntityGoal allocation and selector insertion'),
        ('public static BehaviorFactory<?> getFactory()', 'actual registered flee behavior')]) +
    beh('registry/MobBehaviors', [('public static void register()', 'register concrete behavior variants')]) +
    beh('registry/ApugliPowerFactories', [('public static void register()', 'register ModifyMobBehaviorPower')]) +
    beh('Apugli', [('public void onInitialize()', 'actual initializer connects both registries')]),
    'fabric/behavior固定提交（配置为Minecraft 1.18、Apugli 1.5.1）中，ModifyMobBehaviorPower将mob候选表与已修改表分开；每entity.age%10==0在持有者当前ServerWorld扫描Mob，删除死/removed候选，只有power active、条件仍成立且同MobBehavior实例尚无登记goal才initGoals。失效时调用removeGoals；onRemoved也遍历已修改对象撤销，并在目标关联持有者时处理仇恨。Flee实际创建FleeEntityGoal并加入mob.goalSelector。注册、构造、tick和移除整链只建议一条，Passive空实现和选择器包装不另计。',
    '任务登记和任务撤销应保存同一个任务句柄及实际所属容器；取消仅清候选表不足以撤销已经排入执行器的任务。消费前重新检查eligibility与登记身份是两件事。方天设计审阅可检查“候选→已登记→已消费/已取消”的每个转移，不能只依赖一个时间相等判断。',
    '这是官方仓库历史开发分支的实际玩法实现，不宣称已发布、编译成功或运行验证。Flee把goal加进goalSelector，却记进modifiedTargetSelectorGoals；removeGoals因此向targetSelector移除，存在残留任务风险。候选ArrayList每次扫描add而不清/去重，修改表在Passive无goal时可持续增加；判断hasAppliedGoals用behavior对象引用，非持有者/任务UUID；多个power共用行为对象时隔离不足。候选死/removed清理不等于已登记表清理；无原维度匹配/TTL/换世界清理。onRemoved不clear两张列表，UUID用==比较值不可靠。tick没有侧检查而直接转ServerWorldAccessor，onAdded侧检查不能证明后续tick均为服务端。',
    'reviewed_valid_pending_carson')

add('enchantment-gameplay-invalidation-and-deferred-remove',
    std('next', 'common:power/factory/ModifyEnchantmentLevelPowerFactory', [
        ('default boolean shouldReapplyEnchantments(', 'consume modifier/condition change flags for item rebuild'),
        ('default boolean updateIfDifferent(', 'update modifier/active snapshot'),
        ('default void onAdded(', 'UUID buckets plus actual deferred packet producer'),
        ('default void onRemoved(', 'power removal and last-holder empty-slot rollback'),
        ('default void tick(', 'later entity tick links workable empty slots'),
        ('static ItemStack getWorkableEmptyStack(', 'per-UUID holder-bound empty instance'),
        ('static boolean isWorkableEmptyStack(', 'slot identity test'),
        ('default ListTag getEnchantments(', 'concrete enchantment result cache consumer'),
        ('default ListTag generateEnchantments(', 'rebuild actual gameplay enchantment tags'),
        ('default boolean doesApply(', 'enchantment and item eligibility'),
        ('default boolean checkItemCondition(', 'optional item condition'),
        ('default Optional<Integer> findEnchantIndex(', 'locate enchantment tag'),
        ('default int getItemEnchantmentLevel(', 'numeric gameplay consumer'),
        ('default Map<Enchantment, Integer> getItemEnchantments(', 'map gameplay consumer')]) +
    std('next', 'fabric:power/ModifyEnchantmentLevelPower', [
        ('public void onAdded()', 'real power lifecycle callback'),
        ('public void onRemoved()', 'real power lifecycle callback'),
        ('public ConcurrentHashMap<UUID, ConcurrentHashMap<ComparableItemStack, ListTag>> getEntityItemEnchants()', 'actual static UUID storage'),
        ('public ConcurrentHashMap<UUID, ConcurrentHashMap<Instance, Tuple<Integer, Boolean>>> getPowerModifierCache()', 'actual per-power dirty snapshots')]) +
    std('next', 'fabric:mixin/fabric/common/LivingEntityMixin', [('private void apugli$setItemStackEntities(', 'real tick producer')]) +
    std('next', 'fabric:mixin/fabric/common/EnchantmentHelperMixin', [
        ('private static void apugli$getEnchantmentItemStack(EnchantmentHelper.EnchantmentVisitor', 'real enchanting gameplay input capture'),
        ('private static ListTag apugli$getEnchantmentsForEachEnchantment(', 'real tag-consumption hook'),
        ('private static ListTag apugli$getEnchantmentsGetLevel(', 'same gameplay result consumer')]) +
    std('next', 'common:network/s2c/ModifyEnchantmentLevelPacket', [
        ('public void handle()', 'queued current entity/power lookup then lifecycle callback'),
        ('public void encode(', 'actual entityId/powerId/remove payload'),
        ('public static ModifyEnchantmentLevelPacket decode(', 'matching payload decode')]) +
    std('next', 'fabric:network/ApugliPackets', [('public static void registerS2C()', 'real receiver registration')]) +
    std('next', 'fabric:platform/FabricPowerHelper', [('public <P> P getPowerFromId(', 'resolve power from current holder')]) +
    std('next', 'common:util/ComparableItemStack', [('public boolean equals(', 'item-content identity'), ('public int hashCode()', 'item/count/NBT hash')]) +
    std('next', 'common:mixin/xplatform/common/ItemStackMixin', [
        ('public void apugli$setEntity(', 'holder assignment'), ('public Entity apugli$getEntity(', 'holder read'),
        ('private ItemStack apugli$copyNewParams(', 'copy retains holder or replaces empty instance')]),
    'next/1.20固定提交（Minecraft 1.20.1、Apugli 2.9.1）的附魔玩法工厂完整存在，未用它补写1.20.4缺失类。onAdded建立UUID→物品附魔结果和UUID→power(修饰值,条件)快照；shouldReapplyEnchantments在物品缺项或快照改变时使getEnchantments重建标签。真实LivingEntity.tick还为可操作空槽放入绑定持有者的空ItemStack，附魔迭代/等级Mixin消费工厂结果。onRemoved删该power快照，最后power时撤销空槽并删附魔桶。服务端增删确实发ModifyEnchantmentLevelPacket，Fabric确实注册；客户端execute后验证LivingEntity和当前power存在，再调用增删生命周期。以上是一个具体玩法结果失效/延后同步链，不按缓存方法、平台或包方向拆分。',
    '新观察是脏状态的消费作用域：缓存结果属于每个物品，变化快照却只属于power。首个物品读取并更新快照后，其他已有结果的物品可能看不到同一次变化。方天整合时应让伤害事实、攻击级消费和每个次目标的处理状态各有明确作用域，不能让首目标读取把后续目标需要的事实一起抹掉。延后remove还需核对原power代次，避免删到同ID新实例。',
    '专用附魔玩法缓存及真实调度链，非通用缓存；仍需Carson范围裁定。shouldReapply的anyMatch短路会分次消费变化；item_condition状态也未按物品分开。getItemEnchantments/getItemEnchantmentLevel有直接缓存读取路径，不能承诺每次都先重建。ComparableItemStack有的路径包copy有的包原对象，修改NBT/数量可能改变键hash。EMPTY_STACK_MAP及空POWER_MODIFIER_CACHE外层桶未随最后移除删除；无TTL、server-stop/disconnect清理或原维度/side键。包仅数字entityId和powerId，无UUID/维度/序号/代次，level-null和power工厂类型未验证。当前树只看到空实例与copy路径写apugli$entity，普通非空新物品如何取得绑定未闭合，不能声称覆盖全部装备。与batch002缺源候选语义相同但在那里credit0；只对本固定版本完整整链建议一次，不能给旧候选补一份credit。',
    'reviewed_valid_pending_carson', 'batch002:enchantment-cache-unresolved (zero-credit; superseded only at this different complete revision)')

add('bunny-hop-grace-counter-boundaries',
    std('default', 'fabric:power/BunnyHopPower', [('public void tick()', 'per-power invalid-movement grace counter')]) +
    std('default', 'common:power/factory/BunnyHopPowerFactory', [
        ('default void onTravel(', 'server travel callback periodic resource increment'),
        ('default void reset(', 'zero and sync only on value change'),
        ('default boolean canGainResource(', 'actual airborne eligibility'),
        ('static SerializableData getSerializableData()', 'tick_rate and increment configuration')]) +
    std('default', 'fabric:mixin/fabric/common/LivingEntityMixin', [('private void apugli$travelLivingEntity(', 'actual alive/server callback')]) +
    std('default', 'fabric:power/AbstractResourcePower', [('public int assign(', 'external resource setter delegation'), ('public void sync(', 'actual power sync call')]),
    'BunnyHop Instance每个power tick先判断framesOnGround>4再reset；随后不满足腾空条件时把计数增加至5，重新腾空时归零。故从0开始连续5次不符合后变5，第6次tick才首次reset；若第6次已腾空，reset仍在重新判断资格之前发生。onTravel以entity.tickCount%max(1,tick_rate)==0增长资源并按变化同步，再按当前资源moveRelative。',
    '完整记录比较、递增、清理顺序导致的边界：宽限5次不意味着第5次消费。可供时钟边界审阅作反例，不推定方天TTL=5，也不把资源变化当伤害事实。',
    'framesOnGround实际统计所有不能gain的状态，包含落地/液体/乘骑/滑翔；变量名不能当语义证明。不是事件回执或一次任务容器，无UUID/维度/消费ID。属于宽泛移动资源宽限，与主账排除宽泛装备周期的口径一致，本条不建议新增有效数。travel回调同刻可能多次而无lastProcessedTick，本仓库未证明调用频率。',
    'reviewed_excluded_zero_credit')

add('packet-action-role-codec-audit',
    std('default', 'common:action/factory/bientity/meta/PacketAction', [('public void execute(', 'actual actor/target orientation producer')]) +
    std('default', 'common:network/c2s/ExecuteBiEntityActionServerPacket', [
        ('public void encode(', 'bi-entity action serializer'), ('public static <A> ExecuteBiEntityActionServerPacket<A> decode(', 'entity-action deserializer mismatch'),
        ('public void handle(', 'queued current player-level entity lookup')]) +
    std('default', 'common:network/s2c/ExecuteBiEntityActionClientPacket', [
        ('public void encode(', 'entity-action datatype for a bi-entity payload'),
        ('public static <A> ExecuteBiEntityActionClientPacket<A> decode(', 'same mismatched datatype'),
        ('public void handle()', 'queued actor/target existence checks')]) +
    std('default', 'common:action/factory/entity/meta/PacketAction', [('public void execute(', 'same packet-action family single target')]) +
    std('default', 'common:network/c2s/ExecuteEntityActionServerPacket', [('public void handle(', 'same family queue using sender')]) +
    std('default', 'common:network/s2c/ExecuteEntityActionClientPacket', [('public void handle()', 'same family single-target lookup')]) +
    std('default', 'fabric:network/ApugliPackets', [('public static void registerC2S()', 'registered C2S dispatcher'), ('public static void registerS2C()', 'registered S2C dispatcher')]) +
    std('default', 'fabric:platform/FabricActionHelper', [('public <A> void executeBiEntity(', 'consumer accepts tuple without actor/target null validation')]),
    '注册的packet元动作按LocalPlayer位于pair哪端编码otherEntityId与isOtherEntityTarget，server.execute时以发送者当前level解析另一端。C2S encode使用biEntityDataType，decode却用entityDataType；S2C双实体包encode/decode两端也都用entityDataType。S2C任务检查两实体非null，C2S任务没有检查otherEntity是否存在，FabricActionHelper仅检查action非null。单实体和双实体、C2S/S2C合并一个审阅族。',
    '具体新增核验点为回执actor/target角色是否跨编码保持一致，以及排队后重新解析是否仍是同一个身份。方向布尔值不能替代目标UUID。此处保存反例，不把反序列化成功当成来源授权或原攻击事实。',
    '这是通用可配置动作运输，没有在该固定缓存中补出具体战斗玩法配置使用链，按用户规则零信用。没有执行数据包，不能断言错误类型在所有配置下一定抛错。无维度快照/TTL/代次/重放去重/源权限检查，server.execute自身是否内联或稍后执行由外部Minecraft实现决定，不能据名字断言必跨tick。',
    'reviewed_excluded_zero_credit')

add('raycast-recipient-and-pierce-selection',
    std('default', 'common:action/factory/entity/RaycastAction', [
        ('public void execute(', 'ray geometry to configured callbacks'),
        ('protected void onHitEntity(', 'predicate polarity and recipient'),
        ('protected void handlePierce(', 'self action outside target loop'),
        ('protected void executeSelfAction(', 'alive check after callbacks'),
        ('protected void onHitBlock(', 'block condition and callback')]) +
    std('default', 'common:util/RaycastUtil', [
        ('public static List<EntityHitResult> raycastEntities(', 'iteration-order nearest-so-far collector'),
        ('public static EntityHitResult raycastEntity(BlockHitResult blockHitResult, Entity actor, double dis, Vec3 direction', 'single entity selection'),
        ('public static BlockHitResult raycastBlock(Entity actor, double dis, Vec3 direction', 'block clip')]) +
    std('default', 'fabric:platform/FabricConditionHelper', [
        ('public boolean checkEntity(SerializableData.Instance', 'absent condition evaluates true'),
        ('public boolean checkBiEntity(SerializableData.Instance', 'optional pair predicate')]),
    'RaycastAction.onHitEntity把target_condition检查传给actor，且检查为true直接return；FabricConditionHelper对未配置条件返回true，因此默认缺target_condition也会跳过实体动作。存在target_action时executeEntity又传actor，双实体动作则传actor/真正target。pierce循环在每个实体条件前已画路径，结束统一executeSelfAction；列表非空不证明任何目标动作成功。raycastEntities用平方targetDis比较初始线性dis，并在遍历中把dis缩小为最近已见距离，既没有排序也不是全部穿透交点集。',
    '建议审阅横扫时把几何选中目标、条件检查对象、实际动作接收者分开核对，并保留每个目标结果；不能从一次穿透结束回调推断所有次目标成功。新增证据关注错误接收者与过滤，未重新申报coordinator关于挥手/冷却不等于伤害的12条建议。',
    '同步几何查询与动作分派，无独立延迟状态/TTL/去重容器，零信用。动作配置具体是否伤害不在该链证明范围内；未运行射线，也不声称实际主游戏受影响。createParticles调用不是成功事实，本条不对美术表现计数。',
    'reviewed_excluded_zero_credit')

add('instant-effect-head-cancellation',
    std('default', 'common:mixin/xplatform/common/StatusEffectMixin', [('private void apugli$cancelInstantEffectWhenBlacklisted(', 'actual instant effect cancellation at HEAD')]) +
    std('default', 'common:power/InstantEffectImmunityPower', [('public boolean doesApply(MobEffect effect)', 'inverted XOR effect membership'), ('public InstantEffectImmunityPower addEffect(', 'populate concrete gameplay immunity set')]),
    'MobEffect.applyInstantenousEffect的HEAD用target当前INSTANT_EFFECT_IMMUNITY power匹配效果并cancel，匹配规则为inverted XOR effects.contains(effect)。source、attacker、target是不同参数，此处只从target查询免疫；没有保存伤害事实。',
    '仅为取消门定位的补充证据：若今后回执研究追踪瞬时效果，应在取消门之后核对其结果。该一般建议与coordinator已有取消/伤害事实原则重叠，不新增建议或计数。',
    '同步条件Set是效果配置，不是任务去重Set；无延迟消费、时钟或一次消费状态，零信用。不从ci.cancel推定整个上游施药/投射物动作都已回滚；原版调用者未在授权仓库内研究。',
    'reviewed_excluded_zero_credit', 'coordinator-receipt: cancellation/fact principle; supplemental code only')

add('lightning-hook-predicate-order',
    std('default', 'fabric:mixin/fabric/common/LightningBoltMixin', [('private void apugli$performLightningStruckActions(', 'before vanilla thunderHit call')]) +
    std('default', 'common:power/factory/ActionWhenLightningStruckPowerFactory', [('default void execute(', 'positive condition returns early before configured action/use')]) +
    std('default', 'fabric:power/AbstractCooldownPower', [('public boolean canUse(', 'delegated cooldown gate'), ('public void use(', 'delegated cooldown write')]),
    'LightningBolt.tick在调用Entity.thunderHit之前执行动作；工厂若canUse=false或“已配置bientity_condition且检查为true”便返回，条件通过反而阻止执行。否则先执行entity_action再use冷却。此处没有hurt返回或真实减血记录，冷却实现也只委托外部Apoli。',
    '新增具体观察是条件极性与先回调后占用的顺序。已有coordinator关于前置攻击表现不证明伤害的建议不再申报；本记录供排除相似关键词命中。',
    '与batch002 weather-target-registry是不同回调，但没有新状态队列，不能因同为雷击再计一条；冷却父类内部时钟不在本仓库，无法把该包装当独立时钟消费实现。',
    'reviewed_excluded_zero_credit')

add('durability-break-action-entry-supplement',
    std('default', 'common:action/factory/item/DamageAction', [('public void execute(', 'actual stack damage/break producer')]),
    'DamageAction先对正损耗逐点进行unbreaking减免；实际damage<=0提前退出。破损分支在找到持有者同引用装备槽后广播break，随后shrink(1)并setDamageValue(0)；未破损才setDamageValue(newDamage)。因此break广播与ItemStack.setDamageValue TAIL“新Damage>=max”是两个不同事实入口，本动作破损分支传入0，不能仅靠该TAIL阈值代表全部破损。',
    '为batch002耐久去重整链补充真实入口限制，审阅时明确观察了哪个状态改变以及是否有其他路径绕过该观察点；不把新入口再包装成独立实现。',
    '该方法没有延迟或独立任务状态；与batch002耐久生命周期同族，仅辅助0信用。不运行物品损耗，不声称所有break都会漏通知；仅描述该静态调用路径。',
    'reviewed_excluded_zero_credit', 'batch002:durability-slot-reentrancy-window')


add('edible-use-finish-mutable-input',
    std('next', 'fabric:mixin/fabric/common/ItemStackMixin', [
        ('private void apugliuseEdibleItem(', 'start using before bucket fallback'),
        ('private void apugli$finishUsingEdibleItem(', 'return hook rechecks power then actions and shrink')]) +
    std('next', 'common:mixin/xplatform/common/ItemStackMixin', [
        ('private void apugli$getMaxUseTime(', 'configured 16 or 32 duration'),
        ('private void apugli$getUseAction(', 'configured eating/drinking pose')]) +
    std('next', 'common:power/EdibleItemPower', [
        ('public boolean doesApply(', 'current stack predicate'),
        ('public static void executeEntityActions(', 'entity actions before eating and shrink'),
        ('public static ItemStack executeItemActions(', 'copy result but recheck originalStack argument'),
        ('public ItemStack getReturnStack()', 'configured return stack')]) +
    std('next', 'fabric:mixin/fabric/common/LivingEntityMixin', [('private void apugli$eatStackFood(', 'custom food effects at eat HEAD')]) +
    std('next', 'fabric:mixin/fabric/common/HungerManagerMixin', [('private void apugli$eat(', 'custom nutrition then cancels vanilla eat')]),
    'next/1.20中已补全EdibleItemPower源码。use检查当前power后startUsingItem，桶射线命中方块时return并继续原use；时长钩子按当前power设16或32。finishUsingItem RETURN重新匹配power，先实体动作和eat，再shrink；传给executeItemActions的originalStack仍是已shrink的同一个可变stack，函数再次用它检查item_condition。故finish最初匹配成立不能保证返还物品动作再次匹配，尤其最后一个物品变empty后。',
    '新增观察是“原输入”参数名不代表不可变快照：事件资格在回调/消耗前成立，后续以已改变的输入重查会变成另一问题。仅作回执原事实与消费时状态区分的辅助证据；没有建议复制该饮食逻辑。',
    '实际使用时长计时、取消与finish调度仍属原版，未在授权两仓库内补读，不能把钩子包装成自有短TTL任务，零信用。未见此链保存不可变开始stack、任务ID或一次finish令牌；不声称重复调用必发生。1.20.4缺失类仍缺失，不把1.20.1源码拼接过去。与batch002同步capture/use族相关，不另计一个新回执实现。',
    'reviewed_excluded_zero_credit', 'batch002:edible-snapshot-unresolved (separate revision, no additional credit)')

add('forge-damage-amount-stage-and-external-death-cache',
    std('next', 'forge:ApugliForgeEventHandler', [
        ('public static void onLivingHurt(', 'writes final amount but callbacks receive earlier amount'),
        ('public static void onLivingAttack(', 'calculation for cancel and crit effects'),
        ('private static float calculateEnchantmentDamage(', 'direct/indirect source split'),
        ('public static void onLivingKilled(', 'external cached damage to kill credit callbacks')]),
    'Forge LivingHurt LOWEST且receiveCanceled=true：先读amount，计算extra与finalAmount并setAmount；只在修改后为0时cancel，回调置于!isCanceled分支内。但传给全部Harm/Nearby/Attacker/Tame回调的是先前amount而非finalAmount。LivingAttack另算一次用于特效和取消；onLivingKilled又从外部Apoli IPowerDataCache.getDamage读取数值，按killCredit或source attacker发死亡动作。',
    '具体新增核验点是回执数值的阶段标签：输入amount、该监听器写回的finalAmount、以及外部死亡缓存不是可互换字段。Carson若保留研究证据，可注明数值在哪个阶段产生，不把该事件阶段额外计成新延迟实现。',
    'IPowerDataCache的生产、年龄、清空实现位于未授权研究的Apoli仓库，本岗没有读，不能断言缓存就是本次成功减血或自有TTL。事件总线后续监听与原版血量结果也未闭合。本条补充batch002致死上下文与附魔伤害同步族，同链/跨loader变体零信用；coordinator既有攻击表现、取消门与真实伤害原则不重复申报。',
    'reviewed_excluded_zero_credit', 'batch002:fatal-damage-snapshot-to-kill-credit and enchantment-damage-phase-guard')


def main():
    index = {x['source_local']: x for x in json.loads((DOCS / 'source-index.json').read_text())}
    for branch in json.loads((DOCS / 'branch-source-index-003.json').read_text()):
        index.update({x['source_local']: x for x in branch['files']})
    unique = {}
    for row in ROWS:
        for e in row['evidence']:
            raw = (WORKSPACE / e['source_local']).read_bytes()
            assert e['source_sha256'] == sha(raw) == index[e['source_local']]['source_sha256']
            assert e['excerpt'] == '\n'.join(raw.decode().splitlines()[e['line'] - 1:e['end_line']])
            unique[(e['revision'], e['path'], e['line'], e['end_line'])] = e
    root = DOCS.parents[1]
    inputs = []
    accepted = []
    for name in ['protocol.json', 'accepted.jsonl', 'reviewed.jsonl',
                 'helpers/coordinator-receipt/batch-001.json', 'helpers/coordinator-receipt/supporting-methods-001.json']:
        p = root / name
        raw = p.read_bytes()
        inputs.append(dict(path=str(p.relative_to(WORKSPACE)), source_sha256=sha(raw), read_only=True))
        if name == 'accepted.jsonl':
            accepted = [json.loads(line) for line in raw.decode().splitlines() if line]
    prior = []
    for name in ['reviewed.jsonl', 'reviewed-002.jsonl']:
        prior.extend(json.loads(line) for line in (DOCS / name).read_text().splitlines() if line)
    exact_main_duplicates = []
    for row in ROWS:
        exact = [x.get('candidate_id') for x in accepted if (x.get('revision'), x.get('path'), x.get('line')) == (row['revision'], row['path'], row['line'])]
        if exact:
            exact_main_duplicates.append(dict(candidate_id=row['candidate_id'], existing=exact))
        assert not exact or row['proposed_credit'] == 0
        assert row['dedup_key'] not in {x.get('dedup_key') for x in prior}
    proposals = [x for x in ROWS if x['proposed_credit']]
    zero = [x for x in ROWS if not x['proposed_credit']]
    dump('batch-003.json', dict(schema_version=1, reviewed_at=NOW, applied_credit=0,
                              final_count_owner='Carson', proposed_valid=len(proposals), entries=proposals))
    dump('excluded-003.json', dict(schema_version=1, credit=0, entries=zero))
    (DOCS / 'reviewed-003.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in ROWS))
    dump('validation-003.json', dict(valid=True, reviewed_groups=len(ROWS), proposed_valid=len(proposals),
                                   zero_credit_groups=len(zero), distinct_complete_method_ranges=len(unique),
                                   evidence_hash_and_range_verified=True, all_source_files_git_blob_verified=True,
                                   credit_applied=0, main_accepted_rows_observed=len(accepted),
                                   exact_main_duplicates=exact_main_duplicates, read_only_inputs=inputs,
                                   game_started=False, server_started=False, downloaded_code_executed=False,
                                   network_requests=7, network_http_errors=0,
                                   historical_branch_names_are_not_release_guarantees=True))
    print(json.dumps(dict(proposals=len(proposals), zero=len(zero), methods=len(unique), credit=0)))


if __name__ == '__main__':
    main()
